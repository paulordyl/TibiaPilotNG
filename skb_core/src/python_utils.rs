use pyo3::prelude::*;

#[pyfunction]
fn coordinates_are_equal(first_coordinate: (i32, i32, i32), second_coordinate: (i32, i32, i32)) -> bool {
    first_coordinate == second_coordinate
}

use pyo3::exceptions::PyIOError; // Added for error handling
use crate::global_app_context; // To access the global AppContext
use crate::AppError; // To map AppError to PyErr

#[pyfunction]
fn release_keys(key: String) -> PyResult<()> {
    let app_context = global_app_context().map_err(|e| {
        PyIOError::new_err(format!("Failed to get global AppContext: {}", e))
    })?;

    // Lock the Mutex to get access to Option<ArduinoCom>
    let mut arduino_com_option_guard = app_context.arduino_com.lock().map_err(|e| {
        PyIOError::new_err(format!("Failed to lock ArduinoCom Mutex: {}", e.toString()))
    })?;

    // Check if ArduinoCom instance exists
    if let Some(arduino_com) = arduino_com_option_guard.as_mut() {
        match crate::input::keyboard::key_up(arduino_com, &key) {
            Ok(_) => Ok(()),
            Err(e) => {
                // Convert AppError from key_up to PyErr
                let py_err_msg = format!("Failed to release key '{}': {}", key, e);
                match e {
                    AppError::ArduinoError(_) | AppError::InputError(_) => {
                        Err(PyIOError::new_err(py_err_msg))
                    }
                    _ => Err(PyIOError::new_err(format!("An unexpected error occurred: {}", py_err_msg))),
                }
            }
        }
    } else {
        Err(PyIOError::new_err("Arduino communication is not initialized."))
    }
}

#[pymodule]
fn rust_utils_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(coordinates_are_equal, m)?)?;
    m.add_function(wrap_pyfunction!(release_keys, m)?)?;
    Ok(())
}
