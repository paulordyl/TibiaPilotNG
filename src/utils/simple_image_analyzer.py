# src/utils/simple_image_analyzer.py
import cv2
import numpy as np

def find_largest_object_by_hsv(
    frame: np.ndarray,
    hsv_ranges: list[tuple[np.ndarray, np.ndarray]],
    min_contour_area: int = 100
) -> tuple[int, int] | None:
    """
    Finds the largest continuous area matching any of the specified HSV color ranges.

    Args:
        frame (np.ndarray): The input image in RGB format.
        hsv_ranges (list[tuple[np.ndarray, np.ndarray]]): A list of HSV range tuples.
            Each tuple should contain (lower_bound_hsv_array, upper_bound_hsv_array).
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

    if not hsv_ranges:
        print("Warning: hsv_ranges list is empty. No color to detect.")
        return None

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    combined_mask = None
    for lower_bound, upper_bound in hsv_ranges:
        if not (isinstance(lower_bound, np.ndarray) and isinstance(upper_bound, np.ndarray)):
            print(f"Warning: HSV range item {(lower_bound, upper_bound)} is not a tuple of NumPy arrays. Skipping this range.")
            continue
        individual_mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        if combined_mask is None:
            combined_mask = individual_mask
        else:
            combined_mask = cv2.bitwise_or(combined_mask, individual_mask)

    if combined_mask is None: # Could happen if hsv_ranges was empty or all items were invalid
        print("Warning: No valid HSV ranges provided or mask could not be created.")
        return None

    mask = combined_mask

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
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            return center_x, center_y
        else:
            x, y, w, h = cv2.boundingRect(largest_contour)
            return x + w // 2, y + h // 2

    return None

if __name__ == '__main__':
    print("Simple Image Analyzer Example (Generalized)")
    sample_frame_main = np.zeros((300, 300, 3), dtype=np.uint8)
    sample_frame_main[100:200, 100:200, 0] = 200
    sample_frame_main[100:200, 100:200, 1] = 20
    sample_frame_main[100:200, 100:200, 2] = 20

    # Define HSV ranges for red
    # Range 1 (more vibrant red)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    # Range 2 (for reds that wrap around hue spectrum)
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    RED_HSV_RANGES = [
        (lower_red1, upper_red1),
        (lower_red2, upper_red2)
    ]

    print(f"Looking for red object using combined HSV ranges...")
    # The sample red (R=200, G=20, B=20) has Hue near 0.
    # It should be found by the first range in RED_HSV_RANGES.
    center_coords = find_largest_object_by_hsv(sample_frame_main, RED_HSV_RANGES, min_contour_area=50)
    if center_coords:
        print(f"Largest red object found at: {center_coords}")
    else:
        print("No significant red object found.")

    # Test with an empty list of ranges
    print("Testing with empty HSV ranges list...")
    coords_empty_ranges = find_largest_object_by_hsv(sample_frame_main, [], min_contour_area=50)
    if coords_empty_ranges is None:
        print("Correctly returned None for empty HSV ranges.")
    else:
        print(f"Error: Expected None for empty HSV ranges, got {coords_empty_ranges}")

    # Test with invalid item in ranges list
    print("Testing with invalid item in HSV ranges list...")
    invalid_ranges = [(np.array([0,0,0]), "not an array")] # type: ignore
    coords_invalid_item = find_largest_object_by_hsv(sample_frame_main, invalid_ranges, min_contour_area=50)
    if coords_invalid_item is None: # Should still be None as the valid ranges part might be empty or not produce a result
        print("Returned None for list with invalid item (or no object found with valid part).")
    else:
        print(f"Found object at {coords_invalid_item} despite invalid item in ranges (check logic).")


    # Test with an empty frame
    print("Testing with an empty frame...")
    empty_frame = np.array([])
    coords_empty = find_largest_object_by_hsv(empty_frame, RED_HSV_RANGES) # type: ignore
    if coords_empty is None:
        print("Correctly returned None for empty frame.")
    else:
        print(f"Error: Expected None for empty frame, got {coords_empty}")

    print("Finished example executions.")
