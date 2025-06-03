import numpy as np
from src.utils import mouse as bot_mouse
from src.utils import keyboard as bot_keyboard
from src.utils import screen_capture as bot_screen_capture
import mss # To get screen dimensions
import time # Potentially for small delays if needed

class AgentInterface:
    def __init__(self, default_screen_width: int = 1920, default_screen_height: int = 1080):
        """
        Initializes the AgentInterface.
        Attempts to fetch primary screen dimensions using mss.
        Falls back to default dimensions if mss fails or only one monitor (all) is found.
        """
        self.screen_width = default_screen_width
        self.screen_height = default_screen_height
        self.screen_left = 0
        self.screen_top = 0

        try:
            with mss.mss() as sct:
                # sct.monitors[0] is a dict for all monitors combined
                # sct.monitors[1] is the primary monitor
                if len(sct.monitors) > 1:
                    primary_monitor = sct.monitors[1]
                    self.screen_width = primary_monitor["width"]
                    self.screen_height = primary_monitor["height"]
                    self.screen_left = primary_monitor["left"]
                    self.screen_top = primary_monitor["top"]
                    print(f"AgentInterface: Found primary monitor: L:{self.screen_left} T:{self.screen_top} W:{self.screen_width} H:{self.screen_height}")
                else:
                    # This case might happen in some virtual environments or if mss doesn't list individual monitors correctly
                    print(f"Warning: AgentInterface: Only one monitor description found (sct.monitors has {len(sct.monitors)} items). This might be the 'all monitors' entry. Using defaults or provided values: W:{self.screen_width} H:{self.screen_height}")
        except Exception as e:
            print(f"Warning: AgentInterface: Could not get screen dimensions using mss: {e}. Using defaults: W:{self.screen_width} H:{self.screen_height}")
            # Defaults are already set

    def _transform_coords(self, x: float, y: float, raw_pixels: bool) -> tuple[int, int]:
        """Transforms coordinates from percentage (0.0-1.0) to absolute screen pixels if raw_pixels is False."""
        if raw_pixels:
            return int(x), int(y)
        else:
            # Clamp percentages to be within [0.0, 1.0]
            x_clamped = max(0.0, min(1.0, x))
            y_clamped = max(0.0, min(1.0, y))

            # Calculate absolute pixel coordinates relative to the primary monitor's top-left
            abs_x = self.screen_left + int(x_clamped * self.screen_width)
            abs_y = self.screen_top + int(y_clamped * self.screen_height)
            return abs_x, abs_y

    # --- Action Methods ---
    def click(self, x: float, y: float, raw_pixels: bool = True, button: str = 'left'):
        """Performs a mouse click at the given coordinates."""
        abs_x, abs_y = self._transform_coords(x, y, raw_pixels)
        if button == 'left':
            bot_mouse.leftClick((abs_x, abs_y))
        elif button == 'right':
            bot_mouse.rightClick((abs_x, abs_y))
        else:
            print(f"Warning: AgentInterface: Unsupported click button: {button}. Defaulting to left click.")
            bot_mouse.leftClick((abs_x, abs_y))

    def drag(self, x1: float, y1: float, x2: float, y2: float, raw_pixels: bool = True):
        """Performs a mouse drag from (x1,y1) to (x2,y2)."""
        abs_x1, abs_y1 = self._transform_coords(x1, y1, raw_pixels)
        abs_x2, abs_y2 = self._transform_coords(x2, y2, raw_pixels)
        bot_mouse.drag((abs_x1, abs_y1), (abs_x2, abs_y2))

    def type_string(self, text: str):
        """Types the given string."""
        bot_keyboard.write(text)

    def press_key(self, key_name: str):
        """Presses and releases a key."""
        bot_keyboard.press(key_name)

    def hold_key(self, key_name: str):
        """Presses and holds a key down."""
        bot_keyboard.keyDown(key_name)

    def release_key(self, key_name: str):
        """Releases a key."""
        bot_keyboard.keyUp(key_name)

    def hotkey(self, keys: list[str]):
        """
        Presses a combination of keys simultaneously.
        Example: hotkey(['ctrl', 'c'])
        """
        if keys and isinstance(keys, list) and all(isinstance(k, str) for k in keys):
            bot_keyboard.hotkey(*keys) # Unpack list into arguments
        else:
            print("Warning: AgentInterface: Hotkey requires a list of key strings (e.g., ['ctrl', 'shift', 'a']).")
            # Consider raising TypeError for stricter API

    # --- Observation Method ---
    def get_current_frame(self, region: tuple[int, int, int, int] = None) -> np.ndarray:
        """
        Captures the current screen frame.

        Args:
            region (tuple, optional): (left, top, width, height) in raw, absolute screen pixels
                                      to capture a specific region.
                                      If None, captures the full primary screen.

        Returns:
            np.ndarray: The captured frame as an RGB NumPy array.
        """
        if region:
            if not (isinstance(region, tuple) and len(region) == 4 and all(isinstance(n, int) for n in region)):
                print("Warning: AgentInterface: Invalid region format for get_current_frame. Must be tuple of 4 ints (left, top, width, height). Capturing full screen instead.")
                return bot_screen_capture.capture_full_screen()
            # capture_region expects absolute coordinates
            return bot_screen_capture.capture_region(region)
        else:
            # capture_full_screen captures the primary monitor based on its own logic using sct.monitors[1]
            return bot_screen_capture.capture_full_screen()
