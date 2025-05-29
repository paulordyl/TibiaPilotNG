use crate::AppError; // Assuming AppError is in the root or accessible via crate::
use image::DynamicImage;
use log::info;
use screenshots::Screen; // Using the screenshots crate

// Placeholder for AppError if not defined globally, for compilation
/*
#[derive(Debug)]
pub enum AppError {
    ScreenCaptureError(String),
    NotImplemented,
    // Add other error variants as needed
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::ScreenCaptureError(s) => write!(f, "Screen Capture Error: {}", s),
            AppError::NotImplemented => write!(f, "Functionality not implemented"),
        }
    }
}

impl std::error::Error for AppError {}
*/

/// Captures the primary screen.
pub fn capture_primary_screen() -> Result<DynamicImage, AppError> {
    info!("Attempting to capture primary screen.");
    let screen = Screen::all().map_err(|e| AppError::ScreenCaptureError(format!("Failed to get screen information: {}", e)))?
        .into_iter()
        .find(|s| s.display_info.is_primary)
        .ok_or_else(|| AppError::ScreenCaptureError("Could not find primary screen".to_string()))?;

    info!("Capturing screen: {:?}", screen.display_info);
    let image_buffer = screen.capture().map_err(|e| AppError::ScreenCaptureError(format!("Failed to capture screen: {}", e)))?;
    
    // Convert RgbaImage to DynamicImage
    let dynamic_image = DynamicImage::ImageRgba8(image_buffer);
    info!("Screen captured successfully.");
    Ok(dynamic_image)
}

/// Captures a specific region of the primary screen.
/// (x, y) are the top-left coordinates of the region.
/// (width, height) are the dimensions of the region.
pub fn capture_screen_region(x: i32, y: i32, width: u32, height: u32) -> Result<DynamicImage, AppError> {
    info!("Attempting to capture screen region: x={}, y={}, width={}, height={}", x, y, width, height);
    let screen = Screen::all().map_err(|e| AppError::ScreenCaptureError(format!("Failed to get screen information: {}", e)))?
        .into_iter()
        .find(|s| s.display_info.is_primary)
        .ok_or_else(|| AppError::ScreenCaptureError("Could not find primary screen".to_string()))?;

    info!("Capturing region from screen: {:?}", screen.display_info);
    let image_buffer = screen.capture_area(x, y, width, height)
        .map_err(|e| AppError::ScreenCaptureError(format!("Failed to capture screen region: {}", e)))?;
    
    // Convert RgbaImage to DynamicImage
    let dynamic_image = DynamicImage::ImageRgba8(image_buffer);
    info!("Screen region captured successfully.");
    Ok(dynamic_image)
}

// Placeholder for a function to capture a specific window by name (more complex)
// This would likely require platform-specific code or a different crate.
pub fn capture_window_by_name(_window_name: &str) -> Result<DynamicImage, AppError> {
    info!("capture_window_by_name is not yet implemented.");
    Err(AppError::ScreenCaptureError("capture_window_by_name is not implemented".to_string())) // Or use a specific AppError::NotImplemented variant
}
