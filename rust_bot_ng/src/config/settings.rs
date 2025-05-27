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
    // TODO: Add other general settings
}

#[derive(Deserialize, Debug, Clone)] // Added Clone
pub struct Config {
    pub general: GeneralSettings,
    pub arduino: ArduinoConfig,
    pub hotkeys: HotkeyConfig,
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
        AppError::IOError(e) // Convert std::io::Error to AppError::IOError
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
