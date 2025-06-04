//! Provides functions for simulating keyboard and mouse input using the `enigo` crate.
//!
//! Each function that performs an input action typically creates a new `Enigo` instance.
//! Errors during Enigo initialization or during the input simulation are mapped to
//! `InputError::SimulationError`.

use crate::error::InputError;
use enigo::{Enigo, Key as EnigoKey, MouseButton as EnigoMouseButton, Keyboard, Mouse, Settings as EnigoSettings, Coordinate};
// use std::sync::Mutex; // Currently unused, can be re-added if a shared Enigo instance is implemented

// Use lazy_static or once_cell for a global Enigo instance.
// For this subtask, to keep dependencies minimal for skb_input for now,
// we will create an Enigo instance per call. This might be less efficient
// if rapidly calling input functions. A shared instance would be an optimization.
// However, Enigo::new() can fail, so we need to handle that.

/// Helper function to create a new Enigo instance.
/// Not public as action functions encapsulate its use.
fn get_enigo_instance() -> Result<Enigo, InputError> {
    Enigo::new(&EnigoSettings::default())
        .map_err(|e| InputError::SimulationError(format!("Failed to initialize Enigo: {}", e)))
}

// --- Keyboard Actions ---

/// Sends a key event (press or release) for the specified key.
///
/// # Arguments
/// * `key` - The `EnigoKey` (re-exported from `enigo` by `skb_input::lib`) to simulate.
/// * `is_press` - `true` for a key press, `false` for a key release.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn send_key_event(key: EnigoKey, is_press: bool) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    if is_press {
        enigo.key(key, enigo::Direction::Press)
            .map_err(|e| InputError::SimulationError(format!("Failed to press key {:?}: {}", key, e)))?;
    } else {
        enigo.key(key, enigo::Direction::Release)
            .map_err(|e| InputError::SimulationError(format!("Failed to release key {:?}: {}", key, e)))?;
    }
    Ok(())
}

/// Types the given text string.
///
/// This function simulates individual key presses and releases for each character in the text.
/// Note: Behavior for special characters, unicode, or complex scripts can be platform-dependent
/// and might not be perfectly simulated by `enigo`'s `text` method. For precise control over
/// complex sequences, consider using `send_key_event` for individual keys.
///
/// # Arguments
/// * `text` - The string to type.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn type_text(text: &str) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    // enigo.text() is a convenience that handles individual key presses/releases for chars.
    // It may not support all special characters or unicode sequences perfectly on all platforms via this method.
    // For more complex text or specific character control, manual key event sequences might be needed.
    enigo.text(text)
        .map_err(|e| InputError::SimulationError(format!("Failed to type text: {}", e)))?;
    Ok(())
}

// --- Mouse Actions ---

/// Moves the mouse cursor to the specified absolute screen coordinates.
///
/// # Arguments
/// * `x` - The absolute x-coordinate on the screen.
/// * `y` - The absolute y-coordinate on the screen.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn move_mouse_abs(x: i32, y: i32) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    enigo.move_mouse(x, y, Coordinate::Abs)
        .map_err(|e| InputError::SimulationError(format!("Failed to move mouse to ({}, {}): {}", x, y, e)))?;
    Ok(())
}

/// Moves the mouse cursor relative to its current position.
///
/// # Arguments
/// * `dx` - The change in the x-coordinate (pixels to move horizontally).
/// * `dy` - The change in the y-coordinate (pixels to move vertically).
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn move_mouse_rel(dx: i32, dy: i32) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    enigo.move_mouse(dx, dy, Coordinate::Rel)
        .map_err(|e| InputError::SimulationError(format!("Failed to move mouse by ({}, {}): {}", dx, dy, e)))?;
    Ok(())
}

/// Sends a mouse button event (press or release) for the specified button.
///
/// # Arguments
/// * `button` - The `EnigoMouseButton` (re-exported from `enigo` by `skb_input::lib`) to simulate.
/// * `is_press` - `true` for a button press, `false` for a button release.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn send_mouse_button_event(button: EnigoMouseButton, is_press: bool) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    if is_press {
        enigo.button(button, enigo::Direction::Press)
            .map_err(|e| InputError::SimulationError(format!("Failed to press mouse button {:?}: {}", button, e)))?;
    } else {
        enigo.button(button, enigo::Direction::Release)
            .map_err(|e| InputError::SimulationError(format!("Failed to release mouse button {:?}: {}", button, e)))?;
    }
    Ok(())
}

/// Simulates a click (press followed by release) of the specified mouse button.
///
/// # Arguments
/// * `button` - The `EnigoMouseButton` (re-exported from `enigo` by `skb_input::lib`) to click.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn click_mouse(button: EnigoMouseButton) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    // Enigo's `click` method combines press and release.
    enigo.click(button)
        .map_err(|e| InputError::SimulationError(format!("Failed to click mouse button {:?}: {}", button, e)))?;
    Ok(())
}

/// Scrolls the mouse wheel.
///
/// The scroll amounts are relative. Positive `y_amount` usually scrolls down,
/// positive `x_amount` usually scrolls right, but behavior can be OS/application dependent.
///
/// # Arguments
/// * `x_amount` - The amount to scroll horizontally.
/// * `y_amount` - The amount to scroll vertically.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn scroll_mouse_wheel(x_amount: i32, y_amount: i32) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    enigo.scroll(x_amount, y_amount, Coordinate::Rel) // Assuming scroll is relative
         .map_err(|e| InputError::SimulationError(format!("Failed to scroll mouse wheel by ({},{}): {}", x_amount, y_amount, e)))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    // Re-import EnigoKey and EnigoMouseButton if they are not already in super's scope
    // or qualify them, e.g. enigo::Key::A.
    // The lib.rs re-exports them, but actions.rs itself might not have them directly in scope.
    // For simplicity in this test module, let's assume we can access them.
    // If not, we'd use crate::EnigoKey or similar.
    // Let's use the direct enigo types here as our functions take them.
    use enigo::{Key as EnigoKeyTest, MouseButton as EnigoMouseButtonTest}; // Renamed to avoid conflict if EnigoKey/MouseButton are brought into scope by `use super::*` already. Or, just use super::EnigoKey.
                                                                    // Actually, the functions take EnigoKey and EnigoMouseButton which are already aliased in the outer scope.
                                                                    // So, direct use of EnigoKey, EnigoMouseButton should be fine.

    // Test for Enigo instance creation
    #[test]
    fn test_get_enigo_instance_smoke() {
        // This test might fail on headless CI servers if Enigo::new() needs a display.
        // If it does, this test might need to be cfg'd out for such environments.
        match get_enigo_instance() {
            Ok(_) => println!("Enigo instance created successfully (or would be)."),
            Err(e) => {
                // Allow specific error if no display, otherwise panic
                let err_msg = e.to_string();
                if err_msg.contains("Failed to initialize Enigo") && (err_msg.contains("Wayland") || err_msg.contains("X11") || err_msg.contains("windows") || err_msg.contains("macos") || err_msg.contains("Cannot connect to server") || err_msg.contains("No protocol specified")) {
                    // This error is common in headless environments. Consider it a pass for smoke test.
                    // Or use #[ignore] for this test in CI.
                    println!("Enigo instantiation failed as expected in headless environment: {}", e);
                } else {
                    panic!("get_enigo_instance failed unexpectedly: {}", e);
                }
            }
        }
    }

    // Smoke tests for each public input function
    // These primarily check that the function call completes without panic
    // and returns Ok. They don't verify actual input simulation.

    #[test]
    fn test_send_key_event_smoke() {
        // This test will likely fail if no display server is available (e.g., on CI)
        // because get_enigo_instance() will fail.
        // Consider #[ignore] for CI or conditional compilation.
        if get_enigo_instance().is_err() {
            println!("Skipping test_send_key_event_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(send_key_event(EnigoKey::A, true).is_ok());
        assert!(send_key_event(EnigoKey::A, false).is_ok());
    }

    #[test]
    fn test_type_text_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_type_text_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(type_text("hello").is_ok());
    }

    #[test]
    fn test_move_mouse_abs_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_move_mouse_abs_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(move_mouse_abs(10, 10).is_ok());
    }

    #[test]
    fn test_move_mouse_rel_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_move_mouse_rel_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(move_mouse_rel(5, 5).is_ok());
    }

    #[test]
    fn test_send_mouse_button_event_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_send_mouse_button_event_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(send_mouse_button_event(EnigoMouseButton::Left, true).is_ok());
        assert!(send_mouse_button_event(EnigoMouseButton::Left, false).is_ok());
    }

    #[test]
    fn test_click_mouse_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_click_mouse_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(click_mouse(EnigoMouseButton::Right).is_ok());
    }

    #[test]
    fn test_scroll_mouse_wheel_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_scroll_mouse_wheel_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(scroll_mouse_wheel(0, 1).is_ok()); // Scroll down
        assert!(scroll_mouse_wheel(1, 0).is_ok()); // Scroll right
    }
}
