use pyo3::prelude::*;
use numpy::PyReadonlyArray2;
use numpy::ndarray::{ArrayView, Ix2}; 
use std::collections::HashMap;
use farmhash::FarmHasher;
use std::hash::Hasher;

// --- Existing Functions ---
#[pyfunction]
fn coordinates_are_equal(first_coordinate: (i32, i32, i32), second_coordinate: (i32, i32, i32)) -> bool {
    first_coordinate == second_coordinate
}

#[pyfunction]
fn release_keys(_py: Python, last_pressed_key: Option<String>) -> PyResult<Option<String>> {
    if let Some(key) = last_pressed_key {
        println!("Rust (py_rust_utils): 'keyUp({})' action placeholder. Actual key release should be handled by Python or a dedicated input crate.", key);
    }
    Ok(None)
}

// --- New Helper Functions ---
fn extract_and_process_region(
    screenshot_view: &ArrayView<u8, Ix2>, 
    region_x: usize, region_y: usize, region_width: usize, region_height: usize,
    apply_value_filter: bool,
) -> Option<Vec<u8>> {
    if region_width == 0 || region_height == 0 { 
        return None;
    }
    if region_y.saturating_add(region_height) > screenshot_view.shape()[0] || 
       region_x.saturating_add(region_width) > screenshot_view.shape()[1] ||
       region_y >= screenshot_view.shape()[0] || region_x >= screenshot_view.shape()[1] {
        return None; 
    }

    let mut processed_data = Vec::with_capacity(region_width * region_height);
    for r in 0..region_height {
        for c in 0..region_width {
            let val = screenshot_view[(region_y + r, region_x + c)];
            let mut processed_val = val;
            
            if val >= 50 && val <= 100 { 
                processed_val = 0;
            }
            
            if apply_value_filter { 
                if processed_val == 126 || processed_val == 192 {
                    processed_val = 192;
                } else if processed_val != 192 { 
                    processed_val = 0;
                }
            }
            processed_data.push(processed_val);
        }
    }
    Some(processed_data)
}

fn hashit_rust(data: &[u8]) -> i64 {
    let mut hasher = FarmHasher::default();
    hasher.write(data);
    hasher.finish() as i64 
}

fn get_hashed_value(
    screenshot_view: &ArrayView<u8, Ix2>, 
    base_x: i32, 
    base_y: i32, 
    img_slice_x_offset: i32, 
    img_slice_width: usize, 
    img_slice_height: usize, 
    hashes_map: &HashMap<i64, i32>,
    is_value_type: bool,
) -> i32 {
    let final_x = base_x.saturating_add(img_slice_x_offset);
    let final_y = base_y;

    if final_x < 0 || final_y < 0 {
        return 0; 
    }

    let region_data = extract_and_process_region(
        screenshot_view,
        final_x as usize,
        final_y as usize,
        img_slice_width,
        img_slice_height,
        is_value_type,
    );

    if let Some(data) = region_data {
        if data.is_empty() { 
            return 0;
        }
        let hash = hashit_rust(&data);
        *hashes_map.get(&hash).unwrap_or(&0)
    } else {
        0 
    }
}

// --- New FFI Functions ---
#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, numbers_hashes))]
fn get_hp_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>, 
    numbers_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() {
        return Ok(None);
    }
    let bbox = skills_icon_bbox.unwrap();
    let icon_x = bbox.0;
    let icon_y = bbox.1;

    let base_x = icon_x + 6;
    let base_y = icon_y + 90;
    let screenshot_view = screenshot.as_array(); 

    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &numbers_hashes, true);
    
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, numbers_hashes))]
fn get_mana_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    numbers_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 104; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, numbers_hashes))]
fn get_capacity_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    numbers_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 132; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}
   
#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, numbers_hashes))]
fn get_speed_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    numbers_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 146; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, minutes_or_hours_hashes))]
fn get_food_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    minutes_or_hours_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 160; 
    let screenshot_view = screenshot.as_array();
    let minutes_val = get_hashed_value(&screenshot_view, base_x, base_y, 130, 14, 8, &minutes_or_hours_hashes, false);
    let hours_val = get_hashed_value(&screenshot_view, base_x, base_y, 110, 14, 8, &minutes_or_hours_hashes, false);
    Ok(Some((hours_val * 60) + minutes_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, minutes_or_hours_hashes))]
fn get_stamina_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    minutes_or_hours_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 174; 
    let screenshot_view = screenshot.as_array();
    let minutes_val = get_hashed_value(&screenshot_view, base_x, base_y, 130, 14, 8, &minutes_or_hours_hashes, false);
    let hours_val = get_hashed_value(&screenshot_view, base_x, base_y, 110, 14, 8, &minutes_or_hours_hashes, false);
    Ok(Some((hours_val * 60) + minutes_val))
}
   
// --- Updated PyModule ---
#[pymodule]
#[pyo3(name = "py_rust_utils_module")] 
fn rust_utils_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(coordinates_are_equal, m)?)?;
    m.add_function(wrap_pyfunction!(release_keys, m)?)?;
    m.add_function(wrap_pyfunction!(get_hp_rust, m)?)?;
    m.add_function(wrap_pyfunction!(get_mana_rust, m)?)?;
    m.add_function(wrap_pyfunction!(get_capacity_rust, m)?)?;
    m.add_function(wrap_pyfunction!(get_speed_rust, m)?)?;
    m.add_function(wrap_pyfunction!(get_food_rust, m)?)?;
    m.add_function(wrap_pyfunction!(get_stamina_rust, m)?)?;
    Ok(())
}

// --- Tests ---
#[cfg(test)]
mod tests {
    use super::*;
    use numpy::{PyArray, PyArrayMethods}; // Added PyArrayMethods
    use numpy::ndarray::Array; 

    fn get_reference_hash(data: &[u8]) -> i64 {
        let mut hasher = FarmHasher::default();
        hasher.write(data);
        hasher.finish() as i64
    }

    // Corrected signature and usage for create_mock_screenshot_array
    fn create_mock_screenshot_array<'a>(py: Python<'a>, data: &'a [u8], rows: usize, cols: usize) -> PyReadonlyArray2<'a, u8> {
        PyArray::from_slice_bound(py, data) 
            .reshape((rows, cols)).unwrap()
            .readonly()
    }
    
    fn get_mock_numbers_hashes() -> HashMap<i64, i32> {
        let mut hashes = HashMap::new();
        let data_192_22x8 = vec![192u8; 22 * 8];
        hashes.insert(get_reference_hash(&data_192_22x8), 1); 
        let data_0_22x8 = vec![0u8; 22 * 8];
        hashes.insert(get_reference_hash(&data_0_22x8), 0); 
        let mut data_5_22x8 = vec![0u8; 22 * 8];
        for i in 0..(22*8) { if i % 2 == 0 { data_5_22x8[i] = 192; } } 
        hashes.insert(get_reference_hash(&data_5_22x8), 5);
        hashes
    }

    fn get_mock_minutes_hours_hashes() -> HashMap<i64, i32> {
        let mut hashes = HashMap::new();
        let data_0_14x8 = vec![0u8; 14 * 8];
        hashes.insert(get_reference_hash(&data_0_14x8), 0); 
        let mut data_3_14x8 = vec![0u8; 14*8];
        for i in 0..(14*8) { if i % 3 == 0 { data_3_14x8[i] = 120; } } 
        hashes.insert(get_reference_hash(&data_3_14x8), 3);
        hashes
    }

    #[test]
    fn test_extract_and_process_region_normal() {
        let data = Array::from_shape_vec((2, 3), vec![10u8, 60, 120, 20, 70, 130]).unwrap();
        let view = data.view();
        let result = extract_and_process_region(&view, 0, 0, 3, 2, false).unwrap();
        assert_eq!(result, vec![10u8, 0, 120, 20, 0, 130]);
    }

    #[test]
    fn test_extract_and_process_region_filtered() {
        let data = Array::from_shape_vec((2, 3), vec![10u8, 126, 192, 20, 70, 130]).unwrap();
        let view = data.view();
        let result = extract_and_process_region(&view, 0, 0, 3, 2, true).unwrap();
        assert_eq!(result, vec![0u8, 192, 192, 0, 0, 0]);
    }

    #[test]
    fn test_extract_and_process_region_out_of_bounds() {
        let data = Array::from_shape_vec((2, 2), vec![1u8, 2, 3, 4]).unwrap();
        let view = data.view();
        assert!(extract_and_process_region(&view, 0, 0, 3, 2, false).is_none()); 
        assert!(extract_and_process_region(&view, 0, 0, 2, 3, false).is_none()); 
        assert!(extract_and_process_region(&view, 1, 1, 2, 2, false).is_none()); 
        assert!(extract_and_process_region(&view, 2, 0, 1, 1, false).is_none()); 
        assert!(extract_and_process_region(&view, 0, 2, 1, 1, false).is_none()); 
        assert!(extract_and_process_region(&view, 0, 0, 0, 1, false).is_none()); 
    }

    #[test]
    fn test_hashit_rust_known_value() {
        let data: &[u8] = &[0, 1, 2, 3, 4, 5];
        assert_eq!(hashit_rust(data), 2645327907902100037i64);
    }

    #[test]
    fn test_get_hashed_value_logic() {
        let screenshot_data = vec![70u8; 10 * 10];
        let screenshot_arr = Array::from_shape_vec((10,10), screenshot_data).unwrap();
        let screenshot_view = screenshot_arr.view();

        let mut hashes = HashMap::new();
        let all_zeros_2x2 = vec![0u8; 2 * 2];
        let expected_hash = get_reference_hash(&all_zeros_2x2);
        hashes.insert(expected_hash, 99);

        let val = get_hashed_value(&screenshot_view, 0, 0, 0, 2, 2, &hashes, false);
        assert_eq!(val, 99);
        
        let mut other_hashes = HashMap::new();
        other_hashes.insert(12345, 10); 
        let val_other_map = get_hashed_value(&screenshot_view, 0, 0, 0, 2, 2, &other_hashes, false);
        assert_eq!(val_other_map, 0);

        let val_oob = get_hashed_value(&screenshot_view, 0, 0, 0, 20, 20, &hashes, false);
        assert_eq!(val_oob, 0);
    }
    
    fn create_targeted_screenshot_data(val_for_thousands: u8, val_for_hundreds: u8, width: usize, height: usize) -> Vec<u8> {
        let mut data = vec![150u8; width * height]; 
        let base_x = 50 + 6; 
        let base_y_hp = 50 + 90; 

        let thousands_x_start = base_x + 94;
        for r in 0..8 {
            for c in 0..22 {
                if (base_y_hp + r) < height && (thousands_x_start + c) < width { 
                    data[(base_y_hp + r) * width + (thousands_x_start + c)] = val_for_thousands;
                }
            }
        }
        let hundreds_x_start = base_x + 122;
         for r in 0..8 {
            for c in 0..22 {
                 if (base_y_hp + r) < height && (hundreds_x_start + c) < width { 
                    data[(base_y_hp + r) * width + (hundreds_x_start + c)] = val_for_hundreds;
                }
            }
        }
        data
    }

    #[test]
    fn test_get_hp_rust_specific_val() {
        Python::with_gil(|py| {
            let screenshot_data = create_targeted_screenshot_data(70, 126, 300, 300); 
            let screenshot = create_mock_screenshot_array(py, &screenshot_data, 300, 300);
            let mock_bbox = Some((50, 50, 160, 200)); 

            let mut numbers_hashes = HashMap::new();
            let data_all_zeros_22x8 = vec![0u8; 22 * 8];
            let data_all_192s_22x8 = vec![192u8; 22 * 8];
            numbers_hashes.insert(get_reference_hash(&data_all_zeros_22x8), 0); 
            numbers_hashes.insert(get_reference_hash(&data_all_192s_22x8), 1); 
            
            let result = get_hp_rust(screenshot, mock_bbox, numbers_hashes).unwrap();
            assert_eq!(result, Some(1)); 
        });
    }
    
    #[test] fn test_get_hp_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_hp_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }
    #[test] fn test_get_mana_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_mana_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }
    #[test] fn test_get_capacity_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_capacity_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }
    #[test] fn test_get_speed_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_speed_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }
    #[test] fn test_get_food_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_food_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }
    #[test] fn test_get_stamina_rust_no_bbox() { Python::with_gil(|py| { assert_eq!(get_stamina_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None, HashMap::new()).unwrap(), None); }); }

    // --- Existing Tests (coordinates_are_equal, release_keys) ---
    #[test] fn test_coordinates_are_equal_positive() { assert!(coordinates_are_equal((1, 2, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_x() { assert!(!coordinates_are_equal((0, 2, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_y() { assert!(!coordinates_are_equal((1, 0, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_z() { assert!(!coordinates_are_equal((1, 2, 0), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_all_different() { assert!(!coordinates_are_equal((0, 0, 0), (1, 2, 3))); }
    #[test] fn test_release_keys_with_some_key() { Python::with_gil(|py| { let result = release_keys(py, Some("test_key".to_string())); assert!(result.is_ok()); assert_eq!(result.unwrap(), None); }); }
    #[test] fn test_release_keys_with_none_key() { Python::with_gil(|py| { let result = release_keys(py, None); assert!(result.is_ok()); assert_eq!(result.unwrap(), None); }); }
}
