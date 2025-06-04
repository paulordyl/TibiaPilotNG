// skb_utils/src/file_ops.rs
use crate::error::UtilsError;
use std::fs;
use std::path::Path;

/// Reads the entire contents of a file into a string.
pub fn read_file_to_string(path: &Path) -> Result<String, UtilsError> {
    fs::read_to_string(path).map_err(UtilsError::IoError)
}

/// Writes a string slice to a file, creating the file if it does not exist,
/// and truncating it if it does.
pub fn write_string_to_file(path: &Path, content: &str) -> Result<(), UtilsError> {
    fs::write(path, content).map_err(UtilsError::IoError)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    use tempfile::tempdir; // Using tempfile for more robust test file handling

    #[test]
    fn test_write_and_read_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test_file.txt");

        let content_to_write = "Hello, SKB Utils!";

        // Test writing
        assert!(write_string_to_file(&file_path, content_to_write).is_ok());

        // Test reading
        match read_file_to_string(&file_path) {
            Ok(read_content) => {
                assert_eq!(read_content, content_to_write);
            }
            Err(e) => {
                panic!("Failed to read file: {}", e);
            }
        }
    }

    #[test]
    fn test_read_non_existent_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("non_existent_file.txt");

        match read_file_to_string(&file_path) {
            Ok(_) => {
                panic!("Should have failed to read non-existent file");
            }
            Err(UtilsError::IoError(_)) => {
                // Expected error
            }
            Err(e) => {
                panic!("Unexpected error type: {}", e);
            }
        }
    }

    #[test]
    fn test_write_to_file_overwrites_existing_content() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("overwrite_test.txt");

        let initial_content = "Initial content.";
        let new_content = "New overwritten content.";

        // Write initial content
        fs::write(&file_path, initial_content).unwrap();

        // Test writing new content (should overwrite)
        assert!(write_string_to_file(&file_path, new_content).is_ok());

        // Verify content is overwritten
        let read_content = fs::read_to_string(&file_path).unwrap();
        assert_eq!(read_content, new_content);
    }
}
