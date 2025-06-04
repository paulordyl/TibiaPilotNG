import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import sys
import os

# Adjust sys.path to import from src.utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.utils.simple_image_analyzer import find_largest_object_by_hsv # UPDATED import

# Define path for patching cv2 as it's imported in simple_image_analyzer
PATCH_PATH_CV2 = 'src.utils.simple_image_analyzer.cv2'

class TestSimpleImageAnalyzer(unittest.TestCase):

    def setUp(self):
        self.mock_frame_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        self.mock_frame_hsv = np.zeros((100, 100, 3), dtype=np.uint8)
        self.mock_mask = np.zeros((100,100), dtype=np.uint8)
        self.hsv_lower = np.array([0, 0, 0])
        self.hsv_upper = np.array([179, 255, 255])
        self.single_hsv_range_list = [(self.hsv_lower, self.hsv_upper)] # For adapting old tests
        self.min_area = 50

    # Renamed test methods slightly for clarity, though not strictly required by prompt
    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_no_frame_or_invalid_frame(self, mock_cv2):
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_object_by_hsv(None, self.single_hsv_range_list))
            mock_print.assert_any_call("Warning: Input frame is None or empty.")

        empty_frame = np.array([])
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_object_by_hsv(empty_frame, self.single_hsv_range_list))
            mock_print.assert_any_call("Warning: Input frame is None or empty.")

        invalid_shape_frame = np.zeros((100,100), dtype=np.uint8) # Grayscale
        with patch('builtins.print') as mock_print:
            self.assertIsNone(find_largest_object_by_hsv(invalid_shape_frame, self.single_hsv_range_list))
            mock_print.assert_any_call(f"Warning: Input frame must be an RGB NumPy array (shape HxWx3). Got shape {invalid_shape_frame.shape}")

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_empty_ranges_list(self, mock_cv2):
        with patch('builtins.print') as mock_print:
            result = find_largest_object_by_hsv(self.mock_frame_rgb, [], self.min_area)
        self.assertIsNone(result)
        mock_cv2.cvtColor.assert_not_called() # Should return early
        mock_print.assert_any_call("Warning: hsv_ranges list is empty. No color to detect.")

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_no_contours(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask # Mock combined mask
        mock_cv2.findContours.return_value = ([], None)

        result = find_largest_object_by_hsv(self.mock_frame_rgb, self.single_hsv_range_list, self.min_area)
        self.assertIsNone(result)
        mock_cv2.cvtColor.assert_called_once_with(self.mock_frame_rgb, mock_cv2.COLOR_RGB2HSV)
        mock_cv2.inRange.assert_called_once_with(self.mock_frame_hsv, self.hsv_lower, self.hsv_upper)
        # bitwise_or shouldn't be called if only one range
        mock_cv2.bitwise_or.assert_not_called()
        mock_cv2.findContours.assert_called_once_with(self.mock_mask, mock_cv2.RETR_TREE, mock_cv2.CHAIN_APPROX_SIMPLE)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_contours_below_min_area(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area - 1

        result = find_largest_object_by_hsv(self.mock_frame_rgb, self.single_hsv_range_list, self.min_area)
        self.assertIsNone(result)
        mock_cv2.contourArea.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_one_valid_contour_moments(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 100

        moments_dict = {"m00": 10.0, "m10": 200.0, "m01": 150.0} # cx=20, cy=15
        mock_cv2.moments.return_value = moments_dict

        result = find_largest_object_by_hsv(self.mock_frame_rgb, self.single_hsv_range_list, self.min_area)
        self.assertEqual(result, (20, 15))
        mock_cv2.moments.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_one_valid_contour_m00_zero_fallback_boundingRect(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask

        contour1 = MagicMock(name="contour1_mock")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 50

        moments_dict_zero_m00 = {"m00": 0.0, "m10": 200.0, "m01": 150.0}
        mock_cv2.moments.return_value = moments_dict_zero_m00

        mock_cv2.boundingRect.return_value = (10, 20, 30, 40)

        result = find_largest_object_by_hsv(self.mock_frame_rgb, self.single_hsv_range_list, self.min_area)
        self.assertEqual(result, (25, 40)) # x + w//2, y + h//2
        mock_cv2.moments.assert_called_once_with(contour1)
        mock_cv2.boundingRect.assert_called_once_with(contour1)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_multiple_contours_selects_largest(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv
        mock_cv2.inRange.return_value = self.mock_mask # Assume combined mask is this for simplicity here

        contour_small = MagicMock(name="small_contour")
        contour_large = MagicMock(name="large_contour")
        mock_cv2.findContours.return_value = ([contour_small, contour_large], None)

        def area_side_effect(contour_arg):
            if contour_arg.name == "small_contour":
                return self.min_area + 10
            if contour_arg.name == "large_contour":
                return self.min_area + 100
            return 0
        mock_cv2.contourArea.side_effect = area_side_effect

        moments_large = {"m00": 20.0, "m10": 600.0, "m01": 400.0} # cx=30, cy=20
        moments_small = {"m00": 5.0, "m10": 50.0, "m01": 50.0}

        def moments_side_effect(contour_arg):
            if contour_arg.name == "large_contour": return moments_large
            if contour_arg.name == "small_contour": return moments_small
            return {"m00": 0}
        mock_cv2.moments.side_effect = moments_side_effect

        result = find_largest_object_by_hsv(self.mock_frame_rgb, self.single_hsv_range_list, self.min_area)
        self.assertEqual(result, (30, 20))

        self.assertEqual(mock_cv2.contourArea.call_count, 2)
        mock_cv2.moments.assert_called_once_with(contour_large)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_multiple_ranges_color_in_first(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv

        hsv_range1 = self.single_hsv_range_list[0] # Main range (lower, upper)
        hsv_range2 = (np.array([50,0,0]), np.array([60,255,255]))

        mask1 = np.ones((100,100), dtype=np.uint8)
        mask2 = np.zeros((100,100), dtype=np.uint8)

        mock_cv2.inRange.side_effect = [mask1, mask2]
        mock_cv2.bitwise_or.return_value = mask1

        contour1 = MagicMock(name="valid_contour")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 100
        moments_dict = {"m00": 10.0, "m10": 200.0, "m01": 150.0} # cx=20, cy=15
        mock_cv2.moments.return_value = moments_dict

        result = find_largest_object_by_hsv(self.mock_frame_rgb, [hsv_range1, hsv_range2], self.min_area)
        self.assertEqual(result, (20, 15))

        self.assertEqual(mock_cv2.inRange.call_count, 2)
        mock_cv2.inRange.assert_has_calls([call(self.mock_frame_hsv, hsv_range1[0], hsv_range1[1]),
                                           call(self.mock_frame_hsv, hsv_range2[0], hsv_range2[1])])
        mock_cv2.bitwise_or.assert_called_once_with(mask1, mask2)
        mock_cv2.findContours.assert_called_once_with(mask1, mock_cv2.RETR_TREE, mock_cv2.CHAIN_APPROX_SIMPLE)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_multiple_ranges_color_in_second(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv

        hsv_range1 = (np.array([50,0,0]), np.array([60,255,255]))
        hsv_range2 = self.single_hsv_range_list[0]

        mask1 = np.zeros((100,100), dtype=np.uint8)
        mask2 = np.ones((100,100), dtype=np.uint8)

        mock_cv2.inRange.side_effect = [mask1, mask2]
        mock_cv2.bitwise_or.return_value = mask2

        contour1 = MagicMock(name="valid_contour")
        mock_cv2.findContours.return_value = ([contour1], None)
        mock_cv2.contourArea.return_value = self.min_area + 100
        moments_dict = {"m00": 10.0, "m10": 250.0, "m01": 50.0} # cx=25, cy=5
        mock_cv2.moments.return_value = moments_dict

        result = find_largest_object_by_hsv(self.mock_frame_rgb, [hsv_range1, hsv_range2], self.min_area)
        self.assertEqual(result, (25, 5))

        self.assertEqual(mock_cv2.inRange.call_count, 2)
        mock_cv2.bitwise_or.assert_called_once_with(mask1, mask2)
        mock_cv2.findContours.assert_called_once_with(mask2, mock_cv2.RETR_TREE, mock_cv2.CHAIN_APPROX_SIMPLE)

    @patch(PATCH_PATH_CV2)
    def test_find_largest_object_by_hsv_multiple_ranges_no_color_found(self, mock_cv2):
        mock_cv2.cvtColor.return_value = self.mock_frame_hsv

        hsv_range1 = (np.array([50,0,0]), np.array([60,255,255]))
        hsv_range2 = (np.array([70,0,0]), np.array([80,255,255]))

        mask_empty = np.zeros((100,100), dtype=np.uint8)

        mock_cv2.inRange.side_effect = [mask_empty, mask_empty]
        mock_cv2.bitwise_or.return_value = mask_empty

        mock_cv2.findContours.return_value = ([], None)

        result = find_largest_object_by_hsv(self.mock_frame_rgb, [hsv_range1, hsv_range2], self.min_area)
        self.assertIsNone(result)

        self.assertEqual(mock_cv2.inRange.call_count, 2)
        mock_cv2.bitwise_or.assert_called_once_with(mask_empty, mask_empty) # First mask_empty is `combined_mask` after 1st iteration
        mock_cv2.findContours.assert_called_once_with(mask_empty, mock_cv2.RETR_TREE, mock_cv2.CHAIN_APPROX_SIMPLE)

if __name__ == '__main__':
    unittest.main()
