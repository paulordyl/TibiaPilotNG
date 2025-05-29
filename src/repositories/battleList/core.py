import ctypes # Added
from numba import njit
import numpy as np
from typing import Generator, Union, List # Added List
from src.shared.typings import CreatureCategory, CreatureCategoryOrUnknown, GrayImage
from src.utils.core import hashit, locate
from src.utils.image import RustImageData, _numpy_to_rust_image_data, py_rust_lib # Added
from .config import creaturesNamesImagesHashes, images
from .extractors import getCreaturesNamesImages
from .typings import CreatureList, Creature


# FFI Function Signature Setup 

# count_filled_slots_rust
if hasattr(py_rust_lib, 'count_filled_slots_rust'):
    py_rust_lib.count_filled_slots_rust.argtypes = [RustImageData]
    py_rust_lib.count_filled_slots_rust.restype = ctypes.c_int32
else:
    # Consistent with warnings in other modules
    print("Warning: FFI function 'count_filled_slots_rust' not found in py_rust_lib.")

# determine_being_attacked_rust
if hasattr(py_rust_lib, 'determine_being_attacked_rust'):
    py_rust_lib.determine_being_attacked_rust.argtypes = [
        RustImageData,      # battle_list_content_data
        ctypes.c_int32      # filled_slots_count
    ]
    py_rust_lib.determine_being_attacked_rust.restype = ctypes.POINTER(ctypes.c_bool)
else:
    print("Warning: FFI function 'determine_being_attacked_rust' not found in py_rust_lib.")

# free_rust_bool_array
if hasattr(py_rust_lib, 'free_rust_bool_array'):
    py_rust_lib.free_rust_bool_array.argtypes = [
        ctypes.POINTER(ctypes.c_bool),  # pointer to the boolean array
        ctypes.c_size_t                 # number of elements in the array
    ]
    py_rust_lib.free_rust_bool_array.restype = None
else:
    print("Warning: FFI function 'free_rust_bool_array' not found in py_rust_lib.")


# PERF: [0.13737060000000056, 4.999999987376214e-07]
@njit(cache=True, fastmath=True)
def getBeingAttackedCreatureCategory(creatures: CreatureList) -> Union[CreatureCategory, None]:
    for creature in creatures:
        if creature['isBeingAttacked']:
            return creature['name']
    return None


# PERF: [1.3400000000274304e-05, 2.9000000001389026e-06] # Original PERF comment
def getBeingAttackedCreatures(content: GrayImage, filledSlotsCount: int) -> List[bool]:
    if not hasattr(py_rust_lib, 'determine_being_attacked_rust') or \
       not hasattr(py_rust_lib, 'free_rust_bool_array'):
        raise RuntimeError("Rust FFI functions for getBeingAttackedCreatures are not available.")

    if _numpy_to_rust_image_data is None:
        raise RuntimeError("Helper function '_numpy_to_rust_image_data' is not available.")

    if filledSlotsCount == 0:
        return []

    # Convert input GrayImage to RustImageData
    rust_content_data = _numpy_to_rust_image_data(content, "GRAY")

    # Call the FFI function
    bool_array_ptr = py_rust_lib.determine_being_attacked_rust(
        rust_content_data,
        ctypes.c_int32(filledSlotsCount)
    )

    results = []
    if bool_array_ptr:
        try:
            # Convert C array of booleans to Python list
            for i in range(filledSlotsCount):
                results.append(bool(bool_array_ptr[i]))
        finally:
            # Free the memory allocated by Rust
            py_rust_lib.free_rust_bool_array(bool_array_ptr, ctypes.c_size_t(filledSlotsCount))
    else:
        # Handle null pointer return from Rust, e.g., allocation failure in Rust
        # Return empty list or raise an error. For now, empty list.
        print("Warning: determine_being_attacked_rust returned a null pointer.")
    
    return results


# PERF: [0.00017040000000001498, 7.330000000038694e-05] # Original PERF comment
def getCreatures(content: GrayImage) -> CreatureList:
    if content is not None:
        filledSlotsCount = getFilledSlotsCount(content)
        if filledSlotsCount == 0:
            return np.array([], dtype=Creature)
        beingAttackedCreatures = [
            beingAttackedCreature for beingAttackedCreature in getBeingAttackedCreatures(content, filledSlotsCount)]
        creaturesNames = [creatureName for creatureName in getCreaturesNames(
            content, filledSlotsCount)]
        creatures = np.array([(creatureName, beingAttackedCreatures[slotIndex])
                        for slotIndex, creatureName in enumerate(creaturesNames)], dtype=Creature)
        creaturesAfterCheck = checkDust(content, creatures)
        return creaturesAfterCheck
    else:
        return []


# PERF: [0.019119499999998624, 4.020000000082291e-05]
def getCreaturesNames(content: GrayImage, filledSlotsCount: int) -> Generator[CreatureCategoryOrUnknown, None, None]:
    for creatureNameImage in getCreaturesNamesImages(content, filledSlotsCount):
        yield creaturesNamesImagesHashes.get(hashit(creatureNameImage), 'Unknown')


# PERF: [0.5794668999999999, 3.9999999934536845e-07] # Original PERF comment
def getFilledSlotsCount(content: GrayImage) -> int:
    if not hasattr(py_rust_lib, 'count_filled_slots_rust'):
        raise RuntimeError("Rust FFI function 'count_filled_slots_rust' is not available.")
    
    if _numpy_to_rust_image_data is None: # Should have been imported
        raise RuntimeError("Helper function '_numpy_to_rust_image_data' is not available.")

    # Convert input GrayImage (NumPy array) to RustImageData
    # Assuming "GRAY" format for single channel image data.
    rust_content_data = _numpy_to_rust_image_data(content, "GRAY")

    # Call the FFI function
    count = py_rust_lib.count_filled_slots_rust(rust_content_data)
    
    return count


# PERF: [7.5999999999964984e-06, 7.999999986907369e-07] # Original PERF comment
def hasSkull(content: GrayImage, creatures: CreatureList) -> bool:
    for creatureIndex, creature in enumerate(creatures):
        if creature['name'] != 'Unknown':
            continue
        y = (creatureIndex * 22)
        creatureIconsImage = content[y + 2:y + 13, -38:-2]
        if locate(creatureIconsImage, images['skulls']['black']):
            return True
        if locate(creatureIconsImage, images['skulls']['orange']):
            return True
        if locate(creatureIconsImage, images['skulls']['red']):
            return True
        if locate(creatureIconsImage, images['skulls']['white']):
            return True
        if locate(creatureIconsImage, images['skulls']['yellow']):
            return True
    return False

def checkDust(content: GrayImage, creatures: CreatureList):
    for creatureIndex, creature in enumerate(creatures):
        if creature['name'] != 'Unknown':
            continue
        y = (creatureIndex * 22)
        creatureIconsImage = content[y + 2:y + 13, -38:-2]
        if locate(creatureIconsImage, images['icons']['dust'], confidence=0.75):
            creature['name'] = 'Dusted'
    return creatures

# PERF: [4.499999999296733e-06, 9.999999992515995e-07]
@njit(cache=True, fastmath=True)
def isAttackingSomeCreature(creatures: CreatureList) -> bool:
    if creatures is not None and len(creatures) > 0:
        for isBeingAttacked in creatures['isBeingAttacked']:
            if isBeingAttacked:
                return True
    return False
