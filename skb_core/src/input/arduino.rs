use crate::AppError; // Assuming AppError is in the root of the crate
use base64::{encode};
use log::{debug, error};
use serialport::SerialPort;
use std::{io::{self, Write}, thread, time::Duration}; // Import io::Write

pub struct ArduinoCom {
    port: Box<dyn SerialPort>,
}

impl ArduinoCom {
    pub fn new(port_name: &str, baud_rate: u32) -> Result<Self, AppError> {
        debug!("Initializing ArduinoCom with port: {} and baud_rate: {}", port_name, baud_rate);
        let port = serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100)) // Set a timeout for operations
            .open()
            .map_err(|e| {
                error!("Failed to open serial port {}: {}", port_name, e);
                AppError::InputError(format!("Failed to open serial port {}: {}", port_name, e))
            })?;
        debug!("Serial port {} opened successfully", port_name);
        Ok(ArduinoCom { port })
    }

    pub fn send_command(&mut self, command: &str) -> Result<(), AppError> {
        debug!("Sending command: {}", command);
        let encoded_command = encode(command);
        debug!("Base64 encoded command: {}", encoded_command);

        // Append newline character
        let final_command = format!("{}\n", encoded_command);

        match self.port.write_all(final_command.as_bytes()) {
            Ok(_) => {
                // Small delay after sending, similar to Python's sleep(0.01)
                thread::sleep(Duration::from_millis(10));
                debug!("Command sent successfully");
                Ok(())
            }
            Err(e) => {
                error!("Failed to send command: {}", e);
                // Check if the error is due to a broken pipe, which might indicate the Arduino was disconnected
                if e.kind() == io::ErrorKind::BrokenPipe {
                    Err(AppError::InputError(format!(
                        "Failed to send command: Broken pipe. Arduino might be disconnected. Original error: {}",
                        e
                    )))
                } else {
                    Err(AppError::InputError(format!(
                        "Failed to send command: {}. Command: '{}'",
                        e, command
                    )))
                }
            }
        }
    }
}

// Example of how to integrate AppError if it's defined in main.rs or lib.rs
// This assumes AppError is accessible from crate::AppError
// If AppError is in a different module, adjust the path accordingly.

// Mock AppError for compilation if not available globally - remove this if AppError is globally accessible
/*
#[derive(Debug)]
pub enum AppError {
    InputError(String),
    // Add other error variants as needed
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::InputError(s) => write!(f, "Input Error: {}", s),
        }
    }
}

impl std::error::Error for AppError {}
*/
