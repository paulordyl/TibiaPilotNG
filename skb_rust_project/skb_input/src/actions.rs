//! Provides functions for simulating keyboard and mouse input using the `enigo` crate.
//!
//! Each function that performs an input action typically creates a new `Enigo` instance.
//! Errors during Enigo initialization or during the input simulation are mapped to
//! `InputError::SimulationError`.

use crate::error::InputError;
// Corrected imports for enigo 0.2.0
use enigo::{
    Enigo,
    Key, // Direct use of Key
    Button, // Direct use of Button
    Keyboard, // Trait for keyboard methods
    Mouse,    // Trait for mouse methods
    Settings as EnigoSettings,
    Coordinate,
    Direction, // For key/button press/release/click
    Axis       // For scroll direction
};

// Helper function to create a new Enigo instance.
/// Not public as action functions encapsulate its use.
fn get_enigo_instance() -> Result<Enigo, InputError> {
    Enigo::new(&EnigoSettings::default())
        .map_err(|e| InputError::SimulationError(format!("Failed to initialize Enigo: {}", e)))
}

// --- Keyboard Actions ---

/// Sends a key event (press or release) for the specified key.
///
/// # Arguments
/// * `key` - The `enigo::Key` to simulate.
/// * `is_press` - `true` for a key press, `false` for a key release.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn send_key_event(key: Key, is_press: bool) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    let direction = if is_press { Direction::Press } else { Direction::Release };
    enigo.key(key, direction) // Uses Keyboard trait method
        .map_err(|e| InputError::SimulationError(format!("Failed to send key_event for {:?}, direction {:?}: {}", key, direction, e)))?;
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
    enigo.text(text) // Uses Keyboard trait method
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
    enigo.move_mouse(x, y, Coordinate::Abs) // Uses Mouse trait method
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
    enigo.move_mouse(dx, dy, Coordinate::Rel) // Uses Mouse trait method
        .map_err(|e| InputError::SimulationError(format!("Failed to move mouse by ({}, {}): {}", dx, dy, e)))?;
    Ok(())
}

/// Sends a mouse button event (press or release) for the specified button.
///
/// # Arguments
/// * `button` - The `enigo::Button` to simulate.
/// * `is_press` - `true` for a button press, `false` for a button release.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn send_mouse_button_event(button: Button, is_press: bool) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    let direction = if is_press { Direction::Press } else { Direction::Release };
    enigo.button(button, direction) // Uses Mouse trait method
        .map_err(|e| InputError::SimulationError(format!("Failed to send button_event for {:?}, direction {:?}: {}", button, direction, e)))?;
    Ok(())
}

/// Simulates a click (press followed by release) of the specified mouse button.
///
/// # Arguments
/// * `button` - The `enigo::Button` to click.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails.
pub fn click_mouse(button: Button) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    enigo.button(button, Direction::Click) // Uses Mouse trait method, with Direction::Click
        .map_err(|e| InputError::SimulationError(format!("Failed to click mouse button {:?}: {}", button, e)))?;
    Ok(())
}

/// Scrolls the mouse wheel. Positive `y_amount` scrolls "down", positive `x_amount` scrolls "right".
///
/// # Arguments
/// * `x_amount` - The amount to scroll horizontally.
/// * `y_amount` - The amount to scroll vertically.
///
/// # Errors
/// Returns `InputError::SimulationError` if the Enigo instance cannot be initialized
/// or if the underlying input simulation fails for either axis.
pub fn scroll_mouse_wheel(x_amount: i32, y_amount: i32) -> Result<(), InputError> {
    let mut enigo = get_enigo_instance()?;
    if y_amount != 0 {
        enigo.scroll(y_amount, Axis::Vertical) // Uses Mouse trait method
             .map_err(|e| InputError::SimulationError(format!("Failed to scroll mouse vertically by {}: {}", y_amount, e)))?;
    }
    if x_amount != 0 {
        enigo.scroll(x_amount, Axis::Horizontal) // Uses Mouse trait method
             .map_err(|e| InputError::SimulationError(format!("Failed to scroll mouse horizontally by {}: {}", x_amount, e)))?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    // Test with direct enigo types as they are used in function signatures now
    // No need for EnigoKeyTest alias if Key is imported directly.

    #[test]
    fn test_get_enigo_instance_smoke() {
        match get_enigo_instance() {
            Ok(_) => println!("Enigo instance created successfully (or would be)."),
            Err(e) => {
                let err_msg = e.to_string();
                if err_msg.contains("Failed to initialize Enigo") &&
                   (err_msg.contains("Wayland") || err_msg.contains("X11") ||
                    err_msg.contains("windows") || err_msg.contains("macos") ||
                    err_msg.contains("Cannot connect to server") || err_msg.contains("No protocol specified")) {
                    println!("Enigo instantiation failed as expected in headless environment: {}", e);
                } else {
                    panic!("get_enigo_instance failed unexpectedly: {}", e);
                }
            }
        }
    }

    #[test]
    fn test_send_key_event_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_send_key_event_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        // Use an actual Key variant, e.g. Key::Layout for characters
        assert!(send_key_event(Key::Layout('a'), true).is_ok());
        assert!(send_key_event(Key::Layout('a'), false).is_ok());
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
        assert!(send_mouse_button_event(Button::Left, true).is_ok());
        assert!(send_mouse_button_event(Button::Left, false).is_ok());
    }

    #[test]
    fn test_click_mouse_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_click_mouse_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(click_mouse(Button::Right).is_ok());
    }

    #[test]
    fn test_scroll_mouse_wheel_smoke() {
        if get_enigo_instance().is_err() {
            println!("Skipping test_scroll_mouse_wheel_smoke due to Enigo initialization failure (likely headless).");
            return;
        }
        assert!(scroll_mouse_wheel(0, 1).is_ok()); // Scroll down
        assert!(scroll_mouse_wheel(1, 0).is_ok()); // Scroll right
        assert!(scroll_mouse_wheel(1, 1).is_ok()); // Scroll both
    }
}
