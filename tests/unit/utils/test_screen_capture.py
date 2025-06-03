import unittest
from unittest.mock import patch, MagicMock, ANY
import numpy as np
import sys
import os

# Adjust sys.path to import from src.utils
# This assumes tests might be run from the project root or a similar context
# where 'src' is a sibling directory to 'tests'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.utils import screen_capture # Imports src.utils.screen_capture

# Helper function at module level for creating mock mss.screenshot.ScreenShot objects
def create_mock_sct_image(width, height, bgra_fill_value=(0,0,0,255)):
    """
    Creates a mock mss.screenshot.ScreenShot object.
    BGRA fill value is a tuple (B, G, R, A).
    """
    mock_img = MagicMock()
    mock_img.width = width
    mock_img.height = height
    mock_img.size = (width, height)

    # Create flat BGRA data (bytes)
    # For a 1x1 pixel (10,20,30,255) -> B=10, G=20, R=30, A=255
    # np.array([[[10,20,30,255]]], dtype=np.uint8).tobytes() would produce this
    # For multiple pixels, it's (B,G,R,A, B,G,R,A, ...)
    bgra_bytes_list = list(bgra_fill_value) * (width * height)
    mock_img.bgra = bytes(bgra_bytes_list)

    # .rgb attribute for mss.tools.to_png is RGB bytes
    # RGB for (10,20,30,255) is (30,20,10)
    rgb_pixel = bgra_fill_value[:3][::-1] # BGR -> RGB
    rgb_bytes_list = list(rgb_pixel) * (width * height)
    mock_img.rgb = bytes(rgb_bytes_list)

    # When np.array(sct_img) is called in the main code, it uses __array_interface__
    # or iterates. We need to mock how np.array() would convert this.
    # The simplest way is to ensure the mock can be converted to a NumPy array
    # that reflects the BGRA data.
    # Let's make the mock itself behave like a NumPy array when np.array() is called on it.
    # This is tricky. A better approach for the test is to mock what np.array(sct_img) returns.
    # However, the current structure has np.array() inside the function.
    # Let's assume np.array(sct_img) correctly uses the .bgra data to form a HxWx4 array.
    # We will control the sct_img.bgra and sct_img.size and test the output.
    # The conversion `img = np.array(sct_img)` will effectively create:
    # np.frombuffer(sct_img.bgra, dtype=np.uint8).reshape((sct_img.height, sct_img.width, 4))
    # This detail is handled by mss internals. Our mock_img.bgra is what matters for np.array().

    return mock_img

class TestScreenCapture(unittest.TestCase):

    @patch('src.utils.screen_capture.mss.tools.to_png')
    @patch('src.utils.screen_capture.mss.mss')
    def test_capture_full_screen_no_save(self, mock_mss_constructor, mock_to_png):
        mock_sct_instance = mock_mss_constructor.return_value.__enter__.return_value
        # Primary monitor data
        monitor_data = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mock_sct_instance.monitors = [{}, monitor_data]

        # Mock sct.grab to return our controlled image data (1x1 pixel for simplicity)
        # BGRA: B=10, G=20, R=30, A=255
        mock_grabbed_image = create_mock_sct_image(width=1, height=1, bgra_fill_value=(10,20,30,255))
        mock_sct_instance.grab.return_value = mock_grabbed_image

        img_array = screen_capture.capture_full_screen()

        mock_sct_instance.grab.assert_called_once_with(monitor_data)
        self.assertIsInstance(img_array, np.ndarray)
        self.assertEqual(img_array.shape, (1, 1, 3)) # H, W, C
        # Expected RGB: R=30, G=20, B=10
        np.testing.assert_array_equal(img_array, np.array([[[30, 20, 10]]], dtype=np.uint8))
        mock_to_png.assert_not_called()

    @patch('src.utils.screen_capture.mss.tools.to_png')
    @patch('src.utils.screen_capture.mss.mss')
    def test_capture_full_screen_with_save(self, mock_mss_constructor, mock_to_png):
        mock_sct_instance = mock_mss_constructor.return_value.__enter__.return_value
        monitor_data = {"left": 0, "top": 0, "width": 1920, "height": 1080}
        mock_sct_instance.monitors = [{}, monitor_data]

        mock_grabbed_image = create_mock_sct_image(width=2, height=1, bgra_fill_value=(10,20,30,255))
        mock_sct_instance.grab.return_value = mock_grabbed_image

        filename = "test_fullscreen.png"
        img_array = screen_capture.capture_full_screen(filename=filename)

        # Check returned array content as well
        self.assertEqual(img_array.shape, (1, 2, 3))
        expected_pixel = np.array([30,20,10], dtype=np.uint8) # R,G,B
        np.testing.assert_array_equal(img_array[0,0,:], expected_pixel)
        np.testing.assert_array_equal(img_array[0,1,:], expected_pixel)

        mock_to_png.assert_called_once_with(mock_grabbed_image.rgb, mock_grabbed_image.size, output=filename)

    @patch('src.utils.screen_capture.mss.tools.to_png')
    @patch('src.utils.screen_capture.mss.mss')
    def test_capture_region_no_save(self, mock_mss_constructor, mock_to_png):
        mock_sct_instance = mock_mss_constructor.return_value.__enter__.return_value
        bbox = (10, 20, 100, 50) # left, top, width, height
        monitor_desc = {"left": 10, "top": 20, "width": 100, "height": 50, "mon": 1}

        # For capture_region, the created mock image should match the bbox width and height
        mock_grabbed_image = create_mock_sct_image(width=100, height=50, bgra_fill_value=(10,20,30,255))
        mock_sct_instance.grab.return_value = mock_grabbed_image

        img_array = screen_capture.capture_region(bbox)

        mock_sct_instance.grab.assert_called_once_with(monitor_desc)
        self.assertIsInstance(img_array, np.ndarray)
        self.assertEqual(img_array.shape, (50, 100, 3)) # H, W, C
        # Check a sample pixel (e.g., top-left)
        expected_pixel = np.array([30,20,10], dtype=np.uint8) # R,G,B
        np.testing.assert_array_equal(img_array[0,0,:], expected_pixel)
        mock_to_png.assert_not_called()

    @patch('src.utils.screen_capture.mss.tools.to_png')
    @patch('src.utils.screen_capture.mss.mss')
    def test_capture_region_with_save(self, mock_mss_constructor, mock_to_png):
        mock_sct_instance = mock_mss_constructor.return_value.__enter__.return_value
        bbox = (10, 20, 100, 50)
        monitor_desc = {"left": 10, "top": 20, "width": 100, "height": 50, "mon": 1}

        mock_grabbed_image = create_mock_sct_image(width=100, height=50, bgra_fill_value=(10,20,30,255))
        mock_sct_instance.grab.return_value = mock_grabbed_image

        filename = "test_region.png"
        img_array = screen_capture.capture_region(bbox, filename=filename)

        self.assertEqual(img_array.shape, (50, 100, 3))
        mock_to_png.assert_called_once_with(mock_grabbed_image.rgb, mock_grabbed_image.size, output=filename)

    def test_capture_region_invalid_bbox(self):
        with self.assertRaisesRegex(ValueError, "bbox must be a tuple of 4 integers"):
            screen_capture.capture_region((10, 20, 100)) # Too few elements
        with self.assertRaisesRegex(ValueError, "bbox must be a tuple of 4 integers"):
            screen_capture.capture_region("not a tuple")
        with self.assertRaisesRegex(ValueError, "bbox must be a tuple of 4 integers"):
            screen_capture.capture_region((10, 20, '100', 50)) # Wrong type

    def test_capture_window_by_title_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            screen_capture.capture_window_by_title("AnyTitle")

if __name__ == '__main__':
    unittest.main()
