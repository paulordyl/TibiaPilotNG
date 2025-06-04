// skb_config/src/loader.rs
use crate::types::Config; // Assuming types.rs is in the same crate root
use crate::error::ConfigError;
use config_rs::{Config as ConfigRs, File, Environment}; // Alias config_rs::Config to ConfigRs
use std::path::Path;

pub fn load_config(config_dir_path: &Path) -> Result<Config, ConfigError> {
    let default_config_path = config_dir_path.join("default.toml");
    let local_config_path = config_dir_path.join("local.toml");
    // Optional: Add other sources like environment-specific files, e.g., development.toml, production.toml

    let mut builder = ConfigRs::builder()
        // Add default values (if any are not covered by Config::default() orserde defaults)
        // .set_default("some_key", "default_value")?
        // This line would require ConfigError to have a variant for config_rs::ConfigError if set_default can fail
        // For now, assuming Config::default() or TOML files provide all necessary defaults.

        // Load default configuration file
        .add_source(File::from(default_config_path).required(false)); // Make default optional for flexibility

    // Load local overrides if local.toml exists
    if local_config_path.exists() {
        builder = builder.add_source(File::from(local_config_path).required(true));
    }

    // Add environment variables overrides
    // Example: SKB_BOT_NAME would override config.bot_name
    // Adjust prefix and separator as needed
    builder = builder.add_source(Environment::with_prefix("SKB").separator("__"));

    // Build the configuration
    let settings = builder.build()?; // This will map to ConfigError::LoadError due to #[from]

    // Deserialize into the Config struct
    match settings.try_deserialize::<Config>() {
        Ok(config) => Ok(config),
        Err(e) => Err(ConfigError::LoadError(e)), // Ensure this mapping is correct
    }
}
