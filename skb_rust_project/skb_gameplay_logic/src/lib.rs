//! `skb_gameplay_logic` - The decision-making core of the SKB bot.
//!
//! This crate consumes game state information (from `skb_game_state`) and
//! orchestrates actions (via `skb_input` and potentially other action modules)
//! to achieve bot objectives like survival (healing), combat, and task completion (e.g., looting).
//!
//! # Main Components
//! - [`GameplayLogicManager`]: The central orchestrator. Its `tick()` method is called repeatedly
//!   to process the current game state and execute logic.
//! - `healing`: Module responsible for player survival logic, primarily healing actions.
//! - `combat`: Module for handling targeting, attack sequences, and other combat decisions.
//! - `looting`: Placeholder module for future item looting logic.
//! - `error`: Defines [`GameplayError`] for handling errors specific to this crate, including
//!   those propagated from `skb_game_state` and `skb_input`.
//!
//! # Basic Usage
//! ```no_run
//! use skb_gameplay_logic::{GameplayLogicManager, GameplayError};
//! use skb_game_state::MainGameState; // Assumes MainGameState is populated by a perception system.
//! // Assume skb_utils and skb_config are initialized elsewhere for logging and config access.
//!
//! fn main() -> Result<(), GameplayError> {
//!     // Initialize the main logic manager.
//!     let logic_manager = GameplayLogicManager::new();
//!
//!     // Game loop (conceptual)
//!     loop {
//!         // 1. Acquire the current game state (e.g., from a perception module).
//!         let current_game_state = MainGameState::new(); // Placeholder, should be updated.
//!         //    ... populate current_game_state based on actual game ...
//!
//!         // 2. Execute a logic tick.
//!         match logic_manager.tick(&current_game_state) {
//!             Ok(_) => log::debug!("Gameplay tick successful."),
//!             Err(e) => {
//!                 log::error!("Gameplay error during tick: {}", e);
//!                 // Handle error, e.g., pause bot, notify user, etc.
//!             }
//!         }
//!
//!         // 3. Add delay or synchronization for the next tick.
//!         // std::thread::sleep(std::time::Duration::from_millis(100)); // Example delay
//! #       break; // Example to make test pass
//!     }
//!     Ok(())
//! }
//! ```

pub mod error;
pub use error::GameplayError;

pub mod manager;
pub use manager::GameplayLogicManager; // Re-export the manager

// Declare other logic modules that will be called by the manager
pub mod healing;
pub mod combat;
pub mod looting; // looting.rs was created, so this should be declared

// TODO: FFI Exposure (PyO3)
// The `GameplayLogicManager` and its core `tick()` method, along with potential
// configuration settings, might need to be exposed to Python. This would allow
// a Python-based main application or UI to control the bot's logic execution
// (e.g., start/stop, pause/resume) and potentially configure its parameters.
//
// This would likely involve:
// 1. Adding `pyo3` to Cargo.toml dependencies (with `macros` feature).
// 2. Creating a PyO3 wrapper class for `GameplayLogicManager`:
//    - `#[pyclass] struct PyGameplayLogicManager { manager: Arc<Mutex<GameplayLogicManager>> }`
//      (Using Arc<Mutex<>> or Arc<RwLock<>> if the manager needs to be shared
//      or called from multiple Python threads, or if its methods take &mut self).
//      If `tick` takes `&self` and `GameplayLogicManager` is `Send + Sync` (or can be made so),
//      direct wrapping might be simpler if Python side is single-threaded for calls.
//    - `#[pymethods]` block for `PyGameplayLogicManager` to expose:
//        - A constructor (`#[new]`).
//        - A `tick_py(&self, py_game_state: PyGameState) -> PyResult<()>` method that would
//          take a Python wrapper of `MainGameState` (requiring `MainGameState` to also be a `#[pyclass]`),
//          convert it to the Rust `MainGameState`, call the Rust `manager.tick()`,
//          and handle error conversion from `GameplayError` to `PyErr`.
//        - Methods to update configuration if gameplay parameters are to be set from Python.
// 3. Ensuring `MainGameState` (from `skb_game_state`) is also a `#[pyclass]` if it's to be passed
//    between Python and Rust for the `tick()` method.
// 4. Error handling: `GameplayError` would need to be convertible to Python exceptions.
// 5. Defining the pymodule itself, e.g., `skb_gameplay_logic_py(_py: Python, m: &PyModule)`.
//
// Example (conceptual for the manager wrapper):
/*
use pyo3::prelude::*;
// Assuming skb_game_state::MainGameState is already a PyClass as PyMainGameState
// use skb_game_state::MainGameState as RustMainGameState;


#[pyclass(name = "GameplayLogicManager")]
struct PyGameplayLogicManager {
    // Assuming GameplayLogicManager itself doesn't need to be mutable after creation,
    // or mutations are handled internally and it's Send+Sync.
    // If GameplayLogicManager::tick took &mut self, or if it held non-Send/Sync types
    // and needed to be called from Python, it would need a Mutex/RwLock.
    // For a simple &self tick, and if manager holds no complex state itself:
    manager: GameplayLogicManager,
}

#[pymethods]
impl PyGameplayLogicManager {
    #[new]
    fn new() -> Self {
        PyGameplayLogicManager { manager: GameplayLogicManager::new() }
    }

    // This assumes PyMainGameState can be converted into a reference to RustMainGameState.
    // This would typically mean PyMainGameState holds an Arc<RwLock<RustMainGameState>>
    // or similar, and we'd get a read lock.
    // For simplicity here, let's assume a direct reference if PyMainGameState is carefully handled.
    fn tick_py(&self, game_state_py: &skb_game_state::MainGameState) -> PyResult<()> {
        // If game_state_py is a PyCell<MainGameState>, then:
        // let rust_game_state_ref = game_state_py.borrow();
        // self.manager.tick(&*rust_game_state_ref).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))

        // Simpler if MainGameState is just passed by value and is Clone for FFI (if small enough)
        // or if it's an immutable reference from a shared Python-owned resource.
        // The exact mechanism depends on how MainGameState is exposed from skb_game_state via PyO3.
        self.manager.tick(game_state_py) // Assuming game_state_py is directly usable as &MainGameState
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }
}

#[pymodule]
fn skb_gameplay_logic_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyGameplayLogicManager>()?;
    Ok(())
}
*/
