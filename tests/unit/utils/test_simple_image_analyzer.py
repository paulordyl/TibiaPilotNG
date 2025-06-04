import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import sys
import os

# Adjust sys.path to import from src.utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.utils.simple_image_analyzer import find_largest_color_area

# Define path for patching cv2 as it's imported in simple_image_analyzer
PATCH_PATH_CV2 = 'src.utils.simple_image_analyzer.cv2'

class TestSimpleImageAnalyzer(unittest.TestCase):

    def setUp(self):
        self.mock_frame_rgb = np.zeros((100, 100, 3), dtype=np.uint8) # Dummy 100x100 RGB frame
        self.mock_frame_hsv = np.zeros((100, 100, 3), dtype=np.uint8) # Dummy 100x100 HSV frame (mocked output of cvtColor)
        self.mock_mask = np.zeros((100,100), dtype=np.uint8) # Dummy mask
        self.hsv_lower = np.array([0, 0, 0])
        self.hsv_upper = np.array([179, 255, 255])
        self.min_area = 50

    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_no_frame_or_invalid_frame(self, mock_cv2):
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_color_area(None, self.hsv_lower, self.hsv_upper))
            mock_print.assert_any_call("Warning: Input frame is None or empty.")

        empty_frame = np.array([])
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_color_area(empty_frame, self.hsv_lower, self.hsv_upper))
            mock_print.assert_any_call("Warning: Input frame is None or empty.")

        invalid_shape_frame = np.zeros((100,100), dtype=np.uint8) # Grayscale
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_color_area(invalid_shape_frame, self.hsv_lower, self.hsv_upper))
            mock_print.assert_any_call(f"Warning: Input frame must be an RGB NumPy array (shape HxWx3). Got shape {invalid_shape_frame.shape}")


    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_no_contours(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask
        mock_cv2.findContours.return_value = ([], None) # No contours found

        result = find_largest_color_area(self.mock_frame_rgb, self.hsv_lower, self.hsv_upper, self.min_area)
        self.assertIsNone(result)
        mock_cv2.cvtColor.assert_called_once_with(self.mock_frame_rgb, mock_cv2.COLOR_RGB2HSV)
        mock_cv2.inRange.assert_called_once_with(self.mock_frame_hsv, self.hsv_lower, self.hsv_upper)
        mock_cv2.findContours.assert_called_once_with(self.mock_mask, mock_cv2.RETR_TREE, mock_cv2.CHAIN_APPROX_SIMPLE)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_contours_below_min_area(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area - 1 # Area less than min_area

        result = find_largest_color_area(self.mock_frame_rgb, self.hsv_lower, self.hsv_upper, self.min_area)
        self.assertIsNone(result)
        mock_cv2.contourArea.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_one_valid_contour_moments(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 100 # Valid area

        moments_dict = {"m00": 10.0, "m10": 200.0, "m01": 150.0} # cx=20, cy=15
        mock_cv2.moments.return_value = moments_dict

        result = find_largest_color_area(self.mock_frame_rgb, self.hsv_lower, self.hsv_upper, self.min_area)
        self.assertEqual(result, (20, 15))
        mock_cv2.moments.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_one_valid_contour_m00_zero_fallback_boundingRect(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 50

        moments_dict_zero_m00 = {"m00": 0.0, "m10": 200.0, "m01": 150.0}
        mock_cv2.moments.return_value = moments_dict_zero_m00

        mock_cv2.boundingRect.return_value = (10, 20, 30, 40) # Center should be (10+15, 20+20) = (25, 40)

        result = find_largest_color_area(self.mock_frame_rgb, self.hsv_lower, self.hsv_upper, self.min_area)
        self.assertEqual(result, (25, 40)) # x + w//2, y + h//2
        mock_cv2.moments.assert_called_once_with(contour1)
        mock_cv2.boundingRect.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_color_area_multiple_contours_selects_largest(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour_small = MagicMock(name="small_contour")
        contour_large = MagicMock(name="large_contour")
        # Ensure findContours returns them in some order
        mock_cv2.findContours.return_value = ([contour_small, contour_large], None)

        def area_side_effect(contour_arg):
            if contour_arg.name == "small_contour": # Access mock's name attribute
                return self.min_area + 10
            if contour_arg.name == "large_contour":
                return self.min_area + 100
            return 0
        mock_cv2.contourArea.side_effect = area_side_effect

        moments_large = {"m00": 20.0, "m10": 600.0, "m01": 400.0} # cx=30, cy=20
        moments_small = {"m00": 5.0, "m10": 50.0, "m01": 50.0} # cx=10, cy=10

        def moments_side_effect(contour_arg):
            if contour_arg.name == "large_contour":
                return moments_large
            if contour_arg.name == "small_contour":
                return moments_small
            return {"m00": 0}
        mock_cv2.moments.side_effect = moments_side_effect

        result = find_largest_color_area(self.mock_frame_rgb, self.hsv_lower, self.hsv_upper, self.min_area)
        self.assertEqual(result, (30, 20)) # Center of the largest contour

        self.assertEqual(mock_cv2.contourArea.call_count, 2)
        mock_cv2.moments.assert_called_once_with(contour_large)

if __name__ == '__main__':
    unittest.main()
