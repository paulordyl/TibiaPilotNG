//! Contains all core data structures and enums for representing the state of game action bars
//! and their individual slots.

// Potentially use serde later if these need to be serialized (e.g. from config or for logging).
// use serde::{Serialize, Deserialize};

/// Describes the content of an action slot, which can be empty, a spell, or an item.
#[derive(Debug, Clone, PartialEq, Eq)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub enum SlotContentType {
    /// The slot is currently empty.
    Empty,
    /// The slot contains a spell.
    Spell {
        /// A unique identifier for the spell (e.g., its name or an internal game ID).
        spell_id: String,
    },
    /// The slot contains an item.
    Item {
        /// A unique identifier for the item type (e.g., its name or an internal game ID).
        item_id: String,
        /// The quantity of the item in this slot, if stackable.
        quantity: u32,
    },
}

impl Default for SlotContentType {
    /// Returns `SlotContentType::Empty` as the default content type.
    fn default() -> Self {
        SlotContentType::Empty
    }
}

/// Represents the dynamic state of a single action slot on the action bar.
/// This information is typically gathered by perception modules.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct ActionSlot {
    /// A string identifying the slot, e.g., "F1", "1", "MainBar_Slot3".
    /// This should match a configured slot designator used for consistent identification.
    pub slot_key_designator: String,

    /// The observed content of the slot (e.g., empty, a specific spell, or an item).
    pub content: SlotContentType,

    /// Whether the action or item in the slot is currently on cooldown.
    pub is_on_cooldown: bool,

    /// Estimated remaining cooldown time in milliseconds, if known and currently on cooldown.
    /// `None` if not on cooldown or if the remaining time is unknown.
    pub cooldown_remaining_ms: Option<u32>,

    /// For abilities or spells that can be toggled on/off, this indicates if it's currently active.
    /// `None` if the content is not toggleable or if its active state is unknown.
    pub is_active: Option<bool>,

    /// An optional hash of the slot's last observed image or visual representation.
    /// This can be used by perception modules to quickly detect if a slot's visual appearance
    /// has changed, potentially triggering a more detailed analysis of its state.
    pub last_observed_image_hash: Option<String>,
}

/// Represents the overall observed state of all monitored action slots on one or more action bars.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct ActionBarState {
    /// A list of the current states of all known or monitored action slots.
    /// The order might be significant if it reflects a specific action bar layout.
    pub slots: Vec<ActionSlot>,

    /// Timestamp of the last update to any slot in this state, in milliseconds since UNIX epoch.
    /// Can be used to determine the freshness of the action bar information.
    pub last_update_timestamp_ms: Option<u64>,
}
