use crate::AppError; // Assuming AppError is in the root or accessible via crate::
use log::{debug, error};
use serde::Deserialize;
use std::{fs, path::Path};

#[derive(Deserialize, Debug, Clone)] // Added Clone
pub struct HotkeyConfig {
    pub heal: String,
    pub attack_spell: String,
    // TODO: Add other hotkeys as needed, e.g., mana_potion, haste, etc.
}

#[derive(Deserialize, Debug, Clone)] // Added Clone
pub struct ArduinoConfig {
    pub port: String,
    pub baud_rate: u32,
}

#[derive(Deserialize, Debug, Clone)] // Added Clone
pub struct GeneralSettings {
    pub character_name: String,
    pub auto_login: bool,
    pub templates_path: String,
    // TODO: Add other general settings
}

#[derive(Deserialize, Debug, Clone)]
pub struct ScreenRegion {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

#[derive(Deserialize, Debug, Clone)]
pub struct PlayerStatusRegions {
    pub hp: ScreenRegion,
    pub mp: ScreenRegion,
}

#[derive(Deserialize, Debug, Clone)]
pub struct ImageFilterParameters {
    pub filter_range_low: u8,
    pub filter_range_high: u8,
    pub value_to_filter_to_zero_for_range: u8,
    pub val_is_126: u8,
    pub val_is_192: u8,
    pub val_to_assign_if_126_or_192: u8,
    pub val_else_filter_to_zero: u8,
}

#[derive(Deserialize, Debug, Clone)]
pub struct RadarDataPaths {
    pub base_path: String,
    pub floors_imgs_npy: Option<String>,
    pub floors_paths_npy: Option<String>,
    pub radar_coords_npy: Option<String>,
    pub walkable_sqms_npy: Option<String>,
    pub floor_png_pattern: Option<String>, // e.g., "floor-{}.png"
}

#[derive(Deserialize, Debug, Clone)]
pub struct Config {
    pub general: GeneralSettings,
    pub arduino: ArduinoConfig,
    pub hotkeys: HotkeyConfig,
    pub player_status_regions: PlayerStatusRegions,
    pub value_type_filter_params: ImageFilterParameters,
    pub non_value_type_filter_params: ImageFilterParameters,
    pub radar_data: Option<RadarDataPaths>,
}

/// Loads configuration from a TOML file.
///
/// # Arguments
/// * `file_path` - The path to the configuration file (e.g., "config.toml").
///
/// # Returns
/// `Ok(Config)` if loading and parsing are successful.
/// `Err(AppError)` if the file cannot be read or if parsing fails.
pub fn load_config(file_path: &str) -> Result<Config, AppError> {
    debug!("Attempting to load configuration from: {}", file_path);

    let path = Path::new(file_path);
    if !path.exists() {
        error!("Configuration file not found at: {}", file_path);
        return Err(AppError::ConfigError(format!(
            "Configuration file not found: {}",
            file_path
        )));
    }

    let contents = fs::read_to_string(path).map_err(|e| {
        error!("Failed to read configuration file '{}': {}", file_path, e);
        AppError::ConfigError(format!("Failed to read configuration file '{}': {}", file_path, e))
    })?;

    let config: Config = toml::from_str(&contents).map_err(|e| {
        error!("Failed to parse TOML from configuration file '{}': {}", file_path, e);
        AppError::ConfigError(format!(
            "Failed to parse TOML from '{}': {}",
            file_path, e
        ))
    })?;

    debug!("Configuration loaded successfully from: {}", file_path);
    Ok(config)
}

// Example of how to integrate AppError if it's defined in main.rs or lib.rs
// This assumes AppError has variants like ConfigError(String) and IOError(std::io::Error)
/*
#[derive(Debug)]
pub enum AppError {
    ConfigError(String),
    IOError(std::io::Error),
    // ... other error variants
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::ConfigError(s) => write!(f, "Config Error: {}", s),
            AppError::IOError(e) => write!(f, "IO Error: {}", e),
            // ... other variants
        }
    }
}

impl std::error::Error for AppError {}

impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> AppError {
        AppError::IOError(err)
    }
}
*/

#[cfg(test)]
mod tests {
    use super::*; // To import load_config, Config, AppError, etc.
    use tempfile::Builder;
    use std::io::Write;

    fn get_valid_toml_content() -> String {
        r#"
        [general]
        character_name = "TestBot"
        auto_login = true

        [arduino]
        port = "/dev/ttyACM0"
        baud_rate = 115200

        [hotkeys]
        heal = "F1"
        attack_spell = "F2"

        [player_status_regions]
            [player_status_regions.hp]
            x = 10; y = 20; width = 100; height = 10
            [player_status_regions.mp]
            x = 10; y = 30; width = 100; height = 10

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
        "#.to_string()
    }

    #[test]
    fn test_load_config_valid() {
        let toml_content = get_valid_toml_content();
        let mut tmpfile = Builder::new().suffix(".toml").tempfile().unwrap();
        tmpfile.write_all(toml_content.as_bytes()).unwrap();
        let path_str = tmpfile.path().to_str().unwrap();

        let config_result = load_config(path_str);
        assert!(config_result.is_ok(), "load_config failed for valid TOML: {:?}", config_result.err());
        let config = config_result.unwrap();

        assert_eq!(config.general.character_name, "TestBot");
        assert_eq!(config.general.auto_login, true);
        assert_eq!(config.arduino.port, "/dev/ttyACM0");
        assert_eq!(config.arduino.baud_rate, 115200);
        assert_eq!(config.hotkeys.heal, "F1");
        assert_eq!(config.player_status_regions.hp.x, 10);
        assert_eq!(config.value_type_filter_params.filter_range_low, 50);
        assert_eq!(config.non_value_type_filter_params.val_is_126, 0);
    }

    #[test]
    fn test_load_config_missing_file() {
        let result = load_config("a_non_existent_file.toml");
        assert!(result.is_err());
        match result.err().unwrap() {
            AppError::ConfigError(msg) => assert!(msg.contains("Configuration file not found")),
            _ => panic!("Expected ConfigError for missing file"),
        }
    }

    #[test]
    fn test_load_config_malformed_toml() {
        let malformed_toml = "this is not valid toml content---";
        let mut tmpfile = Builder::new().suffix(".toml").tempfile().unwrap();
        tmpfile.write_all(malformed_toml.as_bytes()).unwrap();
        let path_str = tmpfile.path().to_str().unwrap();

        let result = load_config(path_str);
        assert!(result.is_err());
        match result.err().unwrap() {
            AppError::ConfigError(msg) => assert!(msg.contains("Failed to parse TOML")),
            _ => panic!("Expected ConfigError for malformed TOML"),
        }
    }

    #[test]
    fn test_load_config_missing_required_field() {
        let incomplete_toml = r#"
        [general]
        # character_name = "TestBot" ; Missing this required field
        auto_login = false

        [arduino]
        port = "/dev/ttyS0"
        baud_rate = 9600

        [hotkeys]
        heal = "F1"
        attack_spell = "F2"

        [player_status_regions]
            [player_status_regions.hp]
            x = 10; y = 20; width = 100; height = 10
            [player_status_regions.mp]
            x = 10; y = 30; width = 100; height = 10

        [value_type_filter_params]
        filter_range_low = 50; filter_range_high = 100; value_to_filter_to_zero_for_range = 0;
        val_is_126 = 126; val_is_192 = 192; val_to_assign_if_126_or_192 = 192; val_else_filter_to_zero = 0;

        [non_value_type_filter_params]
        filter_range_low = 50; filter_range_high = 100; value_to_filter_to_zero_for_range = 0;
        val_is_126 = 0; val_is_192 = 0; val_to_assign_if_126_or_192 = 0; val_else_filter_to_zero = 0;
        "#;
        let mut tmpfile = Builder::new().suffix(".toml").tempfile().unwrap();
        tmpfile.write_all(incomplete_toml.as_bytes()).unwrap();
        let path_str = tmpfile.path().to_str().unwrap();

        let result = load_config(path_str);
        assert!(result.is_err());
        match result.err().unwrap() {
            AppError::ConfigError(msg) => {
                // Serde's error for missing field is usually "missing field `field_name`"
                assert!(msg.contains("missing field `character_name`") || msg.contains("Failed to parse TOML"));
            }
            _ => panic!("Expected ConfigError for missing required field"),
        }
    }

    #[test]
    fn test_load_config_empty_file() {
        let empty_toml = "";
        let mut tmpfile = Builder::new().suffix(".toml").tempfile().unwrap();
        tmpfile.write_all(empty_toml.as_bytes()).unwrap();
        let path_str = tmpfile.path().to_str().unwrap();

        let result = load_config(path_str);
        assert!(result.is_err());
        match result.err().unwrap() {
            AppError::ConfigError(msg) => assert!(msg.contains("Failed to parse TOML") || msg.contains("empty")), // Error msg might vary slightly
            _ => panic!("Expected ConfigError for empty file"),
        }
    }
}
