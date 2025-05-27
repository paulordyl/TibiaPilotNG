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
#[allow(unused_variables)] // max_overlap is not used yet
pub fn locate_all_templates_on_image(
    haystack: &DynamicImage,
    needle: &DynamicImage,
    confidence_threshold: f32,
    max_overlap: f32, // For future NMS
) -> Result<Vec<(i32, i32, u32, u32)>, AppError> {
    info!("Attempting to locate all occurrences of a template on image.");

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

    let mut found_locations: Vec<(i32, i32, u32, u32)> = Vec::new();
    let needle_width = needle_mat.cols();
    let needle_height = needle_mat.rows();

    loop {
        let mut min_val = 0.0;
        let mut max_val = 0.0;
        let mut min_loc = core::Point::new(0, 0);
        let mut max_loc = core::Point::new(0, 0);

        core::min_max_loc(&result_mat, Some(&mut min_val), Some(&mut max_val), Some(&mut min_loc), Some(&mut max_loc), &Mat::default())
            .map_err(|e| AppError::ImageProcessingError(format!("Failed to find min/max location in result matrix: {}", e)))?;

        if max_val >= confidence_threshold as f64 {
            info!(
                "Found template match at ({}, {}) with confidence {:.2}",
                max_loc.x, max_loc.y, max_val
            );
            found_locations.push((max_loc.x, max_loc.y, needle_width as u32, needle_height as u32));

            // "Clear" or "mask out" the region of this found match in the result matrix.
            // This is a simple way to prevent finding the same match again.
            // The region to clear is centered around max_loc and is typically related to needle size.
            // For simplicity, we clear a rectangle of the needle's size.
            // A more sophisticated NMS might use `max_overlap`.
            let clear_rect_x = max_loc.x - needle_width / 2; // Start clearing a bit to the left of the found match
            let clear_rect_y = max_loc.y - needle_height / 2; // Start clearing a bit above the found match
            
            // Ensure clear_rect coordinates are within the bounds of result_mat
            let roi_x = core::max(0, clear_rect_x) as i32;
            let roi_y = core::max(0, clear_rect_y) as i32;

            // Calculate width and height of ROI, ensuring it doesn't exceed result_mat dimensions
            let roi_width = core::min(needle_width, result_mat.cols() - roi_x) as i32;
            let roi_height = core::min(needle_height, result_mat.rows() - roi_y) as i32;

            if roi_width > 0 && roi_height > 0 {
                let mut roi = Mat::roi(&mut result_mat, Rect_::new(roi_x, roi_y, roi_width, roi_height))
                    .map_err(|e| AppError::ImageProcessingError(format!("Failed to get ROI for clearing: {}", e)))?;
                
                // Set this region to a value below the threshold (e.g., 0 or min_val - epsilon)
                roi.set_to(core::Scalar::new(min_val - 0.1, 0.0, 0.0, 0.0)) // Set to a low value
                    .map_err(|e| AppError::ImageProcessingError(format!("Failed to clear region in result matrix: {}", e)))?;
                debug!("Cleared region around ({}, {}) in result matrix.", max_loc.x, max_loc.y);
            } else {
                debug!("Skipping clear for match at ({},{}) as calculated ROI is invalid (width/height <=0)", max_loc.x, max_loc.y);
                 // If the ROI is invalid (e.g. match at edge), we might risk an infinite loop if this match isn't properly suppressed.
                 // For now, we break to avoid potential infinite loops if clearing fails at edges.
                 // A more robust solution might be needed if this becomes an issue.
                 // One simple fix: ensure at least a 1x1 area around max_loc itself is cleared.
                 if result_mat.cols() > max_loc.x && result_mat.rows() > max_loc.y {
                     result_mat.at_2d_mut::<core::Vec<f32, 1>>(max_loc.y, max_loc.x).unwrap()[0] = min_val as f32 - 0.1f32;
                 }
                 // Break if we can't clear properly to avoid issues, or handle more gracefully.
                 // break; 
            }
        } else {
            info!("No more matches found with confidence >= {:.2}. Max found was {:.2}", confidence_threshold, max_val);
            break; // No more matches above threshold
        }
    }

    info!("Found {} locations in total for the template.", found_locations.len());
    Ok(found_locations)
}


use crate::image_processing::{templates::TemplateManager, cache::DetectionCache}; // Added DetectionCache
use crate::screen_capture::capture; // Import screen capture functions

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
