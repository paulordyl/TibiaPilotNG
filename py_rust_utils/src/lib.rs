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

// --- Helper Functions (existing) ---
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

// --- Skill FFI Functions (existing) ---
#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox, numbers_hashes))]
fn get_hp_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>, 
    numbers_hashes: HashMap<i64, i32>,
) -> PyResult<Option<i32>> {
    if skills_icon_bbox.is_none() { return Ok(None); }
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

// --- ActionBar FFI Functions ---
#[pyfunction]
fn check_specific_cooldown_rust(
    cooldowns_image: PyReadonlyArray2<u8>, 
    area_key: String,
    cooldown_hashes: HashMap<i64, String>,
) -> PyResult<bool> {
    let view = cooldowns_image.as_array();
    let (y_start, y_end, x_start, x_end) = match area_key.as_str() {
        "attack" => (0, 20, 4, 24),
        "healing" => (0, 20, 29, 49),
        "support" => (0, 20, 54, 74),
        _ => return Ok(false), 
    };

    if y_end > view.shape()[0] || x_end > view.shape()[1] {
        return Ok(false); 
    }
    
    let mut region_data = Vec::with_capacity((y_end - y_start) * (x_end - x_start));
    for r in y_start..y_end {
        for c in x_start..x_end {
            region_data.push(view[(r,c)]);
        }
    }

    let hash = hashit_rust(&region_data);

    if let Some(hash_area_key_from_map) = cooldown_hashes.get(&hash) {
        if *hash_area_key_from_map == area_key {
            return Ok(true);
        }
    }
    Ok(false)
}

#[pyfunction]
fn is_action_bar_slot_equipped_rust(
    screenshot: PyReadonlyArray2<u8>,
    left_arrows_x: i32,
    left_arrows_y: i32,
    left_arrows_width: i32,
    slot: u32, 
) -> PyResult<bool> {
    if slot == 0 { return Ok(false); } 
    let slot_i32 = slot as i32;
    let x0 = left_arrows_x + left_arrows_width + (slot_i32 * 2) + ((slot_i32 - 1) * 34);
    let y = left_arrows_y;

    let view = screenshot.as_array();
    
    if y < 0 || x0 < 0 { return Ok(false); }
    let y_usize = y as usize;
    let x_usize = x0 as usize;

    if y_usize >= view.shape()[0] || x_usize >= view.shape()[1] {
        return Ok(false); 
    }
    
    Ok(view[(y_usize, x_usize)] == 41)
}

#[pyfunction]
fn is_action_bar_slot_available_rust(
    screenshot: PyReadonlyArray2<u8>,
    left_arrows_x: i32,
    left_arrows_y: i32,
    left_arrows_width: i32,
    slot: u32, 
) -> PyResult<bool> {
    if slot == 0 { return Ok(true); } 
    let slot_i32 = slot as i32;
    let x0 = left_arrows_x + left_arrows_width + (slot_i32 * 2) + ((slot_i32 - 1) * 34);
    let check_y = left_arrows_y + 1;

    if check_y < 0 || x0 < 0 { return Ok(true); } 
    let check_y_usize = check_y as usize;

    let view = screenshot.as_array();
    let check_x_coords = [x0 + 2, x0 + 4, x0 + 6, x0 + 8, x0 + 10];

    for check_x_offset in check_x_coords.iter() {
        let check_x = *check_x_offset;
        if check_x < 0 { return Ok(true); } 
        
        let check_x_usize = check_x as usize;

        if check_y_usize >= view.shape()[0] || check_x_usize >= view.shape()[1] {
            return Ok(true); 
        }
        if view[(check_y_usize, check_x_usize)] != 54 {
            return Ok(true); 
        }
    }
    Ok(false) 
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
    
    m.add_function(wrap_pyfunction!(check_specific_cooldown_rust, m)?)?;
    m.add_function(wrap_pyfunction!(is_action_bar_slot_equipped_rust, m)?)?;
    m.add_function(wrap_pyfunction!(is_action_bar_slot_available_rust, m)?)?;
    Ok(())
}

// --- Tests ---
#[cfg(test)]
mod tests {
    use super::*;
    use numpy::{PyArray, PyArrayMethods}; 
    use numpy::ndarray::Array; 

    fn get_reference_hash(data: &[u8]) -> i64 {
        let mut hasher = FarmHasher::default();
        hasher.write(data);
        hasher.finish() as i64
    }

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

    // --- New ActionBar Tests ---
    #[test]
    fn test_check_specific_cooldown_rust_scenarios() {
        Python::with_gil(|py| {
            let cooldown_img_width = 78;
            let cooldown_img_height = 20;
            
            let mut cooldown_hashes = HashMap::new();
            let attack_data_raw = vec![1u8; 20 * 20]; 
            let attack_hash = get_reference_hash(&attack_data_raw);
            cooldown_hashes.insert(attack_hash, "attack".to_string());

            let healing_data_raw = vec![2u8; 20 * 20];
            let healing_hash = get_reference_hash(&healing_data_raw);
            cooldown_hashes.insert(healing_hash, "healing".to_string());

            let support_data_raw = vec![3u8; 20 * 20];
            let support_hash = get_reference_hash(&support_data_raw);
            cooldown_hashes.insert(support_hash, "support".to_string());

            // 1. Matching "attack" cooldown
            let mut current_img_data_vec = vec![0u8; cooldown_img_width * cooldown_img_height];
            for r in 0..20 { for c in 4..24 { current_img_data_vec[r * cooldown_img_width + c] = 1; } }
            let cooldowns_image_s1 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(check_specific_cooldown_rust(cooldowns_image_s1, "attack".to_string(), cooldown_hashes.clone()).unwrap());

            // 2. Matching "healing" cooldown
            current_img_data_vec = vec![0u8; cooldown_img_width * cooldown_img_height]; 
            for r in 0..20 { for c in 29..49 { current_img_data_vec[r * cooldown_img_width + c] = 2; } }
            let cooldowns_image_s2 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(check_specific_cooldown_rust(cooldowns_image_s2, "healing".to_string(), cooldown_hashes.clone()).unwrap());
            
            // 3. Matching "support" cooldown
            current_img_data_vec = vec![0u8; cooldown_img_width * cooldown_img_height]; 
            for r in 0..20 { for c in 54..74 { current_img_data_vec[r * cooldown_img_width + c] = 3; } }
            let cooldowns_image_s3 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(check_specific_cooldown_rust(cooldowns_image_s3, "support".to_string(), cooldown_hashes.clone()).unwrap());

            // 4. Hash found, but area_key string does not match
            let mut mismatched_hashes = HashMap::new();
            mismatched_hashes.insert(attack_hash, "healing".to_string()); 
            current_img_data_vec = vec![0u8; cooldown_img_width * cooldown_img_height]; 
            for r in 0..20 { for c in 4..24 { current_img_data_vec[r * cooldown_img_width + c] = 1; } } 
            let cooldowns_image_s4 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(!check_specific_cooldown_rust(cooldowns_image_s4, "attack".to_string(), mismatched_hashes).unwrap());
            
            // 5. Hash not found in the map
            let empty_hashes = HashMap::new(); 
            // Re-use current_img_data_vec which contains data for "attack"
            let cooldowns_image_s5 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(!check_specific_cooldown_rust(cooldowns_image_s5, "attack".to_string(), empty_hashes).unwrap());

            // 6. Unknown area_key string provided
            let cooldowns_image_s6 = create_mock_screenshot_array(py, &current_img_data_vec, cooldown_img_height, cooldown_img_width);
            assert!(!check_specific_cooldown_rust(cooldowns_image_s6, "unknown_key".to_string(), cooldown_hashes.clone()).unwrap());

            // 7. Cooldowns_image is too small
            let small_image_data = vec![0u8; 10 * 10];
            let small_cooldowns_image = create_mock_screenshot_array(py, &small_image_data, 10, 10);
            assert!(!check_specific_cooldown_rust(small_cooldowns_image, "attack".to_string(), cooldown_hashes).unwrap());
        });
    }

    #[test]
    fn test_is_action_bar_slot_equipped_rust_scenarios() {
        Python::with_gil(|py| {
            let mut screenshot_data_vec = vec![0u8; 100 * 100];
            let (rows, cols) = (100, 100);
            let (lx, ly, lw) = (10, 10, 5);
            
            // Scenario 1: Pixel value is 41 (equipped)
            let slot_eq = 1_u32;
            let x0_eq = lx + lw + (slot_eq as i32 * 2) + ((slot_eq as i32 - 1) * 34);
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = 41;
            let screenshot_s1 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(is_action_bar_slot_equipped_rust(screenshot_s1, lx, ly, lw, slot_eq).unwrap());

            // Scenario 2: Pixel value is not 41 (not equipped)
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = 40; 
            let screenshot_s2 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(!is_action_bar_slot_equipped_rust(screenshot_s2, lx, ly, lw, slot_eq).unwrap());
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = 0; 

            // Scenario 3: Target pixel out of bounds
            let screenshot_s3_data = vec![0u8; 100 * 100]; // Fresh data for these checks
            assert!(!is_action_bar_slot_equipped_rust(create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols), 90, 90, 5, 3).unwrap());
            assert!(!is_action_bar_slot_equipped_rust(create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols), -10, 10, 5, 1).unwrap()); 
            assert!(!is_action_bar_slot_equipped_rust(create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols), 10, -10, 5, 1).unwrap()); 

            // Scenario 4: slot is 0
            let screenshot_s4 = create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols); // Can reuse s3_data
            assert!(!is_action_bar_slot_equipped_rust(screenshot_s4, lx, ly, lw, 0).unwrap());
        });
    }

    #[test]
    fn test_is_action_bar_slot_available_rust_scenarios() {
        Python::with_gil(|py| {
            let mut screenshot_data_vec = vec![0u8; 100 * 100];
            let (rows, cols) = (100, 100);
            let (lx, ly, lw) = (10, 10, 5);

            // Scenario 1: All five pixels are 54 (not available / on cooldown)
            let slot_na = 1_u32;
            let x0_na = lx + lw + (slot_na as i32 * 2) + ((slot_na as i32 - 1) * 34);
            let check_y_na = (ly + 1) as usize;
            for i in 0..5 {
                screenshot_data_vec[check_y_na * cols + (x0_na + 2 + i*2) as usize] = 54;
            }
            let screenshot_s1 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(!is_action_bar_slot_available_rust(screenshot_s1, lx, ly, lw, slot_na).unwrap());

            // Scenario 2: At least one pixel is not 54 (available)
            screenshot_data_vec[check_y_na * cols + (x0_na + 2) as usize] = 50; 
            let screenshot_s2 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(is_action_bar_slot_available_rust(screenshot_s2, lx, ly, lw, slot_na).unwrap());
            for i in 0..5 { screenshot_data_vec[check_y_na * cols + (x0_na + 2 + i*2) as usize] = 0; }


            // Scenario 3: One or more pixels out of bounds (available)
            let screenshot_s3_data = vec![0u8; 100*100]; // Fresh data
            assert!(is_action_bar_slot_available_rust(create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols), 90, 90, 5, 3).unwrap()); 

            // Scenario 4: slot is 0 (should be available as per logic)
            let screenshot_s4 = create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols);
            assert!(is_action_bar_slot_available_rust(screenshot_s4, lx, ly, lw, 0).unwrap());
        });
    }
}
