use rdev::{simulate as rdev_simulate, EventType, Key as RdevKey, Button as RdevButton, SimulateError as RdevSimulateError};
use thiserror::Error;
use std::{thread, time};

#[derive(Error, Debug)]
pub enum InputError {
    #[error("Input simulation failed: {0}")]
    SimulationError(String),
    #[error("Hotkey listener error: {0}")]
    ListenerError(String),
    #[error("Unsupported key or button: {0}")]
    UnsupportedInput(String),
}

#[derive(Debug, Clone, Copy)]
pub enum KeyboardKey {
    Space,
    Enter,
    Escape,
    KeyA, KeyB, KeyC,
    F1, F2, F3,
}

impl TryFrom<KeyboardKey> for RdevKey {
    type Error = InputError;
    fn try_from(key: KeyboardKey) -> Result<Self, Self::Error> {
        match key {
            KeyboardKey::Space => Ok(RdevKey::Space),
            KeyboardKey::Enter => Ok(RdevKey::Return),
            KeyboardKey::Escape => Ok(RdevKey::Escape),
            KeyboardKey::KeyA => Ok(RdevKey::KeyA),
            KeyboardKey::KeyB => Ok(RdevKey::KeyB),
            KeyboardKey::KeyC => Ok(RdevKey::KeyC),
            KeyboardKey::F1 => Ok(RdevKey::F1),
            KeyboardKey::F2 => Ok(RdevKey::F2),
            KeyboardKey::F3 => Ok(RdevKey::F3),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum MouseButton {
    Left,
    Right,
    Middle,
}

impl TryFrom<MouseButton> for RdevButton {
    type Error = InputError;
    fn try_from(button: MouseButton) -> Result<Self, Self::Error> {
        match button {
            MouseButton::Left => Ok(RdevButton::Left),
            MouseButton::Right => Ok(RdevButton::Right),
            MouseButton::Middle => Ok(RdevButton::Middle),
        }
    }
}

fn map_rdev_error(err: RdevSimulateError) -> InputError {
    InputError::SimulationError(format!("{:?}", err))
}

pub mod sender {
    use super::*;

    fn simulate_event(event_type: EventType) -> Result<(), InputError> {
        log::debug!("Simulating input event: {:?}", event_type);
        rdev_simulate(&event_type).map_err(map_rdev_error)
    }

    pub fn send_key_down(key: KeyboardKey) -> Result<(), InputError> {
        let rdev_key = RdevKey::try_from(key)?;
        log::info!("Sending key down: {:?}", key);
        simulate_event(EventType::KeyPress(rdev_key))
    }

    pub fn send_key_up(key: KeyboardKey) -> Result<(), InputError> {
        let rdev_key = RdevKey::try_from(key)?;
        log::info!("Sending key up: {:?}", key);
        simulate_event(EventType::KeyRelease(rdev_key))
    }

    pub fn send_key_click(key: KeyboardKey) -> Result<(), InputError> {
        log::info!("Sending key click: {:?}", key);
        send_key_down(key)?;
        thread::sleep(time::Duration::from_millis(20));
        send_key_up(key)
    }

    pub fn send_mouse_move(x: i32, y: i32) -> Result<(), InputError> {
        log::info!("Sending mouse move to ({}, {})", x, y);
        simulate_event(EventType::MouseMove { x: x as f64, y: y as f64 })
    }

    pub fn send_mouse_click(button: MouseButton) -> Result<(), InputError> {
        let rdev_button = RdevButton::try_from(button)?;
        log::info!("Sending mouse click: {:?}", button);
        simulate_event(EventType::ButtonPress(rdev_button))?;
        thread::sleep(time::Duration::from_millis(20));
        simulate_event(EventType::ButtonRelease(rdev_button))
    }
}

pub mod listener {
    use super::*;

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub enum ModifierKey {
        Control,
        Shift,
        Alt,
        Meta,
    }

    #[derive(Debug, Clone, PartialEq, Eq, Hash)]
    pub struct HotkeyCombination {
        pub base_key: KeyboardKey,
        pub modifiers: Vec<ModifierKey>,
    }

    pub fn listen_for_hotkey(
        _hotkey: HotkeyCombination,
        _callback: impl Fn() + Send + Sync + 'static,
    ) -> Result<(), InputError> {
        log::warn!("listen_for_hotkey is a placeholder and not yet implemented.");
        Err(InputError::ListenerError("Not implemented".to_string()))
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::sender::*;

    fn setup_test_logging() {
        let _ = env_logger::builder().is_test(true).try_init();
    }

    #[test]
    fn test_key_mapping() {
        setup_test_logging();
        assert_eq!(RdevKey::try_from(KeyboardKey::Space).unwrap(), RdevKey::Space);
        assert_eq!(RdevKey::try_from(KeyboardKey::KeyA).unwrap(), RdevKey::KeyA);
    }

    #[test]
    fn test_send_key_click_runs() {
        setup_test_logging();
        log::info!("Testing send_key_click (Space)...");
        let result = send_key_click(KeyboardKey::Space);
        match result {
            Ok(_) => log::info!("send_key_click(Space) succeeded (unexpected in CI)."),
            Err(InputError::SimulationError(e_str)) => {
                log::warn!("send_key_click(Space) failed as expected in CI/headless: {}", e_str);
                assert!(e_str.to_lowercase().contains("xcb") ||
                        e_str.to_lowercase().contains("wayland") ||
                        e_str.to_lowercase().contains("xopendisplay failed") ||
                        e_str.to_lowercase().contains("connectionrefused") ||
                        e_str.to_lowercase().contains("permissiondenied") ||
                        e_str.to_lowercase().contains("noscreen") // Common for rdev simulate
                       );
            }
            Err(e) => panic!("send_key_click(Space) failed with unexpected error: {:?}", e),
        }
    }

    #[test]
    fn test_send_mouse_move_runs() {
        setup_test_logging();
        log::info!("Testing send_mouse_move...");
        let result = send_mouse_move(100, 100);
        match result {
            Ok(_) => log::info!("send_mouse_move succeeded (unexpected in CI)."),
            Err(InputError::SimulationError(e_str)) => {
                log::warn!("send_mouse_move failed as expected in CI/headless: {}", e_str);
                 assert!(e_str.to_lowercase().contains("xcb") ||
                         e_str.to_lowercase().contains("wayland") ||
                         e_str.to_lowercase().contains("xopendisplay failed") ||
                         e_str.to_lowercase().contains("connectionrefused") ||
                         e_str.to_lowercase().contains("permissiondenied") ||
                         e_str.to_lowercase().contains("noscreen")
                        );
            }
            Err(e) => panic!("send_mouse_move failed with unexpected error: {:?}", e),
        }
    }

    #[test]
    fn test_send_mouse_click_runs() {
        setup_test_logging();
        log::info!("Testing send_mouse_click (Left)...");
        let result = send_mouse_click(MouseButton::Left);
        match result {
            Ok(_) => log::info!("send_mouse_click(Left) succeeded (unexpected in CI)."),
            Err(InputError::SimulationError(e_str)) => {
                log::warn!("send_mouse_click(Left) failed as expected in CI/headless: {}", e_str);
                assert!(e_str.to_lowercase().contains("xcb") ||
                        e_str.to_lowercase().contains("wayland") ||
                        e_str.to_lowercase().contains("xopendisplay failed") ||
                        e_str.to_lowercase().contains("connectionrefused") ||
                        e_str.to_lowercase().contains("permissiondenied") ||
                        e_str.to_lowercase().contains("noscreen")
                       );
            }
            Err(e) => panic!("send_mouse_click(Left) failed with unexpected error: {:?}", e),
        }
    }

    #[test]
    fn test_hotkey_listener_placeholder() {
        setup_test_logging();
        let hotkey = listener::HotkeyCombination {
            base_key: KeyboardKey::KeyA,
            modifiers: vec![listener::ModifierKey::Control],
        };
        let result = listener::listen_for_hotkey(hotkey, || println!("Hotkey pressed!"));
        assert!(result.is_err());
        match result.err().unwrap() {
            InputError::ListenerError(s) => assert_eq!(s, "Not implemented"),
            _ => panic!("Unexpected error from placeholder listen_for_hotkey"),
        }
    }
}
