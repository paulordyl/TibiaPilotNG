//! Provides the `ActionBarManager` for managing the state of action bar(s)
//! based on perceived information from the game.

use crate::types::{ActionBarState, ActionSlot, SlotContentType};
use crate::error::ActionBarError; // Keep even if not directly returned by public methods, for consistency or future use.
use std::collections::HashMap;

// For timestamping, similar to skb_game_state
#[cfg(not(target_arch = "wasm32"))]
use std::time::{SystemTime, UNIX_EPOCH};

/// Manages the collective state of all observed action bar slots.
///
/// This struct allows updating slot information (typically from perception modules based on screen observation)
/// and querying the current state of these slots (which can be used by gameplay logic modules
/// to make decisions, e.g., checking if a spell is on cooldown or an item is available).
/// It uses a `HashMap` internally for efficient lookup of slots by their string identifiers.
#[derive(Debug, Clone, Default)]
pub struct ActionBarManager {
    state: ActionBarState,
    // Optional: For quick lookup of slot index by its key designator
    slot_index_map: HashMap<String, usize>,
}

impl ActionBarManager {
    /// Creates a new, empty `ActionBarManager`.
    /// The internal state is initialized to default values, meaning no slots are present
    /// and the `last_update_timestamp_ms` is `None`.
    pub fn new() -> Self {
        Self::default() // Relies on derive(Default) for both ActionBarManager and ActionBarState
    }

    /// Adds a new action slot or updates an existing one based on `slot_key_designator`.
    ///
    /// If a slot with the same `slot_key_designator` as `new_slot_data` already exists,
    /// its data is replaced with `new_slot_data`. Otherwise, `new_slot_data` is added
    /// to the manager's list of slots.
    /// The internal `slot_index_map` is updated accordingly for quick lookups.
    /// The manager's `last_update_timestamp_ms` (on the internal `ActionBarState`) is updated.
    ///
    /// # Arguments
    /// * `new_slot_data`: The `ActionSlot` data to add or update.
    pub fn update_slot(&mut self, new_slot_data: ActionSlot) {
        let key = new_slot_data.slot_key_designator.clone();
        if let Some(index) = self.slot_index_map.get(&key) {
            if let Some(slot) = self.state.slots.get_mut(*index) {
                *slot = new_slot_data;
            }
        } else {
            let new_index = self.state.slots.len();
            self.state.slots.push(new_slot_data);
            self.slot_index_map.insert(key, new_index);
        }
        self.update_timestamp();
    }

    /// Replaces all currently managed action slots with a new set of slots.
    ///
    /// This is useful for performing a full refresh of the action bar state,
    /// for example, when perception modules provide a complete new snapshot.
    /// The internal `slot_index_map` is rebuilt, and the `last_update_timestamp_ms` is updated.
    ///
    /// # Arguments
    /// * `all_slots`: A `Vec<ActionSlot>` containing the new set of action slots.
    pub fn replace_all_slots(&mut self, all_slots: Vec<ActionSlot>) {
        self.state.slots = all_slots;
        self.rebuild_slot_index_map();
        self.update_timestamp();
    }

    /// Helper to rebuild the `slot_index_map` for efficient lookups.
    /// This should be called whenever `state.slots` is entirely replaced or significantly restructured.
    fn rebuild_slot_index_map(&mut self) {
        self.slot_index_map.clear();
        for (index, slot) in self.state.slots.iter().enumerate() {
            self.slot_index_map.insert(slot.slot_key_designator.clone(), index);
        }
    }

    /// Retrieves a read-only reference to a specific action slot by its key designator.
    ///
    /// # Arguments
    /// * `slot_key_designator`: The unique string identifier of the slot to retrieve.
    ///
    /// # Returns
    /// Returns `Some(&ActionSlot)` if a slot with the given designator is found,
    /// otherwise returns `None`.
    pub fn get_slot(&self, slot_key_designator: &str) -> Option<&ActionSlot> {
        self.slot_index_map.get(slot_key_designator)
            .and_then(|index| self.state.slots.get(*index))
    }

    /// Retrieves a read-only reference to the vector of all currently monitored action slots.
    pub fn get_all_slots(&self) -> &Vec<ActionSlot> {
        &self.state.slots
    }

    /// Checks if a specific spell is currently observed to be on cooldown.
    ///
    /// This method iterates through all managed action slots. If a slot containing
    /// a spell with the given `spell_id_to_check` is found, its `is_on_cooldown`
    /// status is returned.
    ///
    /// # Arguments
    /// * `spell_id_to_check`: The unique identifier (e.g., name or game ID) of the spell.
    ///
    /// # Returns
    /// - `Some(true)` if the spell is found in a slot and `is_on_cooldown` is true.
    /// - `Some(false)` if the spell is found in a slot and `is_on_cooldown` is false.
    /// - `None` if no slot contains a spell with the specified ID.
    pub fn is_spell_on_cooldown(&self, spell_id_to_check: &str) -> Option<bool> {
        for slot in &self.state.slots {
            if let SlotContentType::Spell { spell_id } = &slot.content {
                if spell_id == spell_id_to_check {
                    return Some(slot.is_on_cooldown);
                }
            }
        }
        None // Spell not found
    }

    /// Finds the first action slot containing an item with the specified item ID.
    ///
    /// This method iterates through all managed action slots. If a slot containing
    /// an item with the given `item_id_to_find` is found, a reference to that
    /// `ActionSlot` is returned.
    ///
    /// # Arguments
    /// * `item_id_to_find`: The unique identifier (e.g., name or game ID) of the item.
    ///
    /// # Returns
    /// Returns `Some(&ActionSlot)` if an item with the specified ID is found in any slot,
    /// otherwise returns `None`. If multiple slots contain the item, only the first one
    /// encountered during iteration is returned.
    pub fn find_item_in_slots(&self, item_id_to_find: &str) -> Option<&ActionSlot> {
        self.state.slots.iter().find(|slot| {
            if let SlotContentType::Item { item_id, .. } = &slot.content {
                item_id == item_id_to_find
            } else {
                false
            }
        })
    }

    /// Helper to update the `last_update_timestamp_ms` of the internal `ActionBarState`.
    ///
    /// On non-wasm32 targets, this sets the timestamp to the current system time
    /// in milliseconds since the UNIX epoch.
    /// On wasm32 targets, this currently sets the timestamp to `None` as a placeholder,
    /// indicating that a platform-specific time source might be needed for wasm if precise
    /// update times are critical in that environment.
    fn update_timestamp(&mut self) {
        #[cfg(not(target_arch = "wasm32"))]
        {
            self.state.last_update_timestamp_ms = Some(
                SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64,
            );
        }
        #[cfg(target_arch = "wasm32")]
        {
            // Placeholder for wasm-compatible time source or leave None
            self.state.last_update_timestamp_ms = None;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*; // Imports ActionBarManager
    use crate::types::{ActionSlot, SlotContentType}; // Import types from the same crate

    #[test]
    fn test_new_action_bar_manager() {
        let manager = ActionBarManager::new();
        assert!(manager.get_all_slots().is_empty(), "New manager should have no slots");
        assert!(manager.slot_index_map.is_empty(), "New manager slot_index_map should be empty");
        // Timestamp is None by default from ActionBarState's Default derive.
        assert!(manager.state.last_update_timestamp_ms.is_none(), "Timestamp should be None for new manager");
    }

    #[test]
    fn test_update_and_get_slot() {
        let mut manager = ActionBarManager::new();
        let slot_f1 = ActionSlot {
            slot_key_designator: "F1".to_string(),
            content: SlotContentType::Spell { spell_id: "heal_light".to_string() },
            is_on_cooldown: false,
            ..Default::default()
        };
        manager.update_slot(slot_f1.clone());

        assert_eq!(manager.get_all_slots().len(), 1);
        assert_eq!(manager.get_slot("F1"), Some(&slot_f1));
        assert_eq!(manager.slot_index_map.get("F1"), Some(&0));

        #[cfg(not(target_arch = "wasm32"))]
        assert!(manager.state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(manager.state.last_update_timestamp_ms.is_none());


        // Update existing slot
        let slot_f1_updated = ActionSlot {
            slot_key_designator: "F1".to_string(),
            content: SlotContentType::Spell { spell_id: "heal_greater".to_string() },
            is_on_cooldown: true,
            cooldown_remaining_ms: Some(5000),
            ..Default::default()
        };
        manager.update_slot(slot_f1_updated.clone());

        assert_eq!(manager.get_all_slots().len(), 1, "Slot count should remain 1 after update");
        assert_eq!(manager.get_slot("F1"), Some(&slot_f1_updated));
        assert!(manager.get_slot("F1").unwrap().is_on_cooldown);
    }

    #[test]
    fn test_replace_all_slots() {
        let mut manager = ActionBarManager::new();
        manager.update_slot(ActionSlot { slot_key_designator: "F1".to_string(), ..Default::default() });

        let new_slots = vec![
            ActionSlot { slot_key_designator: "1".to_string(), content: SlotContentType::Item { item_id: "mana_potion".to_string(), quantity: 5 }, ..Default::default()},
            ActionSlot { slot_key_designator: "2".to_string(), content: SlotContentType::Spell { spell_id: "attack_spell".to_string() }, ..Default::default()},
        ];
        manager.replace_all_slots(new_slots.clone());

        assert_eq!(manager.get_all_slots().len(), 2);
        assert_eq!(manager.get_slot("1"), Some(&new_slots[0]));
        assert_eq!(manager.get_slot("2"), Some(&new_slots[1]));
        assert!(manager.get_slot("F1").is_none(), "Old F1 slot should be gone");
        assert_eq!(manager.slot_index_map.len(), 2);
        assert_eq!(manager.slot_index_map.get("1"), Some(&0));
        assert_eq!(manager.slot_index_map.get("2"), Some(&1));
    }

    #[test]
    fn test_get_non_existent_slot() {
        let manager = ActionBarManager::new();
        assert!(manager.get_slot("DoesNotExist").is_none());
    }

    #[test]
    fn test_is_spell_on_cooldown() {
        let mut manager = ActionBarManager::new();
        let heal_spell = ActionSlot {
            slot_key_designator: "F1".to_string(),
            content: SlotContentType::Spell { spell_id: "heal_light".to_string() },
            is_on_cooldown: true,
            cooldown_remaining_ms: Some(3000),
            ..Default::default()
        };
        let attack_spell = ActionSlot {
            slot_key_designator: "F2".to_string(),
            content: SlotContentType::Spell { spell_id: "fireball".to_string() },
            is_on_cooldown: false,
            ..Default::default()
        };
        let item_slot = ActionSlot {
            slot_key_designator: "1".to_string(),
            content: SlotContentType::Item { item_id: "potion".to_string(), quantity: 1 },
            ..Default::default()
        };
        manager.replace_all_slots(vec![heal_spell, attack_spell, item_slot]);

        assert_eq!(manager.is_spell_on_cooldown("heal_light"), Some(true));
        assert_eq!(manager.is_spell_on_cooldown("fireball"), Some(false));
        assert_eq!(manager.is_spell_on_cooldown("unknown_spell"), None);
    }

    #[test]
    fn test_find_item_in_slots() {
        let mut manager = ActionBarManager::new();
        let potion_slot_data = ActionSlot {
            slot_key_designator: "1".to_string(),
            content: SlotContentType::Item { item_id: "health_potion".to_string(), quantity: 5 },
            ..Default::default()
        };
        let spell_slot_data = ActionSlot {
            slot_key_designator: "F1".to_string(),
            content: SlotContentType::Spell { spell_id: "heal".to_string() },
            ..Default::default()
        };
         manager.replace_all_slots(vec![potion_slot_data.clone(), spell_slot_data]);

        let found_item_slot = manager.find_item_in_slots("health_potion");
        assert_eq!(found_item_slot, Some(&potion_slot_data));

        let not_found_item = manager.find_item_in_slots("mana_potion");
        assert!(not_found_item.is_none());
    }
}
