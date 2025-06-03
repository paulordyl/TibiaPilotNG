use crate::input::arduino::ArduinoCom;
use crate::AppError;
use log::debug;

// Command Generation Helpers
fn generate_drag_command(x1y1: (i32, i32), x2y2: (i32, i32)) -> String {
    format!("drag,{},{},{},{}", x1y1.0, x1y1.1, x2y2.0, x2y2.1)
}

fn generate_left_click_command(coordinate: Option<(i32, i32)>) -> String {
    if let Some(coord) = coordinate {
        format!("left_click,{},{}", coord.0, coord.1)
    } else {
        "left_click".to_string()
    }
}

fn generate_move_to_command(coordinate: (i32, i32)) -> String {
    format!("move_to,{},{}", coordinate.0, coordinate.1)
}

fn generate_right_click_command(coordinate: Option<(i32, i32)>) -> String {
    if let Some(coord) = coordinate {
        format!("right_click,{},{}", coord.0, coord.1)
    } else {
        "right_click".to_string()
    }
}

fn generate_scroll_command(clicks: i32) -> String {
    format!("scroll,{}", clicks)
}


// Public Functions
pub fn drag(arduino: &mut ArduinoCom, x1y1: (i32, i32), x2y2: (i32, i32)) -> Result<(), AppError> {
    let command = generate_drag_command(x1y1, x2y2);
    debug!("Executing mouse drag from ({}, {}) to ({}, {}) (command: {})", x1y1.0, x1y1.1, x2y2.0, x2y2.1, command);
    arduino.send_command(&command)
}

pub fn left_click(arduino: &mut ArduinoCom, coordinate: Option<(i32, i32)>) -> Result<(), AppError> {
    let command = generate_left_click_command(coordinate);
    if let Some(coord) = coordinate {
        debug!("Executing left click at ({}, {}) (command: {})", coord.0, coord.1, command);
    } else {
        debug!("Executing left click at current position (command: {})", command);
    }
    arduino.send_command(&command)
}

pub fn move_to(arduino: &mut ArduinoCom, coordinate: (i32, i32)) -> Result<(), AppError> {
    let command = generate_move_to_command(coordinate);
    debug!("Executing mouse move to ({}, {}) (command: {})", coordinate.0, coordinate.1, command);
    arduino.send_command(&command)
}

pub fn right_click(arduino: &mut ArduinoCom, coordinate: Option<(i32, i32)>) -> Result<(), AppError> {
    let command = generate_right_click_command(coordinate);
     if let Some(coord) = coordinate {
        debug!("Executing right click at ({}, {}) (command: {})", coord.0, coord.1, command);
    } else {
        debug!("Executing right click at current position (command: {})", command);
    }
    arduino.send_command(&command)
}

pub fn scroll(arduino: &mut ArduinoCom, clicks: i32) -> Result<(), AppError> {
    let command = generate_scroll_command(clicks);
    debug!("Executing mouse scroll with {} clicks (command: {})", clicks, command);
    arduino.send_command(&command)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_generate_drag_command() {
        assert_eq!(generate_drag_command((10, 20), (30, 40)), "drag,10,20,30,40");
    }

    #[test]
    fn test_generate_left_click_command() {
        assert_eq!(generate_left_click_command(Some((100, 150))), "left_click,100,150");
        assert_eq!(generate_left_click_command(None), "left_click");
    }

    #[test]
    fn test_generate_move_to_command() {
        assert_eq!(generate_move_to_command((50, 75)), "move_to,50,75");
    }

    #[test]
    fn test_generate_right_click_command() {
        assert_eq!(generate_right_click_command(Some((200, 250))), "right_click,200,250");
        assert_eq!(generate_right_click_command(None), "right_click");
    }

    #[test]
    fn test_generate_scroll_command() {
        assert_eq!(generate_scroll_command(5), "scroll,5");
        assert_eq!(generate_scroll_command(-3), "scroll,-3");
    }
}
