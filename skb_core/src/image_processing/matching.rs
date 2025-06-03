use crate::AppError; // Assuming AppError is in the root or accessible via crate::
use image::DynamicImage;
use log::{info, error}; // Added error log
use opencv::{
    core::{self, Mat, Rect_}, // Added Rect_
    imgcodecs, // For debugging, to write images
    imgproc,
    prelude::*, // For Mat::roi
};

// Placeholder for AppError if not defined globally, for compilation
/*
#[derive(Debug)]
pub enum AppError {
    ImageProcessingError(String),
    NotImplemented,
    // Add other error variants as needed
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::ImageProcessingError(s) => write!(f, "Image Processing Error: {}", s),
            AppError::NotImplemented => write!(f, "Functionality not implemented"),
        }
    }
}

impl std::error::Error for AppError {}
*/

// Helper function to convert image::DynamicImage to opencv::Mat
// This is a simplified conversion and might need adjustments based on image formats
fn dynamic_image_to_mat(img: &DynamicImage) -> Result<Mat, AppError> {
    let img_rgba8 = img.to_rgba8(); // Convert to RgbaImage
    let (width, height) = img_rgba8.dimensions();
    let data = img_rgba8.into_raw(); // This gives Vec<u8>

    // Create Mat from raw data. For RGBA, type is CV_8UC4.
    // OpenCV typically uses BGR or BGRA order, so color conversion might be needed if issues arise.
    unsafe {
        Mat::new_rows_cols_with_data(height as i32, width as i32, core::CV_8UC4, data.as_ptr() as *mut _, core::Mat_AUTO_STEP)
            .map_err(|e| AppError::ImageProcessingError(format!("Failed to create Mat from DynamicImage: {}", e)))
            .and_then(|mat_ref| mat_ref.clone().map_err(|e| AppError::ImageProcessingError(format!("Failed to clone Mat: {}", e)))) // Clone to own the Mat
    }
}


/// Locates a template image within a larger image (haystack) using OpenCV's template matching.
///
/// # Arguments
/// * `haystack` - The larger image in which to search.
/// * `needle` - The template image to search for.
/// * `confidence_threshold` - A float between 0.0 and 1.0. Matches below this threshold are ignored.
///                           A typical starting value might be 0.8 or 0.9.
///
/// # Returns
/// `Ok(Some((x, y, width, height)))` if the template is found with sufficient confidence.
/// `Ok(None)` if the template is not found or confidence is too low.
/// `Err(AppError)` if an error occurs during processing.
pub fn locate_template_on_image(
    haystack: &DynamicImage,
    needle: &DynamicImage,
    confidence_threshold: f32,
) -> Result<Option<(i32, i32, i32, i32)>, AppError> {
    info!("Attempting to locate template on image.");

    let haystack_mat = dynamic_image_to_mat(haystack)
        .map_err(|e| {
            error!("Failed to convert haystack to Mat: {}", e);
            e
        })?;
    let needle_mat = dynamic_image_to_mat(needle)
        .map_err(|e| {
            error!("Failed to convert needle to Mat: {}", e);
            e
        })?;

    if needle_mat.cols() > haystack_mat.cols() || needle_mat.rows() > haystack_mat.rows() {
        error!("Needle dimensions are larger than haystack dimensions.");
        return Err(AppError::ImageProcessingError(
            "Needle dimensions cannot be larger than haystack dimensions".to_string(),
        ));
    }

    // The result matrix will have dimensions: (W-w+1) x (H-h+1)
    // W, H = dimensions of haystack; w, h = dimensions of needle
    let result_cols = haystack_mat.cols() - needle_mat.cols() + 1;
    let result_rows = haystack_mat.rows() - needle_mat.rows() + 1;
    let mut result_mat = Mat::default();

    // Perform template matching
    // TM_CCOEFF_NORMED is often a good choice as it normalizes for brightness and contrast.
    match imgproc::match_template(&haystack_mat, &needle_mat, &mut result_mat, imgproc::TM_CCOEFF_NORMED, &Mat::default()) {
        Ok(_) => {
            // Find the location of the best match
            let mut min_val = 0.0;
            let mut max_val = 0.0;
            let mut min_loc = core::Point::new(0, 0);
            let mut max_loc = core::Point::new(0, 0);

            match core::min_max_loc(&result_mat, Some(&mut min_val), Some(&mut max_val), Some(&mut min_loc), Some(&mut max_loc), &Mat::default()) {
                Ok(_) => {
                    // For TM_CCOEFF_NORMED, the best match is the max_val at max_loc.
                    info!("Template matching completed. Max confidence: {:.2}, Location: ({}, {})", max_val, max_loc.x, max_loc.y);
                    if max_val >= confidence_threshold as f64 { // Ensure comparison is f64 if max_val is f64
                        let (x, y, width, height) = (max_loc.x, max_loc.y, needle_mat.cols(), needle_mat.rows());
                        info!("Template found at ({}, {}) with width {} and height {}", x, y, width, height);
                        Ok(Some((x, y, width, height)))
                    } else {
                        info!("Template not found with sufficient confidence (max_val: {} < threshold: {}).", max_val, confidence_threshold);
                        Ok(None)
                    }
                }
                Err(e) => {
                    error!("Failed to find min/max location in result matrix: {}", e);
                    Err(AppError::ImageProcessingError(format!("Failed to find min/max location in result matrix: {}", e)))
                }
            }
        }
        Err(e) => {
            error!("OpenCV template matching failed: {}", e);
            Err(AppError::ImageProcessingError(format!("OpenCV template matching failed: {}", e)))
        }
    }
}

// Example of saving a Mat to a file for debugging.
// Not used in the main function but can be helpful.
#[allow(dead_code)]
fn _save_mat_to_file(mat: &Mat, filename: &str) -> Result<(), AppError> {
    let params = core::Vector::new(); // Empty params for default behavior
    imgcodecs::imwrite(filename, mat, &params)
        .map_err(|e| AppError::ImageProcessingError(format!("Failed to write image to {}: {}", filename, e)))
}

// Example of taking a sub-image (ROI - Region of Interest) from a Mat
#[allow(dead_code)]
fn _get_roi_from_mat(mat: &Mat, x: i32, y: i32, width: i32, height: i32) -> Result<Mat, AppError> {
    if x < 0 || y < 0 || width <= 0 || height <= 0 {
        return Err(AppError::ImageProcessingError("Invalid ROI dimensions".to_string()));
    }
    if x + width > mat.cols() || y + height > mat.rows() {
        return Err(AppError::ImageProcessingError("ROI exceeds Mat boundaries".to_string()));
    }
    let rect = Rect_::new(x, y, width, height);
    Mat::roi(mat, rect).map_err(|e| AppError::ImageProcessingError(format!("Failed to get ROI: {}", e)))
}

/// Locates all non-overlapping occurrences of a template image within a larger image.
///
/// # Arguments
/// * `haystack` - The larger image in which to search.
/// * `needle` - The template image to search for.
/// * `confidence_threshold` - A float between 0.0 and 1.0. Matches below this threshold are ignored.
/// * `max_overlap` - Not strictly used in the current "clearing" NMS, but a parameter for future, more advanced NMS.
///                   The current method clears a region the size of the needle around a found match.
///
/// # Returns
/// `Ok(Vec<(i32, i32, u32, u32)>)` containing all found locations `(x, y, width, height)`.
/// `Err(AppError)` if an error occurs during processing.
use log::debug; // Added debug log

// Helper struct for NMS
#[derive(Debug, Clone)]
struct Detection {
    rect: Rect_<i32>,
    score: f32,
}

/// Calculates the Intersection over Union (IoU) for two rectangles.
/// Rectangles are opencv::core::Rect_<i32>
fn calculate_iou(rect1: &Rect_<i32>, rect2: &Rect_<i32>) -> f32 {
    let x_a = core::max(rect1.x, rect2.x);
    let y_a = core::max(rect1.y, rect2.y);
    let x_b = core::min(rect1.x + rect1.width, rect2.x + rect2.width);
    let y_b = core::min(rect1.y + rect1.height, rect2.y + rect2.height);

    let intersection_area = core::max(0, x_b - x_a) * core::max(0, y_b - y_a);
    if intersection_area <= 0 {
        return 0.0;
    }

    let rect1_area = rect1.width * rect1.height;
    let rect2_area = rect2.width * rect2.height;

    let union_area = (rect1_area + rect2_area - intersection_area) as f32;
    if union_area <= 0.0 { // Should not happen if areas are positive and intersection is less
        return 0.0;
    }

    intersection_area as f32 / union_area
}


/// Locates all non-overlapping occurrences of a template image within a larger image
/// using Non-Maximum Suppression (NMS).
///
/// # Arguments
/// * `haystack` - The larger image in which to search.
/// * `needle` - The template image to search for.
/// * `confidence_threshold` - A float between 0.0 and 1.0. Matches below this threshold are ignored.
/// * `max_overlap_threshold` - A float between 0.0 and 1.0. If IoU between two detections is
///                             greater than this, the one with lower score is suppressed.
///
/// # Returns
/// `Ok(Vec<(i32, i32, u32, u32)>)` containing all found locations `(x, y, width, height)`.
/// `Err(AppError)` if an error occurs during processing.
pub fn locate_all_templates_on_image(
    haystack: &DynamicImage,
    needle: &DynamicImage,
    confidence_threshold: f32,
    max_overlap_threshold: f32,
) -> Result<Vec<(i32, i32, u32, u32)>, AppError> {
    info!(
        "Locating all templates. Confidence: {}, Max Overlap: {}",
        confidence_threshold, max_overlap_threshold
    );

    let haystack_mat = dynamic_image_to_mat(haystack)?;
    let needle_mat = dynamic_image_to_mat(needle)?;

    if needle_mat.cols() > haystack_mat.cols() || needle_mat.rows() > haystack_mat.rows() {
        error!("Needle dimensions are larger than haystack dimensions.");
        return Err(AppError::ImageProcessingError(
            "Needle dimensions cannot be larger than haystack dimensions".to_string(),
        ));
    }

    let mut result_mat = Mat::default();
    imgproc::match_template(&haystack_mat, &needle_mat, &mut result_mat, imgproc::TM_CCOEFF_NORMED, &Mat::default())
        .map_err(|e| AppError::ImageProcessingError(format!("OpenCV template matching failed: {}", e)))?;

    let needle_width = needle_mat.cols();
    let needle_height = needle_mat.rows();

    let mut potential_detections: Vec<Detection> = Vec::new();

    // Iterate through the result_mat to find all points above the confidence threshold.
    // result_mat is a CV_32F (float) matrix.
    for y in 0..result_mat.rows() {
        for x in 0..result_mat.cols() {
            let score = *result_mat.at_2d::<f32>(y, x).map_err(|e| AppError::ImageProcessingError(format!("Failed to access result_mat at ({},{}): {}", y, x, e)))?;
            if score >= confidence_threshold {
                potential_detections.push(Detection {
                    rect: Rect_::new(x, y, needle_width, needle_height),
                    score,
                });
            }
        }
    }
    debug!("Found {} potential detections above confidence threshold {}.", potential_detections.len(), confidence_threshold);

    // Sort potential detections by score in descending order.
    potential_detections.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));

    let mut final_detections: Vec<Rect_<i32>> = Vec::new();
    while !potential_detections.is_empty() {
        // Take the detection with the highest score.
        let best_detection = potential_detections.remove(0);
        final_detections.push(best_detection.rect.clone());
        debug!("Selected best detection: {:?} with score {}", best_detection.rect, best_detection.score);

        // Remove detections that significantly overlap with the best_detection.
        potential_detections.retain(|detection| {
            let iou = calculate_iou(&best_detection.rect, &detection.rect);
            let should_retain = iou <= max_overlap_threshold;
            if !should_retain {
                debug!("Suppressing detection {:?} (score {}) due to IoU {} with {:?}.",
                       detection.rect, detection.score, iou, best_detection.rect);
            }
            should_retain
        });
    }

    info!("NMS complete. Found {} final detections.", final_detections.len());

    // Convert final_detections (Vec<Rect_<i32>>) to Vec<(i32, i32, u32, u32)>
    let output_locations = final_detections
        .into_iter()
        .map(|rect| (rect.x, rect.y, rect.width as u32, rect.height as u32))
        .collect();

    Ok(output_locations)
}


use crate::image_processing::{templates::TemplateManager, cache::DetectionCache};
use crate::screen_capture::capture; // Import screen capture functions


#[cfg(test)]
mod tests {
    use super::*;
    use opencv::core::Rect_;

    #[test]
    fn test_calculate_iou_no_overlap() {
        let rect1 = Rect_::new(0, 0, 10, 10);
        let rect2 = Rect_::new(20, 20, 10, 10);
        assert_eq!(calculate_iou(&rect1, &rect2), 0.0);
    }

    #[test]
    fn test_calculate_iou_full_overlap() {
        let rect1 = Rect_::new(0, 0, 10, 10);
        let rect2 = Rect_::new(0, 0, 10, 10);
        assert_eq!(calculate_iou(&rect1, &rect2), 1.0);
    }

    #[test]
    fn test_calculate_iou_partial_overlap() {
        let rect1 = Rect_::new(0, 0, 10, 10);  // Area = 100
        let rect2 = Rect_::new(5, 5, 10, 10);  // Area = 100
        // Intersection: x_a=5, y_a=5, x_b=10, y_b=10. width=5, height=5. Area_I = 25
        // Union: 100 + 100 - 25 = 175
        // IoU = 25 / 175 = 1/7
        assert_eq!(calculate_iou(&rect1, &rect2), 25.0 / 175.0);
    }

    #[test]
    fn test_calculate_iou_one_contains_other() {
        let rect1 = Rect_::new(0, 0, 20, 20); // Area = 400
        let rect2 = Rect_::new(5, 5, 10, 10); // Area = 100
        // Intersection: x_a=5, y_a=5, x_b=15, y_b=15. width=10, height=10. Area_I = 100
        // Union: 400 + 100 - 100 = 400
        // IoU = 100 / 400 = 0.25
        assert_eq!(calculate_iou(&rect1, &rect2), 100.0 / 400.0);
    }

    #[test]
    fn test_calculate_iou_touching_edges() {
        let rect1 = Rect_::new(0,0,10,10);
        let rect2 = Rect_::new(10,0,10,10); // Touches at x=10
        assert_eq!(calculate_iou(&rect1, &rect2), 0.0);
    }

    // It's challenging to create a full integration test for locate_all_templates_on_image
    // without actual image files and a more complex setup.
    // However, we can test the NMS logic conceptually if we could mock `match_template`
    // or provide a pre-computed `result_mat`. This is beyond simple changes here.
    // The existing test in `digit_recognition.rs` will cover the basic flow.

    // --- Tests for NMS Logic Simulation ---
    // Re-define MockDetection locally for this test module if not accessible otherwise
    // (it's defined at the module level where locate_all_templates_on_image is)
    // For testing, we can just use the same struct definition if it's private to the parent module.
    // If `Detection` struct is private to parent, we might need to re-define or make it pub(crate).
    // Assuming `Detection` struct is accessible for now, or we'll use tuples/local struct.
    // For simplicity, let's assume we can create `Detection` instances here for the mock NMS.
    // If not, the `perform_mock_nms` can take Vec<(Rect_<i32>, f32)>

    fn perform_mock_nms(mut potential_detections: Vec<super::Detection>, max_overlap_threshold: f32) -> Vec<Rect_<i32>> {
        potential_detections.sort_by(|a, b| b.score.partial_cmp(&a.score).unwrap_or(std::cmp::Ordering::Equal));
        let mut final_detections: Vec<Rect_<i32>> = Vec::new();
        while !potential_detections.is_empty() {
            let best_detection = potential_detections.remove(0);
            final_detections.push(best_detection.rect.clone());
            potential_detections.retain(|detection| {
                let iou = calculate_iou(&best_detection.rect, &detection.rect);
                iou <= max_overlap_threshold
            });
        }
        final_detections
    }

    #[test]
    fn test_nms_no_overlap() {
        let detections = vec![
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.9 },
            super::Detection { rect: Rect_::new(20, 20, 10, 10), score: 0.8 },
        ];
        let kept = perform_mock_nms(detections, 0.3);
        assert_eq!(kept.len(), 2);
    }

    #[test]
    fn test_nms_full_overlap() {
        let detections = vec![
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.9 },
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.8 }, // Same rect, lower score
        ];
        let kept = perform_mock_nms(detections, 0.3);
        assert_eq!(kept.len(), 1);
        assert_eq!(kept[0], Rect_::new(0, 0, 10, 10)); // Ensures the one with score 0.9 was kept
    }

    #[test]
    fn test_nms_partial_overlap_suppress() {
        let detections = vec![
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.9 }, // Area 100
            super::Detection { rect: Rect_::new(5, 0, 10, 10), score: 0.8 }, // Area 100, Overlap 50 (5x10), IoU = 50 / (100+100-50) = 50/150 = 0.333
        ];
        let kept = perform_mock_nms(detections, 0.3); // Threshold 0.3, IoU is > 0.3
        assert_eq!(kept.len(), 1);
        assert_eq!(kept[0], Rect_::new(0, 0, 10, 10));
    }

    #[test]
    fn test_nms_partial_overlap_keep() {
        let detections = vec![
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.9 }, // Area 100
            super::Detection { rect: Rect_::new(8, 0, 10, 10), score: 0.8 }, // Area 100, Overlap 20 (2x10), IoU = 20 / (100+100-20) = 20/180 = 0.111
        ];
        let kept = perform_mock_nms(detections, 0.3); // Threshold 0.3, IoU is < 0.3
        assert_eq!(kept.len(), 2);
    }

    #[test]
    fn test_nms_multiple_overlaps() {
        let detections = vec![
            super::Detection { rect: Rect_::new(0, 0, 10, 10), score: 0.9 },  // A
            super::Detection { rect: Rect_::new(5, 0, 10, 10), score: 0.8 },  // B (overlaps A significantly)
            super::Detection { rect: Rect_::new(20, 0, 10, 10), score: 0.7 }, // C (no overlap with A)
            super::Detection { rect: Rect_::new(22, 0, 10, 10), score: 0.6 }, // D (overlaps C significantly)
        ];
        // Expected: A is kept. B is suppressed by A. C is kept. D is suppressed by C.
        let kept = perform_mock_nms(detections, 0.3);
        assert_eq!(kept.len(), 2);
        assert!(kept.contains(&Rect_::new(0,0,10,10)));
        assert!(kept.contains(&Rect_::new(20,0,10,10)));
    }

    // --- Tests for locate_template_on_image ---
    use image::{GrayImage, RgbImage, Luma, Rgb};

    fn create_test_gray_image(width: u32, height: u32, pattern: Option<(Rect_<i32>, u8)>) -> DynamicImage {
        let mut img = GrayImage::new(width, height);
        for y in 0..height { // Fill with a base color (e.g., 50)
            for x in 0..width {
                img.put_pixel(x, y, Luma([50]));
            }
        }
        if let Some((rect, val)) = pattern {
            for r_y in rect.y..(rect.y + rect.height) {
                for r_x in rect.x..(rect.x + rect.width) {
                    if r_x >=0 && r_x < width as i32 && r_y >=0 && r_y < height as i32 {
                        img.put_pixel(r_x as u32, r_y as u32, Luma([val]));
                    }
                }
            }
        }
        DynamicImage::ImageLuma8(img)
    }

    #[test]
    fn test_locate_template_on_image_clear_match() {
        let needle_pattern_rect = Rect_::new(0,0,3,3); // Relative to needle itself
        let needle = create_test_gray_image(3, 3, Some((needle_pattern_rect, 200))); // 3x3 needle, all 200

        let haystack_pattern_rect = Rect_::new(5,5,3,3); // Place needle at (5,5) in haystack
        let haystack = create_test_gray_image(10, 10, Some((haystack_pattern_rect, 200)));

        let result = locate_template_on_image(&haystack, &needle, 0.9).unwrap();
        assert_eq!(result, Some((5, 5, 3, 3))); // x, y, width, height
    }

    #[test]
    fn test_locate_template_on_image_no_match() {
        let needle = create_test_gray_image(3, 3, Some((Rect_::new(0,0,3,3), 200)));
        let haystack = create_test_gray_image(10, 10, Some((Rect_::new(0,0,10,10), 100))); // Haystack all 100s

        let result = locate_template_on_image(&haystack, &needle, 0.9).unwrap();
        assert_eq!(result, None);
    }

    #[test]
    fn test_locate_template_on_image_low_confidence() {
        // Create a needle (e.g. all 200s)
        let needle = create_test_gray_image(3, 3, Some((Rect_::new(0,0,3,3), 200)));

        // Create a haystack where a region is *similar* but not identical (e.g. all 190s)
        let mut haystack_img = GrayImage::new(10, 10);
        for y in 0..10 { for x in 0..10 { haystack_img.put_pixel(x, y, Luma([50])); } } // Base
        for r_y in 5..(5 + 3) { // Similar pattern at (5,5)
            for r_x in 5..(5 + 3) {
                haystack_img.put_pixel(r_x, r_y, Luma([190]));
            }
        }
        let haystack = DynamicImage::ImageLuma8(haystack_img);

        // With high threshold, should not match
        let result_high_thresh = locate_template_on_image(&haystack, &needle, 0.95).unwrap();
        assert_eq!(result_high_thresh, None);

        // With very low threshold, it should find the "best" of the weak matches
        let result_low_thresh = locate_template_on_image(&haystack, &needle, 0.1).unwrap();
        assert!(result_low_thresh.is_some());
        // The exact location might vary based on normalization, but it should be around (5,5)
        if let Some((x,y,_,_)) = result_low_thresh {
            assert!((x - 5).abs() <= 1 && (y - 5).abs() <= 1, "Match location {:?} is not around (5,5)", (x,y));
        }
    }
}


/// Finds a template on the screen within a specified region, optionally using a cache.
///
/// # Arguments
/// * `template_name` - The name of the template to find (must be loaded in `template_manager`).
/// * `template_manager` - The `TemplateManager` instance holding the loaded templates.
/// * `cache` - A reference to the `DetectionCache` to use for speeding up lookups.
/// * `screen_capture_region` - A tuple `(x, y, width, height)` defining the region of the screen to capture and search within.
///                             `x`, `y` are the top-left coordinates of the region.
///                             `width`, `height` are the dimensions of the region.
///                             TODO: This region should ideally be determined by the game window's actual position and size.
/// * `confidence_threshold` - The minimum confidence required for a match (0.0 to 1.0).
/// * `use_cache` - If true, try to retrieve from cache first. If false, always perform a fresh search.
///                 TODO: More sophisticated cache invalidation strategies might be needed later, potentially driven by game events.
///
/// # Returns
/// `Ok(Some((screen_x, screen_y, template_width, template_height)))` if the template is found,
/// where `screen_x` and `screen_y` are the coordinates relative to the entire screen.
/// `Ok(None)` if the template is not found or confidence is too low.
/// `Err(AppError)` if an error occurs (e.g., template not found, capture error, processing error).
pub fn find_template_on_screen(
    template_name: &str,
    template_manager: &TemplateManager,
    cache: &DetectionCache,
    screen_capture_region: (i32, i32, u32, u32),
    confidence_threshold: f32,
    use_cache: bool,
) -> Result<Option<(i32, i32, u32, u32)>, AppError> {
    info!(
        "Attempting to find template '{}' on screen in region {:?}, use_cache: {}",
        template_name, screen_capture_region, use_cache
    );

    // If use_cache is true, try to get from cache first.
    if use_cache {
        if let Some(location) = cache.get(template_name) {
            info!("Cache hit for template '{}'. Location: {:?}", template_name, location);
            return Ok(Some(location));
        }
        info!("Cache miss for template '{}', proceeding with screen search.", template_name);
    }

    // 1. Get the named Template from the TemplateManager.
    let template = template_manager.get_template(template_name).ok_or_else(|| {
        error!("Template '{}' not found in TemplateManager.", template_name);
        AppError::ImageProcessingError(format!("Template '{}' not found in TemplateManager.", template_name))
    })?;
    info!("Template '{}' retrieved from manager.", template_name);

    // 2. Capture the specified screen_capture_region.
    let (region_x, region_y, region_width, region_height) = screen_capture_region;
    let captured_image = capture::capture_screen_region(region_x, region_y, region_width, region_height)
        .map_err(|e| {
            error!("Failed to capture screen region {:?}: {}", screen_capture_region, e);
            e // AppError::ScreenCaptureError is already the type
        })?;
    info!("Screen region captured successfully.");

    // 3. Use locate_template_on_image() to find the template in the captured image.
    match locate_template_on_image(&captured_image, &template.image, confidence_threshold)? {
        Some((local_x, local_y, t_width, t_height)) => {
            // 4. Calculate bounding box relative to the screen.
            let screen_x = region_x + local_x;
            let screen_y = region_y + local_y;
            let location = (screen_x, screen_y, t_width as u32, t_height as u32);
            
            info!(
                "Template '{}' found at screen coordinates: {:?}, size: ({}, {})",
                template_name, (screen_x, screen_y), t_width, t_height
            );
            
            // Update the cache with the new location.
            cache.update(template_name.to_string(), location);
            info!("Cache updated for template '{}'.", template_name);

            Ok(Some(location))
        }
        None => {
            info!("Template '{}' not found in the captured region with confidence >= {}.", template_name, confidence_threshold);
            // Optionally, we could remove the item from cache if it's not found,
            // but current behavior is to only update on successful find.
            // cache.clear_template(template_name); 
            Ok(None)
        }
    }
}
