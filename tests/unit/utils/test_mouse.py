import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adjust the path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from utils import mouse

class TestMouseUtils(unittest.TestCase):

    @patch('utils.mouse.pyautogui')
    def test_moveTo(self, mock_pyautogui):
        mouse.moveTo((100, 200))
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.2, tween=mock_pyautogui.easeInOutQuad)

    @patch('utils.mouse.pyautogui')
    def test_leftClick_with_coordinate(self, mock_pyautogui):
        mouse.leftClick((100, 200))
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.2, tween=mock_pyautogui.easeInOutQuad)
        mock_pyautogui.click.assert_called_once_with()

    @patch('utils.mouse.pyautogui')
    def test_leftClick_without_coordinate(self, mock_pyautogui):
        mouse.leftClick()
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.click.assert_called_once_with()

    @patch('utils.mouse.pyautogui')
    def test_rightClick_with_coordinate(self, mock_pyautogui):
        mouse.rightClick((100, 200))
        mock_pyautogui.moveTo.assert_called_once_with(100, 200, duration=0.2, tween=mock_pyautogui.easeInOutQuad)
        mock_pyautogui.click.assert_called_once_with(button='right')

    @patch('utils.mouse.pyautogui')
    def test_rightClick_without_coordinate(self, mock_pyautogui):
        mouse.rightClick()
        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.click.assert_called_once_with(button='right')

    @patch('utils.mouse.pyautogui')
    def test_drag(self, mock_pyautogui):
        mouse.drag((100, 200), (300, 400))
        self.assertEqual(mock_pyautogui.moveTo.call_args_list[0], unittest.mock.call(100, 200, duration=0.2, tween=mock_pyautogui.easeInOutQuad))
        mock_pyautogui.mouseDown.assert_called_once_with()
        self.assertEqual(mock_pyautogui.moveTo.call_args_list[1], unittest.mock.call(300, 400, duration=0.3, tween=mock_pyautogui.easeInOutQuad))
        mock_pyautogui.mouseUp.assert_called_once_with()

    @patch('utils.mouse.pyautogui')
    def test_scroll(self, mock_pyautogui):
        mouse.scroll(10)
        mock_pyautogui.scroll.assert_called_once_with(10)

if __name__ == '__main__':
    unittest.main()
