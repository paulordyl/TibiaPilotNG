//! Defines the error type for the `skb_gameplay_logic` crate.

use thiserror::Error;

/// Represents errors that can occur during gameplay logic operations.
#[derive(Error, Debug, Clone, PartialEq, Eq)]
pub enum GameplayError {
    /// A required component or state was not available for a gameplay decision.
    /// Contains a description of the missing precondition.
    #[error("Gameplay precondition failed: {0}")]
    PreconditionFailed(String),

    /// A decision-making process within the gameplay logic failed.
    /// Contains a description of the logic error.
    #[error("Gameplay decision logic error: {0}")]
    DecisionLogicError(String),

    /// An action initiated by gameplay logic failed during its execution.
    #[error("Action execution failed for '{action_description}': {source_error:?}")]
    ActionExecutionError {
        /// A description of the action that was being attempted.
        action_description: String,
        /// Optionally, the error message from the underlying cause (e.g., from `skb_input`).
        source_error: Option<String>,
    },

    /// The current game state is not valid for the attempted action.
    /// Contains a description of why the state is invalid.
    #[error("Invalid game state for action: {0}")]
    InvalidStateForAction(String),

    /// An error occurred within the input simulation module (`skb_input`).
    #[error("Input action failed")]
    InputError(#[from] skb_input::InputError),

    /// An error occurred while accessing or interpreting game state (`skb_game_state`).
    #[error("Game state access failed")]
    GameStateError(#[from] skb_game_state::GameStateError),

    // Add other specific error types as they become necessary.
}
