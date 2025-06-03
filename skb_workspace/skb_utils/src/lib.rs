// --- Logging Submodule ---
pub mod logging {
    use thiserror::Error;

    #[derive(Error, Debug)]
    pub enum LogError {
        #[error("Failed to initialize logger: {0}")]
        InitializationError(String),
    }

    pub fn setup_logging() -> Result<(), LogError> {
        match env_logger::try_init() {
            Ok(_) => {
                log::info!("Logger initialized successfully.");
                Ok(())
            }
            Err(e) => {
                log::warn!("Logger setup issue (possibly already initialized): {}", e);
                if e.to_string().contains("already initialized") {
                    Ok(())
                } else {
                    Err(LogError::InitializationError(e.to_string()))
                }
            }
        }
    }
}

// --- File Operations Submodule ---
pub mod file_ops {
    use std::fs;
    use std::io::{self, Write};
    use std::path::Path;

    pub fn read_file_to_string(path: &Path) -> Result<String, io::Error> {
        fs::read_to_string(path)
    }

    pub fn write_string_to_file(path: &Path, content: &str) -> Result<(), io::Error> {
        let mut file = fs::File::create(path)?;
        file.write_all(content.as_bytes())
    }
}

// --- Timing Submodule (Basic Placeholder) ---
pub mod timing {
    use std::time::Duration;
    use std::thread;

    pub fn precise_delay(duration: Duration) {
        thread::sleep(duration);
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::env;

    #[test]
    fn test_setup_logging_runs() {
        let _ = logging::setup_logging();
        log::info!("This is a test log message from skb_utils test.");
        assert!(logging::setup_logging().is_ok());
    }

    #[test]
    fn test_write_and_read_file() {
        let temp_dir = env::temp_dir();
        let test_file_path = temp_dir.join("skb_utils_test_file.txt");

        let content_to_write = "Hello, skb_utils! This is a test.";

        match file_ops::write_string_to_file(&test_file_path, content_to_write) {
            Ok(_) => log::debug!("Test file written successfully: {:?}", test_file_path),
            Err(e) => panic!("Failed to write test file: {}", e),
        }

        match file_ops::read_file_to_string(&test_file_path) {
            Ok(read_content) => {
                assert_eq!(read_content, content_to_write);
                log::debug!("Test file read successfully and content matches.");
            }
            Err(e) => panic!("Failed to read test file: {}", e),
        }

        fs::remove_file(&test_file_path).expect("Failed to clean up test file");
        log::debug!("Test file cleaned up.");
    }

    #[test]
    fn test_read_non_existent_file() {
        let temp_dir = env::temp_dir();
        let non_existent_path = temp_dir.join("skb_utils_non_existent_file.txt");
        if non_existent_path.exists() {
            fs::remove_file(&non_existent_path).unwrap();
        }

        let result = file_ops::read_file_to_string(&non_existent_path);
        assert!(result.is_err());
        if let Err(e) = result {
            assert_eq!(e.kind(), std::io::ErrorKind::NotFound);
            log::debug!("Reading non-existent file correctly returned error: {}", e);
        } else {
            panic!("Should have failed for non-existent file");
        }
    }

    #[test]
    fn test_timing_delay() {
        let start = std::time::Instant::now();
        timing::precise_delay(std::time::Duration::from_millis(10));
        let duration = start.elapsed();
        assert!(duration >= std::time::Duration::from_millis(10));
        log::debug!("Precise delay of 10ms took {:?}", duration);
    }
}
