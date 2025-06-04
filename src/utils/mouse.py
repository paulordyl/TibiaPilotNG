# src/utils/mouse.py
import time # May not be needed as much, but good to keep if any small delays are introduced
from src.shared.typings import XYCoordinate # Assuming this is still relevant for type hints

try:
    import skb_input_rust
    RUST_INPUT_AVAILABLE = True
    print("Successfully imported Rust `skb_input_rust` module for mouse.")
except ImportError as e:
    RUST_INPUT_AVAILABLE = False
    print(f"Failed to import Rust `skb_input_rust` module for mouse: {e}")
    print("Mouse functions will be no-ops or raise errors.")

# Removed ArduinoComm initialization

def drag(x1y1: XYCoordinate, x2y2: XYCoordinate):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Mouse 'drag' will be a no-op.")
        return

    try:
        # Ensure coordinates are integers as expected by Rust FFI for positions
        x1, y1 = int(x1y1[0]), int(x1y1[1])
        x2, y2 = int(x2y2[0]), int(x2y2[1])

        skb_input_rust.move_mouse_abs_py(x1, y1)
        skb_input_rust.send_mouse_button_event_py("left", True) # Press left button
        # Small delay can sometimes help ensure the press is registered before drag
        # time.sleep(0.05) # Optional: if dragging is unreliable
        skb_input_rust.move_mouse_abs_py(x2, y2) # Move to destination
        skb_input_rust.send_mouse_button_event_py("left", False) # Release left button
    except RuntimeError as e:
        print(f"Error during drag operation: {e}")
    except Exception as e:
        print(f"Unexpected error during drag: {e}")


def leftClick(windowCoordinate: XYCoordinate = None):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Mouse 'leftClick' will be a no-op.")
        return

    try:
        if windowCoordinate is not None:
            x, y = int(windowCoordinate[0]), int(windowCoordinate[1])
            skb_input_rust.move_mouse_abs_py(x, y)
            # Optional: short delay after move before click
            # time.sleep(0.02)
        skb_input_rust.click_mouse_py("left")
    except RuntimeError as e:
        print(f"Error during leftClick: {e}")
    except Exception as e:
        print(f"Unexpected error during leftClick: {e}")


def moveTo(windowCoordinate: XYCoordinate):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Mouse 'moveTo' will be a no-op.")
        return
    if not windowCoordinate or len(windowCoordinate) < 2:
        print("moveTo: Invalid coordinate provided.")
        return

    try:
        x, y = int(windowCoordinate[0]), int(windowCoordinate[1])
        skb_input_rust.move_mouse_abs_py(x, y)
    except RuntimeError as e:
        print(f"Error during moveTo to ({windowCoordinate[0]}, {windowCoordinate[1]}): {e}")
    except Exception as e:
        print(f"Unexpected error during moveTo: {e}")


def rightClick(windowCoordinate: XYCoordinate = None):
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Mouse 'rightClick' will be a no-op.")
        return

    try:
        if windowCoordinate is not None:
            x, y = int(windowCoordinate[0]), int(windowCoordinate[1])
            skb_input_rust.move_mouse_abs_py(x, y)
            # time.sleep(0.02) # Optional delay
        skb_input_rust.click_mouse_py("right")
    except RuntimeError as e:
        print(f"Error during rightClick: {e}")
    except Exception as e:
        print(f"Unexpected error during rightClick: {e}")

def scroll(clicks: int):
    """
    Scrolls the mouse wheel vertically.
    Positive clicks for scrolling down (standard behavior).
    Negative clicks for scrolling up (standard behavior).
    The scroll is relative to the current mouse position.
    """
    if not RUST_INPUT_AVAILABLE:
        print("Rust input module not available. Mouse 'scroll' will be a no-op.")
        return
    if not isinstance(clicks, int):
        print("Scroll: 'clicks' must be an integer.")
        return

    try:
        # skb_input_rust.scroll_mouse_wheel_py takes (x_amount, y_amount)
        # Standard vertical scroll means x_amount is 0.
        # Positive y_amount for scroll down, negative for scroll up with enigo usually.
        # However, 'clicks' often implies "notches". Let's assume positive 'clicks' means scroll down one unit.
        # And negative 'clicks' means scroll up one unit.
        # The 'clicks' value in enigo's scroll function is often a pixel or line delta, not notches.
        # For simplicity, let's map our 'clicks' to y_amount.
        # If clicks = 1 (scroll down one notch), y_amount could be e.g. 1 or some positive multiplier.
        # If clicks = -1 (scroll up one notch), y_amount could be e.g. -1 or some negative multiplier.
        # The exact scaling might need adjustment based on desired sensitivity.
        # Let's assume clicks directly maps to y_amount for now.
        # Positive 'clicks' in original code meant scroll down.
        # Positive 'y_amount' in skb_input_rust.scroll_mouse_wheel_py also typically means scroll down.
        skb_input_rust.scroll_mouse_wheel_py(0, clicks)
    except RuntimeError as e:
        print(f"Error during scroll: {e}")
    except Exception as e:
        print(f"Unexpected error during scroll: {e}")
