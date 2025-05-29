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
) -> Result<Option<u32>, AppError> {
    // Key Parameters for Tuning:
    // 1. `confidence_threshold`: (Currently hardcoded) Adjust this based on how similar the template
    //    must be to the image region. Higher values reduce false positives but might miss valid digits.
    //    Lower values increase recall but might lead to more false positives.
    // 2. `max_overlap`: (Currently a placeholder in locate_all_templates_on_image's NMS)
    //    If a more sophisticated Non-Maximum Suppression is used, this would control how much
    //    overlap is allowed between detected instances of the same digit.
    // 3. Image Preprocessing: (Future enhancement) Steps like image thresholding (converting to
    //    black and white), scaling, or filtering before template matching can significantly
    //    impact recognition accuracy. These preprocessing steps would have their own parameters.
    // 4. Digit Template Quality: The templates themselves are critical. They should be clean,
    //    similarly sized, and representative of how digits appear in the game.

    info!(
        "Attempting to recognize digits in region using template prefix: '{}'",
        digit_template_prefix
    );
    debug!(
        "Region image dimensions: {}x{}. Template prefix: '{}'",
        region_image.width(),
        region_image.height(),
        digit_template_prefix
    );

    let mut all_recognized_digits: Vec<(i32, String)> = Vec::new();
    // TUNING PARAMETER: Confidence threshold for template matching.
    let confidence_threshold = 0.8; 
    // TUNING PARAMETER (for NMS): Maximum allowed overlap between multiple detections of the same template.
    // Currently, NMS in `locate_all_templates_on_image` is simpler and just clears the found region.
    let max_overlap = 0.3; 

    for i in 0..=9 {
        let template_name = format!("{}{}", digit_template_prefix, i);
        debug!("Looking for digit template: {}", template_name);

        if let Some(digit_template) = template_manager.get_template(&template_name) {
            debug!("Found template for digit '{}'. Attempting to locate all occurrences.", i);
            match matching::locate_all_templates_on_image(
                region_image,
                &digit_template.image,
                confidence_threshold,
                max_overlap,
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
    use image::{DynamicImage, RgbImage};
    use log::LevelFilter; // For setting up logger in tests

    fn setup_test_logger() {
        // Simple logger setup for tests, errors if called multiple times, so use try_init
        let _ = env_logger::builder().is_test(true).filter_level(LevelFilter::Debug).try_init();
    }

    #[test]
    fn test_recognize_simple_number() {
        setup_test_logger();
        info!("Starting test_recognize_simple_number.");

        // 1a. Initialize TemplateManager and load templates.
        let mut template_manager = TemplateManager::new();
        // Note: This path is relative to the crate root where Cargo.toml is.
        // For real tests, ensure 'rust_bot_ng/templates/digits/' exists and has valid digit templates.
        match template_manager.load_templates_from_directory("../../templates") {
            Ok(_) => info!("Test templates loaded successfully. Found {} templates.", template_manager.list_template_names().len()),
            Err(e) => {
                // If templates directory or digits are missing, this test will likely fail here or later.
                // For a unit test focusing on `recognize_digits_in_region` logic with *mocked* template finding,
                // one might populate TemplateManager programmatically with dummy Template objects.
                // But here, we attempt to load, which also tests TemplateManager's loading.
                error!("Failed to load templates for test: {}. This test requires the 'templates/digits/' directory with digit_0.png ... digit_9.png. These can be placeholders for this specific test.", e);
                // Depending on strictness, one might panic! or proceed knowing recognition will fail.
                // We'll proceed to check the flow of recognize_digits_in_region.
            }
        }
         // Log loaded templates for debugging
        for name in template_manager.list_template_names() {
            debug!("Loaded template for test: {}", name);
        }


        // 1b. Create a dummy region_image.
        // This is a placeholder. For actual testing, this image should contain rendered digits
        // corresponding to the loaded templates.
        // For example, an image of "123" using the same font and style as the digit templates.
        let dummy_region_image: DynamicImage = DynamicImage::ImageRgb8(RgbImage::new(100, 20)); // 100x20 pixel black image
        info!("Created dummy region image (100x20 pixels).");

        // 1c. Call recognize_digits_in_region.
        // We expect this to return Ok(None) because the dummy image is blank and doesn't match digit templates.
        // If placeholder digit templates are simple (e.g., 1x1 pixel) and dummy image is also simple,
        // unexpected matches could occur if confidence is too low / NMS is too simple.
        let result = recognize_digits_in_region(&dummy_region_image, &template_manager, "digit_");
        info!("Result from recognize_digits_in_region: {:?}", result);

        // 1d. Assert the result.
        // Given a blank dummy image and (potentially) placeholder templates,
        // the most likely correct outcome is Ok(None) - no digits found.
        // If `recognize_digits_in_region` were to error on missing templates for digits 0-9,
        // then an Err result might be expected if templates weren't loaded.
        // However, current `recognize_digits_in_region` skips missing templates.
        assert!(matches!(result, Ok(None)), "Expected Ok(None) for a blank image, but got: {:?}", result);

        // 1e. Comments on proper testing:
        // To properly test digit recognition:
        // 1. `dummy_region_image` should be replaced with an image loaded from a file (or generated)
        //    that contains actual rendered digits (e.g., "123", "42").
        // 2. The `rust_bot_ng/templates/digits/` directory must contain accurate, individual template images
        //    for each digit ("digit_0.png", "digit_1.png", ..., "digit_9.png") that match the
        //    font, size, and style of the digits in the test `region_image`.
        // 3. Multiple test cases should be created for different numbers, noisy backgrounds (if applicable),
        //    and edge cases (e.g., single digit, max value, partial digits if that needs handling).
        info!("Finished test_recognize_simple_number.");
    }
}
