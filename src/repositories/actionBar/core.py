# import pytesseract # No longer needed for getSlotCount
import numpy as np
from typing import Union
import src.repositories.actionBar.extractors as actionBarExtractors
import src.repositories.actionBar.locators as actionBarLocators
from src.shared.typings import GrayImage
import src.utils.core as coreUtils # Retain for hashit in getSlotCountOld if needed
from .config import hashes, images
# from skimage import exposure # No longer needed for getSlotCount

# pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe" # Not needed if Rust handles OCR

# Attempt to import the new PyO3 OCR function along with existing ones
try:
    from skb_core import rust_utils_module as skb_rust_utils
    # Check if the specific OCR function is available, otherwise, other functions might still be usable.
    if not hasattr(skb_rust_utils, 'perform_ocr_on_slot_image'):
        print("Warning: skb_rust_utils.perform_ocr_on_slot_image not found. getSlotCount will fail.")
        # Optionally, define a mock for it to prevent AttributeError if only this one is missing
        # class MockOcr: def perform_ocr_on_slot_image(self, *args, **kwargs): raise NotImplementedError("perform_ocr_on_slot_image mock")
        # skb_rust_utils.perform_ocr_on_slot_image = MockOcr().perform_ocr_on_slot_image
except ImportError:
    class MockRustUtils:
        def __getattr__(self, name):
            print(f"Attempted to call '{name}' on a non-existent skb_rust_utils module.")
            raise AttributeError(f"Rust function {name} is not available (skb_core.rust_utils_module not found).")
    skb_rust_utils = MockRustUtils()
    print("Warning: skb_core.rust_utils_module not found. Using a mock object. Ensure Rust library is compiled and in PYTHONPATH.")


RUST_ACTION_BAR_FUNCTIONS_LOADED = False
try:
    # Assuming these might come from a different (older?) Rust module or are separate.
    # If they are also in skb_core.rust_utils_module, this import block might need adjustment
    # or could be merged with the skb_rust_utils import above.
    # For now, keeping it separate as per original structure.
    # The following specific FFI functions might be from an older setup.
    # We are replacing check_specific_cooldown_rust with skb_rust_utils.check_cooldown_status.
    # is_action_bar_slot_equipped_rust and is_action_bar_slot_available_rust are not part of this subtask's scope for migration.
    # If they are also intended to be part of skb_core.rust_utils_module, their import should be consolidated.
    # gameplay.py_rust_utils_module imports are removed as their functionalities
    # (check_specific_cooldown_rust, is_action_bar_slot_equipped_rust, is_action_bar_slot_available_rust)
    # are being replaced by skb_core.rust_utils_module equivalents.
    RUST_ACTION_BAR_FUNCTIONS_LOADED = True # Assuming skb_rust_utils is the source of truth now.
    # If specific functions from gameplay module were still needed, their imports would remain.
    # For this task, we aim to fully migrate the specified functionalities.
except ImportError: # This top-level try-except now primarily catches skb_core import issues
    class MockRustUtils: # Defined earlier if skb_core import fails
        pass # Already has getattr defined
    # RUST_ACTION_BAR_FUNCTIONS_LOADED = False # Set by the skb_core import failure
    print("Critical: skb_core.rust_utils_module failed to load. All Rust-dependent functions will fail.")

# Mock individual functions if skb_rust_utils itself loaded but specific functions are missing (e.g., during development)
if hasattr(skb_rust_utils, '__class__') and skb_rust_utils.__class__.__name__ != 'MockRustUtils': # Check if not the main mock
    if not hasattr(skb_rust_utils, 'has_cooldown_by_name'):
        def mock_has_cooldown_by_name(*args, **kwargs): raise NotImplementedError("skb_rust_utils.has_cooldown_by_name missing")
        skb_rust_utils.has_cooldown_by_name = mock_has_cooldown_by_name
        print("Warning: skb_rust_utils.has_cooldown_by_name is not available. Using mock.")

    if not hasattr(skb_rust_utils, 'check_cooldown_status'):
        def mock_check_cooldown_status(*args, **kwargs): raise NotImplementedError("skb_rust_utils.check_cooldown_status missing")
        skb_rust_utils.check_cooldown_status = mock_check_cooldown_status
        print("Warning: skb_rust_utils.check_cooldown_status is not available. Using mock.")

    if not hasattr(skb_rust_utils, 'get_action_bar_roi'):
        def mock_get_action_bar_roi(*args, **kwargs): raise NotImplementedError("skb_rust_utils.get_action_bar_roi missing")
        skb_rust_utils.get_action_bar_roi = mock_get_action_bar_roi
        print("Warning: skb_rust_utils.get_action_bar_roi is not available. Using mock.")

    if not hasattr(skb_rust_utils, 'is_slot_equipped'):
        def mock_is_slot_equipped(*args, **kwargs): raise NotImplementedError("skb_rust_utils.is_slot_equipped missing")
        skb_rust_utils.is_slot_equipped = mock_is_slot_equipped
        print("Warning: skb_rust_utils.is_slot_equipped is not available. Using mock.")
    
    if not hasattr(skb_rust_utils, 'is_slot_available'):
        def mock_is_slot_available(*args, **kwargs): raise NotImplementedError("skb_rust_utils.is_slot_available missing")
        skb_rust_utils.is_slot_available = mock_is_slot_available
        print("Warning: skb_rust_utils.is_slot_available is not available. Using mock.")
else: # skb_rust_utils is the MockRustUtils because skb_core failed to import
    RUST_ACTION_BAR_FUNCTIONS_LOADED = False


# TODO: add unit tests
# PERF: [0.04209370000000012, 9.999999999621423e-06] (Original perf comment)
def getSlotCount(screenshot: GrayImage, slot: int) -> Union[int, None]:
    leftSideArrowsPos = actionBarLocators.getLeftArrowsPosition(screenshot)
    if leftSideArrowsPos is None:
        return None
    x0 = leftSideArrowsPos[0] + leftSideArrowsPos[2] + \
        (slot * 2) + ((slot - 1) * 34)
    # slotImage = screenshot[leftSideArrowsPos[1]:leftSideArrowsPos[1] + 34, x0:x0 + 34] # Full slot
    # The OCR region was more specific:
    digits_slot_image = screenshot[leftSideArrowsPos[1] + 24:leftSideArrowsPos[1] + 32, x0 + 3:x0 + 33]

    # Ensure digits_slot_image is a 2D np.uint8 grayscale NumPy array
    if not isinstance(digits_slot_image, np.ndarray) or digits_slot_image.dtype != np.uint8:
        digits_slot_image = np.array(digits_slot_image, dtype=np.uint8)
    
    if digits_slot_image.ndim == 3 and digits_slot_image.shape[2] == 1: # If (H, W, 1)
        digits_slot_image = digits_slot_image.squeeze(axis=2)
    elif digits_slot_image.ndim == 3: # If color, try to convert to gray
        # This case should ideally not happen if screenshot is GrayImage and processed correctly
        print("Warning: getSlotCount received a color slotImage for OCR, attempting grayscale conversion.")
        digits_slot_image = np.dot(digits_slot_image[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

    if digits_slot_image.ndim != 2:
        print(f"Error: digits_slot_image is not 2D after processing, shape: {digits_slot_image.shape}")
        return None # Or 0, based on previous behavior for empty count

    if not digits_slot_image.flags['C_CONTIGUOUS']:
        digits_slot_image = np.ascontiguousarray(digits_slot_image)

    try:
        # Call the Rust OCR function
        # perform_ocr_on_slot_image expects PyReadonlyArray2<u8>
        ocr_result = skb_rust_utils.perform_ocr_on_slot_image(digits_slot_image)
        
        if ocr_result is None:
            return 0 # Original logic returned 0 for empty pytesseract count
        
        return ocr_result # Rust function directly returns Option<i32>, PyO3 converts to int or None
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.perform_ocr_on_slot_image: {e}. Ensure skb_core module is correctly built and imported.")
        # Fallback or raise error. For now, returning None to indicate failure.
        return None 
    except Exception as e:
        print(f"An error occurred during Rust OCR processing: {e}")
        return None


def getSlotCountOld(screenshot: GrayImage, slot: int) -> Union[int, None]:
    leftSideArrowsPos = actionBarLocators.getLeftArrowsPosition(screenshot)
    if leftSideArrowsPos is None:
        return None
    x0 = leftSideArrowsPos[0] + leftSideArrowsPos[2] + \
        (slot * 2) + ((slot - 1) * 34)
    slotImage = screenshot[leftSideArrowsPos[1]:leftSideArrowsPos[1] + 34, x0:x0 + 34]
    digits = slotImage[24:32, 2:32]
    count = 0
    # math.pow is not defined, assuming it was meant to be from math module, which is not imported.
    # This function seems to be old/unused. Keeping it as is per instruction.
    # For it to work, `import math` would be needed.
    power_val = 1 
    for i in range(5):
        x = ((6 * (5 - i)) - 3)
        number_img_region = digits[2:6, x:x + 1]
        # Ensure it's np.uint8 for hashit if it's still the old one
        if not isinstance(number_img_region, np.ndarray) or number_img_region.dtype != np.uint8:
             number_img_region = np.array(number_img_region, dtype=np.uint8)
        number = images['digits'].get(
            coreUtils.hashit(number_img_region), None) # Assuming coreUtils.hashit is still available
        if number is None:
            # If number is None, it implies 0 for that position but doesn't stop accumulation
            power_val *= 10
            continue
        count += number * power_val
        power_val *= 10
    return int(count)


# Removing hasCooldownByImage as its logic is now in Rust's has_cooldown_by_name
# def hasCooldownByImage(screenshot: GrayImage, cooldownImage: GrayImage) -> Union[bool, None]:
#     ...

def _ensure_screenshot_format(screenshot: GrayImage) -> Union[np.ndarray, None]:
    """Helper to ensure screenshot is a C-contiguous uint8 NumPy array."""
    if not isinstance(screenshot, np.ndarray):
        # This case should ideally be handled by type hints, but good for runtime safety.
        print("Warning: screenshot is not a NumPy array. Attempting conversion.")
        screenshot = np.array(screenshot, dtype=np.uint8)
    if screenshot.dtype != np.uint8:
        screenshot = screenshot.astype(np.uint8)
    if not screenshot.flags['C_CONTIGUOUS']:
        screenshot = np.ascontiguousarray(screenshot)
    if screenshot.ndim == 3 and screenshot.shape[2] == 1: # If (H, W, 1)
        screenshot = screenshot.squeeze(axis=2)
    elif screenshot.ndim == 3: # If color, try to convert to gray. Rust expects 2D.
        print("Warning: Cooldown check received a color image, attempting grayscale conversion for Rust.")
        screenshot = np.dot(screenshot[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)

    if screenshot.ndim != 2:
        print(f"Error: Screenshot for cooldown check is not 2D after processing. Shape: {screenshot.shape}")
        return None
    return screenshot

def hasCooldownByName(screenshot: GrayImage, name: str) -> Union[bool, None]:
    """Checks if a specific named cooldown is active using Rust implementation."""
    processed_screenshot = _ensure_screenshot_format(screenshot)
    if processed_screenshot is None:
        return None # Or False, depending on desired error behavior for bad input
    try:
        return skb_rust_utils.has_cooldown_by_name(processed_screenshot, name)
    except AttributeError as e: # skb_rust_utils might be a mock if import failed
        print(f"Error calling skb_rust_utils.has_cooldown_by_name for '{name}': {e}.")
        raise # Or return default / handle
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.has_cooldown_by_name for '{name}': {e}")
        return None # Or False

def _check_group_cooldown(screenshot: GrayImage, group_name: str) -> Union[bool, None]:
    """Helper to check group cooldowns using Rust."""
    processed_screenshot = _ensure_screenshot_format(screenshot)
    if processed_screenshot is None:
        return None # Or False
    try:
        return skb_rust_utils.check_cooldown_status(processed_screenshot, group_name)
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.check_cooldown_status for '{group_name}': {e}.")
        raise # Or return default / handle
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.check_cooldown_status for '{group_name}': {e}")
        return None # Or False

def hasAttackCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return _check_group_cooldown(screenshot, "attack")

def hasExoriCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "exori") # Assuming "exori" is a key in Rust's cooldown_templates

def hasExoriGranCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "exori gran") # Key needs to match Rust

def hasExoriMasCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "exori mas") # Key needs to match Rust

def hasExuraGranIcoCooldown(screenshot: GrayImage) -> Union[bool, None]:
    # Python used 'utura gran' for this, ensure Rust key matches if this is intentional
    return hasCooldownByName(screenshot, "utura gran") 

def hasExoriMinCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "exori min") # Key needs to match Rust

def hasHealingCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return _check_group_cooldown(screenshot, "healing")

def hasSupportCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return _check_group_cooldown(screenshot, "support")

def hasUturaCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "utura") # Key needs to match Rust

def hasUturaGranCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByName(screenshot, "utura gran") # Key needs to match Rust


def slotIsEquipped(screenshot: GrayImage, slot: int) -> Union[bool, None]:
    processed_screenshot = _ensure_screenshot_format(screenshot)
    if processed_screenshot is None:
        return None # Or False, based on error policy

    try:
        # get_action_bar_roi returns Option<(i32, i32, u32, u32)> for the left arrow position and size
        action_bar_roi = skb_rust_utils.get_action_bar_roi(processed_screenshot)
        if action_bar_roi is None:
            # print("Action bar ROI (left arrow) not found by Rust in slotIsEquipped")
            return None # Or False

        bar_x, bar_y, left_arrow_width, _ = action_bar_roi # Unpack (x, y, w, h) of left arrow

        if slot <= 0: # Rust function expects 1-indexed slot (u32 but > 0)
            print("Warning: slotIsEquipped called with invalid slot number <= 0.")
            return False
        
        return skb_rust_utils.is_slot_equipped(processed_screenshot, slot, bar_x, bar_y, left_arrow_width)
    except AttributeError as e: # Handle if skb_rust_utils or its methods are mocks
        print(f"Error calling Rust function in slotIsEquipped for slot {slot}: {e}.")
        raise 
    except Exception as e:
        print(f"An error occurred in slotIsEquipped for slot {slot}: {e}")
        return None # Or False


def slotIsAvailable(screenshot: GrayImage, slot: int) -> Union[bool, None]:
    processed_screenshot = _ensure_screenshot_format(screenshot)
    if processed_screenshot is None:
        return None # Or False

    try:
        action_bar_roi = skb_rust_utils.get_action_bar_roi(processed_screenshot)
        if action_bar_roi is None:
            # print("Action bar ROI (left arrow) not found by Rust in slotIsAvailable")
            # Match original behavior: if arrows not found, slot is considered available.
            return True 
            
        bar_x, bar_y, left_arrow_width, _ = action_bar_roi

        if slot <= 0: # Rust function expects 1-indexed slot (u32 but > 0)
            print("Warning: slotIsAvailable called with invalid slot number <= 0.")
            return True # Default to available for invalid slot, or handle as error
            
        return skb_rust_utils.is_slot_available(processed_screenshot, slot, bar_x, bar_y, left_arrow_width)
    except AttributeError as e:
        print(f"Error calling Rust function in slotIsAvailable for slot {slot}: {e}.")
        raise
    except Exception as e:
        print(f"An error occurred in slotIsAvailable for slot {slot}: {e}")
        return None # Or True, to match original default
