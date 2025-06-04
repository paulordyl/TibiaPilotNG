//! `skb_input` - A Rust crate for simulating keyboard and mouse input.
//!
//! This crate provides a simple API to send key presses, type text, move the mouse cursor,
//! simulate mouse button clicks, and scroll the mouse wheel. It primarily wraps the
//! `enigo` library to provide these functionalities.
//!
//! The main goals are to offer a straightforward way to programmatically control input
//! for automation tasks, testing, or bot development, and to define a clear error type
//! (`InputError`) for operations that might fail (e.g., if the underlying input system
//! cannot be initialized).
//!
//! # Modules
//! - `error`: Defines the [`InputError`] type for this crate.
//! - `actions`: Contains functions for performing input simulations (e.g., [`send_key_event`], [`move_mouse_abs`]).
//!
//! # Basic Usage
//! ```no_run
//! use skb_input::{move_mouse_abs, click_mouse, EnigoMouseButton, InputError, EnigoKey, send_key_event, type_text};
//!
//! fn main() -> Result<(), InputError> {
//!     // Move mouse to absolute coordinates (100, 100)
//!     move_mouse_abs(100, 100)?;
//!
//!     // Click the left mouse button
//!     click_mouse(EnigoMouseButton::Left)?;
//!
//!     // Press the 'A' key
//!     send_key_event(EnigoKey::A, true)?;
//!     // Release the 'A' key
//!     send_key_event(EnigoKey::A, false)?;
//!
//!     // Type some text
//!     type_text("Hello, world!")?;
//!
//!     Ok(())
//! }
//! ```
//!
//! # Re-exports
//! For convenience, this crate re-exports key types from `enigo`:
//! - [`EnigoKey`]: Represents keyboard keys.
//! - [`EnigoMouseButton`]: Represents mouse buttons.

pub mod error;
pub use error::InputError;

pub mod actions;
// Re-export specific functions for easier use.
// Documentation for these functions can be found in the `actions` module.
pub use actions::{
    send_key_event, type_text,
    move_mouse_abs, move_mouse_rel,
    send_mouse_button_event, click_mouse,
    scroll_mouse_wheel
};

// Re-export enigo's Key and MouseButton so users of skb_input don't need a direct enigo dependency
// just to specify which key or button to use with this crate's functions.
pub use enigo::{Key as EnigoKey, MouseButton as EnigoMouseButton};

// TODO: FFI Exposure (PyO3)
// The functions in the `actions` module will need to be wrapped in
// `#[pyfunction]` blocks and exposed in a `#[pymodule]` for use by Python.
// This will likely involve:
// 1. Adding `pyo3` to Cargo.toml dependencies (with `macros` and `multiple-pymethods` features potentially).
// 2. Defining wrapper functions for each action that handle PyAny arguments
//    and convert them to Rust types (e.g., Python strings to EnigoKey, handling Python enums for keys/buttons).
// 3. Handling Python exceptions and converting them from/to InputError (e.g., using PyErr::new).
// 4. Defining the PyO3 module itself, e.g., `skb_input_module`.
/*
Example (conceptual for one function):
use pyo3::prelude::*;

#[pyfunction]
fn move_mouse_abs_py(x: i32, y: i32) -> PyResult<()> {
    // The error mapping should be more robust, potentially creating a custom Python exception type.
    actions::move_mouse_abs(x, y)
        .map_err(|e: InputError| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

#[pymodule]
fn skb_input_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(move_mouse_abs_py, m)?)?;
    // ... add other wrapped functions ...
    Ok(())
}
*/
