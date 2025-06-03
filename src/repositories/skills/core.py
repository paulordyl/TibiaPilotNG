import numpy as np
from typing import Union
from src.shared.typings import BBox, GrayImage
# Removed: from .config import minutesOrHoursHashes, numbersHashes
# The locators import might be removed if getSkillsIconPosition is fully replaced or becomes trivial.
# For now, keep it if Python's getSkillsIconPosition still has some logic,
# otherwise, it will be removed if getSkillsIconPosition is also fully replaced.
# from .locators import getSkillsIconPosition # This will be replaced by Rust version

# Import the new Rust utility module
try:
    from skb_core import rust_utils_module as skb_rust_utils
    # Check for one of the new functions to confirm module contents
    if not hasattr(skb_rust_utils, 'get_hp'): 
        raise ImportError("Specific Rust skill functions not found in skb_core.rust_utils_module")
    RUST_SKILL_FUNCTIONS_LOADED = True
    # print("Successfully loaded Rust skill extraction functions from skb_core.")
except ImportError as e:
    print(f"Could not import Rust skill functions from skb_core: {e}. Skill functions will not work.")
    RUST_SKILL_FUNCTIONS_LOADED = False
    # Define a mock skb_rust_utils to prevent NameError if import fails, allowing module to parse.
    class MockRustSkillsUtils:
        def __getattr__(self, name):
            raise NotImplementedError(f"Rust skill function {name} is not available (skb_core not loaded or function missing).")
    skb_rust_utils = MockRustSkillsUtils()


def _ensure_screenshot_format_for_rust(screenshot: GrayImage) -> Union[np.ndarray, None]:
    """Helper to ensure screenshot is a C-contiguous uint8 NumPy array, 2D."""
    if not isinstance(screenshot, np.ndarray):
        screenshot = np.array(screenshot, dtype=np.uint8)
    if screenshot.dtype != np.uint8:
        screenshot = screenshot.astype(np.uint8) # Ensure uint8
    if screenshot.ndim == 3: # Ensure 2D if it's (H, W, 1)
        if screenshot.shape[2] == 1:
            screenshot = screenshot.squeeze(axis=2)
        else: # True color image, convert to grayscale
            # This should ideally not happen if GrayImage type hint is respected upstream
            print("Warning: Received color image for skill check, converting to grayscale.")
            screenshot = np.dot(screenshot[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
    if not screenshot.flags['C_CONTIGUOUS']:
        screenshot = np.ascontiguousarray(screenshot)
    if screenshot.ndim != 2:
        print(f"Error: Screenshot for skill check is not 2D after processing. Shape: {screenshot.shape}")
        return None
    return screenshot

def getSkillsIconPosition(screenshot: GrayImage) -> Union[BBox, None]:
    """Locates the skills icon using Rust."""
    if not RUST_SKILL_FUNCTIONS_LOADED:
        raise ImportError("Rust skill functions not loaded. Cannot get skills icon position.")
    
    processed_screenshot = _ensure_screenshot_format_for_rust(screenshot)
    if processed_screenshot is None:
        return None
        
    try:
        return skb_rust_utils.get_skills_icon_roi(processed_screenshot)
    except Exception as e:
        print(f"Error calling skb_rust_utils.get_skills_icon_roi: {e}")
        return None

# Helper macro-like function to define skill getters
def _create_skill_getter(skill_name_rust: str):
    def getter_func(screenshot: GrayImage) -> Union[int, None]:
        if not RUST_SKILL_FUNCTIONS_LOADED:
            raise ImportError(f"Rust skill functions not loaded. Cannot get {skill_name_rust}.")
        
        skills_icon_pos = getSkillsIconPosition(screenshot)
        if skills_icon_pos is None:
            return None
            
        processed_screenshot = _ensure_screenshot_format_for_rust(screenshot)
        if processed_screenshot is None:
            return None
            
        try:
            # Dynamically get the correct Rust function (e.g., skb_rust_utils.get_hp, skb_rust_utils.get_mana)
            rust_func = getattr(skb_rust_utils, f"get_{skill_name_rust.lower()}")
            return rust_func(processed_screenshot, skills_icon_pos)
        except AttributeError:
            print(f"Error: Rust function get_{skill_name_rust.lower()} not found in skb_rust_utils.")
            # Fallback or raise error
            return None 
        except Exception as e:
            print(f"Error calling skb_rust_utils.get_{skill_name_rust.lower()}: {e}")
            return None
            
    getter_func.__name__ = f"get{skill_name_rust.capitalize()}"
    getter_func.__doc__ = f"Gets the {skill_name_rust} value using Rust implementation."
    return getter_func

getHp = _create_skill_getter("hp")
getMana = _create_skill_getter("mana")
getCapacity = _create_skill_getter("capacity")
getSpeed = _create_skill_getter("speed")
getFood = _create_skill_getter("food")
getStamina = _create_skill_getter("stamina")
