import logging
import cv2
import numpy as np
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScreenParser:
    """
    Analyzes image frames for specific visual cues, like the presence of a target color.
    """
    def __init__(self, roi_x: int = 0, roi_y: int = 0, roi_width: int = -1, roi_height: int = -1,
                 target_color_hsv_lower: tuple = (35, 100, 100), # Default: Green
                 target_color_hsv_upper: tuple = (85, 255, 255), # Default: Green
                 detection_threshold_pixels: int = 1000):
        """
        Initializes the ScreenParser.

        Args:
            roi_x (int): X-coordinate of the top-left corner of the Region of Interest.
            roi_y (int): Y-coordinate of the top-left corner of the Region of Interest.
            roi_width (int): Width of the ROI. -1 means full width from roi_x.
            roi_height (int): Height of the ROI. -1 means full height from roi_y.
            target_color_hsv_lower (tuple): Lower bound for the target color in HSV (H, S, V).
            target_color_hsv_upper (tuple): Upper bound for the target color in HSV (H, S, V).
            detection_threshold_pixels (int): Minimum number of pixels matching the target color
                                              to consider it "detected".
        """
        self.roi_x = roi_x
        self.roi_y = roi_y
        self.roi_width = roi_width
        self.roi_height = roi_height
        self.target_color_hsv_lower = np.array(target_color_hsv_lower, dtype=np.uint8)
        self.target_color_hsv_upper = np.array(target_color_hsv_upper, dtype=np.uint8)
        self.detection_threshold_pixels = detection_threshold_pixels
        logger.info(f"ScreenParser initialized. ROI: (x={roi_x}, y={roi_y}, w={roi_width}, h={roi_height}). "
                    f"Target HSV range: {target_color_hsv_lower} to {target_color_hsv_upper}. "
                    f"Detection threshold: {detection_threshold_pixels} pixels.")

    def _get_roi(self, frame_cv):
        """
        Extracts the Region of Interest from the frame.
        """
        h, w = frame_cv.shape[:2]

        roi_x_abs = self.roi_x if self.roi_x >= 0 else 0
        roi_y_abs = self.roi_y if self.roi_y >= 0 else 0

        roi_w_abs = self.roi_width if self.roi_width > 0 else w - roi_x_abs
        # Ensure roi_w_abs does not exceed frame boundaries
        roi_w_abs = min(roi_w_abs, w - roi_x_abs)


        roi_h_abs = self.roi_height if self.roi_height > 0 else h - roi_y_abs
        # Ensure roi_h_abs does not exceed frame boundaries
        roi_h_abs = min(roi_h_abs, h - roi_y_abs)

        if roi_w_abs <= 0 or roi_h_abs <= 0:
            logger.warning(f"Invalid ROI dimensions ({roi_w_abs}x{roi_h_abs}) for frame size ({w}x{h}). Using full frame.")
            return frame_cv

        logger.debug(f"Extracting ROI: x={roi_x_abs}, y={roi_y_abs}, w={roi_w_abs}, h={roi_h_abs} from frame size {w}x{h}")
        return frame_cv[roi_y_abs:roi_y_abs + roi_h_abs, roi_x_abs:roi_x_abs + roi_w_abs]


    def analyze_frame(self, frame_pil: Image.Image) -> dict:
        """
        Analyzes the provided image frame for a target color.

        Args:
            frame_pil (PIL.Image.Image): The image frame to analyze.

        Returns:
            dict: A dictionary containing the analysis result:
                  {
                      "status": "target_color_detected" | "target_color_not_detected",
                      "pixel_count": <int_pixel_count>,
                      "roi_applied": <tuple_or_none_of_roi_coords_used>
                  }
        """
        if frame_pil is None:
            logger.error("Received None frame for analysis.")
            return {
                "status": "target_color_not_detected",
                "pixel_count": 0,
                "roi_applied": None,
                "error": "Input frame was None"
            }

        try:
            # 1. Convert Pillow Image to OpenCV NumPy array (BGR)
            # PIL images are typically RGB. OpenCV uses BGR by default.
            frame_cv_rgb = np.array(frame_pil)
            if frame_cv_rgb.shape[2] == 4: # RGBA
                frame_cv_bgr = cv2.cvtColor(frame_cv_rgb, cv2.COLOR_RGBA2BGR)
                logger.debug("Converted RGBA Pillow Image to BGR OpenCV format.")
            elif frame_cv_rgb.shape[2] == 3: # RGB
                frame_cv_bgr = cv2.cvtColor(frame_cv_rgb, cv2.COLOR_RGB2BGR)
                logger.debug("Converted RGB Pillow Image to BGR OpenCV format.")
            else:
                logger.error(f"Unsupported number of channels in Pillow image: {frame_cv_rgb.shape[2]}")
                return {
                    "status": "target_color_not_detected",
                    "pixel_count": 0,
                    "roi_applied": None,
                    "error": f"Unsupported image channels: {frame_cv_rgb.shape[2]}"
                }

            # Apply ROI
            roi_frame_bgr = self._get_roi(frame_cv_bgr)
            h, w = roi_frame_bgr.shape[:2]
            roi_coords_used = (self.roi_x, self.roi_y, self.roi_width if self.roi_width > 0 else w, self.roi_height if self.roi_height > 0 else h)


            # 2. Convert the input image (or ROI) to HSV color space
            frame_hsv = cv2.cvtColor(roi_frame_bgr, cv2.COLOR_BGR2HSV)
            logger.debug("Converted ROI to HSV color space.")

            # 3. Create a mask for the target color
            # Target color (e.g., bright green) and tolerance are defined in __init__
            mask = cv2.inRange(frame_hsv, self.target_color_hsv_lower, self.target_color_hsv_upper)
            logger.debug("Created color mask.")

            # 4. Calculate the number of non-zero pixels in the mask
            matching_pixel_count = cv2.countNonZero(mask)
            logger.info(f"Number of pixels matching target color in ROI: {matching_pixel_count}")

            # 5. Decision: If the count exceeds a threshold, color is "detected"
            if matching_pixel_count >= self.detection_threshold_pixels:
                status = "target_color_detected"
                logger.info(f"Target color DETECTED (count {matching_pixel_count} >= threshold {self.detection_threshold_pixels}).")
            else:
                status = "target_color_not_detected"
                logger.info(f"Target color NOT detected (count {matching_pixel_count} < threshold {self.detection_threshold_pixels}).")

            return {
                "status": status,
                "pixel_count": matching_pixel_count,
                "roi_applied": roi_coords_used
            }

        except Exception as e:
            logger.error(f"Error during frame analysis: {e}", exc_info=True)
            return {
                "status": "target_color_not_detected",
                "pixel_count": 0,
                "roi_applied": None,
                "error": str(e)
            }

# Example usage for standalone testing
if __name__ == "__main__":
    # Create a dummy green and red image for testing
    width, height = 640, 480

    # Test Case 1: Image with significant green
    green_image_np = np.zeros((height, width, 3), dtype=np.uint8)
    green_image_np[100:200, 100:200] = [0, 255, 0]  # BGR for green (OpenCV style)
    # Add more green to pass threshold
    green_image_np[0:50, 0:200] = [0, 250, 0] # 50 * 200 = 10000 pixels
    pil_green_image = Image.fromarray(cv2.cvtColor(green_image_np, cv2.COLOR_BGR2RGB)) # Convert to RGB for PIL

    # Test Case 2: Image with no (or very little) green
    red_image_np = np.zeros((height, width, 3), dtype=np.uint8)
    red_image_np[:, :] = [0, 0, 255]  # BGR for red
    pil_red_image = Image.fromarray(cv2.cvtColor(red_image_np, cv2.COLOR_BGR2RGB))

    # Test Case 3: Image with RGBA (e.g. from PNG)
    rgba_image_np = np.zeros((height, width, 4), dtype=np.uint8) # RGBA
    rgba_image_np[100:150, 100:300] = [0, 255, 0, 255] # Green with full alpha
    pil_rgba_image = Image.fromarray(rgba_image_np, 'RGBA')


    # Initialize parser (default uses green target, threshold 1000 pixels)
    # For testing ROI, let's define one
    # parser = ScreenParser(roi_x=50, roi_y=50, roi_width=300, roi_height=200)
    parser = ScreenParser() # Full frame for these tests initially.

    logger.info("--- Testing with Green Image ---")
    result_green = parser.analyze_frame(pil_green_image)
    logger.info(f"Analysis result for green image: {result_green}")
    assert result_green["status"] == "target_color_detected"
    assert result_green["pixel_count"] > parser.detection_threshold_pixels

    logger.info("--- Testing with Red Image ---")
    result_red = parser.analyze_frame(pil_red_image)
    logger.info(f"Analysis result for red image: {result_red}")
    assert result_red["status"] == "target_color_not_detected"
    assert result_red["pixel_count"] < parser.detection_threshold_pixels

    logger.info("--- Testing with RGBA Green Image ---")
    result_rgba_green = parser.analyze_frame(pil_rgba_image)
    logger.info(f"Analysis result for RGBA green image: {result_rgba_green}")
    assert result_rgba_green["status"] == "target_color_detected"
    assert result_rgba_green["pixel_count"] > parser.detection_threshold_pixels

    logger.info("--- Testing with ROI that excludes most green ---")
    # Green is at [0:50, 0:200] and [100:200, 100:200]
    # ROI from (250,250) to (end,end) should have no green
    parser_roi_test = ScreenParser(roi_x=250, roi_y=250, roi_width=-1, roi_height=-1)
    result_green_roi_miss = parser_roi_test.analyze_frame(pil_green_image)
    logger.info(f"Analysis result for green image with ROI missing green: {result_green_roi_miss}")
    assert result_green_roi_miss["status"] == "target_color_not_detected"
    assert result_green_roi_miss["pixel_count"] == 0

    logger.info("--- Testing with ROI that includes some green ---")
    # ROI from (0,0) to (150,150) should catch some green from both areas
    parser_roi_hit = ScreenParser(roi_x=0, roi_y=0, roi_width=150, roi_height=150, detection_threshold_pixels=100) # Lower threshold for this test
    result_green_roi_hit = parser_roi_hit.analyze_frame(pil_green_image)
    logger.info(f"Analysis result for green image with ROI hitting green: {result_green_roi_hit}")
    assert result_green_roi_hit["status"] == "target_color_detected"
    assert result_green_roi_hit["pixel_count"] > parser_roi_hit.detection_threshold_pixels


    logger.info("--- Testing with None image ---")
    result_none = parser.analyze_frame(None)
    logger.info(f"Analysis result for None image: {result_none}")
    assert result_none["status"] == "target_color_not_detected"
    assert "error" in result_none

    logger.info("ScreenParser standalone tests completed.")

    # Example of loading from settings.toml (conceptual, needs config file and toml lib)
    # try:
    #     import toml
    #     config_path = "../config/settings.toml" # Adjust path as needed
    #     config = toml.load(config_path)
    #     vision_settings = config.get('vision', {})
    #     parser_from_config = ScreenParser(
    #         roi_x=vision_settings.get('roi_x', 0),
    #         roi_y=vision_settings.get('roi_y', 0),
    #         roi_width=vision_settings.get('roi_width', -1),
    #         roi_height=vision_settings.get('roi_height', -1)
    #         # Could also load target_color and threshold from config
    #     )
    #     logger.info(f"Successfully initialized ScreenParser from config (conceptual): {config_path}")
    #     # result_config_test = parser_from_config.analyze_frame(pil_green_image)
    #     # logger.info(f"Analysis with config-loaded parser: {result_config_test}")
    # except ImportError:
    #     logger.warning("toml library not installed, skipping config load example.")
    # except FileNotFoundError:
    #     logger.warning(f"Config file for ScreenParser not found at {config_path}, skipping config load example.")
    # except Exception as e:
    #     logger.error(f"Error in config loading example: {e}")

```
