import pathlib
import unittest
from unittest.mock import patch, MagicMock
import numpy as np # For creating sample screenshot arrays if needed
from src.repositories.actionBar.core import hasAttackCooldown
# from src.utils.image import loadFromRGBToGray # This itself now calls Rust. For unit tests, we might not need to load real images.
# Instead, we can pass a NumPy array directly and mock the Rust call.
# However, if these images are small and specifically crafted for these states,
# keeping loadFromRGBToGray (which now internally calls Rust) is fine,
# as we will mock the final skb_rust_utils.check_cooldown_status call.
# For true unit testing of hasAttackCooldown's Python logic, we'd mock the Rust call.
# Let's assume loadFromRGBToGray is working and returns a valid np.ndarray.
from src.utils.image import loadFromRGBToGray # Keep for now, ensure it returns proper np.ndarray


currentPath = pathlib.Path(__file__).parent.resolve()

# Test class structure for unittest
class TestHasAttackCooldown(unittest.TestCase):

    # Patch the skb_rust_utils module imported in src.repositories.actionBar.core
    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_return_False_when_has_no_attack_cooldown(self, mock_skb_rust_utils):
        # Configure the mock for the Rust function
        mock_skb_rust_utils.check_cooldown_status.return_value = False
        
        # Load the image (or use a dummy np.array if loadFromRGBToGray is also too heavy/complex)
        # For this test, we assume loadFromRGBToGray provides a valid GrayImage np.ndarray
        screenshotImage = loadFromRGBToGray(f'{currentPath}/withoutAttackCooldown.png')
        # Ensure it's a numpy array as expected by _ensure_screenshot_format
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)


        hasCooldown = hasAttackCooldown(screenshotImage)
        
        # Assert that the Python function returned the expected value
        self.assertFalse(hasCooldown)
        # Assert that the mocked Rust function was called correctly
        # The _ensure_screenshot_format makes a new array if not C-contiguous or wrong dtype.
        # So, checking the argument directly might fail if a copy was made.
        # Instead, check that it was called. For more specific argument checks,
        # you might need to inspect properties of the passed np.ndarray.
        mock_skb_rust_utils.check_cooldown_status.assert_called_once()
        args, _ = mock_skb_rust_utils.check_cooldown_status.call_args
        self.assertIsInstance(args[0], np.ndarray) # Check type of first arg
        self.assertEqual(args[1], "attack")       # Check group_name

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_return_True_when_has_attack_cooldown(self, mock_skb_rust_utils):
        mock_skb_rust_utils.check_cooldown_status.return_value = True
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/withAttackCooldown.png')
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)

        hasCooldown = hasAttackCooldown(screenshotImage)
        
        self.assertTrue(hasCooldown)
        mock_skb_rust_utils.check_cooldown_status.assert_called_once()
        args, _ = mock_skb_rust_utils.check_cooldown_status.call_args
        self.assertIsInstance(args[0], np.ndarray)
        self.assertEqual(args[1], "attack")

    @patch('src.repositories.actionBar.core.skb_rust_utils')
    def test_should_handle_rust_exception(self, mock_skb_rust_utils):
        # Simulate an exception from the Rust call
        mock_skb_rust_utils.check_cooldown_status.side_effect = Exception("Rust error")
        
        screenshotImage = loadFromRGBToGray(f'{currentPath}/withoutAttackCooldown.png')
        if not isinstance(screenshotImage, np.ndarray):
             screenshotImage = np.array(screenshotImage, dtype=np.uint8)

        # The Python wrapper function `_check_group_cooldown` currently returns None on Exception.
        # Depending on desired behavior, it might re-raise, or this test asserts None.
        result = hasAttackCooldown(screenshotImage)
        self.assertIsNone(result) # Based on current error handling in _check_group_cooldown

if __name__ == '__main__':
    unittest.main()
