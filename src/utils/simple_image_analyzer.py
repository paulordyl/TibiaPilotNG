# src/utils/simple_image_analyzer.py
import cv2
import numpy as np

def find_largest_color_area(
    frame: np.ndarray,
    target_hsv_lower: np.ndarray,
    target_hsv_upper: np.ndarray,
    min_contour_area: int = 100 # Optional: minimum area to consider a contour valid
    ) -> tuple[int, int] | None:
    """
    Finds the largest continuous area of a specified color in an image.

    Args:
        frame (np.ndarray): The input image in RGB format.
        target_hsv_lower (np.ndarray): The lower bound of the target color in HSV.
        target_hsv_upper (np.ndarray): The upper bound of the target color in HSV.
        min_contour_area (int): Minimum area for a contour to be considered.

    Returns:
        tuple[int, int] | None: (x, y) coordinates of the center of the largest area,
                                 or None if no suitable area is found.
    """
    if frame is None or frame.size == 0:
        print("Warning: Input frame is None or empty.")
        return None

    if not isinstance(frame, np.ndarray) or frame.ndim != 3 or frame.shape[2] != 3:
        print(f"Warning: Input frame must be an RGB NumPy array (shape HxWx3). Got shape {frame.shape if isinstance(frame, np.ndarray) else type(frame)}")
        return None

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Create a mask for the target color
    # Note: For colors like red that wrap around the hue spectrum (0-10 and 170-180),
    # two masks might be needed and then combined. This function assumes a single range.
    mask = cv2.inRange(hsv_frame, target_hsv_lower, target_hsv_upper)

    # Optional: Morphological operations to reduce noise and connect regions
    # kernel = np.ones((5, 5), np.uint8)
    # mask = cv2.erode(mask, kernel, iterations=1)
    # mask = cv2.dilate(mask, kernel, iterations=2) # Dilate more to connect parts

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest_contour = None
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area and area >= min_contour_area:
            max_area = area
            largest_contour = contour

    if largest_contour is not None:
        # Calculate the center of the contour using moments
        M = cv2.moments(largest_contour)
        if M["m00"] != 0: # Avoid division by zero
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            return center_x, center_y
        else:
            # Fallback if m00 is zero (e.g. extremely small contour not filtered by area, or a line)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return x + w // 2, y + h // 2

    return None

if __name__ == '__main__':
    # Example Usage (requires an image file 'test_image.png' with some red)
    # Create a dummy frame for basic testing if no image is available.
    # This is not a unit test, just a simple execution check.

    print("Simple Image Analyzer Example")
    # Create a sample frame: 300x300, RGB, with a red square
    sample_frame_main = np.zeros((300, 300, 3), dtype=np.uint8) # Renamed to avoid conflict
    # Make the square red: R=200, G=20, B=20
    sample_frame_main[100:200, 100:200, 0] = 200 # Red channel
    sample_frame_main[100:200, 100:200, 1] = 20  # Green channel
    sample_frame_main[100:200, 100:200, 2] = 20  # Blue channel
    # Expected center: (150, 150) roughly (center of 100-199 is (100+199)/2 = 149.5)

    # Define HSV range for red (example - might need tuning)
    # OpenCV Hue values are typically 0-179 for 8-bit images.
    # Lower bound for red (around hue 0-10)
    lower_red1_main = np.array([0, 100, 100])    # Low H, Med S, Med V
    upper_red1_main = np.array([10, 255, 255])   # High H, High S, High V

    # Lower bound for red (around hue 170-180, for colors that wrap around)
    lower_red2_main = np.array([170, 100, 100])
    upper_red2_main = np.array([179, 255, 255]) # Max Hue is 179 for 8-bit OpenCV

    # --- Test with first red range ---
    print(f"Looking for primary red range (0-10 Hue)...")
    center_coords1_main = find_largest_color_area(sample_frame_main, lower_red1_main, upper_red1_main, min_contour_area=50)
    if center_coords1_main:
        print(f"Largest red area (range 1) found at: {center_coords1_main}")
        # Expected: (149, 149) or (150, 150) depending on exact moment calculation for a square
    else:
        print("No significant red area (range 1) found.")

    # --- Test with second red range (should not find the sample red) ---
    # The sample red (R=200, G=20, B=20) has a Hue close to 0.
    # This second range (170-179 Hue) should NOT find it.
    print(f"Looking for secondary red range (170-179 Hue)...")
    center_coords2_main = find_largest_color_area(sample_frame_main, lower_red2_main, upper_red2_main, min_contour_area=50)
    if center_coords2_main:
        print(f"Largest red area (range 2) found at: {center_coords2_main}")
    else:
        print("No significant red area (range 2) found.")

    # Example of how to display (if you have cv2 windowing available and uncomment cv2 calls):
    # if center_coords1_main:
    #   frame_to_show = sample_frame_main.copy() # Avoid drawing on original if reused
    #   cv2.circle(frame_to_show, center_coords1_main, 7, (0,255,0), -1) # Green circle
    #   # OpenCV uses BGR for display, so convert RGB frame to BGR
    #   cv2.imshow("Frame with Red Dot", cv2.cvtColor(frame_to_show, cv2.COLOR_RGB2BGR))
    #   cv2.waitKey(0)
    #   cv2.destroyAllWindows()

    # Test with an empty frame
    print("Testing with an empty frame...")
    empty_frame = np.array([])
    coords_empty = find_largest_color_area(empty_frame, lower_red1_main, upper_red1_main)
    if coords_empty is None:
        print("Correctly returned None for empty frame.")
    else:
        print(f"Error: Expected None for empty frame, got {coords_empty}")

    # Test with a frame of wrong shape/type
    print("Testing with a wrong shape frame (2D grayscale)...")
    wrong_shape_frame = np.zeros((100,100), dtype=np.uint8)
    coords_wrong_shape = find_largest_color_area(wrong_shape_frame, lower_red1_main, upper_red1_main)
    if coords_wrong_shape is None:
        print("Correctly returned None for wrong shape frame.")
    else:
        print(f"Error: Expected None for wrong shape frame, got {coords_wrong_shape}")

    print("Testing with a frame of correct shape but wrong type (float)...")
    float_frame = np.zeros((100,100,3), dtype=np.float32)
    # cvtColor would raise error here if not uint8. Our check is for ndim/shape[2]
    # The cv2.cvtColor itself will handle the type error for non-uint8 input for RGB2HSV.
    # Let's see if our basic check catches it or if cvtColor's error is the primary gate.
    # The function expects uint8 for image processing.
    # The check `frame.ndim != 3 or frame.shape[2] != 3` doesn't check dtype.
    # cv2.cvtColor will raise: cv2.error: OpenCV(4.x.x) ...Unsupported combination of source format (=5) and destination format (=2)
    # It's fine to let cv2 handle this, or add an explicit dtype check.
    # For now, the current checks are as per implementation.
    # coords_float_frame = find_largest_color_area(float_frame, lower_red1_main, upper_red1_main)
    # This would likely error out in cvtColor, which is acceptable.
    # For robustness, one might add `and frame.dtype == np.uint8` to the check.
    # The prompt didn't specify such strict type checking beyond shape.
    print("Finished example executions.")
