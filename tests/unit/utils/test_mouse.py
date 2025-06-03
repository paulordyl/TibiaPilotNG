import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

# Adjust the path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from utils import mouse # Imports src.utils.mouse

class TestMouseUtils(unittest.TestCase):

    @patch('utils.mouse.random.randint')
    @patch('utils.mouse.random.uniform')
    @patch('utils.mouse.random.choice')
    @patch('utils.mouse.pyautogui')
    def test_moveTo(self, mock_pyautogui, mock_random_choice, mock_random_uniform, mock_random_randint):
        mock_random_randint.return_value = 1  # Offset x and y by +1
        mock_random_uniform.return_value = 0.25  # Fixed duration
        mock_random_choice.return_value = mouse.linear  # Fixed tween

        mouse.moveTo((100, 200))

        mock_pyautogui.moveTo.assert_called_once_with(101, 101, duration=0.25, tween=mouse.linear)
        mock_random_randint.assert_has_calls([call(-1, 1), call(-1, 1)])
        mock_random_uniform.assert_called_once_with(0.15, 0.35)
        mock_random_choice.assert_called_once_with(mouse.TWEEN_FUNCTIONS)


    @patch('utils.mouse.time.sleep')
    @patch('utils.mouse.random.randint')
    @patch('utils.mouse.random.uniform') # This will mock all calls to random.uniform
    @patch('utils.mouse.random.choice')
    @patch('utils.mouse.pyautogui')
    def test_leftClick_with_coordinate(self, mock_pyautogui, mock_random_choice, mock_random_uniform, mock_random_randint, mock_time_sleep):
        mock_random_randint.return_value = 1  # Offset x and y by +1
        # random.uniform is called for moveTo duration, then for sleep duration
        mock_random_uniform.side_effect = [0.25, 0.06]  # moveTo duration, then sleep duration
        mock_random_choice.return_value = mouse.linear  # Fixed tween for moveTo

        mouse.leftClick((100, 200))

        mock_pyautogui.moveTo.assert_called_once_with(101, 101, duration=0.25, tween=mouse.linear)
        mock_pyautogui.mouseDown.assert_called_once_with(button='left')
        mock_time_sleep.assert_called_once_with(0.06)
        mock_pyautogui.mouseUp.assert_called_once_with(button='left')

        mock_random_randint.assert_has_calls([call(-1, 1), call(-1, 1)])
        mock_random_uniform.assert_has_calls([call(0.15, 0.35), call(0.04, 0.08)])
        mock_random_choice.assert_called_once_with(mouse.TWEEN_FUNCTIONS)


    @patch('utils.mouse.time.sleep')
    @patch('utils.mouse.random.uniform') # This will mock the sleep duration
    @patch('utils.mouse.pyautogui')
    def test_leftClick_without_coordinate(self, mock_pyautogui, mock_random_uniform, mock_time_sleep):
        mock_random_uniform.return_value = 0.06 # Sleep duration

        mouse.leftClick()

        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.mouseDown.assert_called_once_with(button='left')
        mock_time_sleep.assert_called_once_with(0.06)
        mock_pyautogui.mouseUp.assert_called_once_with(button='left')
        mock_random_uniform.assert_called_once_with(0.04, 0.08)


    @patch('utils.mouse.time.sleep')
    @patch('utils.mouse.random.randint')
    @patch('utils.mouse.random.uniform')
    @patch('utils.mouse.random.choice')
    @patch('utils.mouse.pyautogui')
    def test_rightClick_with_coordinate(self, mock_pyautogui, mock_random_choice, mock_random_uniform, mock_random_randint, mock_time_sleep):
        mock_random_randint.return_value = 1  # Offset x and y by +1
        mock_random_uniform.side_effect = [0.25, 0.06]  # moveTo duration, then sleep duration
        mock_random_choice.return_value = mouse.linear  # Fixed tween for moveTo

        mouse.rightClick((100, 200))

        mock_pyautogui.moveTo.assert_called_once_with(101, 101, duration=0.25, tween=mouse.linear)
        mock_pyautogui.mouseDown.assert_called_once_with(button='right')
        mock_time_sleep.assert_called_once_with(0.06)
        mock_pyautogui.mouseUp.assert_called_once_with(button='right')

        mock_random_randint.assert_has_calls([call(-1, 1), call(-1, 1)])
        mock_random_uniform.assert_has_calls([call(0.15, 0.35), call(0.04, 0.08)])
        mock_random_choice.assert_called_once_with(mouse.TWEEN_FUNCTIONS)

    @patch('utils.mouse.time.sleep')
    @patch('utils.mouse.random.uniform')
    @patch('utils.mouse.pyautogui')
    def test_rightClick_without_coordinate(self, mock_pyautogui, mock_random_uniform, mock_time_sleep):
        mock_random_uniform.return_value = 0.06 # Sleep duration

        mouse.rightClick()

        mock_pyautogui.moveTo.assert_not_called()
        mock_pyautogui.mouseDown.assert_called_once_with(button='right')
        mock_time_sleep.assert_called_once_with(0.06)
        mock_pyautogui.mouseUp.assert_called_once_with(button='right')
        mock_random_uniform.assert_called_once_with(0.04, 0.08)

    @patch('utils.mouse.random.randint')
    @patch('utils.mouse.random.uniform')
    @patch('utils.mouse.random.choice')
    @patch('utils.mouse.pyautogui')
    def test_drag(self, mock_pyautogui, mock_random_choice, mock_random_uniform, mock_random_randint):
        # Offset x1,y1 by +1,+1 and x2,y2 by -1,-1
        mock_random_randint.side_effect = [1, 1, -1, -1]
        # Durations for first moveTo, then second moveTo
        mock_random_uniform.side_effect = [0.25, 0.35]
        # Tweens for first moveTo, then second moveTo
        mock_random_choice.side_effect = [mouse.linear, mouse.easeInOutQuad]

        mouse.drag((100, 200), (300, 400))

        # Check moveTo calls
        self.assertEqual(mock_pyautogui.moveTo.call_args_list[0], call(101, 101, duration=0.25, tween=mouse.linear))
        self.assertEqual(mock_pyautogui.moveTo.call_args_list[1], call(299, 399, duration=0.35, tween=mouse.easeInOutQuad))

        mock_pyautogui.mouseDown.assert_called_once_with()
        mock_pyautogui.mouseUp.assert_called_once_with()

        mock_random_randint.assert_has_calls([
            call(-1, 1), call(-1, 1),  # For first coordinate
            call(-1, 1), call(-1, 1)   # For second coordinate
        ])
        mock_random_uniform.assert_has_calls([
            call(0.15, 0.35), # Duration for first moveTo
            call(0.2, 0.4)    # Duration for second moveTo
        ])
        mock_random_choice.assert_has_calls([
            call(mouse.TWEEN_FUNCTIONS), # Tween for first moveTo
            call(mouse.TWEEN_FUNCTIONS)  # Tween for second moveTo
        ])


    @patch('utils.mouse.pyautogui')
    def test_scroll(self, mock_pyautogui): # This test remains unchanged
        mouse.scroll(10)
        mock_pyautogui.scroll.assert_called_once_with(10)

if __name__ == '__main__':
    unittest.main()
