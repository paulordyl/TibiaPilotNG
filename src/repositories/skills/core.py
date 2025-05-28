import numpy as np
from typing import Union
from src.shared.typings import BBox, GrayImage
# Removed: from src.utils.core import hashit
# Removed: from src.utils.image import convertGraysToBlack
from .config import minutesOrHoursHashes, numbersHashes
from .locators import getSkillsIconPosition

RUST_SKILL_FUNCTIONS_LOADED = False
try:
    from gameplay.py_rust_utils_module import (
        get_hp_rust,
        get_mana_rust,
        get_capacity_rust,
        get_speed_rust,
        get_food_rust,
        get_stamina_rust
    )
    RUST_SKILL_FUNCTIONS_LOADED = True
    # print("Successfully loaded Rust skill extraction functions.")
except ImportError as e:
    print(f"Could not import Rust skill functions: {e}. Falling back to Python or raising error.")
    # Depending on desired behavior, can raise error or have Python fallbacks.
    # For this task, the functions below will raise if not loaded.


def getHp(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get HP.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    # Ensure screenshot is np.ndarray of np.uint8
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_hp_rust(screenshot, skillsIconPosition, numbersHashes)


def getMana(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get Mana.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_mana_rust(screenshot, skillsIconPosition, numbersHashes)


def getCapacity(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get Capacity.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_capacity_rust(screenshot, skillsIconPosition, numbersHashes)


def getSpeed(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get Speed.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_speed_rust(screenshot, skillsIconPosition, numbersHashes)


def getFood(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get Food.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_food_rust(screenshot, skillsIconPosition, minutesOrHoursHashes)


def getStamina(screenshot: GrayImage) -> Union[int, None]:
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get Stamina.")
    skillsIconPosition = getSkillsIconPosition(screenshot)
    if skillsIconPosition is None:
        return None
    if not isinstance(screenshot, np.ndarray) or screenshot.dtype != np.uint8:
        screenshot = np.array(screenshot, dtype=np.uint8)
    return get_stamina_rust(screenshot, skillsIconPosition, minutesOrHoursHashes)

# Obsolete Python functions getMinutesCount and getValuesCount are removed.
