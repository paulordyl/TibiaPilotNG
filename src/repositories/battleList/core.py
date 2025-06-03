from numba import njit
import numpy as np
from typing import Generator, Union, List
from src.shared.typings import CreatureCategory, CreatureCategoryOrUnknown, GrayImage
from src.utils.core import hashit, locate
# from src.utils.image import RustImageData, _numpy_to_rust_image_data, py_rust_lib # Removed CFFI utils
from .config import creaturesNamesImagesHashes, images
from .extractors import getCreaturesNamesImages
from .typings import CreatureList, Creature

try:
    from skb_core import rust_utils_module
except ImportError as e:
    raise ImportError(
        "Failed to import 'rust_utils_module' from 'skb_core'. "
        "Ensure the skb_core Rust library is compiled and installed in your Python environment. "
        f"Original error: {e}"
    )


# PERF: [0.13737060000000056, 4.999999987376214e-07] # Numba perf comment, can remain
@njit(cache=True, fastmath=True)
def getBeingAttackedCreatureCategory(creatures: CreatureList) -> Union[CreatureCategory, None]:
    for creature in creatures:
        if creature['isBeingAttacked']:
            return creature['name']
    return None


# PERF: [1.3400000000274304e-05, 2.9000000001389026e-06]
def getBeingAttackedCreatures(content: GrayImage, filledSlotsCount: int) -> List[bool]:
    if filledSlotsCount <= 0: # Return empty list if no slots or invalid count
        return []
    try:
        # Call the PyO3 function, which directly returns a Python list of booleans
        results = rust_utils_module.determine_being_attacked(content, filledSlotsCount)
        return results
    except Exception as e:
        # Handle potential errors from the Rust call, e.g., if image conversion fails
        # or if the Rust function itself panics (though PyO3 tries to convert panics to PyErr).
        print(f"Error calling rust_utils_module.determine_being_attacked: {e}")
        # Fallback to returning a list of False, or re-raise, or handle as appropriate.
        # For consistency with previous behavior of returning empty on some errors,
        # we might return a list of False of the expected length.
        return [False] * filledSlotsCount


# PERF: [0.00017040000000001498, 7.330000000038694e-05]
def getCreatures(content: GrayImage) -> CreatureList:
    if content is None: # Check if content is None first
        return []

    filledSlotsCount = getFilledSlotsCount(content)
    if filledSlotsCount == 0:
        return np.array([], dtype=Creature)

    beingAttackedCreatures = getBeingAttackedCreatures(content, filledSlotsCount)
    # Ensure beingAttackedCreatures has the correct length if an error occurred in Rust call
    if len(beingAttackedCreatures) != filledSlotsCount:
        # This might happen if the Rust call failed and returned a default.
        # Decide on a consistent error handling strategy or ensure Rust always returns correct length or raises.
        # For now, assume it might return less if error, or adjust placeholder in Rust to always return correct length.
        # If it's critical, this should raise an error.
        # For robustness, if lengths mismatch, we could pad `beingAttackedCreatures` or truncate `creaturesNames`.
        # Simplest is to proceed, but this could lead to IndexError if lists don't align.
        # A safer approach if Rust might return partial data on error:
        # beingAttackedCreatures = [False] * filledSlotsCount # Or handle specific error
        pass


    creaturesNames = [creatureName for creatureName in getCreaturesNames(
        content, filledSlotsCount)]

    # Ensure lists are of the same length before zipping
    # This is a defensive measure if getBeingAttackedCreatures or getCreaturesNames might not return expected length
    min_len = min(len(creaturesNames), len(beingAttackedCreatures))

    creatures = np.array([(creaturesNames[i], beingAttackedCreatures[i])
                          for i in range(min_len)], dtype=Creature)

    creaturesAfterCheck = checkDust(content, creatures)
    return creaturesAfterCheck


# PERF: [0.019119499999998624, 4.020000000082291e-05]
def getCreaturesNames(content: GrayImage, filledSlotsCount: int) -> Generator[CreatureCategoryOrUnknown, None, None]:
    for creatureNameImage in getCreaturesNamesImages(content, filledSlotsCount):
        yield creaturesNamesImagesHashes.get(hashit(creatureNameImage), 'Unknown')


# PERF: [0.5794668999999999, 3.9999999934536845e-07]
def getFilledSlotsCount(content: GrayImage) -> int:
    try:
        # Call the PyO3 function, which expects a NumPy array directly
        count = rust_utils_module.count_filled_slots(content)
        return count
    except Exception as e:
        # Handle potential errors from the Rust call
        print(f"Error calling rust_utils_module.count_filled_slots: {e}")
        # Fallback to returning 0 or handle as appropriate.
        return 0


# PERF: [7.5999999999964984e-06, 7.999999986907369e-07]
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
