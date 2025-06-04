//! Defines the error types for the `skb_game_state` crate.

use thiserror::Error;

/// Represents errors that can occur during game state operations.
#[derive(Error, Debug, Clone, PartialEq, Eq)] // Added Clone, PartialEq, Eq for potential usability in state comparisons or tests
pub enum GameStateError {
    /// Indicates that an operation was attempted on a game state that
    /// has not been initialized or is missing essential components.
    #[error("The game state has not been initialized yet.")]
    NotInitialized,

    /// Signifies that an attempted update to the game state was invalid
    /// or inconsistent with the current state.
    #[error("An invalid update was attempted on the game state: {0}")]
    InvalidUpdate(String),

    /// Occurs when a requested entity, item, or other specific piece of
    /// state information could not be found.
    #[error("Requested entity or item not found: {0}")]
    NotFound(String),

    /// Denotes that a required piece of information is absent from the
    /// current game state, preventing an operation's completion.
    #[error("A required piece of information is missing from the state: {0}")]
    MissingInformation(String),
    // Add other specific error types as they become necessary during development.
}
