use image::{DynamicImage, GenericImageView, ImageError, RgbaImage, imageops, Rgba, LumaA}; // Added Rgba, LumaA
use imageproc::rect::Rect as ImageProcRect;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ImageProcError {
    #[error("Image processing error: {0}")]
    ProcessingError(String),
    #[error("Invalid parameters for operation: {0}")]
    InvalidParameters(String),
    #[error("Image crate error: {0}")]
    ImageLibError(#[from] ImageError),
    #[error("Pattern not found")]
    PatternNotFound,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Rect {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

pub type ImageHash = String;

pub fn convert_to_grayscale(img: &DynamicImage) -> DynamicImage {
    log::debug!("Converting image to grayscale. Original dimensions: {}x{}", img.width(), img.height());
    // imageops::grayscale returns Luma<u8>, convert to LumaA for wider compatibility if needed, or keep as Luma8
    let gray_luma8_img = imageops::grayscale(img);
    DynamicImage::ImageLuma8(gray_luma8_img)
}

pub fn crop_image(img: &DynamicImage, rect: Rect) -> Result<DynamicImage, ImageProcError> {
    log::debug!("Cropping image to rect: {:?}", rect);
    if rect.width == 0 || rect.height == 0 {
        return Err(ImageProcError::InvalidParameters("Crop rectangle width and height must be greater than 0".to_string()));
    }
    if rect.x < 0 || rect.y < 0 ||
       (rect.x as u32 + rect.width) > img.width() ||
       (rect.y as u32 + rect.height) > img.height() {
        return Err(ImageProcError::InvalidParameters(format!(
            "Crop rectangle [x:{}, y:{}, w:{}, h:{}] is outside image bounds [w:{}, h:{}]",
            rect.x, rect.y, rect.width, rect.height, img.width(), img.height()
        )));
    }
    let cropped_dyn_img = img.crop_imm(rect.x as u32, rect.y as u32, rect.width, rect.height);
    log::debug!("Image cropped successfully. New dimensions: {}x{}", cropped_dyn_img.width(), cropped_dyn_img.height());
    Ok(cropped_dyn_img)
}

pub fn find_pattern(_img: &DynamicImage, _pattern: &DynamicImage, _tolerance: f32) -> Result<Option<Point>, ImageProcError> {
    // log::info!("Attempting to find pattern (size {}x{}) in image (size {}x{}) with tolerance {}",
    //             pattern.width(), pattern.height(), img.width(), img.height(), tolerance);
    // if pattern.width() > img.width() || pattern.height() > img.height() {
    //     return Err(ImageProcError::InvalidParameters("Pattern cannot be larger than the image.".to_string()));
    // }
    log::warn!("find_pattern is a placeholder and currently does not perform matching.");
    Err(ImageProcError::PatternNotFound)
}

pub fn compute_hash(img: &DynamicImage) -> Result<ImageHash, ImageProcError> {
    log::info!("Computing hash for image (size {}x{})", img.width(), img.height());
    log::warn!("compute_hash is a placeholder.");
    Ok(format!("placeholder_hash_for_{}x{}", img.width(), img.height()))
}


#[cfg(test)]
mod tests {
    use super::*;
    use image::{ImageBuffer, Rgba, Luma};

    fn create_test_image(width: u32, height: u32, color: Rgba<u8>) -> DynamicImage {
        DynamicImage::ImageRgba8(ImageBuffer::from_pixel(width, height, color))
    }
     fn setup_test_logging() {
        let _ = env_logger::builder().is_test(true).try_init();
    }

    #[test]
    fn test_convert_to_grayscale_produces_luma_image() {
        setup_test_logging();
        let color_img = create_test_image(10, 10, Rgba([100, 150, 200, 255]));
        let gray_img = convert_to_grayscale(&color_img);

        assert_eq!(gray_img.width(), 10);
        assert_eq!(gray_img.height(), 10);
        assert_eq!(gray_img.color(), image::ColorType::L8);

        let luma_pixel = gray_img.as_luma8().unwrap().get_pixel(0, 0);
        // Luma = 0.299*100 + 0.587*150 + 0.114*200 = 29.9 + 88.05 + 22.8 = 140.75 -> 141
        assert_eq!(luma_pixel[0], 141);
    }

    #[test]
    fn test_crop_image_valid() {
        setup_test_logging();
        let img = create_test_image(100, 100, Rgba([0,0,0,255]));
        let rect = Rect { x: 10, y: 10, width: 50, height: 50 };
        let cropped_img_result = crop_image(&img, rect);

        assert!(cropped_img_result.is_ok());
        let cropped_img = cropped_img_result.unwrap();
        assert_eq!(cropped_img.width(), 50);
        assert_eq!(cropped_img.height(), 50);
    }

    #[test]
    fn test_crop_image_invalid_rect_dimensions() {
        setup_test_logging();
        let img = create_test_image(100, 100, Rgba([0,0,0,255]));
        let rect = Rect { x: 10, y: 10, width: 0, height: 50 };
        let cropped_img_result = crop_image(&img, rect);
        assert!(cropped_img_result.is_err());
        match cropped_img_result.err().unwrap() {
            ImageProcError::InvalidParameters(s) => assert!(s.contains("width and height must be greater than 0")),
            _ => panic!("Unexpected error type"),
        }
    }

    #[test]
    fn test_crop_image_out_of_bounds() {
        setup_test_logging();
        let img = create_test_image(20, 20, Rgba([0,0,0,255]));
        let test_cases = vec![
            Rect { x: 10, y: 10, width: 15, height: 15 },
            Rect { x: -5, y: 5, width: 10, height: 10 },
            Rect { x: 5, y: -5, width: 10, height: 10 },
            Rect { x: 0, y: 0, width: 21, height: 20 },
            Rect { x: 0, y: 0, width: 20, height: 21 },
        ];

        for rect in test_cases {
            let result = crop_image(&img, rect);
            assert!(result.is_err(), "Expected error for rect: {:?}", rect);
            match result.err().unwrap() {
                ImageProcError::InvalidParameters(s) => {
                    assert!(s.contains("is outside image bounds"), "Error message mismatch for rect: {:?}", rect);
                }
                e => panic!("Unexpected error type {:?} for rect: {:?}", e, rect),
            }
        }
    }

    #[test]
    fn test_find_pattern_placeholder() {
        setup_test_logging();
        let img = create_test_image(100,100, Rgba([0,0,0,255]));
        let pattern = create_test_image(10,10, Rgba([0,0,0,255]));
        let result = find_pattern(&img, &pattern, 0.1);
        assert!(result.is_err());
        match result.err().unwrap() {
            ImageProcError::PatternNotFound => {},
            _ => panic!("Unexpected error from placeholder find_pattern"),
        }
    }

    #[test]
    fn test_compute_hash_placeholder() {
        setup_test_logging();
        let img = create_test_image(10,10, Rgba([0,0,0,255]));
        let result = compute_hash(&img);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "placeholder_hash_for_10x10");
    }
}
