use pyo3::prelude::*;

#[pyfunction]
fn coordinates_are_equal(first_coordinate: (i32, i32, i32), second_coordinate: (i32, i32, i32)) -> bool {
    first_coordinate == second_coordinate
}

#[pyfunction]
fn release_keys(_py: Python, last_pressed_key: Option<String>) -> PyResult<Option<String>> {
    if let Some(key) = last_pressed_key {
        // In this isolated crate, we cannot easily call into the main bot's Rust input module.
        // This will be a placeholder. The Python side will still handle the actual keyUp.
        // OR, if direct system key-up is desired here, a crate like 'enigo' could be added.
        // For now, keeping it simple:
        println!("Rust (py_rust_utils): 'keyUp({})' action placeholder. Actual key release should be handled by Python or a dedicated input crate.", key);
    }
    // Python's original logic was: context['ng_lastPressedKey'] = None
    // So we return Ok(None) to signify this.
    Ok(None)
}

#[pymodule]
#[pyo3(name = "py_rust_utils_module")] // Explicitly name the Python module
fn rust_utils_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(coordinates_are_equal, m)?)?;
    m.add_function(wrap_pyfunction!(release_keys, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    //use pyo3::types::PyAny; // Required for with_gil. Not strictly required for these tests as Python::with_gil is used.

    #[test]
    fn test_coordinates_are_equal_positive() {
        assert!(coordinates_are_equal((1, 2, 3), (1, 2, 3)));
    }

    #[test]
    fn test_coordinates_are_equal_negative_x() {
        assert!(!coordinates_are_equal((0, 2, 3), (1, 2, 3)));
    }

    #[test]
    fn test_coordinates_are_equal_negative_y() {
        assert!(!coordinates_are_equal((1, 0, 3), (1, 2, 3)));
    }

    #[test]
    fn test_coordinates_are_equal_negative_z() {
        assert!(!coordinates_are_equal((1, 2, 0), (1, 2, 3)));
    }
    
    #[test]
    fn test_coordinates_are_equal_all_different() {
        assert!(!coordinates_are_equal((0, 0, 0), (1, 2, 3)));
    }

    #[test]
    fn test_release_keys_with_some_key() {
        // PyO3 functions that take Python<'_> argument need a GIL token
        Python::with_gil(|py| {
            let result = release_keys(py, Some("test_key".to_string()));
            assert!(result.is_ok());
            assert_eq!(result.unwrap(), None);
        });
    }

    #[test]
    fn test_release_keys_with_none_key() {
        Python::with_gil(|py| {
            let result = release_keys(py, None);
            assert!(result.is_ok());
            assert_eq!(result.unwrap(), None);
        });
    }
}
