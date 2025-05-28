import pytesseract
import numpy as np
from typing import Union
import src.repositories.actionBar.extractors as actionBarExtractors
import src.repositories.actionBar.locators as actionBarLocators
from src.shared.typings import GrayImage
import src.utils.core as coreUtils # Retain for hashit in getSlotCountOld if needed, though not ideal
from .config import hashes, images
from skimage import exposure

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

RUST_ACTION_BAR_FUNCTIONS_LOADED = False
try:
    from gameplay.py_rust_utils_module import (
        check_specific_cooldown_rust,
        is_action_bar_slot_equipped_rust,
        is_action_bar_slot_available_rust
    )
    RUST_ACTION_BAR_FUNCTIONS_LOADED = True
    # print("Successfully loaded Rust action bar functions.")
except ImportError as e:
    print(f"Could not import Rust action bar functions: {e}. Falling back to Python or raising error.")
    # For this task, functions below will raise if not loaded.

# TODO: add unit tests
# PERF: [0.04209370000000012, 9.999999999621423e-06]
def getSlotCount(screenshot: GrayImage, slot: int) -> Union[int, None]:
    leftSideArrowsPos = actionBarLocators.getLeftArrowsPosition(screenshot)
    if leftSideArrowsPos is None:
        return None
    x0 = leftSideArrowsPos[0] + leftSideArrowsPos[2] + \
        (slot * 2) + ((slot - 1) * 34)
    slotImage = screenshot[leftSideArrowsPos[1]:leftSideArrowsPos[1] + 34, x0:x0 + 34]
    digits = slotImage[24:32, 3:33]
    
    number_region_image = np.array(digits, dtype=np.uint8)

    stretch = exposure.rescale_intensity(number_region_image, in_range=(50,175), out_range=(0,255)).astype(np.uint8)

    equalized = exposure.equalize_hist(stretch)

    equalized_image = (equalized * 255).astype(np.uint8)

    count = pytesseract.image_to_string(equalized_image, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

    if not count:
        return 0

    return int(count)

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


def hasCooldownByImage(screenshot: GrayImage, cooldownImage: GrayImage) -> Union[bool, None]:
    listOfCooldownsImage = actionBarExtractors.getCooldownsImage(screenshot)
    if listOfCooldownsImage is None:
        return None
    cooldownImagePosition = coreUtils.locate(
        listOfCooldownsImage, cooldownImage)
    if cooldownImagePosition is None:
        return False
    # Assuming the check is for a specific pixel indicating cooldown (e.g., white pixel)
    return listOfCooldownsImage[20:21, cooldownImagePosition[0]:cooldownImagePosition[0] + cooldownImagePosition[2]][0][0] == 255


def hasCooldownByName(screenshot: GrayImage, name: str) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns'][name])


def hasAttackCooldown(screenshot: GrayImage) -> Union[bool, None]:
    if not RUST_ACTION_BAR_FUNCTIONS_LOADED:
        raise ImportError("Rust action bar functions not loaded. Cannot check attack cooldown.")
    listOfCooldownsImage = actionBarExtractors.getCooldownsImage(screenshot)
    if listOfCooldownsImage is None:
        return None
    if not isinstance(listOfCooldownsImage, np.ndarray) or listOfCooldownsImage.dtype != np.uint8:
        listOfCooldownsImage = np.array(listOfCooldownsImage, dtype=np.uint8)
    return check_specific_cooldown_rust(listOfCooldownsImage, "attack", hashes['cooldowns'])


def hasExoriCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['exori'])


def hasExoriGranCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['exori gran'])


def hasExoriMasCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['exori mas'])


def hasExuraGranIcoCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['utura gran']) # Assuming 'utura gran' is correct key


def hasExoriMinCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['exori min'])


def hasHealingCooldown(screenshot: GrayImage) -> Union[bool, None]:
    if not RUST_ACTION_BAR_FUNCTIONS_LOADED:
        raise ImportError("Rust action bar functions not loaded. Cannot check healing cooldown.")
    listOfCooldownsImage = actionBarExtractors.getCooldownsImage(screenshot)
    if listOfCooldownsImage is None:
        return None
    if not isinstance(listOfCooldownsImage, np.ndarray) or listOfCooldownsImage.dtype != np.uint8:
        listOfCooldownsImage = np.array(listOfCooldownsImage, dtype=np.uint8)
    return check_specific_cooldown_rust(listOfCooldownsImage, "healing", hashes['cooldowns'])


def hasSupportCooldown(screenshot: GrayImage) -> Union[bool, None]:
    if not RUST_ACTION_BAR_FUNCTIONS_LOADED:
        raise ImportError("Rust action bar functions not loaded. Cannot check support cooldown.")
    listOfCooldownsImage = actionBarExtractors.getCooldownsImage(screenshot)
    if listOfCooldownsImage is None:
        return None
    if not isinstance(listOfCooldownsImage, np.ndarray) or listOfCooldownsImage.dtype != np.uint8:
        listOfCooldownsImage = np.array(listOfCooldownsImage, dtype=np.uint8)
    return check_specific_cooldown_rust(listOfCooldownsImage, "support", hashes['cooldowns'])


def hasUturaCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['utura'])


def hasUturaGranCooldown(screenshot: GrayImage) -> Union[bool, None]:
    return hasCooldownByImage(screenshot, images['cooldowns']['utura gran'])


def slotIsEquipped(screenshot: GrayImage, slot: int) -> Union[bool, None]:
    if not RUST_ACTION_BAR_FUNCTIONS_LOADED:
        raise ImportError("Rust action bar functions not loaded. Cannot check if slot is equipped.")
    leftSideArrowsPos = actionBarLocators.getLeftArrowsPosition(screenshot)
    if leftSideArrowsPos is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    # Rust function expects slot as u32. Python int can be directly passed if non-negative.
    if slot < 0: # Or handle as error, Rust function takes u32
        return False 
    return is_action_bar_slot_equipped_rust(screenshot, leftSideArrowsPos[0], leftSideArrowsPos[1], leftSideArrowsPos[2], slot)


def slotIsAvailable(screenshot: GrayImage, slot: int) -> Union[bool, None]:
    if not RUST_ACTION_BAR_FUNCTIONS_LOADED:
        raise ImportError("Rust action bar functions not loaded. Cannot check if slot is available.")
    leftSideArrowsPos = actionBarLocators.getLeftArrowsPosition(screenshot)
    if leftSideArrowsPos is None:
        # Original Python code might imply True if arrows not found, Rust implies an issue or needs specific handling.
        # For now, if arrows aren't found, can't determine slot availability, returning None or True (as if available by default).
        # Let's match the original Python behavior pattern: if a locator fails, often returns None or a default.
        # The Rust functions return bool, so Python needs to decide what to do if leftSideArrowsPos is None.
        # Here, returning True as a safe default (slot is considered available if context is missing).
        return True 
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    if slot < 0: # Rust function takes u32
        return True # Or handle as error
    return is_action_bar_slot_available_rust(screenshot, leftSideArrowsPos[0], leftSideArrowsPos[1], leftSideArrowsPos[2], slot)
