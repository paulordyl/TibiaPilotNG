import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import sys
import os

# Adjust sys.path to import from src.ai.agent_interface
# This assumes tests are in tests/unit/ai and src is a sibling to tests.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.ai.agent_interface import AgentInterface

# Mocked mss classes for __init__ testing
class MockMSS:
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *args, **kwargs): pass
    monitors = [] # Default to no monitors found beyond 'all' or error state

class MockMSSGood(MockMSS): # Simulates mss finding a primary monitor
    monitors = [
        {"left": 0, "top": 0, "width": 1600, "height": 900, "name": "All"}, # All monitors
        {"left": 0, "top": 0, "width": 1280, "height": 720, "name": "Primary"}  # Primary
    ]

class MockMSSOnlyAll(MockMSS): # Simulates mss finding only the 'all monitors' entry
     monitors = [{"left": 0, "top": 0, "width": 1600, "height": 900, "name": "All"}]


# Define paths for patching based on where they are imported in agent_interface.py
PATCH_PATH_MOUSE = 'src.ai.agent_interface.bot_mouse'
PATCH_PATH_KEYBOARD = 'src.ai.agent_interface.bot_keyboard'
PATCH_PATH_SCREEN_CAPTURE = 'src.ai.agent_interface.bot_screen_capture'
PATCH_PATH_MSS = 'src.ai.agent_interface.mss' # mss is imported directly

class TestAgentInterface(unittest.TestCase):
    def setUp(self):
        # Default screen dimensions for testing percentage calculations when mss fails
        self.default_width = 1000
        self.default_height = 800

    @patch(PATCH_PATH_MSS, new_callable=MockMSSGood)
    def test_init_screen_dimensions_success(self, mock_mss_good_instance_unused):
        # The mock_mss_good_instance_unused is not directly used,
        # new_callable ensures MockMSSGood is instantiated by the patch
        interface = AgentInterface()
        self.assertEqual(interface.screen_width, 1280)
        self.assertEqual(interface.screen_height, 720)
        self.assertEqual(interface.screen_left, 0)
        self.assertEqual(interface.screen_top, 0)

    @patch(PATCH_PATH_MSS, side_effect=Exception("MSS Init Error"))
    def test_init_screen_dimensions_mss_exception(self, mock_mss_exception_unused):
        with patch('builtins.print') as mock_print:
            interface = AgentInterface(default_screen_width=self.default_width, default_screen_height=self.default_height)
        self.assertEqual(interface.screen_width, self.default_width)
        self.assertEqual(interface.screen_height, self.default_height)
        mock_print.assert_any_call(f"Warning: AgentInterface: Could not get screen dimensions using mss: MSS Init Error. Using defaults: W:{self.default_width} H:{self.default_height}")

    @patch(PATCH_PATH_MSS, new_callable=MockMSSOnlyAll)
    def test_init_screen_dimensions_mss_only_all_monitors(self, mock_mss_only_all_instance_unused):
        with patch('builtins.print') as mock_print:
            interface = AgentInterface(default_screen_width=self.default_width, default_screen_height=self.default_height)
        self.assertEqual(interface.screen_width, self.default_width) # Should use defaults
        self.assertEqual(interface.screen_height, self.default_height)
        mock_print.assert_any_call(f"Warning: AgentInterface: Only one monitor description found (sct.monitors has 1 items). This might be the 'all monitors' entry. Using defaults or provided values: W:{self.default_width} H:{self.default_height}")

    def _get_interface_with_known_dims(self, width=None, height=None, left=0, top=0):
        # Helper to create an interface with specific dimensions, bypassing mss via patching
        test_width = width if width is not None else self.default_width
        test_height = height if height is not None else self.default_height

        # Mock mss to return controlled monitor dimensions or raise an error to force defaults
        mock_mss_instance = MagicMock()
        if left == 0 and top == 0 and test_width == self.default_width and test_height == self.default_height : # force default by error
             patcher = patch(PATCH_PATH_MSS, side_effect=Exception("Forcing default dimensions"))
        else: # provide specific dimensions
            mock_monitors = [
                {}, # All monitors
                {"left": left, "top": top, "width": test_width, "height": test_height}
            ]
            mock_sct = mock_mss_instance.return_value.__enter__.return_value
            mock_sct.monitors = mock_monitors
            patcher = patch(PATCH_PATH_MSS, mock_mss_instance)

        with patcher:
            # Suppress print warnings during this specific setup if forcing defaults
            with patch('builtins.print') if (left == 0 and top == 0 and test_width == self.default_width and test_height == self.default_height) else MagicMock():
                 interface = AgentInterface(default_screen_width=self.default_width, default_screen_height=self.default_height)

        # Directly assert what the interface *should* have after init under these controlled conditions
        if not (left == 0 and top == 0 and test_width == self.default_width and test_height == self.default_height):
            self.assertEqual(interface.screen_width, test_width)
            self.assertEqual(interface.screen_height, test_height)
            self.assertEqual(interface.screen_left, left)
            self.assertEqual(interface.screen_top, top)
        else: # defaults were forced by exception
            self.assertEqual(interface.screen_width, self.default_width)
            self.assertEqual(interface.screen_height, self.default_height)
            self.assertEqual(interface.screen_left, 0) # Default screen_left/top
            self.assertEqual(interface.screen_top, 0)

        return interface


    def test_transform_coords_raw_pixels(self):
        interface = self._get_interface_with_known_dims()
        self.assertEqual(interface._transform_coords(100.0, 200.0, True), (100, 200))

    def test_transform_coords_percentage(self):
        interface = self._get_interface_with_known_dims() # Uses 1000x800, left=0, top=0
        self.assertEqual(interface._transform_coords(0.5, 0.5, False), (500, 400))
        self.assertEqual(interface._transform_coords(0.0, 0.0, False), (0, 0))
        self.assertEqual(interface._transform_coords(1.0, 1.0, False), (1000, 800))
        self.assertEqual(interface._transform_coords(1.5, -0.5, False), (1000, 0)) # Test clamping

    def test_transform_coords_percentage_with_offset_screen(self):
        interface = self._get_interface_with_known_dims(width=1000, height=800, left=100, top=50)
        self.assertEqual(interface.screen_left, 100)
        self.assertEqual(interface.screen_top, 50)
        self.assertEqual(interface._transform_coords(0.5, 0.5, False), (100 + 500, 50 + 400)) # (600, 450)

    @patch(PATCH_PATH_MOUSE)
    def test_click_left_raw(self, mock_bot_mouse):
        interface = self._get_interface_with_known_dims()
        interface.click(150, 250, raw_pixels=True, button='left')
        mock_bot_mouse.leftClick.assert_called_once_with((150, 250))

    @patch(PATCH_PATH_MOUSE)
    def test_click_right_percentage(self, mock_bot_mouse):
        interface = self._get_interface_with_known_dims() # 1000x800
        interface.click(0.2, 0.25, raw_pixels=False, button='right')
        mock_bot_mouse.rightClick.assert_called_once_with((200, 200)) # 0.2*1000=200, 0.25*800=200

    @patch(PATCH_PATH_MOUSE)
    def test_click_unsupported_button(self, mock_bot_mouse):
        interface = self._get_interface_with_known_dims()
        with patch('builtins.print') as mock_print:
            interface.click(10, 10, raw_pixels=True, button="middle")
        mock_bot_mouse.leftClick.assert_called_once_with((10,10)) # Defaults to left
        mock_print.assert_any_call("Warning: AgentInterface: Unsupported click button: middle. Defaulting to left click.")

    @patch(PATCH_PATH_MOUSE)
    def test_drag_raw(self, mock_bot_mouse):
        interface = self._get_interface_with_known_dims()
        interface.drag(10, 20, 30, 40, raw_pixels=True)
        mock_bot_mouse.drag.assert_called_once_with(((10, 20), (30, 40)))

    @patch(PATCH_PATH_KEYBOARD)
    def test_type_string(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        interface.type_string("hello world")
        mock_bot_keyboard.write.assert_called_once_with("hello world")

    @patch(PATCH_PATH_KEYBOARD)
    def test_press_key(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        interface.press_key("enter")
        mock_bot_keyboard.press.assert_called_once_with("enter")

    @patch(PATCH_PATH_KEYBOARD)
    def test_hold_key(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        interface.hold_key("shift")
        mock_bot_keyboard.keyDown.assert_called_once_with("shift")

    @patch(PATCH_PATH_KEYBOARD)
    def test_release_key(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        interface.release_key("shift")
        mock_bot_keyboard.keyUp.assert_called_once_with("shift")

    @patch(PATCH_PATH_KEYBOARD)
    def test_hotkey(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        keys_to_press = ["ctrl", "c"]
        interface.hotkey(keys_to_press)
        mock_bot_keyboard.hotkey.assert_called_once_with(*keys_to_press)

    @patch(PATCH_PATH_KEYBOARD)
    def test_hotkey_invalid_input(self, mock_bot_keyboard):
        interface = self._get_interface_with_known_dims()
        with patch('builtins.print') as mock_print:
            interface.hotkey("not a list") # type: ignore
        mock_bot_keyboard.hotkey.assert_not_called()
        mock_print.assert_any_call("Warning: AgentInterface: Hotkey requires a list of key strings (e.g., ['ctrl', 'shift', 'a']).")

    @patch(PATCH_PATH_SCREEN_CAPTURE)
    def test_get_current_frame_full_screen(self, mock_bot_screen_capture):
        interface = self._get_interface_with_known_dims()
        mock_frame = np.array([[[1,2,3]]], dtype=np.uint8)
        mock_bot_screen_capture.capture_full_screen.return_value = mock_frame

        frame = interface.get_current_frame()
        mock_bot_screen_capture.capture_full_screen.assert_called_once()
        mock_bot_screen_capture.capture_region.assert_not_called()
        self.assertIs(frame, mock_frame)

    @patch(PATCH_PATH_SCREEN_CAPTURE)
    def test_get_current_frame_region(self, mock_bot_screen_capture):
        interface = self._get_interface_with_known_dims()
        region_bbox = (10, 20, 100, 200) # Absolute pixel coordinates
        mock_frame = np.array([[[4,5,6]]], dtype=np.uint8)
        mock_bot_screen_capture.capture_region.return_value = mock_frame

        frame = interface.get_current_frame(region=region_bbox)
        mock_bot_screen_capture.capture_region.assert_called_once_with(region_bbox)
        mock_bot_screen_capture.capture_full_screen.assert_not_called()
        self.assertIs(frame, mock_frame)

    @patch(PATCH_PATH_SCREEN_CAPTURE)
    def test_get_current_frame_invalid_region_format(self, mock_bot_screen_capture):
        interface = self._get_interface_with_known_dims()
        mock_frame_fallback = np.array([[[7,8,9]]], dtype=np.uint8)
        mock_bot_screen_capture.capture_full_screen.return_value = mock_frame_fallback

        with patch('builtins.print') as mock_print:
            frame = interface.get_current_frame(region=(1,2,3)) # type: ignore

        mock_bot_screen_capture.capture_full_screen.assert_called_once()
        mock_bot_screen_capture.capture_region.assert_not_called()
        self.assertIs(frame, mock_frame_fallback)
        mock_print.assert_any_call("Warning: AgentInterface: Invalid region format for get_current_frame. Must be tuple of 4 ints (left, top, width, height). Capturing full screen instead.")

if __name__ == '__main__':
    unittest.main()
