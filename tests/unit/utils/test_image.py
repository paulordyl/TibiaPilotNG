import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.utils import image as utils_image # Path to the module

class TestImageUtils(unittest.TestCase):

    @patch('src.utils.image.skb_rust_utils')
    def test_RGBtoGray(self, mock_skb_rust_utils):
        mock_input_rgb = np.zeros((10, 10, 3), dtype=np.uint8)
        mock_output_gray = np.zeros((10, 10), dtype=np.uint8)
        mock_skb_rust_utils.convert_to_grayscale.return_value = mock_output_gray

        result = utils_image.RGBtoGray(mock_input_rgb)

        mock_skb_rust_utils.convert_to_grayscale.assert_called_once()
        called_arg = mock_skb_rust_utils.convert_to_grayscale.call_args[0][0]
        self.assertTrue(np.array_equal(called_arg, mock_input_rgb))
        self.assertEqual(result.shape, (10, 10))
        self.assertTrue(np.array_equal(result, mock_output_gray))

    @patch('src.utils.image.skb_rust_utils')
    def test_loadFromRGBToGray(self, mock_skb_rust_utils):
        mock_output_gray = np.zeros((10, 10), dtype=np.uint8)
        mock_skb_rust_utils.load_image_as_grayscale.return_value = mock_output_gray
        dummy_path = "some/image_path.png"

        result = utils_image.loadFromRGBToGray(dummy_path)

        mock_skb_rust_utils.load_image_as_grayscale.assert_called_once_with(dummy_path)
        self.assertTrue(np.array_equal(result, mock_output_gray))

    @patch('src.utils.image.skb_rust_utils')
    def test_save(self, mock_skb_rust_utils):
        mock_input_gray = np.zeros((10, 10), dtype=np.uint8)
        dummy_path = "some/save_path.png"
        # save_image in Rust returns PyResult<()>, so None on success from Python side
        mock_skb_rust_utils.save_image.return_value = None 

        utils_image.save(mock_input_gray, dummy_path)

        mock_skb_rust_utils.save_image.assert_called_once()
        args, _ = mock_skb_rust_utils.save_image.call_args
        self.assertTrue(np.array_equal(args[0], mock_input_gray))
        self.assertEqual(args[1], dummy_path)

    @patch('src.utils.image.skb_rust_utils')
    def test_crop(self, mock_skb_rust_utils):
        mock_input_image = np.zeros((100, 100, 3), dtype=np.uint8) # HxWxC
        mock_cropped_image = np.zeros((10, 20, 3), dtype=np.uint8)
        mock_skb_rust_utils.crop_image.return_value = mock_cropped_image
        
        x, y, w, h = 10, 20, 20, 10 # Crop width 20, height 10

        result = utils_image.crop(mock_input_image, x, y, w, h)

        mock_skb_rust_utils.crop_image.assert_called_once()
        args, _ = mock_skb_rust_utils.crop_image.call_args
        self.assertTrue(np.array_equal(args[0], mock_input_image))
        self.assertEqual(args[1], x)
        self.assertEqual(args[2], y)
        self.assertEqual(args[3], w)
        self.assertEqual(args[4], h)
        self.assertTrue(np.array_equal(result, mock_cropped_image))

    @patch('src.utils.image.skb_rust_utils')
    def test_load(self, mock_skb_rust_utils):
        mock_output_image = np.zeros((50, 50, 3), dtype=np.uint8) # Example color image
        mock_skb_rust_utils.load_image.return_value = mock_output_image
        dummy_path = "some/load_path.png"

        result = utils_image.load(dummy_path)
        
        mock_skb_rust_utils.load_image.assert_called_once_with(dummy_path)
        self.assertTrue(np.array_equal(result, mock_output_image))

    @patch('src.utils.image.skb_rust_utils')
    def test_convertGraysToBlack(self, mock_skb_rust_utils):
        # Test the Python wrapper for filter_grays_to_black
        # The Rust function modifies in-place and returns None.
        # The Python wrapper returns the modified array.
        mock_input_array = np.array([[50, 100, 150], [0, 75, 101]], dtype=np.uint8)
        # Expected array after in-place modification by Rust (mocked)
        # mock_skb_rust_utils.filter_grays_to_black will be mocked to do nothing to the input array
        # as it's hard to simulate in-place modification on the mock's arg.
        # We'll just ensure it's called. The Python wrapper returns the array passed to it.
        
        # Make a copy for the wrapper to potentially modify
        array_to_pass = np.copy(mock_input_array)

        result = utils_image.convertGraysToBlack(array_to_pass)

        mock_skb_rust_utils.filter_grays_to_black.assert_called_once()
        # Check that the argument was the one we passed (or a C-contiguous, uint8 version of it)
        called_arg = mock_skb_rust_utils.filter_grays_to_black.call_args[0][0]
        # The Python wrapper ensures uint8 and C-contiguous.
        # If input was already suitable, it's the same object. Otherwise, it's a copy.
        # For this test, let's assume the input is already suitable to check if it's passed.
        # If not, the test would need to account for the copy.
        self.assertTrue(np.array_equal(called_arg, mock_input_array)) # It should have been processed by the wrapper
        
        # The result should be the same array object if no copy was made by the wrapper,
        # or a modified copy if conversions were needed.
        # Since the mock doesn't actually modify, we can't check content change here
        # unless we make the mock function more complex.
        # The primary goal is that the Python wrapper calls Rust and returns the array.
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
