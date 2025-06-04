// src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Configuration error")]
    Config(#[from] skb_config::ConfigError),

    #[error("Utility error: {0}")] // Modified to display the underlying error string
    Utils(String), // Placeholder until skb_utils::error::UtilsError is defined and crate exists

    // If skb_utils and its error type were defined:
    // #[error("Utility error")]
    // Utils(#[from] skb_utils::error::UtilsError),

    #[error("I/O error")]
    Io(#[from] std::io::Error),

    #[error("Logger setup failed")]
    Logging(#[from] log::SetLoggerError),

    #[error("Application runtime error: {0}")]
    Runtime(String), // Generic runtime error
}
