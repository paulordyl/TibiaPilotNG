//! Defines the error type for the `skb_input` crate.

use thiserror::Error;

/// Represents errors that can occur during input simulation operations.
#[derive(Error, Debug)]
pub enum InputError {
    /// Indicates a general failure during input simulation, often related to the backend.
    /// This could be due to issues initializing `Enigo` or failures reported by it.
    #[error("Input simulation failed: {0}")]
    SimulationError(String),

    /// Indicates that an unsupported key, mouse button, or specific action was requested.
    #[error("Unsupported key or action: {0}")]
    UnsupportedAction(String),
    // Add other specific error types if they become necessary.
    // For example, if a specific platform returned an error:
    // #[error("Platform-specific input error: {0}")]
    // PlatformError(String),
}
