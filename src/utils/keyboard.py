import pyautogui
import random
from src.utils.config_manager import get_config

PYAUTOGUI_KEY_MAP = {
    'esc': 'escape', 'ctrl': 'ctrl', 'alt': 'alt', 'shift': 'shift',
    'enter': 'enter', 'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right',
    'backspace': 'backspace', 'space': 'space', 'tab': 'tab',
    'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4', 'f5': 'f5', 'f6': 'f6',
    'f7': 'f7', 'f8': 'f8', 'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
    'delete': 'delete', 'home': 'home', 'end': 'end', 'pageup': 'pageup', 'pagedown': 'pagedown',
    'insert': 'insert', 'printscreen': 'printscreen', 'scrolllock': 'scrolllock',
    'pause': 'pause', 'capslock': 'capslock', 'numlock': 'numlock',
    # Symbols that pyautogui might expect as names rather than direct characters
    # Depending on pyautogui's behavior, some of these might not be strictly necessary
    # if passing the character itself works.
    # Example: '!' is usually just '!', but if there are issues:
    # '!': 'exclam', '@': 'at', '#': 'numbersign', '$': 'dollar', '%': 'percent',
    # '^': 'circumflex', '&': 'ampersand', '*': 'asterisk', '(': 'leftparen', ')': 'rightparen',
    # '_': 'underscore', '+': 'plus', '=': 'equal', '-': 'minus',
    # '[': 'leftbracket', ']': 'rightbracket', '{': 'leftbrace', '}': 'rightbrace',
    # '\\': 'backslash', '|': 'bar', ';': 'semicolon', ':': 'colon',
    # "'": 'apostrophe', '"': 'quotedbl', ',': 'comma', '.': 'period',
    # '<': 'less', '>': 'greater', '/': 'slash', '?': 'question'
    # For now, the initial list from the prompt is used, plus a few common ones.
    # Single characters are handled by map_key_to_pyautogui directly.
}

def map_key_to_pyautogui(key: str) -> str:
    if not key:
        return None
    sanitized_key = key.lower()
    if sanitized_key in PYAUTOGUI_KEY_MAP:
        return PYAUTOGUI_KEY_MAP[sanitized_key]
    # For single characters (letters, numbers, symbols not in map)
    # pyautogui handles these directly.
    if len(sanitized_key) == 1:
        return sanitized_key
    # Add any specific numeric keys if needed, e.g. '0' maps to '0'
    if sanitized_key.isdigit(): # Ensures '1', '2' etc are passed directly
        return sanitized_key
    # Return None for unmapped/unrecognized multi-character keys not in the map
    print(f"Warning: Key '{key}' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")
    return None

def hotkey(*args):
    mapped_args = [map_key_to_pyautogui(key) for key in args]
    # Filter out any None values that map_key_to_pyautogui might return
    valid_mapped_args = [arg for arg in mapped_args if arg is not None]
    if valid_mapped_args:
        pyautogui.hotkey(*valid_mapped_args)

def keyDown(key: str):
    mapped_key = map_key_to_pyautogui(key)
    if mapped_key:
        pyautogui.keyDown(mapped_key)

def keyUp(key: str):
    mapped_key = map_key_to_pyautogui(key)
    if mapped_key:
        pyautogui.keyUp(mapped_key)

def press(*args):
    # Assuming sequential presses as per prompt.
    # If a single string argument is passed, treat it as a sequence of characters to press.
    # If multiple arguments are passed, press them sequentially.
    if len(args) == 1 and isinstance(args[0], str) and len(args[0]) > 1 and map_key_to_pyautogui(args[0]) is None :
        # This handles if a single string like "hello" is passed to press,
        # but it's not a special key name itself.
        # In this case, pyautogui.press("h", "e", "l", "l", "o") is desired.
        # However, pyautogui.press() itself doesn't iterate a string, it types it.
        # The current map_key_to_pyautogui would return None for "hello".
        # Let's stick to the prompt: map each key and press.
        # If "hello" is passed, it will be mapped to None and ignored by this logic.
        # The user should pass 'h', 'e', 'l', 'l', 'o' as separate args for sequential press.
        # Or use write() for typing a phrase.
        pass # This condition is tricky, let's rely on map_key_to_pyautogui for each arg

    mapped_keys = [map_key_to_pyautogui(key) for key in args]
    valid_mapped_keys = [k for k in mapped_keys if k is not None]
    for k in valid_mapped_keys:
        pyautogui.press(k)


def write(phrase: str):
    # PyAutoGUI's write function handles typing strings directly.
    # No need to map individual characters for `write`.
    min_interval = get_config('keyboard_delays.write_interval_min', 0.03)
    max_interval = get_config('keyboard_delays.write_interval_max', 0.12)
    interval = random.uniform(min_interval, max_interval)
    pyautogui.write(phrase, interval=interval)

# The old getAsciiFromKey function is now removed.
