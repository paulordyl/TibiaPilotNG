//! Contains all core data structures and enums for representing the game state.
//! These types are designed to be serializable (with optional `serde` feature)
//! and provide methods for updating and querying the game state.

// If serde is to be used later, uncomment in Cargo.toml and add derive here.
// use serde::{Serialize, Deserialize};

/// Represents a 3D coordinate in the game world.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))] // Example for optional serde
pub struct Coordinate {
    /// The x-coordinate.
    pub x: i32,
    /// The y-coordinate.
    pub y: i32,
    /// The z-coordinate (e.g., floor level).
    pub z: i32,
}

/// Represents the player's current status, including health, mana, position, and active effects.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct PlayerStatus {
    /// Current health points.
    pub health: u32,
    /// Maximum possible health points.
    pub max_health: u32,
    /// Current mana points.
    pub mana: u32,
    /// Maximum possible mana points.
    pub max_mana: u32,
    /// Current position in the game world, if known.
    pub position: Option<Coordinate>,
    /// Player's current movement speed, if applicable.
    pub current_speed: Option<u32>,
    /// List of active buffs affecting the player. Names or IDs of buffs.
    pub buffs: Vec<String>, // Consider a more structured Buff type later if needed
    /// List of active debuffs affecting the player. Names or IDs of debuffs.
    pub debuffs: Vec<String>, // Consider a more structured Debuff type later if needed
}

/// Categorizes the type of a game entity.
#[derive(Debug, Clone, PartialEq, Eq)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub enum EntityType {
    /// The player character.
    Player,
    /// A non-player character that is typically hostile.
    Monster,
    /// A non-player character that is typically non-hostile or interactive.
    Npc,
    /// An entity of an unknown or uncategorized type.
    Unknown,
}

impl Default for EntityType {
    /// Returns `EntityType::Unknown` as the default entity type.
    fn default() -> Self { EntityType::Unknown }
}

/// Represents a game entity such as a creature, NPC, or another player observed in the game.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct GameEntity {
    /// A unique identifier for the entity, if available (e.g., from game memory or network).
    pub id: u64,
    /// The name of the entity as displayed in the game or known internally.
    pub name: String,
    /// The type of the entity (e.g., Player, Monster, Npc).
    pub entity_type: EntityType,
    /// The entity's current position in the game world.
    pub position: Coordinate,
    /// The entity's current health percentage (0-100), if known.
    pub health_percent: Option<u8>,
    /// Indicates if the entity is considered hostile towards the player.
    pub is_hostile: Option<bool>,
    /// Indicates if the entity is currently attacking the player.
    pub is_attacking_player: Option<bool>,
    /// Indicates if the entity is currently targeted by the player.
    pub is_targeted_by_player: Option<bool>,
}

/// Represents an item in the game, typically within an inventory or on the ground.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct GameItem {
    /// The game's internal ID or type identifier for the item.
    pub item_id: u32,
    /// The display name of the item.
    pub name: String,
    /// The quantity of this item, if stackable.
    pub quantity: u32,
    /// The location or slot where the item is currently stored, if applicable.
    /// Examples: "backpack_slot_1", "hand_left", "equipment_head".
    pub inventory_slot: Option<String>,
}

/// Represents the player's inventory, containing items and capacity information.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct Inventory {
    /// A list of items currently in the player's inventory.
    pub items: Vec<GameItem>,
    /// The carrying capacity of the player, if known (e.g., weight, slots).
    pub capacity: Option<u32>,
}

/// Represents the player's current attack target, simplified for quick access.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct AttackTarget {
    /// Unique ID of the targeted entity.
    pub id: u64,
    /// Name of the targeted entity.
    pub name: String,
    /// Health percentage (0-100) of the targeted entity.
    /// Assumed to be always available when an entity is a valid attack target.
    pub health_percent: u8,
}

/// The main aggregate struct holding the overall perceived game state.
///
/// This struct consolidates all known information about the game world,
/// player status, entities, inventory, etc. It provides methods to update
/// and query this information.
#[derive(Debug, Clone, PartialEq, Default)]
// #[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
pub struct MainGameState {
    /// Current status of the player (health, mana, position, etc.).
    pub player_status: Option<PlayerStatus>,
    /// The player's current attack target, if any.
    pub current_target: Option<AttackTarget>,
    /// List of entities currently visible or relevant to the player.
    pub visible_entities: Vec<GameEntity>,
    /// The player's inventory status.
    pub inventory: Option<Inventory>,
    /// Timestamp of the last update to any part of the game state, in milliseconds since UNIX epoch.
    /// Can be used to determine the freshness of the state.
    pub last_update_timestamp_ms: Option<u64>,
    /// Indicates whether the player is currently considered to be in combat.
    pub is_in_combat: Option<bool>,
    /// The name or identifier of the current map or zone the player is in.
    pub current_map_name: Option<String>,
}

impl MainGameState {
    /// Creates a new, default/empty game state.
    /// All fields are initialized to their default values (e.g., `None` for `Option` types, empty `Vec`).
    /// The `last_update_timestamp_ms` is initialized to `None`.
    pub fn new() -> Self {
        MainGameState::default()
    }

    // --- Update Methods ---

    /// Updates the player's status information.
    /// This replaces any existing player status.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `status` - The new `PlayerStatus` to set.
    pub fn update_player_status(&mut self, status: PlayerStatus) {
        self.player_status = Some(status);
        self.set_last_update_timestamp();
    }

    /// Clears the player's status information, setting it to `None`.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    pub fn clear_player_status(&mut self) {
        self.player_status = None;
        self.set_last_update_timestamp();
    }

    /// Sets the current attack target for the player.
    /// This replaces any existing target.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `target` - The `AttackTarget` to set.
    pub fn set_current_target(&mut self, target: AttackTarget) {
        self.current_target = Some(target);
        self.set_last_update_timestamp();
    }

    /// Clears the player's current attack target, setting it to `None`.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    pub fn clear_current_target(&mut self) {
        self.current_target = None;
        self.set_last_update_timestamp();
    }

    /// Replaces the entire list of visible entities with a new list.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `entities` - A `Vec<GameEntity>` containing the new list of visible entities.
    pub fn update_visible_entities(&mut self, entities: Vec<GameEntity>) {
        self.visible_entities = entities;
        self.set_last_update_timestamp();
    }

    /// Adds or updates a single entity in the list of visible entities.
    /// If an entity with the same `id` already exists, it is replaced with the new `entity`.
    /// Otherwise, the new `entity` is added to the list.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `entity` - The `GameEntity` to add or update.
    pub fn upsert_visible_entity(&mut self, entity: GameEntity) {
        if let Some(existing_entity) = self.visible_entities.iter_mut().find(|e| e.id == entity.id) {
            *existing_entity = entity;
        } else {
            self.visible_entities.push(entity);
        }
        self.set_last_update_timestamp();
    }

    /// Removes a visible entity from the list by its ID.
    /// If an entity is removed, the `last_update_timestamp_ms` is updated.
    ///
    /// # Arguments
    /// * `entity_id` - The ID of the entity to remove.
    ///
    /// # Returns
    /// Returns `Some(GameEntity)` if an entity with the given ID was found and removed,
    /// otherwise returns `None`.
    pub fn remove_visible_entity(&mut self, entity_id: u64) -> Option<GameEntity> {
        let mut removed_entity: Option<GameEntity> = None;
        self.visible_entities.retain(|entity| {
            if entity.id == entity_id {
                removed_entity = Some(entity.clone()); // Clone to return later
                false // Remove from list
            } else {
                true // Keep in list
            }
        });
        if removed_entity.is_some() {
            self.set_last_update_timestamp();
        }
        removed_entity
    }

    /// Updates the player's inventory information.
    /// This replaces any existing inventory data.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `inventory` - The new `Inventory` to set.
    pub fn update_inventory(&mut self, inventory: Inventory) {
        self.inventory = Some(inventory);
        self.set_last_update_timestamp();
    }

    /// Sets the player's combat status.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `is_in_combat` - `true` if the player is in combat, `false` otherwise.
    pub fn set_combat_status(&mut self, is_in_combat: bool) {
        self.is_in_combat = Some(is_in_combat);
        self.set_last_update_timestamp();
    }

    /// Updates the name of the current map or zone the player is in.
    /// The `last_update_timestamp_ms` of the game state is also updated.
    ///
    /// # Arguments
    /// * `map_name` - The name of the current map.
    pub fn set_current_map_name(&mut self, map_name: String) {
        self.current_map_name = Some(map_name);
        self.set_last_update_timestamp();
    }

    /// Helper to update the timestamp when game state is modified.
    ///
    /// On non-wasm32 targets, this sets `last_update_timestamp_ms` to the current
    /// system time in milliseconds since the UNIX epoch.
    /// On wasm32 targets, this currently sets `last_update_timestamp_ms` to `None`
    /// as a placeholder, requiring platform-specific implementation for time if needed.
    fn set_last_update_timestamp(&mut self) {
        #[cfg(not(target_arch = "wasm32"))]
        {
            use std::time::{SystemTime, UNIX_EPOCH};
            self.last_update_timestamp_ms = Some(
                SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64,
            );
        }
        #[cfg(target_arch = "wasm32")]
        {
            self.last_update_timestamp_ms = None;
        }
    }

    // --- Query Methods ---

    /// Gets a reference to the player's status, if available.
    pub fn get_player_status(&self) -> Option<&PlayerStatus> {
        self.player_status.as_ref()
    }

    /// Gets a reference to the current attack target, if any.
    pub fn get_current_target(&self) -> Option<&AttackTarget> {
        self.current_target.as_ref()
    }

    /// Gets a reference to a specific visible entity by its ID, if found.
    ///
    /// # Arguments
    /// * `entity_id` - The ID of the entity to find.
    pub fn get_visible_entity_by_id(&self, entity_id: u64) -> Option<&GameEntity> {
        self.visible_entities.iter().find(|e| e.id == entity_id)
    }

    /// Gets a reference to the list of all currently visible entities.
    pub fn get_all_visible_entities(&self) -> &Vec<GameEntity> {
        &self.visible_entities
    }

    /// Gets a reference to the player's inventory, if available.
    pub fn get_inventory(&self) -> Option<&Inventory> {
        self.inventory.as_ref()
    }

    /// Gets the player's combat status, if set.
    pub fn get_combat_status(&self) -> Option<bool> {
        self.is_in_combat
    }

    /// Gets a reference to the current map name, if set.
    pub fn get_current_map_name(&self) -> Option<&String> {
        self.current_map_name.as_ref()
    }

    /// Gets the last update timestamp in milliseconds, if set.
    /// This indicates when any part of the game state was last modified.
    pub fn get_last_update_timestamp_ms(&self) -> Option<u64> {
        self.last_update_timestamp_ms
    }
}

#[cfg(test)]
mod tests {
    use super::*; // Imports MainGameState, PlayerStatus, etc.

    #[test]
    fn test_new_game_state() {
        let state = MainGameState::new();
        assert_eq!(state, MainGameState::default(), "New state should be default");
        assert!(state.player_status.is_none());
        assert!(state.current_target.is_none());
        assert!(state.visible_entities.is_empty());
        assert!(state.inventory.is_none());
        assert!(state.is_in_combat.is_none());
        assert!(state.current_map_name.is_none());

        // For new state from default(), timestamp is initially None.
        assert!(state.last_update_timestamp_ms.is_none(), "Timestamp should be None on new/default state for all targets");
    }

    #[test]
    fn test_update_and_get_player_status() {
        let mut state = MainGameState::new();
        let status = PlayerStatus {
            health: 100,
            max_health: 150,
            mana: 50,
            max_mana: 75,
            position: Some(Coordinate { x: 1, y: 2, z: 0 }),
            ..Default::default()
        };
        state.update_player_status(status.clone());

        assert_eq!(state.get_player_status(), Some(&status));
        #[cfg(not(target_arch = "wasm32"))]
        assert!(state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(state.last_update_timestamp_ms.is_none()); // Stays None for wasm

        state.clear_player_status();
        assert!(state.get_player_status().is_none());
    }

    #[test]
    fn test_set_and_get_current_target() {
        let mut state = MainGameState::new();
        let target = AttackTarget {
            id: 123,
            name: "Goblin".to_string(),
            health_percent: 80,
        };
        state.set_current_target(target.clone());
        assert_eq!(state.get_current_target(), Some(&target));
        #[cfg(not(target_arch = "wasm32"))]
        assert!(state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(state.last_update_timestamp_ms.is_none());


        state.clear_current_target();
        assert!(state.get_current_target().is_none());
    }

    #[test]
    fn test_visible_entities_management() {
        let mut state = MainGameState::new();
        let entity1 = GameEntity { id: 1, name: "Wolf".to_string(), ..Default::default() };
        let entity2 = GameEntity { id: 2, name: "Boar".to_string(), ..Default::default() };

        state.update_visible_entities(vec![entity1.clone(), entity2.clone()]);
        assert_eq!(state.get_all_visible_entities().len(), 2);
        assert_eq!(state.get_visible_entity_by_id(1), Some(&entity1));

        let entity1_updated = GameEntity { id: 1, name: "Dire Wolf".to_string(), health_percent: Some(50), ..Default::default() };
        state.upsert_visible_entity(entity1_updated.clone());
        assert_eq!(state.get_all_visible_entities().len(), 2);
        assert_eq!(state.get_visible_entity_by_id(1).unwrap().name, "Dire Wolf");
        assert_eq!(state.get_visible_entity_by_id(1).unwrap().health_percent, Some(50));

        let entity3 = GameEntity { id: 3, name: "Bat".to_string(), ..Default::default() };
        state.upsert_visible_entity(entity3.clone());
        assert_eq!(state.get_all_visible_entities().len(), 3);

        let removed_entity = state.remove_visible_entity(2);
        assert_eq!(removed_entity, Some(entity2)); // Check the correct entity was removed
        assert_eq!(state.get_all_visible_entities().len(), 2);
        assert!(state.get_visible_entity_by_id(2).is_none());

        let non_existent_removed = state.remove_visible_entity(999); // Try removing non-existent
        assert!(non_existent_removed.is_none());
        assert_eq!(state.get_all_visible_entities().len(), 2); // Count should be unchanged
    }

    #[test]
    fn test_update_and_get_inventory() {
        let mut state = MainGameState::new();
        let item1 = GameItem { item_id: 101, name: "Health Potion".to_string(), quantity: 5, ..Default::default() };
        let inventory = Inventory { items: vec![item1.clone()], capacity: Some(20) };

        state.update_inventory(inventory.clone());
        assert_eq!(state.get_inventory(), Some(&inventory));
        #[cfg(not(target_arch = "wasm32"))]
        assert!(state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(state.last_update_timestamp_ms.is_none());
    }

    #[test]
    fn test_set_and_get_combat_status() {
        let mut state = MainGameState::new();
        state.set_combat_status(true);
        assert_eq!(state.get_combat_status(), Some(true));
        #[cfg(not(target_arch = "wasm32"))]
        assert!(state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(state.last_update_timestamp_ms.is_none());
    }

    #[test]
    fn test_set_and_get_map_name() {
        let mut state = MainGameState::new();
        let map_name = "Starting Woods".to_string();
        state.set_current_map_name(map_name.clone());
        assert_eq!(state.get_current_map_name(), Some(&map_name));
        #[cfg(not(target_arch = "wasm32"))]
        assert!(state.last_update_timestamp_ms.is_some());
        #[cfg(target_arch = "wasm32")]
        assert!(state.last_update_timestamp_ms.is_none());
    }

    #[test]
    fn test_timestamp_updates_on_modification() {
        let mut state = MainGameState::new();
        assert!(state.get_last_update_timestamp_ms().is_none(), "Initial timestamp should be None for default state");

        state.set_combat_status(true); // Perform an update

        #[cfg(not(target_arch = "wasm32"))]
        {
            assert!(state.get_last_update_timestamp_ms().is_some(), "Timestamp should be Some on non-wasm after modification");
        }
        #[cfg(target_arch = "wasm32")]
        {
            assert!(state.get_last_update_timestamp_ms().is_none(), "Timestamp should remain None on wasm after update (current impl)");
        }
    }
}
