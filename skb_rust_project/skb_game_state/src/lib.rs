//! `skb_game_state` - A Rust crate for managing and representing the perceived state of a game.
//!
//! This crate provides data structures to hold information about the player,
//! entities, inventory, and other relevant game world aspects. It also includes
//! methods on the `MainGameState` struct to update and query this state.
//! It's designed to be used by a bot's perception and logic modules to make
//! decisions based on the current understanding of the game world.
//!
//! # Modules
//! - `error`: Defines `GameStateError` for error handling within this crate.
//! - `types`: Contains all core data structures (e.g., `MainGameState`, `PlayerStatus`, `GameEntity`).
//!
//! # Core Structures
//! The primary struct is [`MainGameState`], which acts as a container for all other
//! state information. Other key structs include:
//! - [`PlayerStatus`]: Holds information about the player's health, mana, position, etc.
//! - [`GameEntity`]: Represents monsters, NPCs, or other players.
//! - [`GameItem`]: Represents items in the game.
//! - [`Inventory`]: Holds the player's items.
//! - [`AttackTarget`]: Information about the player's current target.
//! - [`Coordinate`]: A simple 3D coordinate.
//! - [`EntityType`]: An enum categorizing game entities.
//!
//! # Basic Usage
//! ```
//! use skb_game_state::{MainGameState, PlayerStatus, Coordinate, GameEntity, EntityType};
//!
//! // Create a new, default game state
//! let mut game_state = MainGameState::new();
//!
//! // Update player status
//! let player_pos = Coordinate { x: 10, y: 20, z: 0 };
//! let status = PlayerStatus {
//!     health: 100,
//!     max_health: 100,
//!     mana: 50,
//!     max_mana: 50,
//!     position: Some(player_pos),
//!     ..Default::default()
//! };
//! game_state.update_player_status(status);
//!
//! // Add a visible entity
//! let monster = GameEntity {
//!     id: 1,
//!     name: "Goblin".to_string(),
//!     entity_type: EntityType::Monster,
//!     position: Coordinate { x: 15, y: 22, z: 0 },
//!     health_percent: Some(100),
//!     is_hostile: Some(true),
//!     ..Default::default()
//! };
//! game_state.upsert_visible_entity(monster);
//!
//! // Query the state
//! if let Some(ps) = game_state.get_player_status() {
//!     println!("Player health: {}/{}", ps.health, ps.max_health);
//! }
//! if let Some(goblin) = game_state.get_visible_entity_by_id(1) {
//!     println!("Found: {} at {:?}", goblin.name, goblin.position);
//! }
//! ```

pub mod error;
pub use error::GameStateError;

pub mod types;
pub use types::*; // Re-export all public items from the types module

// pub mod manager; // Will be added later
// pub use manager::GameStateManager; // Example

// Placeholder function removed (already done in a previous step)

// TODO: FFI Exposure (PyO3)
// The `MainGameState` and its constituent data structures might need to be
// exposed to Python for debugging, UI display, or potentially for Python-based
// game logic components to read the state.
//
// This would likely involve:
// 1. Adding `pyo3` to Cargo.toml dependencies (with `macros` feature).
// 2. Adding `#[pyclass]` attributes to `MainGameState` and other relevant structs/enums
//    in `types.rs` (e.g., `PlayerStatus`, `GameEntity`, `AttackTarget`, `GameItem`, `Inventory`).
//    This might require deriving `Clone` for types passed by value or ensuring
//    Python can handle references correctly.
// 3. For structs, `#[pymethods]` blocks would be needed to expose getter methods
//    to Python. For example, `get_player_status()` could return a PyObject
//    representing the PlayerStatus.
// 4. If Python needs to *update* the state (less common for a Rust-authoritative state),
//    specific `#[pyfunction]` wrappers for update methods might be needed, taking care
//    with Python object conversion and state consistency (e.g., using a shared,
//    thread-safe GameStateManager).
// 5. Enumerations like `EntityType` would need `#[pyclass]` or be converted to Python strings/ints.
// 6. Error handling: `GameStateError` would need to be convertible to Python exceptions.
// 7. Defining the pymodule itself, e.g., `skb_game_state_py(_py: Python, m: &PyModule)`.
//
// Example (conceptual for reading a part of the state):
/*
use pyo3::prelude::*;

// In types.rs, PlayerStatus would have #[pyclass]
// #[cfg_attr(feature = "pyo3", pyclass)]
// #[derive(Debug, Clone, PartialEq, Default)]
// pub struct PlayerStatus { ... }

// #[cfg_attr(feature = "pyo3", pymethods)]
// impl PlayerStatus {
//     #[getter]
//     fn get_health(&self) -> PyResult<u32> { Ok(self.health) }
//     // ... other getters ...
// }

// Assuming MainGameState is managed by a GameStateManager that holds Arc<RwLock<MainGameStateInternal>>
// #[pyclass]
// struct PyGameStateManager {
//     manager_instance: Arc<RwLock<MainGameStateManagerInternal>>, // or similar
// }

// #[pymethods]
// impl PyGameStateManager {
//     #[staticmethod] // Or a constructor if state is passed from Python
//     fn get_instance() -> Self { /* ... */ }
//
//     fn get_player_status_py(&self) -> PyResult<Option<PlayerStatus>> {
//         // Acquire lock, get state, clone relevant part
//         // Ok(self.manager_instance.read().unwrap().get_player_status().cloned())
//         unimplemented!()
//     }
// }

// #[pymodule]
// fn skb_game_state_py(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_class::<PlayerStatus>()?;
//     m.add_class::<PyGameStateManager>()?;
//     Ok(())
// }
*/
