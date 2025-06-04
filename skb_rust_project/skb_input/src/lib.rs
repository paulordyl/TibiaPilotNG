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
//! use skb_input::{move_mouse_abs, click_mouse, EnigoMouseButtonRust, InputError, EnigoKeyRust, send_key_event, type_text};
//!
//! fn main() -> Result<(), InputError> {
//!     // Move mouse to absolute coordinates (100, 100)
//!     move_mouse_abs(100, 100)?;
//!
//!     // Click the left mouse button
//!     click_mouse(EnigoMouseButtonRust::Left)?;
//!
//!     // Press the 'Space' key (example of a non-layout key)
//!     send_key_event(EnigoKeyRust::Space, true)?;
//!     send_key_event(EnigoKeyRust::Space, false)?;
//!
//!     // Type some text
//!     type_text("Hello, world! 123")?;
//!
//!     Ok(())
//! }
//! ```
//!
//! # Re-exports
//! For convenience, this crate re-exports key types from `enigo`:
//! - [`EnigoKeyRust`]: Represents keyboard keys. (Aliased from `enigo::Key`)
//! - [`EnigoMouseButtonRust`]: Represents mouse buttons. (Aliased from `enigo::Button`)

pub mod error;
pub use error::InputError;

pub mod actions;
// Re-export specific functions for easier Rust use.
// Documentation for these functions can be found in the `actions` module.
pub use actions::{
    send_key_event, type_text,
    move_mouse_abs, move_mouse_rel,
    send_mouse_button_event, click_mouse,
    scroll_mouse_wheel
};

// Corrected re-exports for Rust API for enigo 0.2.0
pub use enigo::{Key as EnigoKeyRust, Button as EnigoMouseButtonRust};


// --- PyO3 FFI Layer ---
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::wrap_pyfunction;

// Corrected internal aliases for enigo 0.2.0
use enigo::{Key as EnigoKeyInternal, Button as EnigoMouseButtonInternal};


// Helper function for String to EnigoKey conversion (Revised for enigo 0.2.1 special keys)
// Alphanumeric characters should be sent via type_text_py.
fn string_to_enigo_key(key_str: &str) -> Result<EnigoKeyInternal, InputError> {
    match key_str.to_lowercase().as_str() {
        // Function keys
        "f1" => Ok(EnigoKeyInternal::F1), "f2" => Ok(EnigoKeyInternal::F2), "f3" => Ok(EnigoKeyInternal::F3),
        "f4" => Ok(EnigoKeyInternal::F4), "f5" => Ok(EnigoKeyInternal::F5), "f6" => Ok(EnigoKeyInternal::F6),
        "f7" => Ok(EnigoKeyInternal::F7), "f8" => Ok(EnigoKeyInternal::F8), "f9" => Ok(EnigoKeyInternal::F9),
        "f10" => Ok(EnigoKeyInternal::F10), "f11" => Ok(EnigoKeyInternal::F11), "f12" => Ok(EnigoKeyInternal::F12),

        // Control and special keys
        "space" | " " => Ok(EnigoKeyInternal::Space),
        "enter" | "return" => Ok(EnigoKeyInternal::Return),
        "ctrl" | "control" | "lcontrol" | "lctrl" | "rcontrol" | "rctrl" => Ok(EnigoKeyInternal::Control),
        "alt" | "lalt" | "ralt" => Ok(EnigoKeyInternal::Alt),
        "shift" | "lshift" | "rshift" => Ok(EnigoKeyInternal::Shift),
        "tab" => Ok(EnigoKeyInternal::Tab),
        "escape" | "esc" => Ok(EnigoKeyInternal::Escape),
        "up" | "uparrow" => Ok(EnigoKeyInternal::UpArrow),
        "down" | "downarrow" => Ok(EnigoKeyInternal::DownArrow),
        "left" | "leftarrow" => Ok(EnigoKeyInternal::LeftArrow),
        "right" | "rightarrow" => Ok(EnigoKeyInternal::RightArrow),
        "backspace" => Ok(EnigoKeyInternal::Backspace),
        "capslock" | "caps_lock" => Ok(EnigoKeyInternal::CapsLock),
        "delete" => Ok(EnigoKeyInternal::Delete),
        "end" => Ok(EnigoKeyInternal::End),
        "home" => Ok(EnigoKeyInternal::Home),
        "insert" => Ok(EnigoKeyInternal::Insert),
        "pagedown" | "page_down" | "pgdn" => Ok(EnigoKeyInternal::PageDown),
        "pageup" | "page_up" | "pgup" => Ok(EnigoKeyInternal::PageUp),
        "meta" | "windows" | "command" | "super" | "lmeta" | "rmeta" => Ok(EnigoKeyInternal::Meta),

        // Alphanumeric and Numpad keys are intentionally omitted. Use type_text_py for them.
        // This function is for special keys that don't produce characters directly or for modifiers.
        _ => Err(InputError::UnsupportedAction(format!("Unsupported special key string for send_key_event: '{}'. For typing characters or numbers, use type_text_py.", key_str))),
    }
}

// Helper function for String to EnigoMouseButton conversion
fn string_to_enigo_mouse_button(button_str: &str) -> Result<EnigoMouseButtonInternal, InputError> {
    match button_str.to_lowercase().as_str() {
        "left" => Ok(EnigoMouseButtonInternal::Left),
        "right" => Ok(EnigoMouseButtonInternal::Right),
        "middle" => Ok(EnigoMouseButtonInternal::Middle),
        _ => Err(InputError::UnsupportedAction(format!("Unsupported mouse button string: {}", button_str))),
    }
}

/// Simulates a key event (press or release) for a special (non-character) key.
/// For typing strings of characters (a-z, 0-9, symbols), use `type_text_py`.
///
/// # Arguments
/// * `key_str` - A string representing the special key (e.g., "f1", "space", "enter", "ctrl").
/// * `is_press` - `true` for a key press, `false` for a key release.
#[pyfunction]
fn send_key_event_py(key_str: String, is_press: bool) -> PyResult<()> {
    let enigo_key = string_to_enigo_key(&key_str)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    actions::send_key_event(enigo_key, is_press)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// Types the given text string. This is suitable for alphanumeric characters and symbols.
#[pyfunction]
fn type_text_py(text: String) -> PyResult<()> {
    actions::type_text(&text)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pyfunction]
fn move_mouse_abs_py(x: i32, y: i32) -> PyResult<()> {
    actions::move_mouse_abs(x, y)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pyfunction]
fn move_mouse_rel_py(dx: i32, dy: i32) -> PyResult<()> {
    actions::move_mouse_rel(dx, dy)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pyfunction]
fn send_mouse_button_event_py(button_str: String, is_press: bool) -> PyResult<()> {
    let enigo_button = string_to_enigo_mouse_button(&button_str)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    actions::send_mouse_button_event(enigo_button, is_press)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pyfunction]
fn click_mouse_py(button_str: String) -> PyResult<()> {
    let enigo_button = string_to_enigo_mouse_button(&button_str)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    actions::click_mouse(enigo_button)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

#[pyfunction]
fn scroll_mouse_wheel_py(x_amount: i32, y_amount: i32) -> PyResult<()> {
    actions::scroll_mouse_wheel(x_amount, y_amount)
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))
}

/// A Python module implemented in Rust, providing input simulation functions.
/// This module is named `skb_input_rust` when imported in Python.
#[pymodule]
#[pyo3(name = "skb_input_rust")]
fn skb_input_py_module(_py: Python, m: &PyModule) -> PyResult<()> { // Changed to &PyModule
    m.add_function(wrap_pyfunction!(send_key_event_py, m)?)?;
    m.add_function(wrap_pyfunction!(type_text_py, m)?)?;
    m.add_function(wrap_pyfunction!(move_mouse_abs_py, m)?)?;
    m.add_function(wrap_pyfunction!(move_mouse_rel_py, m)?)?;
    m.add_function(wrap_pyfunction!(send_mouse_button_event_py, m)?)?;
    m.add_function(wrap_pyfunction!(click_mouse_py, m)?)?;
    m.add_function(wrap_pyfunction!(scroll_mouse_wheel_py, m)?)?;

    Ok(())
}
