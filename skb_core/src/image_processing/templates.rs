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
    /// the behavior is undefined (last one loaded might overwrite). Consider making names more unique if needed.
    pub fn load_templates_from_directory(&mut self, dir_path: &str) -> Result<(), AppError> {
        info!("Loading templates from directory: {}", dir_path);
        let path = Path::new(dir_path);
        if !path.is_dir() {
            error!("Provided path is not a directory: {}", dir_path);
            return Err(AppError::ConfigError(format!(
                "Provided path is not a directory: {}",
                dir_path
            )));
        }

        self._load_recursive(&path)?;
        info!("Finished loading {} templates.", self.templates.len());
        Ok(())
    }

    fn _load_recursive(&mut self, current_path: &Path) -> Result<(), AppError> {
        for entry in fs::read_dir(current_path).map_err(|e| {
            AppError::IOError(e) // Convert fs::Error to AppError::IOError
        })? {
            let entry_path = entry.map_err(|e| AppError::IOError(e))?.path();
            if entry_path.is_dir() {
                self._load_recursive(&entry_path)?;
            } else if entry_path.is_file() {
                // Check for common image extensions
                if let Some(ext) = entry_path.extension().and_then(|s| s.to_str()) {
                    match ext.to_lowercase().as_str() {
                        "png" | "jpg" | "jpeg" | "bmp" | "gif" => {
                            // Use filename without extension as template name
                            if let Some(stem) = entry_path.file_stem().and_then(|s| s.to_str()) {
                                let template_name = stem.to_string();
                                debug!("Attempting to load template: {} from {:?}", template_name, entry_path);
                                match ImageReader::open(&entry_path)?.decode() {
                                    Ok(image) => {
                                        let template = Template {
                                            name: template_name.clone(),
                                            image,
                                        };
                                        self.templates.insert(template_name.clone(), template);
                                        debug!("Successfully loaded template: {}", template_name);
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
