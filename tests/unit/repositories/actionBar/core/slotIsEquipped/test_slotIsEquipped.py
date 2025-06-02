import pathlib
import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.repositories.actionBar.core import slotIsEquipped
from src.utils.image import loadFromRGBToGray # Keep for loading test images


currentPath = pathlib.Path(__file__).parent.resolve()

class TestSlotIsEquipped(unittest.TestCase):

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_return_False_when_slot_is_not_equipped(self, mock_skb_rust_utils):
        # Mock the chain of Rust calls: get_action_bar_roi -> is_slot_equipped
        mock_skb_rust_utils.get_action_bar_roi.return_value = (10, 20, 5, 34) # x, y, w, h of left arrow
        mock_skb_rust_utils.is_slot_equipped.return_value = False
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/slotIsNotEquipped.png')
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)

        isEquipped = slotIsEquipped(screenshotImage, 14) # Slot 14
        
        self.assertFalse(isEquipped)
        mock_skb_rust_utils.get_action_bar_roi.assert_called_once()
        # screenshot arg for get_action_bar_roi is processed by _ensure_screenshot_format
        # so direct comparison might be tricky if it was copied. Check type.
        self.assertIsInstance(mock_skb_rust_utils.get_action_bar_roi.call_args[0][0], np.ndarray)

        mock_skb_rust_utils.is_slot_equipped.assert_called_once()
        args_eq, _ = mock_skb_rust_utils.is_slot_equipped.call_args
        self.assertIsInstance(args_eq[0], np.ndarray) # screenshot
        self.assertEqual(args_eq[1], 14)             # slot
        self.assertEqual(args_eq[2], 10)             # bar_x
        self.assertEqual(args_eq[3], 20)             # bar_y
        self.assertEqual(args_eq[4], 5)              # left_arrow_width

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_return_True_when_slot_is_equipped(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_action_bar_roi.return_value = (10, 20, 5, 34)
        mock_skb_rust_utils.is_slot_equipped.return_value = True
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/slotIsEquipped.png')
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)

        isEquipped = slotIsEquipped(screenshotImage, 14) # Slot 14
        
        self.assertTrue(isEquipped)
        mock_skb_rust_utils.get_action_bar_roi.assert_called_once()
        mock_skb_rust_utils.is_slot_equipped.assert_called_once()
        # Args check similar to above could be added for more rigor

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_return_None_if_action_bar_roi_not_found(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_action_bar_roi.return_value = None # Simulate ROI not found
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/slotIsEquipped.png') # Image content doesn't matter much here
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)

        isEquipped = slotIsEquipped(screenshotImage, 14)
        
        self.assertIsNone(isEquipped) # Python function returns None if ROI not found
        mock_skb_rust_utils.get_action_bar_roi.assert_called_once()
        mock_skb_rust_utils.is_slot_equipped.assert_not_called() # Should not be called if ROI is None

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_handle_rust_exception_in_is_slot_equipped(self, mock_skb_rust_utils):
        mock_skb_rust_utils.get_action_bar_roi.return_value = (10, 20, 5, 34)
        mock_skb_rust_utils.is_slot_equipped.side_effect = Exception("Rust error in is_slot_equipped")
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/slotIsEquipped.png')
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)
        
        # The Python wrapper currently returns None on Exception
        result = slotIsEquipped(screenshotImage, 14)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
