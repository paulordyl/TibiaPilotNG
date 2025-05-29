use pyo3::prelude::*;

#[pyfunction]
fn coordinates_are_equal(first_coordinate: (i32, i32, i32), second_coordinate: (i32, i32, i32)) -> bool {
    first_coordinate == second_coordinate
}

#[pyfunction]
fn release_keys(py: Python, last_pressed_key: Option<String>) -> PyResult<Option<String>> {
    if let Some(key) = last_pressed_key {
        // TODO: Implement actual key_up logic by calling into Rust's input module
        // or replicating the behavior of Python's `keyUp`.
        // For now, we'll just print a message.
        println!("Rust: keyUp({}) would be called here.", key);
    }
    // The Python equivalent sets context['py_lastPressedKey'] = None
    Ok(None)
}

#[pymodule]
fn rust_utils_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(coordinates_are_equal, m)?)?;
    m.add_function(wrap_pyfunction!(release_keys, m)?)?;
    Ok(())
}
