import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Adjust the path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from utils import keyboard # This imports src.utils.keyboard

class TestKeyboardUtils(unittest.TestCase):

    # Tests for map_key_to_pyautogui
    def test_map_key_to_pyautogui_known_keys(self):
        self.assertEqual(keyboard.map_key_to_pyautogui('esc'), 'escape')
        self.assertEqual(keyboard.map_key_to_pyautogui('ctrl'), 'ctrl')
        self.assertEqual(keyboard.map_key_to_pyautogui('F1'), 'f1') # Test case insensitivity
        self.assertEqual(keyboard.map_key_to_pyautogui(' '), 'space') # Space from map

    def test_map_key_to_pyautogui_single_chars(self):
        self.assertEqual(keyboard.map_key_to_pyautogui('a'), 'a')
        self.assertEqual(keyboard.map_key_to_pyautogui('1'), '1')
        self.assertEqual(keyboard.map_key_to_pyautogui('?'), '?')

    def test_map_key_to_pyautogui_unmapped_multichar(self):
        # Expect a warning to be printed by the function for "unknownlongkey"
        with patch('builtins.print') as mock_print:
            self.assertIsNone(keyboard.map_key_to_pyautogui('unknownlongkey'))
            mock_print.assert_called_once_with("Warning: Key 'unknownlongkey' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")

    def test_map_key_to_pyautogui_empty_or_none(self):
        self.assertIsNone(keyboard.map_key_to_pyautogui(''))
        self.assertIsNone(keyboard.map_key_to_pyautogui(None))

    # Test for write
    @patch('utils.keyboard.random.uniform') # Patching where random is used in keyboard.py
    @patch('utils.keyboard.pyautogui')    # Patching where pyautogui is in keyboard module
    def test_write(self, mock_pyautogui, mock_uniform):
        mock_uniform.return_value = 0.075
        keyboard.write("hello")
        mock_pyautogui.write.assert_called_once_with("hello", interval=0.075)
        mock_uniform.assert_called_once_with(0.03, 0.12)

    # Tests for press
    @patch('utils.keyboard.pyautogui')
    def test_press_valid_and_invalid_keys(self, mock_pyautogui):
        with patch('builtins.print') as mock_print: # To catch warning for 'unknownkey'
            keyboard.press('a', 'enter', 'unknownkey', 'f1')
            # Expect calls for 'a', 'enter', 'f1'
            self.assertEqual(mock_pyautogui.press.call_count, 3)
            expected_calls = [call('a'), call('enter'), call('f1')]
            mock_pyautogui.press.assert_has_calls(expected_calls, any_order=False)
            mock_print.assert_called_once_with("Warning: Key 'unknownkey' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")


    @patch('utils.keyboard.pyautogui')
    def test_press_no_valid_keys(self, mock_pyautogui):
        with patch('builtins.print') as mock_print:
            keyboard.press('unknownkey1', 'unknownkey2')
            mock_pyautogui.press.assert_not_called()
            expected_print_calls = [
                call("Warning: Key 'unknownkey1' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored."),
                call("Warning: Key 'unknownkey2' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")
            ]
            mock_print.assert_has_calls(expected_print_calls)


    # Tests for keyDown
    @patch('utils.keyboard.pyautogui')
    def test_keyDown_valid(self, mock_pyautogui):
        keyboard.keyDown('shift')
        mock_pyautogui.keyDown.assert_called_once_with('shift')

    @patch('utils.keyboard.pyautogui')
    def test_keyDown_invalid(self, mock_pyautogui):
        with patch('builtins.print') as mock_print:
            keyboard.keyDown('invalidKeyName')
            mock_pyautogui.keyDown.assert_not_called()
            mock_print.assert_called_once_with("Warning: Key 'invalidKeyName' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")


    # Tests for keyUp
    @patch('utils.keyboard.pyautogui')
    def test_keyUp_valid(self, mock_pyautogui):
        keyboard.keyUp('alt')
        mock_pyautogui.keyUp.assert_called_once_with('alt')

    @patch('utils.keyboard.pyautogui')
    def test_keyUp_invalid(self, mock_pyautogui):
        with patch('builtins.print') as mock_print:
            keyboard.keyUp('invalidKeyName')
            mock_pyautogui.keyUp.assert_not_called()
            mock_print.assert_called_once_with("Warning: Key 'invalidKeyName' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")


    # Tests for hotkey
    @patch('utils.keyboard.pyautogui')
    def test_hotkey_valid_and_invalid(self, mock_pyautogui):
        with patch('builtins.print') as mock_print:
            keyboard.hotkey('ctrl', 'shift', 'unknown', 'a')
            mock_pyautogui.hotkey.assert_called_once_with('ctrl', 'shift', 'a')
            mock_print.assert_called_once_with("Warning: Key 'unknown' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")


    @patch('utils.keyboard.pyautogui')
    def test_hotkey_no_valid_keys(self, mock_pyautogui):
        with patch('builtins.print') as mock_print:
            keyboard.hotkey('unknown1', 'unknown2')
            mock_pyautogui.hotkey.assert_not_called()
            expected_print_calls = [
                call("Warning: Key 'unknown1' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored."),
                call("Warning: Key 'unknown2' not found in PYAUTOGUI_KEY_MAP and is not a single character. It will be ignored.")
            ]
            mock_print.assert_has_calls(expected_print_calls)


    @patch('utils.keyboard.pyautogui')
    def test_hotkey_single_valid_key(self, mock_pyautogui):
        keyboard.hotkey('f1')
        mock_pyautogui.hotkey.assert_called_once_with('f1')

if __name__ == '__main__':
    unittest.main()
