use crate::{
    image_processing::templates::TemplateManager, // For TemplateManager
    AppError, // For AppError
};
use image::DynamicImage; // For DynamicImage
use log::{debug, info, warn}; // Added info and warn

/// Recognizes digits in a given image region using templates.
///
/// This function attempts to match digit templates (e.g., "digit_0", "digit_1", ...)
/// within the `region_image`. It tries to form a number from the sequence of
/// recognized digits found from left to right.
///
/// # Arguments
/// * `region_image` - The image (e.g., a captured HP or MP bar region) to recognize digits in.
/// * `template_manager` - A reference to the `TemplateManager` containing the digit templates.
/// * `digit_template_prefix` - The prefix for digit templates (e.g., "digit_"). The function
///                             will look for templates named "digit_0", "digit_1", etc.
///
/// # Returns
/// `Ok(Some(u32))` if digits are successfully recognized and form a valid number.
use crate::image_processing::matching; // For locate_all_templates_on_image

/// `Ok(None)` if no digits are recognized or if the sequence doesn't form a number.
/// `Err(AppError)` if an error occurs during the process (e.g., template matching issues).
pub fn recognize_digits_in_region(
    region_image: &DynamicImage,
    template_manager: &TemplateManager,
    digit_template_prefix: &str,
    confidence_threshold: f32, // New parameter
    max_overlap_threshold: f32,  // New parameter
) -> Result<Option<u32>, AppError> {
    // Key Parameters for Tuning:
    // 1. `confidence_threshold`: Adjust this based on how similar the template
    //    must be to the image region. Higher values reduce false positives but might miss valid digits.
    //    Lower values increase recall but might lead to more false positives.
    // 2. `max_overlap_threshold`: If a more sophisticated Non-Maximum Suppression is used,
    //    this would control how much overlap is allowed between detected instances of the same digit.
    // 3. Image Preprocessing: (Future enhancement) Steps like image thresholding (converting to
    //    black and white), scaling, or filtering before template matching can significantly
    //    impact recognition accuracy. These preprocessing steps would have their own parameters.
    // 4. Digit Template Quality: The templates themselves are critical. They should be clean,
    //    similarly sized, and representative of how digits appear in the game.

    info!(
        "Attempting to recognize digits in region using template prefix: '{}', confidence: {}, overlap: {}",
        digit_template_prefix, confidence_threshold, max_overlap_threshold
    );
    debug!(
        "Region image dimensions: {}x{}. Template prefix: '{}'",
        region_image.width(),
        region_image.height(),
        digit_template_prefix
    );

    let mut all_recognized_digits: Vec<(i32, String)> = Vec::new();
    // Parameters are now passed into the function.
    // let confidence_threshold = 0.8;
    // let max_overlap = 0.3;

    for i in 0..=9 {
        let template_name = format!("{}{}", digit_template_prefix, i);
        debug!("Looking for digit template: {}", template_name);

        if let Some(digit_template) = template_manager.get_template(&template_name) {
            debug!("Found template for digit '{}'. Attempting to locate all occurrences.", i);
            match matching::locate_all_templates_on_image(
                region_image,
                &digit_template.image,
                confidence_threshold, // Use parameter
                max_overlap_threshold, // Use parameter
            ) {
                Ok(locations) => {
                    if !locations.is_empty() {
                        info!("Found {} occurrences of digit '{}'", locations.len(), i);
                    }
                    for (x, _y, _w, _h) in locations {
                        all_recognized_digits.push((x, i.to_string()));
                    }
                }
                Err(e) => {
                    warn!(
                        "Error while locating all occurrences of template '{}': {}. Skipping this digit.",
                        template_name, e
                    );
                    // Depending on desired robustness, one might choose to return Err(e) here.
                    // For now, we log and try other digits.
                }
            }
        } else {
            debug!("Template '{}' not found in TemplateManager. Skipping.", template_name);
        }
    }

    if all_recognized_digits.is_empty() {
        info!("No digits recognized in the region.");
        return Ok(None);
    }

    // Sort recognized digits by their x-coordinate
    all_recognized_digits.sort_by_key(|k| k.0);
    debug!("Sorted recognized digits (x-coord, digit_str): {:?}", all_recognized_digits);

    // Concatenate the digit strings
    let number_string: String = all_recognized_digits.iter().map(|(_, s)| s.clone()).collect();
    info!("Formed number string: '{}'", number_string);

    if number_string.is_empty() {
        info!("Formed number string is empty, no valid digits found in sequence.");
        return Ok(None);
    }

    // Parse the string into a u32
    match number_string.parse::<u32>() {
        Ok(parsed_number) => {
            info!("Successfully parsed recognized digits to number: {}", parsed_number);
            Ok(Some(parsed_number))
        }
        Err(e) => {
            error!("Failed to parse number string '{}' into u32: {}. This might indicate issues with template matching or unexpected characters.", number_string, e);
            // This could happen if non-digit templates were somehow matched or if the sequence is invalid.
            Ok(None) // Or return an AppError::ImageProcessingError if this case is critical
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use image::{GrayImage, Luma, RgbImage, Rgb, GenericImage, Pixel}; // Added GenericImage, Pixel
    use crate::image_processing::templates::{Template, TemplateManager};
    use std::collections::HashMap; // For creating TemplateManager programmatically if needed.
    use log::LevelFilter;

    const TEMPLATE_WIDTH: u32 = 5;
    const TEMPLATE_HEIGHT: u32 = 7;
    const DEFAULT_CONFIDENCE: f32 = 0.7; // Adjusted for potentially less perfect dummy templates
    const DEFAULT_OVERLAP: f32 = 0.3;

    fn setup_test_logger() {
        let _ = env_logger::builder().is_test(true).filter_level(LevelFilter::Debug).try_init();
    }

    // Creates a very simple, unique Luma8 image for each digit
    fn create_dummy_digit_template(digit: u8) -> DynamicImage {
        let mut img = GrayImage::new(TEMPLATE_WIDTH, TEMPLATE_HEIGHT);
        // Fill with black
        for y in 0..TEMPLATE_HEIGHT {
            for x in 0..TEMPLATE_WIDTH {
                img.put_pixel(x, y, Luma([0]));
            }
        }
        // Draw a simple pattern based on digit value (e.g., number of white pixels)
        // This is very basic and relies on perfect matching.
        if digit < 10 { // Ensure digit is 0-9
            for i in 0..=digit {
                if i < TEMPLATE_WIDTH { // Simple horizontal line
                    img.put_pixel(i, TEMPLATE_HEIGHT / 2, Luma([255]));
                }
            }
             // Add a unique pixel to further differentiate if needed, esp for 0
            if digit == 0 && TEMPLATE_WIDTH > 0 && TEMPLATE_HEIGHT > 0 {
                 img.put_pixel(0,0, Luma([128])); // Special mark for 0
            }
        }
        DynamicImage::ImageLuma8(img)
    }

    fn setup_test_template_manager_with_digits() -> TemplateManager {
        let mut tm = TemplateManager::new();
        for i in 0..=9 {
            let digit_template_img = create_dummy_digit_template(i);
            let template = Template {
                name: format!("digit_{}", i),
                image: digit_template_img,
                description: Some(format!("Dummy template for digit {}", i)),
                category: "digit".to_string(),
                creation_date: chrono::Utc::now(), // Requires chrono
                version: 1,
                metadata: HashMap::new(),
            };
            tm.add_template(template);
        }
        tm
    }

    fn create_image_from_digit_sequence(
        digit_sequence: &[u8],
        template_manager: &TemplateManager,
        spacing: u32,
        background_color: Luma<u8>, // Changed to Luma for consistency
        img_height: u32, // Allow specifying total image height
    ) -> DynamicImage {
        if digit_sequence.is_empty() {
            return DynamicImage::ImageLuma8(GrayImage::new(1, img_height)); // Return small blank image
        }

        let mut total_width = 0;
        let mut images_to_stitch = Vec::new();
        for (idx, digit_val) in digit_sequence.iter().enumerate() {
            if let Some(template) = template_manager.get_template(&format!("digit_{}", digit_val)) {
                images_to_stitch.push(template.image.clone()); // Clone to use
                total_width += template.image.width();
                if idx < digit_sequence.len() - 1 {
                    total_width += spacing;
                }
            } else {
                 panic!("Digit template for {} not found in test setup", digit_val);
            }
        }
        if total_width == 0 { total_width = 1; } // Ensure not zero width

        let mut combined_image = GrayImage::from_pixel(total_width, img_height, background_color);

        let mut current_x = 0;
        for digit_image in images_to_stitch {
            let luma_digit_img = digit_image.to_luma8(); // Ensure it's Luma8
            // Basic vertical centering (adjust if templates have different heights)
            let y_offset = (img_height.saturating_sub(luma_digit_img.height())) / 2;
            for y in 0..luma_digit_img.height() {
                for x in 0..luma_digit_img.width() {
                    if current_x + x < total_width && y_offset + y < img_height {
                         combined_image.put_pixel(current_x + x, y_offset + y, *luma_digit_img.get_pixel(x, y));
                    }
                }
            }
            current_x += luma_digit_img.width() + spacing;
        }
        DynamicImage::ImageLuma8(combined_image)
    }

    #[test]
    fn test_recognize_basic() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[1, 2, 3], &tm, 1, Luma([0]), TEMPLATE_HEIGHT + 2);
        let result = recognize_digits_in_region(&test_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, Some(123));
    }

    #[test]
    fn test_recognize_single_digit() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[7], &tm, 0, Luma([0]), TEMPLATE_HEIGHT);
        let result = recognize_digits_in_region(&test_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, Some(7));
    }

    #[test]
    fn test_recognize_number_with_zero() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[1,0,2], &tm, 1, Luma([0]), TEMPLATE_HEIGHT + 4);
        let result = recognize_digits_in_region(&test_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, Some(102));
    }

    #[test]
    fn test_recognize_no_digits_found() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        // Create a blank image or an image with a pattern not matching any digit
        let blank_image = DynamicImage::ImageLuma8(GrayImage::from_pixel(30, TEMPLATE_HEIGHT, Luma([50])));
        let result = recognize_digits_in_region(&blank_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, None);
    }

    #[test]
    fn test_recognize_widely_spaced_digits() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[4, 8], &tm, 5, Luma([10]), TEMPLATE_HEIGHT + 2); // 5px spacing
        let result = recognize_digits_in_region(&test_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, Some(48));
    }

    #[test]
    fn test_recognize_high_confidence_perfect_match() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[1, 2], &tm, 0, Luma([0]), TEMPLATE_HEIGHT);
        // Our dummy templates are perfect matches for themselves.
        let result = recognize_digits_in_region(&test_image, &tm, "digit_", 0.99, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, Some(12));
    }

    #[test]
    fn test_recognize_incorrect_prefix() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let test_image = create_image_from_digit_sequence(&[1, 2], &tm, 0, Luma([0]), TEMPLATE_HEIGHT);
        let result = recognize_digits_in_region(&test_image, &tm, "num_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP).unwrap();
        assert_eq!(result, None);
    }

    #[test]
    fn test_recognize_empty_region_image() {
        setup_test_logger();
        let tm = setup_test_template_manager_with_digits();
        let empty_image = DynamicImage::ImageLuma8(GrayImage::new(0, 0));
        // locate_all_templates_on_image should handle needle > haystack early.
        // If it gets to matching, it might error or return empty.
        // The current recognize_digits_in_region logs errors from locate_all and continues.
        let result = recognize_digits_in_region(&empty_image, &tm, "digit_", DEFAULT_CONFIDENCE, DEFAULT_OVERLAP);
        // Expect Ok(None) because no digits can be found in an empty image.
        // An error could also be valid if locate_all_templates_on_image errors on 0-size haystack.
        // Current locate_all_templates_on_image returns error if needle > haystack, which is true if haystack is 0x0 and needle is not.
        assert!(matches!(result, Err(AppError::ImageProcessingError(_))) || matches!(result, Ok(None)), "Result was: {:?}", result);
    }
}
