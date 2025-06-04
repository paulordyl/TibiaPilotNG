// skb_utils/src/error.rs
use thiserror::Error;

#[derive(Error, Debug)]
pub enum UtilsError {
    #[error("File operation failed")]
    IoError(#[from] std::io::Error),

    #[error("Logger setup failed")]
    LoggerError(#[from] log::SetLoggerError),

    // Add other specific utility errors if needed in the future
    // For example:
    // #[error("Timing operation failed: {0}")]
    // TimingError(String),
}
