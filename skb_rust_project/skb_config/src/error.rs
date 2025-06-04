// skb_config/src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Failed to load configuration")]
    LoadError(#[from] config_rs::ConfigError), // Using config_rs::ConfigError

    #[error("I/O error reading configuration file")]
    IoError(#[from] std::io::Error),

    // Add any other specific error types if they become necessary
    // For example, if we had specific validation errors not covered by ConfigError:
    // #[error("Configuration validation error: {0}")]
    // ValidationError(String),
}
