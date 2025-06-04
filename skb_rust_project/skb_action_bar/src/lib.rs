//! `skb_action_bar` - A Rust crate for representing and managing the state of in-game action bars.
//!
//! This crate provides data structures to hold information about individual action slots,
//! their content (which can be spells or items), cooldown status, and other relevant details.
//! The [`ActionBarManager`] struct is the primary interface for updating and querying the
//! collective state of all monitored action bar slots.
//!
//! This crate is intended to be used by perception modules (which would update the state
//! based on screen analysis) and by gameplay logic modules (which would query the state
//! to make decisions, such as whether a spell can be cast or an item used).
//!
//! # Main Components
//! - [`ActionBarManager`]: The central manager for storing and providing access to action bar state.
//! - [`ActionSlot`]: Represents a single slot on an action bar, including its content and status.
//! - [`SlotContentType`]: An enum describing what a slot contains (e.g., `Empty`, `Spell`, `Item`).
//! - [`ActionBarError`]: Defines errors specific to action bar operations within this crate.
//!
//! # Basic Usage
//! ```
//! use skb_action_bar::{ActionBarManager, ActionSlot, SlotContentType, ActionBarError};
//!
//! fn main() -> Result<(), ActionBarError> { // Using ActionBarError for example simplicity
//!     let mut manager = ActionBarManager::new();
//!
//!     // Simulate an update from a perception module
//!     let slot_f1_data = ActionSlot {
//!         slot_key_designator: "F1".to_string(),
//!         content: SlotContentType::Spell { spell_id: "Fireball".to_string() },
//!         is_on_cooldown: false,
//!         cooldown_remaining_ms: None,
//!         is_active: Some(false),
//!         last_observed_image_hash: Some("hash123".to_string()),
//!     };
//!     manager.update_slot(slot_f1_data);
//!
//!     // Gameplay logic queries the manager
//!     if let Some(slot) = manager.get_slot("F1") {
//!         if !slot.is_on_cooldown {
//!             if let SlotContentType::Spell { spell_id } = &slot.content {
//!                 println!("Slot F1 contains spell '{}' and it's ready!", spell_id);
//!                 // Gameplay logic might decide to use "Fireball"
//!             }
//!         }
//!     }
//!
//!     // Check cooldown for a specific spell
//!     match manager.is_spell_on_cooldown("Fireball") {
//!         Some(true) => println!("Fireball is on cooldown."),
//!         Some(false) => println!("Fireball is ready."),
//!         None => println!("Fireball spell not found on action bar."),
//!     }
//!     Ok(())
//! }
//! ```

pub mod error;
pub use error::ActionBarError;

pub mod types;
pub use types::{ActionSlot, ActionBarState, SlotContentType};

pub mod manager;
pub use manager::ActionBarManager;

// TODO: FFI Exposure (PyO3)
// The `ActionBarManager` and its associated data types (`ActionSlot`, `ActionBarState`,
// `SlotContentType`) may need to be exposed to Python. This would allow Python code
// (e.g., UI, scripting layer, or main bot orchestrator) to:
//  - Read the current state of the action bar.
//  - Potentially receive updates or subscribe to changes (more advanced).
//  - (Less likely for this crate, but possible) Trigger updates to the action bar state
//    if some state is determined or configured from Python.
//
// This would likely involve:
// 1. Adding `pyo3` to Cargo.toml dependencies (with `macros` feature for this crate).
// 2. Making `ActionSlot`, `ActionBarState`, `SlotContentType` (and its inner data if any)
//    `#[pyclass]`es. This requires them to be `Clone` (which they are).
//    - For enums like `SlotContentType`, specific handling for PyO3 might be needed
//      (e.g., converting to/from Python strings or dicts, or making the enum itself a `#[pyclass]`).
// 3. Creating a `#[pyclass]` wrapper for `ActionBarManager`, perhaps named `PyActionBarManager`.
//    - This wrapper would likely hold an `Arc<RwLock<ActionBarManager>>` to allow shared,
//      mutable access from Python if methods modify the state (our current manager methods take `&mut self`).
//      If only read access is needed from Python, `Arc<ActionBarManager>` might suffice if manager methods become `&self`.
//    - Exposing methods like `get_slot_py`, `get_all_slots_py`, `is_spell_on_cooldown_py` via `#[pymethods]`.
//      These would need to handle conversion of Rust types to Python types (e.g., `Vec<ActionSlot>` to `PyList`).
// 4. Error Handling: `ActionBarError` would need to be converted to appropriate Python exceptions.
// 5. Defining a PyO3 module (e.g., `skb_action_bar_py`) to register these classes.
//
// Example (conceptual for exposing ActionBarManager for reading):
/*
use pyo3::prelude::*;
use std::sync::Arc;
use parking_lot::RwLock; // Or std::sync::RwLock

// Assume ActionSlot, SlotContentType are also #[pyclass]
// use crate::types::{ActionSlot as RustActionSlot, SlotContentType as RustSlotContentType};


#[pyclass(name = "ActionBarManager")]
struct PyActionBarManager {
    // ActionBarManager methods take &mut self, so it needs to be behind a RwLock/Mutex
    // for shared access from Python.
    manager: Arc<RwLock<ActionBarManager>>,
}

#[pymethods]
impl PyActionBarManager {
    #[new]
    fn new() -> Self {
        PyActionBarManager {
            manager: Arc::new(RwLock::new(ActionBarManager::new())),
        }
    }

    fn get_slot_py(&self, slot_key_designator: String) -> PyResult<Option<ActionSlot>> {
        let manager = self.manager.read(); // Or .lock() for Mutex
        // .cloned() is important as we can't hold a reference across FFI boundary easily
        // if the ActionSlot is not a PyClass itself that Python can own.
        // If ActionSlot is a PyClass, we might return it directly.
        Ok(manager.get_slot(&slot_key_designator).cloned())
    }

    fn get_all_slots_py(&self, py: Python) -> PyResult<PyObject> {
        let manager = self.manager.read();
        // Convert Vec<ActionSlot> to a Python list of PyActionSlot objects
        let py_slots = manager.get_all_slots().iter().map(|slot| {
            // Assuming ActionSlot has a #[pyclass] and can be converted to Py<ActionSlot>
            // Py::new(py, slot.clone()).unwrap().into_py(py)
            // For simplicity, if ActionSlot is not a PyClass directly passed:
            format!("{:?}", slot) // Or convert to PyDict
        }).collect::<Vec<_>>();
        Ok(pyo3::types::PyList::new(py, &py_slots).into())
    }

    // Add other methods like is_spell_on_cooldown_py, etc.
}

#[pymodule]
fn skb_action_bar_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyActionBarManager>()?;
    m.add_class::<ActionSlot>()?; // If ActionSlot is made a PyClass
    m.add_class::<SlotContentType>()?; // If SlotContentType is made a PyClass (or handled differently)
    Ok(())
}
*/
