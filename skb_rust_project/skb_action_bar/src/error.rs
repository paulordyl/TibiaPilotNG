//! Defines the error types for the `skb_action_bar` crate.

use thiserror::Error;

/// Represents errors that can occur during action bar operations or state management.
#[derive(Error, Debug, Clone, PartialEq, Eq)]
pub enum ActionBarError {
    /// Indicates that an action slot with the specified identifier was not found.
    /// The string argument is typically the `slot_key_designator`.
    #[error("Action slot with ID '{0}' not found.")]
    SlotNotFound(String),

    /// Signifies an attempt to perform an invalid action or assign invalid content
    /// to a specified action slot.
    #[error("Invalid action or content for slot '{slot_id}': {reason}")]
    InvalidSlotAction {
        /// The identifier of the slot where the invalid action was attempted.
        slot_id: String,
        /// The reason why the action or content was considered invalid.
        reason: String,
    },

    /// Denotes an error related to the configuration of the action bar itself
    /// (e.g., invalid layout data, misconfigured slot definitions).
    #[error("Configuration error related to action bar: {0}")]
    ConfigurationError(String),

    /// Occurs when a perception module fails to update the action bar's state
    /// or provides inconsistent or unparseable data.
    #[error("Perception module failed to update action bar state: {0}")]
    PerceptionError(String),

    // If this crate were to also handle input via skb_input:
    // #[error("Input action failed for slot '{slot_id}'")]
    // InputActionFailed {
    //     slot_id: String,
    //     #[source] // Optional: if skb_input::InputError is to be wrapped directly
    //     source_error: skb_input::InputError, // Requires skb_input as a dependency
    // },

    // Add other specific error types as they become necessary.
}
