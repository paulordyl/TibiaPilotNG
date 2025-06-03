use image::DynamicImage;
use leptess::{LepTess, Variable};
use std::path::Path;
use thiserror::Error;
use tempfile::NamedTempFile;
use std::io::Write;


#[derive(Error, Debug)]
pub enum OCRError {
    #[error("Leptess engine initialization failed: {0}")]
    InitializationError(String),
    #[error("Failed to set image for OCR: {0}")]
    SetImageError(String),
    #[error("Failed to retrieve text from OCR: {0}")]
    GetTextError(String),
    #[error("Failed to set Tesseract variable: {0}")]
    SetVariableError(String),
    #[error("Image save error (e.g., to temp file): {0}")]
    ImageSaveError(#[from] image::ImageError),
    #[error("Temporary file operation error: {0}")]
    TempFileError(#[from] std::io::Error),
    #[error("Recognized text could not be parsed to the target type (e.g., u32): {0}")]
    ParseError(String),
}

#[derive(Debug)]
pub struct OcrEngine {
    api: LepTess,
}

impl OcrEngine {
    pub fn new(lang: &str, tessdata_path: Option<&str>) -> Result<Self, OCRError> {
        log::info!("Initializing OcrEngine for language '{}'. Tessdata path: {:?}", lang, tessdata_path);

        let mut api = LepTess::new(tessdata_path, lang)
            .map_err(|e| OCRError::InitializationError(format!("{:?}", e)))?;

        api.set_variable(Variable::TesseditPagesegMode, "7")
            .map_err(|e| OCRError::SetVariableError(format!("{:?}",e)))?;

        log::debug!("OcrEngine initialized successfully.");
        Ok(OcrEngine { api })
    }

    pub fn recognize_text(&mut self, img: &DynamicImage) -> Result<String, OCRError> {
        log::debug!("Recognizing text from image with dimensions {}x{}", img.width(), img.height());

        let mut temp_file = NamedTempFile::new()?;
        img.write_to(&mut temp_file, image::ImageOutputFormat::Png)?;
        temp_file.flush()?;

        let temp_path = temp_file.into_temp_path();

        self.api.set_image(&temp_path)
            .map_err(|e| OCRError::SetImageError(format!("{:?}", e)))?;

        let text = self.api.get_utf8_text()
            .map_err(|e| OCRError::GetTextError(format!("{:?}", e)))?;

        log::debug!("Recognized text: '{}'", text.trim());
        Ok(text.trim().to_string())
    }

    pub fn recognize_digits(&mut self, img: &DynamicImage) -> Result<u32, OCRError> {
        log::info!("Recognizing digits from image (size {}x{})", img.width(), img.height());

        self.api.set_variable(Variable::TesseditCharWhitelist, "0123456789")
            .map_err(|e| OCRError::SetVariableError(format!("{:?}",e)))?;

        let text = self.recognize_text(img)?;

        self.api.set_variable(Variable::TesseditCharWhitelist, "")
             .map_err(|e| OCRError::SetVariableError(format!("Failed to reset whitelist: {:?}",e)))?;

        text.parse::<u32>().map_err(|e| {
            log::error!("Failed to parse recognized text '{}' as u32: {}", text, e);
            OCRError::ParseError(format!("Failed to parse '{}' as u32: {}", text, e))
        })
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use image::{ImageBuffer, Rgba};
    use std::path::PathBuf;
    use lazy_static::lazy_static;
    use std_semaphore::Semaphore;
    use std::env;

    lazy_static! {
        static ref TESSERACT_SEMAPHORE: Semaphore = Semaphore::new(1);
    }

    fn setup_test_logging() {
        let _ = env_logger::builder().is_test(true).try_init();
    }

    fn get_test_ocr_image_path() -> PathBuf {
        let manifest_dir = env::var("CARGO_MANIFEST_DIR").unwrap();
        PathBuf::from(manifest_dir).join("test_data").join("test_ocr_image.png")
    }

    #[test]
    fn test_ocr_engine_new_valid() {
        setup_test_logging();
        let _guard = TESSERACT_SEMAPHORE.access();
        let result = OcrEngine::new("eng", None);
        if let Err(e) = &result {
            eprintln!("OcrEngine init failed: {:?}. Ensure Tesseract & eng.traineddata are installed. TESSDATA_PREFIX might be needed.", e);
        }
        assert!(result.is_ok());
    }

    #[test]
    fn test_ocr_engine_new_invalid_lang() {
        setup_test_logging();
        let _guard = TESSERACT_SEMAPHORE.access();
        let result = OcrEngine::new("invalid_lang_code_skb", None); // Made more unique
        assert!(result.is_err());
        match result.err().unwrap() {
            OCRError::InitializationError(_) => {}
            e => panic!("Unexpected error type: {:?}", e),
        }
    }

    #[test]
    fn test_recognize_text_from_test_image() {
        setup_test_logging();
        let _guard = TESSERACT_SEMAPHORE.access();

        let mut engine = OcrEngine::new("eng", None)
            .expect("OCR Engine initialization failed for test_recognize_text. Check Tesseract installation.");

        let img_path = get_test_ocr_image_path();
        assert!(img_path.exists(), "Test OCR image not found at {:?}", img_path);

        let img = image::open(&img_path).expect("Failed to load test OCR image");

        let result = engine.recognize_text(&img);
        assert!(result.is_ok(), "recognize_text failed: {:?}", result.err());
        let text = result.unwrap();
        assert_eq!(text.to_uppercase().trim(), "OCR");
    }

    #[test]
    fn test_recognize_digits_failure_on_text_image() {
        setup_test_logging();
        let _guard = TESSERACT_SEMAPHORE.access();
        let mut engine = OcrEngine::new("eng", None).expect("Engine init failed");

        let ocr_img_path = get_test_ocr_image_path(); // Contains "OCR"
        let ocr_img = image::open(&ocr_img_path).expect("Failed to load OCR test image");

        let result_non_digit = engine.recognize_digits(&ocr_img);
        assert!(result_non_digit.is_err(), "Expected digit parsing to fail for 'OCR'");
        match result_non_digit.err().unwrap() {
            OCRError::ParseError(_) => {},
            e => panic!("Unexpected error for non-digit parsing: {:?}", e),
        }
    }
}
