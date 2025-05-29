use crate::input::arduino::ArduinoCom;
use crate::AppError;
use log::debug;

pub fn drag(arduino: &mut ArduinoCom, x1y1: (i32, i32), x2y2: (i32, i32)) -> Result<(), AppError> {
    let command = format!("drag,{},{},{},{}", x1y1.0, x1y1.1, x2y2.0, x2y2.1);
    debug!("Executing mouse drag from ({}, {}) to ({}, {})", x1y1.0, x1y1.1, x2y2.0, x2y2.1);
    arduino.send_command(&command)
}

pub fn left_click(arduino: &mut ArduinoCom, coordinate: Option<(i32, i32)>) -> Result<(), AppError> {
    let command = if let Some(coord) = coordinate {
        debug!("Executing left click at ({}, {})", coord.0, coord.1);
        format!("left_click,{},{}", coord.0, coord.1)
    } else {
        debug!("Executing left click at current position");
        "left_click".to_string()
    };
    arduino.send_command(&command)
}

pub fn move_to(arduino: &mut ArduinoCom, coordinate: (i32, i32)) -> Result<(), AppError> {
    let command = format!("move_to,{},{}", coordinate.0, coordinate.1);
    debug!("Executing mouse move to ({}, {})", coordinate.0, coordinate.1);
    arduino.send_command(&command)
}

pub fn right_click(arduino: &mut ArduinoCom, coordinate: Option<(i32, i32)>) -> Result<(), AppError> {
    let command = if let Some(coord) = coordinate {
        debug!("Executing right click at ({}, {})", coord.0, coord.1);
        format!("right_click,{},{}", coord.0, coord.1)
    } else {
        debug!("Executing right click at current position");
        "right_click".to_string()
    };
    arduino.send_command(&command)
}

pub fn scroll(arduino: &mut ArduinoCom, clicks: i32) -> Result<(), AppError> {
    let command = format!("scroll,{}", clicks);
    debug!("Executing mouse scroll with {} clicks", clicks);
    arduino.send_command(&command)
}
