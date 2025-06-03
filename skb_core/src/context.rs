use crate::config::settings::{Config, load_config};
use crate::input::arduino::ArduinoCom;
use crate::image_processing::templates::TemplateManager;
use crate::image_processing::hash_utils; // For hashit_rust and extract_and_process_region
use crate::AppError; // Assuming AppError is in skb_core/src/lib.rs
use std::sync::Mutex;
use std::collections::HashMap; // For HashMap
use image::ImageFormat; // To specify image format if needed for template parsing, though templates are DynamicImage
use log::{info, error, warn, debug}; // Added debug

/// AppContext holds shared resources for the application.
#[derive(Debug)]
pub struct AppContext {
    pub config: Config,
    pub arduino_com: Mutex<Option<ArduinoCom>>,
    pub template_manager: TemplateManager,
    pub numbers_hashes: HashMap<i64, i32>,
    pub minutes_or_hours_hashes: HashMap<i64, i32>,
    pub cooldown_hashes: HashMap<i64, String>, // Added for cooldowns
}

// Constants for filter parameters have been removed. They will be sourced from config.

impl AppContext {
    /// Creates a new AppContext by loading configuration, initializing Arduino communication,
    /// loading templates, and pre-generating hashes for digits.
    pub fn new(config_path: &str, templates_dir: &str) -> Result<Self, AppError> {
        info!("Initializing AppContext...");

        // Load configuration
        let config = load_config(config_path).map_err(|e| {
            error!("Failed to load config from '{}': {}", config_path, e);
            // Convert config error to AppError - assuming ConfigError maps or is new variant
            AppError::ConfigError(format!("Failed to load config from '{}': {}", config_path, e))
        })?;
        info!("Configuration loaded successfully from '{}'.", config_path);

        // Initialize ArduinoCom
        let arduino_com_instance = match ArduinoCom::new(&config.arduino.port, config.arduino.baud_rate) {
            Ok(com) => {
                info!("ArduinoCom initialized successfully for port {} at {} baud.", config.arduino.port, config.arduino.baud_rate);
                Some(com)
            },
            Err(e) => {
                warn!("Failed to initialize ArduinoCom on port {}: {}. Arduino functionality will be unavailable.", config.arduino.port, e);
                // Depending on application requirements, this could be a hard error:
                // return Err(AppError::ArduinoError(format!("Failed to initialize ArduinoCom: {}", e)));
                None
            }
        };
        let arduino_com = Mutex::new(arduino_com_instance);

        // Initialize TemplateManager and load templates
        let mut template_manager = TemplateManager::new();
        match template_manager.load_templates_from_directory(templates_dir) {
            Ok(_) => {
                info!("Templates loaded successfully from '{}'. Found {} templates.", templates_dir, template_manager.list_template_names().len());
            }
            Err(e) => {
                error!("Failed to load templates from '{}': {}. Template matching may fail.", templates_dir, e);
                // Depending on requirements, this could be a hard error:
                // return Err(AppError::TemplateError(format!("Failed to load templates: {}", e)));
                // For now, we allow AppContext to be created even if templates fail to load,
                // but TemplateManager will be empty or partially filled.
            }
        }

        // Generate numbers_hashes
        let mut numbers_hashes = HashMap::new();
        info!("Generating number hashes...");
        for i in 0..=9 {
            let template_name = format!("digits/digit_{}", i); // Changed path
            let full_template_path = format!("{}/{}", templates_dir, template_name); // For logging
            debug!("Attempting to load number template: '{}' from path: '{}'", template_name, full_template_path);
            if let Some(template) = template_manager.get_template(&template_name) {
                debug!("Found number template: '{}'. Processing...", template_name);
                // Convert DynamicImage to Luma8 for processing
                let luma_image = template.image.to_luma8();
                let image_data = luma_image.as_raw();
                let (image_width, image_height) = luma_image.dimensions();

                if let Some(processed_region_data) = hash_utils::extract_and_process_region(
                    image_data, image_width, image_height,
                    0, 0, image_width as usize, image_height as usize, // Process the whole image
                    true, // apply_value_filter for numbers
                    config.value_type_filter_params.filter_range_low,
                    config.value_type_filter_params.filter_range_high,
                    config.value_type_filter_params.value_to_filter_to_zero_for_range,
                    config.value_type_filter_params.val_is_126,
                    config.value_type_filter_params.val_is_192,
                    config.value_type_filter_params.val_to_assign_if_126_or_192,
                    config.value_type_filter_params.val_else_filter_to_zero,
                ) {
                    let hash = hash_utils::hashit_rust(&processed_region_data);
                    numbers_hashes.insert(hash, i);
                    debug!("Generated hash {} for number template '{}' (mapped to value {}). Path: '{}'", hash, template_name, i, full_template_path);
                } else {
                    warn!("Failed to process template data for number hash generation: {}. Path: '{}'", template_name, full_template_path);
                }
            } else {
                warn!("Template not found for number hash generation: {}. Expected at path: '{}'", template_name, full_template_path);
            }
        }
        info!("Number hashes generation complete. {} hashes generated.", numbers_hashes.len());

        // Generate minutes_or_hours_hashes (using same digit templates but different processing)
        let mut minutes_or_hours_hashes = HashMap::new();
        info!("Generating time hashes (minutes/hours)...");
        for i in 0..=9 { // Assuming time digits also use "digits/digit_0" to "digits/digit_9" templates
            let template_name = format!("digits/digit_{}", i); // Changed path
            let full_template_path = format!("{}/{}", templates_dir, template_name); // For logging
            debug!("Attempting to load time template: '{}' from path: '{}'", template_name, full_template_path);
            if let Some(template) = template_manager.get_template(&template_name) {
                debug!("Found time template: '{}'. Processing...", template_name);
                let luma_image = template.image.to_luma8();
                let image_data = luma_image.as_raw();
                let (image_width, image_height) = luma_image.dimensions();

                if let Some(processed_region_data) = hash_utils::extract_and_process_region(
                    image_data, image_width, image_height,
                    0, 0, image_width as usize, image_height as usize, // Process the whole image
                    false, // apply_value_filter is false for time hashes
                    config.non_value_type_filter_params.filter_range_low,
                    config.non_value_type_filter_params.filter_range_high,
                    config.non_value_type_filter_params.value_to_filter_to_zero_for_range,
                    config.non_value_type_filter_params.val_is_126,
                    config.non_value_type_filter_params.val_is_192,
                    config.non_value_type_filter_params.val_to_assign_if_126_or_192,
                    config.non_value_type_filter_params.val_else_filter_to_zero,
                ) {
                    let hash = hash_utils::hashit_rust(&processed_region_data);
                    minutes_or_hours_hashes.insert(hash, i);
                     debug!("Generated hash {} for time template '{}' (mapped to value {}). Path: '{}'", hash, template_name, i, full_template_path);
                } else {
                    warn!("Failed to process template data for time hash generation: {}. Path: '{}'", template_name, full_template_path);
                }
            } else {
                warn!("Template not found for time hash generation: {}. Expected at path: '{}'", template_name, full_template_path);
            }
        }
        info!("Time hashes generation complete. {} hashes generated.", minutes_or_hours_hashes.len());

        // Generate cooldown_hashes
        let mut cooldown_hashes = HashMap::new();
        info!("Generating cooldown hashes...");
        // These keys should match the `area_key` used in `check_specific_cooldown_rust`
        // and the template file names (e.g., "attack.png", "healing.png", "support.png").
        // Template files are expected to be directly in templates_dir, e.g., "templates/attack.png"
        let cooldown_template_names = ["attack", "healing", "support"]; // These are the base names, e.g., attack.png

        for template_base_name in cooldown_template_names.iter() {
            // Template name for lookup in TemplateManager (key is filename without extension, e.g., "attack")
            let template_key = template_base_name.to_string();
            // Actual file name would be like "attack.png", TemplateManager handles stripping extension for the key.
            // So, full_template_path for logging should reflect potential file name.
            let full_template_path = format!("{}/{}.png", templates_dir, template_base_name); // Example with .png

            debug!("Attempting to load cooldown template key: '{}' (expected file like '{}')", template_key, full_template_path);

            if let Some(template) = template_manager.get_template(&template_key) {
                debug!("Found cooldown template: '{}'. Processing...", template_key);
                let luma_image = template.image.to_luma8();
                let image_data = luma_image.as_raw();
                let hash = hash_utils::hashit_rust(image_data);
                cooldown_hashes.insert(hash, template_key.clone()); // area_key is template_key here
                debug!("Generated hash {} for cooldown template key '{}' (mapped to area_key '{}'). Path: '{}'", hash, template_key, template_key, full_template_path);
            } else {
                warn!("Template not found for cooldown hash generation: key '{}'. Expected file like '{}'", template_key, full_template_path);
            }
        }
        info!("Cooldown hashes generation complete. {} hashes generated.", cooldown_hashes.len());

        info!("AppContext initialized successfully.");
        Ok(AppContext {
            config,
            arduino_com,
            template_manager,
            numbers_hashes,
            minutes_or_hours_hashes,
            cooldown_hashes,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::settings::{self, ImageFilterParameters, GeneralSettings, ArduinoConfig, HotkeyConfig, PlayerStatusRegions, ScreenRegion};
    use tempfile::{Builder, TempDir};
    use std::fs::{self, File};
    use std::io::Write;
    use image::{ImageBuffer, Luma, Rgb}; // For creating dummy images

    // Helper to create a dummy PNG image (grayscale)
    fn create_dummy_luma_image(path: &std::path::Path, width: u32, height: u32, pixel_val: u8) {
        let img: ImageBuffer<Luma<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |_, _| Luma([pixel_val]));
        img.save(path).expect("Failed to save dummy luma image");
    }

    // Helper to create a dummy RGB PNG image (though templates are processed as Luma8)
    fn create_dummy_rgb_image(path: &std::path::Path, width: u32, height: u32, color: [u8;3]) {
        let img: ImageBuffer<Rgb<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |_, _| Rgb(color));
        img.save(path).expect("Failed to save dummy rgb image");
    }


    fn setup_test_environment() -> Result<(TempDir, String), Box<dyn std::error::Error>> {
        let temp_dir = Builder::new().prefix("app_context_test").tempdir()?;
        let templates_path = temp_dir.path().join("templates");
        fs::create_dir_all(&templates_path)?;

        let digits_path = templates_path.join("digits");
        fs::create_dir_all(&digits_path)?;

        // Create dummy digit templates (e.g., digit_0.png to digit_9.png)
        for i in 0..=9 {
            // Create simple images, e.g., 10x10 pixels, with a unique pixel value for each digit
            // For simplicity, make digit_i.png have pixel value i*10.
            // Note: Real processing might be more complex, this is just for hash distinctness.
            create_dummy_luma_image(&digits_path.join(format!("digit_{}.png", i)), 10, 10, (i * 10) as u8);
        }

        // Create dummy cooldown templates (e.g., attack.png, healing.png, support.png)
        // These are hashed directly from their Luma8 representation.
        create_dummy_luma_image(&templates_path.join("attack.png"), 20, 20, 10); // Unique pixel value
        create_dummy_luma_image(&templates_path.join("healing.png"), 20, 20, 20);
        create_dummy_luma_image(&templates_path.join("support.png"), 20, 20, 30);

        // Create a dummy config.toml string
        let config_content = format!(
            r#"
            [general]
            character_name = "TestBot"
            auto_login = false

            [arduino]
            port = "/dev/ttyUSB0" # Dummy port
            baud_rate = 9600

            [hotkeys]
            heal = "F1"
            attack_spell = "F2"

            [player_status_regions] # Dummy regions
            [player_status_regions.hp]
            x=0; y=0; width=0; height=0
            [player_status_regions.mp]
            x=0; y=0; width=0; height=0

            [value_type_filter_params]
            filter_range_low = 50
            filter_range_high = 100
            value_to_filter_to_zero_for_range = 0
            val_is_126 = 126
            val_is_192 = 192
            val_to_assign_if_126_or_192 = 192
            val_else_filter_to_zero = 0

            [non_value_type_filter_params]
            filter_range_low = 50
            filter_range_high = 100
            value_to_filter_to_zero_for_range = 0
            val_is_126 = 0
            val_is_192 = 0
            val_to_assign_if_126_or_192 = 0
            val_else_filter_to_zero = 0
            "#
        );
        let config_file_path = temp_dir.path().join("test_config.toml");
        let mut file = File::create(&config_file_path)?;
        file.write_all(config_content.as_bytes())?;

        Ok((temp_dir, config_file_path.to_str().unwrap().to_string()))
    }

    #[test]
    fn test_app_context_new_hash_map_generation() {
        let (_temp_dir, config_path) = setup_test_environment().expect("Failed to set up test environment.");
        let templates_dir_path = _temp_dir.path().join("templates").to_str().unwrap().to_string();

        let app_context_result = AppContext::new(&config_path, &templates_dir_path);
        assert!(app_context_result.is_ok(), "AppContext::new failed: {:?}", app_context_result.err());
        let app_context = app_context_result.unwrap();

        // Verify numbers_hashes
        assert_eq!(app_context.numbers_hashes.len(), 10, "Should have 10 number hashes.");

        // Manually calculate hash for "digit_1.png"
        let digit_1_template_path = _temp_dir.path().join("templates/digits/digit_1.png");
        let digit_1_image = image::open(digit_1_template_path).expect("Failed to open digit_1.png for test").to_luma8();
        let (w, h) = digit_1_image.dimensions();
        let params = &app_context.config.value_type_filter_params;
        let processed_digit_1 = hash_utils::extract_and_process_region(
            digit_1_image.as_raw(), w, h, 0, 0, w as usize, h as usize, true,
            params.filter_range_low, params.filter_range_high, params.value_to_filter_to_zero_for_range,
            params.val_is_126, params.val_is_192, params.val_to_assign_if_126_or_192, params.val_else_filter_to_zero
        ).expect("Processing digit_1 failed for test");
        let manual_hash_digit_1 = hash_utils::hashit_rust(&processed_digit_1);

        let mut found_digit_1_hash_in_map = false;
        for (hash, value) in &app_context.numbers_hashes {
            if *value == 1 && *hash == manual_hash_digit_1 {
                found_digit_1_hash_in_map = true;
                break;
            }
        }
        assert!(found_digit_1_hash_in_map, "Manually calculated hash for digit_1 not found or doesn't match in numbers_hashes.");

        // Verify minutes_or_hours_hashes (similar logic for digit_2, apply_value_filter=false)
        assert_eq!(app_context.minutes_or_hours_hashes.len(), 10, "Should have 10 time hashes.");
        let digit_2_template_path = _temp_dir.path().join("templates/digits/digit_2.png");
        let digit_2_image = image::open(digit_2_template_path).expect("Failed to open digit_2.png for test").to_luma8();
        let (w2, h2) = digit_2_image.dimensions();
        let params_non_value = &app_context.config.non_value_type_filter_params;
        let processed_digit_2_time = hash_utils::extract_and_process_region(
            digit_2_image.as_raw(), w2, h2, 0, 0, w2 as usize, h2 as usize, false,
            params_non_value.filter_range_low, params_non_value.filter_range_high, params_non_value.value_to_filter_to_zero_for_range,
            params_non_value.val_is_126, params_non_value.val_is_192, params_non_value.val_to_assign_if_126_or_192, params_non_value.val_else_filter_to_zero
        ).expect("Processing digit_2 for time failed");
        let manual_hash_digit_2_time = hash_utils::hashit_rust(&processed_digit_2_time);

        let mut found_digit_2_time_hash_in_map = false;
        for (hash, value) in &app_context.minutes_or_hours_hashes {
            if *value == 2 && *hash == manual_hash_digit_2_time {
                found_digit_2_time_hash_in_map = true;
                break;
            }
        }
        assert!(found_digit_2_time_hash_in_map, "Manually calculated hash for digit_2 (time) not found or doesn't match.");


        // Verify cooldown_hashes
        assert_eq!(app_context.cooldown_hashes.len(), 3, "Should have 3 cooldown hashes.");
        let attack_template_path = _temp_dir.path().join("templates/attack.png");
        let attack_image = image::open(attack_template_path).expect("Failed to open attack.png for test").to_luma8();
        let manual_hash_attack = hash_utils::hashit_rust(attack_image.as_raw());
        assert_eq!(app_context.cooldown_hashes.get(&manual_hash_attack).unwrap(), "attack");
    }

    #[test]
    fn test_app_context_new_missing_template() {
        let (_temp_dir, config_path) = setup_test_environment().expect("Failed to set up test environment.");
        let templates_dir_path = _temp_dir.path().join("templates");

        // Remove one digit template, e.g., digit_5.png
        fs::remove_file(templates_dir_path.join("digits/digit_5.png")).expect("Failed to remove digit_5.png for test");

        let app_context_result = AppContext::new(&config_path, templates_dir_path.to_str().unwrap());
        assert!(app_context_result.is_ok(), "AppContext::new failed even with a missing template: {:?}", app_context_result.err());
        let app_context = app_context_result.unwrap();

        // Should have one less number hash if a digit template was missing and warnings were logged.
        assert_eq!(app_context.numbers_hashes.len(), 9, "Should have 9 number hashes if digit_5 is missing.");
        // Ensure digit_5 is not in the map values (or its hash is not a key)
        assert!(!app_context.numbers_hashes.values().any(|&v| v == 5), "Digit 5 should not be in numbers_hashes values.");
    }
}
