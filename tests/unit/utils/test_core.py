import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.utils import core as utils_core # Path to the module being tested

class TestCoreUtils(unittest.TestCase):

    @patch('src.utils.core.skb_rust_utils')
    def test_hashit(self, mock_skb_rust_utils):
        mock_skb_rust_utils.hash_image_data.return_value = 1234567890
        
        # Create a dummy numpy array (e.g., grayscale)
        dummy_array = np.array([[10, 20], [30, 40]], dtype=np.uint8)
        
        result = utils_core.hashit(dummy_array)
        
        mock_skb_rust_utils.hash_image_data.assert_called_once()
        # Check that the first argument to the mocked function was a NumPy array
        called_arg = mock_skb_rust_utils.hash_image_data.call_args[0][0]
        self.assertIsInstance(called_arg, np.ndarray)
        # Potentially more checks on array properties if necessary (dtype, flags)
        # self.assertTrue(np.array_equal(called_arg, dummy_array_prepared)) # If specific prep is done

        self.assertEqual(result, 1234567890)

    @patch('src.utils.core.skb_rust_utils')
    def test_locate(self, mock_skb_rust_utils):
        expected_bbox = (10, 20, 30, 40)
        mock_skb_rust_utils.locate_template.return_value = expected_bbox
        
        dummy_haystack = np.array([[0]*100]*100, dtype=np.uint8)
        dummy_needle = np.array([[0]*10]*10, dtype=np.uint8)
        
        result = utils_core.locate(dummy_haystack, dummy_needle, confidence=0.8)
        
        mock_skb_rust_utils.locate_template.assert_called_once()
        args, _ = mock_skb_rust_utils.locate_template.call_args
        self.assertIsInstance(args[0], np.ndarray) # haystack
        self.assertIsInstance(args[1], np.ndarray) # needle
        self.assertEqual(args[2], 0.8)             # confidence
        self.assertEqual(result, expected_bbox)

    @patch('src.utils.core.skb_rust_utils')
    def test_locate_not_found(self, mock_skb_rust_utils):
        mock_skb_rust_utils.locate_template.return_value = None # Simulate not found
        
        dummy_haystack = np.array([[0]*100]*100, dtype=np.uint8)
        dummy_needle = np.array([[0]*10]*10, dtype=np.uint8)
        
        result = utils_core.locate(dummy_haystack, dummy_needle)
        
        self.assertIsNone(result)

    @patch('src.utils.core.skb_rust_utils')
    def test_locateMultiple(self, mock_skb_rust_utils):
        expected_bouding_boxes = [(10, 20, 30, 40), (50, 60, 30, 40)]
        mock_skb_rust_utils.locate_all_templates.return_value = expected_bouding_boxes
        
        dummy_haystack = np.array([[0]*100]*100, dtype=np.uint8)
        dummy_needle = np.array([[0]*10]*10, dtype=np.uint8)

        result = utils_core.locateMultiple(dummy_haystack, dummy_needle, confidence=0.7)
        mock_skb_rust_utils.locate_all_templates.assert_called_once()
        args, _ = mock_skb_rust_utils.locate_all_templates.call_args
        self.assertIsInstance(args[0], np.ndarray)
        self.assertIsInstance(args[1], np.ndarray)
        self.assertEqual(args[2], 0.7)
        self.assertEqual(result, expected_bouding_boxes)

    @patch('src.utils.core.camera') # Mock the camera object if getScreenshot uses it
    @patch('src.utils.core.skb_rust_utils')
    def test_getScreenshot(self, mock_skb_rust_utils, mock_camera):
        # Simulate camera.grab() returning a BGRA image
        mock_bgra_image = np.zeros((100, 100, 4), dtype=np.uint8)
        mock_camera.grab.return_value = mock_bgra_image
        
        # Simulate Rust conversion returning a grayscale image
        mock_gray_image = np.zeros((100, 100), dtype=np.uint8)
        mock_skb_rust_utils.convert_bgra_to_grayscale.return_value = mock_gray_image
        
        result = utils_core.getScreenshot()
        
        mock_camera.grab.assert_called_once()
        mock_skb_rust_utils.convert_bgra_to_grayscale.assert_called_once()
        # Check that the argument to Rust was the BGRA image (or a C-contiguous version of it)
        rust_call_arg = mock_skb_rust_utils.convert_bgra_to_grayscale.call_args[0][0]
        self.assertTrue(np.array_equal(rust_call_arg, mock_bgra_image))
        self.assertEqual(rust_call_arg.ndim, 3) # Expects HxWx4
        
        self.assertTrue(np.array_equal(result, mock_gray_image))

if __name__ == '__main__':
    unittest.main()
