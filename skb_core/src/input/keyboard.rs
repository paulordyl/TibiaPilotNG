use crate::input::arduino::ArduinoCom;
use crate::AppError;
use log::debug;

// A subset of key mappings. This should be expanded as needed.
// Made public for testing, or could be tested via command generation functions.
// For direct testing, it's easier if it's pub(crate) or pub.
// Let's make it pub(crate) for now, assuming tests are in the same crate.
pub(crate) fn get_ascii_from_key(key: &str) -> u8 {
    match key {
        "a" => b'a', "b" => b'b', "c" => b'c', "d" => b'd', "e" => b'e',
        "f" => b'f', "g" => b'g', "h" => b'h', "i" => b'i', "j" => b'j',
        "k" => b'k', "l" => b'l', "m" => b'm', "n" => b'n', "o" => b'o',
        "p" => b'p', "q" => b'q', "r" => b'r', "s" => b's', "t" => b't',
        "u" => b'u', "v" => b'v', "w" => b'w', "x" => b'x', "y" => b'y',
        "z" => b'z',
        "A" => b'A', "B" => b'B', "C" => b'C', "D" => b'D', "E" => b'E',
        "F" => b'F', "G" => b'G', "H" => b'H', "I" => b'I', "J" => b'J',
        "K" => b'K', "L" => b'L', "M" => b'M', "N" => b'N', "O" => b'O',
        "P" => b'P', "Q" => b'Q', "R" => b'R', "S" => b'S', "T" => b'T',
        "U" => b'U', "V" => b'V', "W" => b'W', "X" => b'X', "Y" => b'Y',
        "Z" => b'Z',
        "1" => b'1', "2" => b'2', "3" => b'3', "4" => b'4', "5" => b'5',
        "6" => b'6', "7" => b'7', "8" => b'8', "9" => b'9', "0" => b'0',
        " " => b' ', "space" => b' ',
        "enter" => 0xB0, // KEY_RETURN
        "esc" => 0xB1,   // KEY_ESC
        "backspace" => 0xB2, // KEY_BACKSPACE
        "tab" => 0xB3,   // KEY_TAB
        "capslock" => 0xC1, // KEY_CAPS_LOCK
        "f1" => 0xC2, "f2" => 0xC3, "f3" => 0xC4, "f4" => 0xC5, "f5" => 0xC6,
        "f6" => 0xC7, "f7" => 0xC8, "f8" => 0xC9, "f9" => 0xCA, "f10" => 0xCB,
        "f11" => 0xCC, "f12" => 0xCD,
        "printscreen" => 0xCE, // KEY_PRINTSCREEN
        "scrolllock" => 0xCF, // KEY_SCROLL_LOCK
        "pause" => 0xD0,      // KEY_PAUSE
        "insert" => 0xD1,     // KEY_INSERT
        "home" => 0xD2,       // KEY_HOME
        "pageup" => 0xD3,     // KEY_PAGE_UP
        "delete" => 0xD4,     // KEY_DELETE
        "end" => 0xD5,        // KEY_END
        "pagedown" => 0xD6,   // KEY_PAGE_DOWN
        "right" => 0xD7,      // KEY_RIGHT_ARROW
        "left" => 0xD8,       // KEY_LEFT_ARROW
        "down" => 0xD9,       // KEY_DOWN_ARROW
        "up" => 0xDA,         // KEY_UP_ARROW
        "ctrl" => 0x80,  // KEY_LEFT_CTRL
        "shift" => 0x81, // KEY_LEFT_SHIFT
        "alt" => 0x82,   // KEY_LEFT_ALT
        "gui" => 0x83,   // KEY_LEFT_GUI (Windows/Command key)
        "ctrl_right" => 0x84, // KEY_RIGHT_CTRL
        "shift_right" => 0x85,// KEY_RIGHT_SHIFT
        "alt_right" => 0x86,  // KEY_RIGHT_ALT
        "gui_right" => 0x87,  // KEY_RIGHT_GUI
        _ => 0x00, // Default to null char if key not found, could also panic or return Result
    }
}

// Command Generation Helpers
fn generate_hotkey_command(keys: &[&str]) -> String {
    let ascii_keys: Vec<String> = keys.iter().map(|k| get_ascii_from_key(k).to_string()).collect();
    format!("hotkey,{}", ascii_keys.join(","))
}

fn generate_key_down_command(key: &str) -> String {
    let ascii_key = get_ascii_from_key(key);
    format!("key_down,{}", ascii_key)
}

fn generate_key_up_command(key: &str) -> String {
    let ascii_key = get_ascii_from_key(key);
    format!("key_up,{}", ascii_key)
}

fn generate_press_command(keys: &[&str]) -> String {
    let ascii_keys: Vec<String> = keys.iter().map(|k| get_ascii_from_key(k).to_string()).collect();
    format!("press,{}", ascii_keys.join(","))
}

fn generate_write_command(phrase: &str) -> String {
    format!("write,{}", phrase)
}


pub fn hotkey(arduino: &mut ArduinoCom, keys: &[&str]) -> Result<(), AppError> {
    if keys.is_empty() {
        return Err(AppError::InputError("Hotkey keys slice cannot be empty".to_string()));
    }
    let command = generate_hotkey_command(keys);
    debug!("Executing hotkey: {:?} (command: {})", keys, command);
    arduino.send_command(&command)
}

pub fn key_down(arduino: &mut ArduinoCom, key: &str) -> Result<(), AppError> {
    let command = generate_key_down_command(key);
    debug!("Executing key_down: {} (command: {})", key, command);
    arduino.send_command(&command)
}

pub fn key_up(arduino: &mut ArduinoCom, key: &str) -> Result<(), AppError> {
    let command = generate_key_up_command(key);
    debug!("Executing key_up: {} (command: {})", key, command);
    arduino.send_command(&command)
}

pub fn press(arduino: &mut ArduinoCom, keys: &[&str]) -> Result<(), AppError> {
    if keys.is_empty() {
        return Err(AppError::InputError("Press keys slice cannot be empty".to_string()));
    }
    let command = generate_press_command(keys);
    debug!("Executing press: {:?} (command: {})", keys, command);
    arduino.send_command(&command)
}

pub fn write(arduino: &mut ArduinoCom, phrase: &str) -> Result<(), AppError> {
    let command = generate_write_command(phrase);
    debug!("Executing write: {} (command: {})", phrase, command);
    arduino.send_command(&command)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_ascii_from_key_known() {
        assert_eq!(get_ascii_from_key("a"), b'a');
        assert_eq!(get_ascii_from_key("Z"), b'Z');
        assert_eq!(get_ascii_from_key("0"), b'0');
        assert_eq!(get_ascii_from_key("space"), b' ');
        assert_eq!(get_ascii_from_key("enter"), 0xB0);
        assert_eq!(get_ascii_from_key("f12"), 0xCD);
        assert_eq!(get_ascii_from_key("ctrl"), 0x80);
        assert_eq!(get_ascii_from_key("alt_right"), 0x86);
    }

    #[test]
    fn test_get_ascii_from_key_unknown() {
        assert_eq!(get_ascii_from_key("unknown_key"), 0x00);
        assert_eq!(get_ascii_from_key(""), 0x00); // Empty string
    }

    #[test]
    fn test_generate_hotkey_command() {
        assert_eq!(generate_hotkey_command(&["ctrl", "a"]), format!("hotkey,{},{}", 0x80, b'a'));
        assert_eq!(generate_hotkey_command(&["f1"]), format!("hotkey,{}", 0xC2));
    }

    #[test]
    fn test_generate_hotkey_command_empty_slice() {
        // Note: The public `hotkey` function has a guard. This tests the generator directly.
        assert_eq!(generate_hotkey_command(&[]), "hotkey,");
    }


    #[test]
    fn test_generate_key_down_command() {
        assert_eq!(generate_key_down_command("b"), format!("key_down,{}", b'b'));
        assert_eq!(generate_key_down_command("esc"), format!("key_down,{}", 0xB1));
    }

    #[test]
    fn test_generate_key_up_command() {
        assert_eq!(generate_key_up_command("c"), format!("key_up,{}", b'c'));
        assert_eq!(generate_key_up_command("tab"), format!("key_up,{}", 0xB3));
    }

    #[test]
    fn test_generate_press_command() {
        assert_eq!(generate_press_command(&["shift", "1"]), format!("press,{},{}", 0x81, b'1'));
        assert_eq!(generate_press_command(&["enter"]), format!("press,{}", 0xB0));
    }

    #[test]
    fn test_generate_press_command_empty_slice() {
        // Note: The public `press` function has a guard. This tests the generator directly.
        assert_eq!(generate_press_command(&[]), "press,");
    }

    #[test]
    fn test_generate_write_command() {
        assert_eq!(generate_write_command("Hello"), "write,Hello");
        assert_eq!(generate_write_command(""), "write,"); // Empty phrase
    }
}
// Based on https://www.arduino.cc/reference/en/language/functions/usb/keyboard/keyboardmodifiers/
// and https://www.arduino.cc/reference/en/language/functions/usb/keyboard/asciichart/
// (Content of get_ascii_from_key remains the same, just moved up due to helper functions needing it)
