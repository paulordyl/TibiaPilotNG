// src/main.rs

mod error;
use error::AppError;

use skb_config::{load_config, Config as SkbAppConfig};
use skb_utils::setup_logging; // Import the actual setup_logging function
use std::path::Path;

// This path will likely need to be verified by the user.
const CONTROL_CONFIG_DIR_PATH: &str = "config";

// setup_logging_placeholder function removed

fn main() -> Result<(), AppError> {
    // Load configuration
    let config = load_config(Path::new(CONTROL_CONFIG_DIR_PATH))?;

    // Setup logging using the function from skb_utils
    // The '?' operator will convert skb_utils::error::UtilsError into AppError::Utils
    // due to the #[from] attribute in AppError's definition for Utils.
    setup_logging(config.log_level.as_deref())?;

    log::info!("SKB Control starting...");
    log::debug!("Configuration loaded: {:?}", config);

    // Placeholder for the main bot loop
    if let Err(e) = run_bot_loop(&config) {
        log::error!("Error in bot loop: {}", e);
        return Err(e);
    }

    log::info!("SKB Control finished successfully.");
    Ok(())
}

fn run_bot_loop(config: &SkbAppConfig) -> Result<(), AppError> {
    log::info!("Bot loop starting.");
    log::debug!("Using scan_interval_ms: {:?}", config.scan_interval_ms);

    if config.bot_name.as_deref().unwrap_or("") == "ErrorBot" {
        return Err(AppError::Runtime("Simulated error from ErrorBot configuration".to_string()));
    }

    println!("Bot loop executed. (Placeholder - implement actual bot logic here)");

    log::info!("Bot loop finished.");
    Ok(())
}
