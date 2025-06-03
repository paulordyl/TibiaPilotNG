use crate::AppError;
use image::{io::Reader as ImageReader, DynamicImage};
use log::{debug, error, info}; // Added info log
use std::{
    collections::HashMap,
    fs,
    path::{Path, PathBuf},
};

#[derive(Clone, Debug)] // Added Debug
pub struct Template {
    pub name: String,
    pub image: DynamicImage,
    // Optionally, add other metadata like default confidence, etc.
}

#[derive(Debug)] // Added Debug
pub struct TemplateManager {
    templates: HashMap<String, Template>,
}

impl TemplateManager {
    pub fn new() -> Self {
        TemplateManager {
            templates: HashMap::new(),
        }
    }

    /// Loads templates recursively from a directory.
    /// The name of the template is derived from its filename without the extension.
    /// Example: "path/to/my_button.png" becomes "my_button".
    /// If multiple files have the same name (e.g., "a/button.png" and "b/button.png"),
    /// they will be stored with keys relative to `dir_path`, e.g., "a/button" and "b/button".
    pub fn load_templates_from_directory(&mut self, dir_path: &str) -> Result<(), AppError> {
        info!("Loading templates from directory: {}", dir_path);
        let base_path = Path::new(dir_path);
        if !base_path.is_dir() {
            error!("Provided path is not a directory: {}", dir_path);
            return Err(AppError::ConfigError(format!(
                "Provided path is not a directory: {}",
                dir_path
            )));
        }

        self._load_recursive(base_path, base_path)?;
        info!("Finished loading {} templates.", self.templates.len());
        Ok(())
    }

    fn _load_recursive(&mut self, base_dir: &Path, current_dir: &Path) -> Result<(), AppError> {
        for entry in fs::read_dir(current_dir).map_err(|e| {
            AppError::TemplateError(format!("Failed to read directory {}: {}", current_dir.display(), e))
        })? {
            let entry_path = entry.map_err(|e| AppError::TemplateError(format!("Failed to read directory entry: {}", e)))?.path();
            debug!("Processing path: {:?}", entry_path);
            if entry_path.is_dir() {
                info!("Entering subdirectory: {:?}", entry_path);
                self._load_recursive(base_dir, &entry_path)?;
            } else if entry_path.is_file() {
                // Check for common image extensions
                if let Some(ext) = entry_path.extension().and_then(|s| s.to_str()) {
                    match ext.to_lowercase().as_str() {
                        "png" | "jpg" | "jpeg" | "bmp" | "gif" => {
                            // Construct relative path from base_dir to use as template name/key
                            let relative_path = entry_path.strip_prefix(base_dir).map_err(|_| {
                                AppError::TemplateError(format!(
                                    "Failed to create relative path for {:?} based on {:?}",
                                    entry_path, base_dir
                                ))
                            })?;

                            if let Some(stem) = relative_path.file_stem().and_then(|s| s.to_str()) {
                                // The key should include the relative directory structure
                                let key_path = relative_path.parent().unwrap_or_else(|| Path::new(""));
                                let template_key = key_path.join(stem).to_str().unwrap_or("").replace("\\", "/");

                                if template_key.is_empty() {
                                    error!("Generated empty template key for path: {:?}", entry_path);
                                    continue;
                                }

                                debug!("Attempting to load template with key: {} from {:?}", template_key, entry_path);
                                match ImageReader::open(&entry_path)?.decode() {
                                    Ok(image) => {
                                        let template = Template {
                                            name: template_key.clone(), // Store the relative path key as its name
                                            image,
                                        };
                                        self.templates.insert(template_key.clone(), template);
                                        debug!("Successfully loaded template with key: {}", template_key);
                                    }
                                    Err(e) => {
                                        error!("Failed to decode image {:?}: {}", entry_path, e);
                                        // Optionally, continue loading other templates or return an error
                                        // For now, we log and continue.
                                    }
                                }
                            }
                        }
                        _ => {
                            // Not a recognized image file, skip
                            debug!("Skipping non-image file: {:?}", entry_path);
                        }
                    }
                }
            }
        }
        Ok(())
    }

    /// Retrieves a template by its name.
    pub fn get_template(&self, name: &str) -> Option<&Template> {
        self.templates.get(name)
    }

    // Optional: Method to list all loaded template names
    #[allow(dead_code)]
    pub fn list_template_names(&self) -> Vec<String> {
        self.templates.keys().cloned().collect()
    }
}

// Default implementation for TemplateManager
impl Default for TemplateManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::Builder;
    use std::fs::{File, create_dir_all};
    use std::io::Write;
    use image::{ImageBuffer, Rgb}; // For dummy images

    // Helper to create a dummy PNG (RGB)
    fn create_dummy_png(path: &std::path::Path, width: u32, height: u32, color: [u8; 3]) {
        if let Some(parent) = path.parent() {
            create_dir_all(parent).expect("Failed to create parent directory for dummy PNG");
        }
        let img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |_, _| Rgb(color));
        img.save_with_format(path, image::ImageFormat::Png).expect(&format!("Failed to save dummy PNG to {:?}", path));
    }

    // Helper to create a dummy JPG (RGB)
    fn create_dummy_jpg(path: &std::path::Path, width: u32, height: u32, color: [u8; 3]) {
        if let Some(parent) = path.parent() {
            create_dir_all(parent).expect("Failed to create parent directory for dummy JPG");
        }
        let img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |_, _| Rgb(color));
        img.save_with_format(path, image::ImageFormat::Jpeg).expect(&format!("Failed to save dummy JPG to {:?}", path));
    }


    #[test]
    fn test_load_templates_valid_structure() {
        let temp_dir = Builder::new().prefix("templates_valid").tempdir().unwrap();
        let root_path = temp_dir.path();

        create_dummy_png(&root_path.join("template_a.png"), 10, 10, [255,0,0]);
        create_dummy_jpg(&root_path.join("template_b.jpg"), 10, 10, [0,255,0]);

        let sub_dir_path = root_path.join("sub_dir");
        create_dir_all(&sub_dir_path).unwrap();
        create_dummy_png(&sub_dir_path.join("template_c.png"), 10, 10, [0,0,255]);

        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory(root_path.to_str().unwrap());

        assert!(result.is_ok(), "Loading valid templates failed: {:?}", result.err());
        assert_eq!(tm.templates.len(), 3, "Expected 3 templates to be loaded.");
        assert!(tm.get_template("template_a").is_some());
        assert_eq!(tm.get_template("template_a").unwrap().name, "template_a");
        assert!(tm.get_template("template_b").is_some());
        assert!(tm.get_template("template_c").is_some());
    }

    #[test]
    fn test_load_templates_empty_directory() {
        let temp_dir = Builder::new().prefix("templates_empty").tempdir().unwrap();
        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory(temp_dir.path().to_str().unwrap());

        assert!(result.is_ok());
        assert_eq!(tm.templates.len(), 0, "Expected 0 templates from an empty directory.");
    }

    #[test]
    fn test_load_templates_with_non_image_files() {
        let temp_dir = Builder::new().prefix("templates_mixed").tempdir().unwrap();
        let root_path = temp_dir.path();

        create_dummy_png(&root_path.join("image.png"), 10, 10, [1,2,3]);
        let mut text_file = File::create(root_path.join("text.txt")).unwrap();
        text_file.write_all(b"This is not an image.").unwrap();

        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory(root_path.to_str().unwrap());

        assert!(result.is_ok());
        assert_eq!(tm.templates.len(), 1, "Expected only 1 image template to be loaded.");
        assert!(tm.get_template("image").is_some());
    }

    #[test]
    fn test_load_templates_invalid_path_is_file() {
        let mut tmp_file = Builder::new().suffix(".txt").tempfile().unwrap();
        tmp_file.write_all(b"I am a file, not a directory.").unwrap();

        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory(tmp_file.path().to_str().unwrap());

        assert!(result.is_err());
        match result.err().unwrap() {
            AppError::ConfigError(msg) => assert!(msg.contains("Provided path is not a directory")),
            e => panic!("Expected ConfigError for invalid path, got {:?}", e),
        }
    }

    #[test]
    fn test_load_templates_invalid_path_not_exist() {
        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory("path_does_not_exist_at_all");
        assert!(result.is_err());
         match result.err().unwrap() {
            AppError::ConfigError(msg) => assert!(msg.contains("Provided path is not a directory")), // fs::read_dir check comes after is_dir
            e => panic!("Expected ConfigError for non-existent path, got {:?}", e),
        }
    }


    #[test]
    fn test_load_templates_duplicate_names() {
        let temp_dir = Builder::new().prefix("templates_dup").tempdir().unwrap();
        let root_path = temp_dir.path();

        create_dummy_png(&root_path.join("img.png"), 10, 10, [255,0,0]); // First img.png

        let sub_dir_path = root_path.join("sub");
        create_dir_all(&sub_dir_path).unwrap();
        create_dummy_png(&sub_dir_path.join("img.png"), 10, 10, [0,0,255]); // Second img.png in sub

        let mut tm = TemplateManager::new();
        let result = tm.load_templates_from_directory(root_path.to_str().unwrap());

        assert!(result.is_ok());
        assert_eq!(tm.templates.len(), 1, "Expected 1 template due to name collision (last one wins).");
        assert!(tm.get_template("img").is_some());
        // Color check would be more robust if we knew which one "wins", but dir order is not guaranteed.
        // For now, just checking count and existence is sufficient for this test's purpose.
    }

    #[test]
    fn test_get_template() {
        let temp_dir = Builder::new().prefix("templates_get").tempdir().unwrap();
        let root_path = temp_dir.path();
        create_dummy_png(&root_path.join("find_me.png"), 5, 5, [1,1,1]);

        let mut tm = TemplateManager::new();
        tm.load_templates_from_directory(root_path.to_str().unwrap()).unwrap();

        assert!(tm.get_template("find_me").is_some(), "Should find 'find_me'");
        assert_eq!(tm.get_template("find_me").unwrap().name, "find_me");
        assert!(tm.get_template("dont_find_me").is_none(), "Should not find 'dont_find_me'");
    }
}
