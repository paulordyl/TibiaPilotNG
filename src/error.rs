// src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Configuration error")]
    Config(#[from] skb_config::ConfigError),

    #[error("Utility error")] // Updated error message for consistency
    Utils(#[from] skb_utils::error::UtilsError), // Changed from Utils(String)

    #[error("I/O error")]
    Io(#[from] std::io::Error),

    #[error("Logger setup failed")]
    Logging(#[from] log::SetLoggerError),

    #[error("Application runtime error: {0}")]
    Runtime(String),
}
