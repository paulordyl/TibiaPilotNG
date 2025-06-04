# src/utils/keyboard.py
import time
try:
    # Attempt to import the Rust extension module
    # The actual name 'skb_input_rust' is defined in the Rust lib's #[pymodule] name attribute
    # and the [lib] name in skb_input's Cargo.toml
    import skb_input_rust
    RUST_INPUT_AVAILABLE = True
    print("Successfully imported Rust `skb_input_rust` module for keyboard.")
except ImportError as e:
    RUST_INPUT_AVAILABLE = False
    print(f"Failed to import Rust `skb_input_rust` module for keyboard: {e}")
    print("Keyboard functions will be no-ops or raise errors.")

# Removed getAsciiFromKey as this logic is now in Rust string_to_enigo_key

def hotkey(*args, interval: float = 0.01):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Keyboard 'hotkey' will be a no-op.")
        return

    try:
        for key_str in args:
            # Key validation (optional, Rust side also does it)
            if not isinstance(key_str, str):
                print(f"Hotkey: Invalid key '{key_str}', must be a string. Skipping.")
                continue
            skb_input_rust.send_key_event_py(key_str, True) # Press
        
        if interval > 0:
            time.sleep(interval)

        for key_str in args:
            if not isinstance(key_str, str):
                # Already warned above, but good to be safe
                continue
            skb_input_rust.send_key_event_py(key_str, False) # Release
    except RuntimeError as e: # Catch PyRuntimeError from Rust
        print(f"Error during hotkey execution: {e}")
    except Exception as e: # Catch any other unexpected errors
        print(f"Unexpected error during hotkey: {e}")


def keyDown(key: str):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Keyboard 'keyDown' will be a no-op.")
        return
    if not isinstance(key, str):
        print(f"keyDown: Invalid key '{key}', must be a string.")
        return
        
    try:
        skb_input_rust.send_key_event_py(key, True) # Press
    except RuntimeError as e:
        print(f"Error during keyDown for key '{key}': {e}")
    except Exception as e:
        print(f"Unexpected error during keyDown for key '{key}': {e}")


def keyUp(key: str):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Keyboard 'keyUp' will be a no-op.")
        return
    if not isinstance(key, str):
        print(f"keyUp: Invalid key '{key}', must be a string.")
        return

    try:
        skb_input_rust.send_key_event_py(key, False) # Release
    except RuntimeError as e:
        print(f"Error during keyUp for key '{key}': {e}")
    except Exception as e:
        print(f"Unexpected error during keyUp for key '{key}': {e}")


def press(*args, duration: float = 0.05):
    """
    Simulates pressing and releasing key(s) with a short delay in between.
    The 'duration' here is the time the key is held down (press followed by release).
    """
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Keyboard 'press' will be a no-op.")
        return

    try:
        for key_str in args:
            if not isinstance(key_str, str):
                print(f"Press: Invalid key '{key_str}', must be a string. Skipping.")
                continue
            skb_input_rust.send_key_event_py(key_str, True) # Press
            if duration > 0:
                time.sleep(duration) # Hold duration
            skb_input_rust.send_key_event_py(key_str, False) # Release
            # Original ino.py had a sleep *after* each "press" command from Arduino.
            # If that behavior is desired (a pause *between* distinct key presses in the *args sequence),
            # another small sleep could be added here, outside the press/release pair.
            # For now, this matches holding a single key for `duration`.
    except RuntimeError as e:
        print(f"Error during press execution: {e}")
    except Exception as e:
        print(f"Unexpected error during press: {e}")


def write(phrase: str, delayBetweenPresses: float = 0.01): # delayBetweenPresses is now more of a post-write delay
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Keyboard 'write' will be a no-op.")
        return
    if not isinstance(phrase, str):
        print(f"Write: Invalid phrase '{phrase}', must be a string.")
        return

    try:
        skb_input_rust.type_text_py(phrase)
        # The original 'delayBetweenPresses' was tied to Arduino's serial write.
        # enigo's type_text is blocking and types the whole phrase.
        # If a delay is still needed *after* typing the phrase, we can use it here.
        # A per-character delay would need a char-by-char loop calling type_text_py(char)
        # or send_key_event_py for each char, which is less efficient than type_text_py for phrases.
        if delayBetweenPresses > 0 and len(phrase) > 0 : # Check len(phrase) to avoid sleep if empty
             # The original sleep was delayBetweenPresses * len(phrase).
             # Let's just use a single delayBetweenPresses as a pause after typing.
             # If a longer, phrase-dependent delay is needed, adjust this.
            time.sleep(delayBetweenPresses)
    except RuntimeError as e:
        print(f"Error during write for phrase '{phrase}': {e}")
    except Exception as e:
        print(f"Unexpected error during write for phrase '{phrase}': {e}")
