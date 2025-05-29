use crate::input::arduino::ArduinoCom;
use crate::AppError;
use log::debug;

// A subset of key mappings. This should be expanded as needed.
// Based on https://www.arduino.cc/reference/en/language/functions/usb/keyboard/keyboardmodifiers/
// and https://www.arduino.cc/reference/en/language/functions/usb/keyboard/asciichart/
fn get_ascii_from_key(key: &str) -> u8 {
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

pub fn hotkey(arduino: &mut ArduinoCom, keys: &[&str]) -> Result<(), AppError> {
    if keys.is_empty() {
        return Err(AppError::InputError("Hotkey keys slice cannot be empty".to_string()));
    }
    let ascii_keys: Vec<String> = keys.iter().map(|k| get_ascii_from_key(k).to_string()).collect();
    let command = format!("hotkey,{}", ascii_keys.join(","));
    debug!("Executing hotkey: {:?}", keys);
    arduino.send_command(&command)
}

pub fn key_down(arduino: &mut ArduinoCom, key: &str) -> Result<(), AppError> {
    let ascii_key = get_ascii_from_key(key);
    let command = format!("key_down,{}", ascii_key);
    debug!("Executing key_down: {}", key);
    arduino.send_command(&command)
}

pub fn key_up(arduino: &mut ArduinoCom, key: &str) -> Result<(), AppError> {
    let ascii_key = get_ascii_from_key(key);
    let command = format!("key_up,{}", ascii_key);
    debug!("Executing key_up: {}", key);
    arduino.send_command(&command)
}

pub fn press(arduino: &mut ArduinoCom, keys: &[&str]) -> Result<(), AppError> {
    if keys.is_empty() {
        return Err(AppError::InputError("Press keys slice cannot be empty".to_string()));
    }
    let ascii_keys: Vec<String> = keys.iter().map(|k| get_ascii_from_key(k).to_string()).collect();
    let command = format!("press,{}", ascii_keys.join(","));
    debug!("Executing press: {:?}", keys);
    arduino.send_command(&command)
}

pub fn write(arduino: &mut ArduinoCom, phrase: &str) -> Result<(), AppError> {
    // The Python version sends one character at a time for `write`.
    // We'll prepare a single command string for simplicity, assuming the Arduino can handle it,
    // or it can be split into multiple `press` commands if needed.
    // The original python code does `press(key)` for each char.
    // A direct translation would be:
    // for char_as_str in phrase.chars().map(|c| c.to_string()) {
    //     press(arduino, &[&char_as_str])?;
    // }
    // Ok(())
    // However, to minimize serial calls, let's try sending the whole phrase.
    // Arduino side will need to parse "write,s,t,r,i,n,g" or similar.
    // Or, if the Arduino side `write` command is smart, "write,string"
    // For now, let's assume the latter for simplicity.
    // If it's char by char, the command should be like `press` for each char.
    let command = format!("write,{}", phrase);
    debug!("Executing write: {}", phrase);
    arduino.send_command(&command)
}
