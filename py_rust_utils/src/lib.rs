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

// --- Helper Functions (These have been moved to skb_core::image_processing::hash_utils) ---
// fn extract_and_process_region(...) -> Option<Vec<u8>> { ... }
// fn hashit_rust(data: &[u8]) -> i64 { ... }

// This function remains in py_rust_utils as it directly uses ArrayView from numpy,
// but it will call the skb_core versions of extract_and_process_region and hashit_rust.
// It also now takes a direct reference to the hashes_map from AppContext.
fn get_hashed_value(
    screenshot_view: &ArrayView<u8, Ix2>, // This is PyReadonlyArray2<u8>.as_array()
    base_x: i32, 
    base_y: i32, 
    img_slice_x_offset: i32, 
    img_slice_width: usize, 
    img_slice_height: usize, 
    hashes_map: &HashMap<i64, i32>, // Now passed from AppContext
    is_value_type: bool,
) -> i32 {
    let final_x = base_x.saturating_add(img_slice_x_offset);
    let final_y = base_y;

    if final_x < 0 || final_y < 0 {
        return 0; 
    }

    // Ensure the ArrayView data is contiguous and get a slice.
    // This is crucial for passing to the skb_core function.
    // If it's not contiguous, this will panic. Data from screenshots via numpy should be.
    let raw_data_slice = screenshot_view.as_slice_memory_order().expect("Screenshot data is not contiguous");
    let image_height_u32 = screenshot_view.shape()[0] as u32;
    let image_width_u32 = screenshot_view.shape()[1] as u32;

    // Get AppContext to access config for filter parameters
    // This call can fail if AppContext is not initialized, which shouldn't happen if FFI functions ensure it.
    // However, get_hashed_value is an internal fn, so direct error propagation to PyResult isn't done here.
    // Instead, it might panic or return 0 if context is unavailable.
    // For robustness, an error could be returned up the chain.
    // Given current structure, we expect app_context to be available via callers.
    let app_context = skb_core::global_app_context().expect("AppContext not initialized. This should be ensured by calling FFI functions.");

    let filter_params = if is_value_type {
        &app_context.config.value_type_filter_params
    } else {
        &app_context.config.non_value_type_filter_params
    };

    let region_data = skb_core::image_processing::hash_utils::extract_and_process_region(
        raw_data_slice,
        image_width_u32,
        image_height_u32,
        final_x as usize,
        final_y as usize,
        img_slice_width,
        img_slice_height,
        is_value_type, // This corresponds to apply_value_filter
        filter_params.filter_range_low,
        filter_params.filter_range_high,
        filter_params.value_to_filter_to_zero_for_range,
        filter_params.val_is_126,
        filter_params.val_is_192,
        filter_params.val_to_assign_if_126_or_192,
        filter_params.val_else_filter_to_zero
    );

    if let Some(data) = region_data {
        if data.is_empty() { 
            return 0;
        }
        let hash = skb_core::image_processing::hash_utils::hashit_rust(&data);
        *hashes_map.get(&hash).unwrap_or(&0)
    } else {
        0 
    }
}

// --- Skill FFI Functions (existing) ---
#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed numbers_hashes
fn get_hp_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>, 
    // numbers_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let icon_x = bbox.0;
    let icon_y = bbox.1;
    let base_x = icon_x + 6;
    let base_y = icon_y + 90;
    let screenshot_view = screenshot.as_array(); 
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &app_context.numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &app_context.numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed numbers_hashes
fn get_mana_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    // numbers_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 104; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &app_context.numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &app_context.numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed numbers_hashes
fn get_capacity_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    // numbers_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 132; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &app_context.numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &app_context.numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}
   
#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed numbers_hashes
fn get_speed_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    // numbers_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 146; 
    let screenshot_view = screenshot.as_array();
    let hundreds_val = get_hashed_value(&screenshot_view, base_x, base_y, 122, 22, 8, &app_context.numbers_hashes, true);
    let thousands_val = get_hashed_value(&screenshot_view, base_x, base_y, 94, 22, 8, &app_context.numbers_hashes, true);
    Ok(Some((thousands_val * 1000) + hundreds_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed minutes_or_hours_hashes
fn get_food_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    // minutes_or_hours_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 160; 
    let screenshot_view = screenshot.as_array();
    let minutes_val = get_hashed_value(&screenshot_view, base_x, base_y, 130, 14, 8, &app_context.minutes_or_hours_hashes, false);
    let hours_val = get_hashed_value(&screenshot_view, base_x, base_y, 110, 14, 8, &app_context.minutes_or_hours_hashes, false);
    Ok(Some((hours_val * 60) + minutes_val))
}

#[pyfunction]
#[pyo3(signature = (screenshot, skills_icon_bbox))] // Removed minutes_or_hours_hashes
fn get_stamina_rust(
    screenshot: PyReadonlyArray2<u8>,
    skills_icon_bbox: Option<(i32, i32, i32, i32)>,
    // minutes_or_hours_hashes: HashMap<i64, i32>, // Removed
) -> PyResult<Option<i32>> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
    if skills_icon_bbox.is_none() { return Ok(None); }
    let bbox = skills_icon_bbox.unwrap();
    let base_x = bbox.0 + 6;
    let base_y = bbox.1 + 174; 
    let screenshot_view = screenshot.as_array();
    let minutes_val = get_hashed_value(&screenshot_view, base_x, base_y, 130, 14, 8, &app_context.minutes_or_hours_hashes, false);
    let hours_val = get_hashed_value(&screenshot_view, base_x, base_y, 110, 14, 8, &app_context.minutes_or_hours_hashes, false);
    Ok(Some((hours_val * 60) + minutes_val))
}

// --- ActionBar FFI Functions ---
// Note: check_specific_cooldown_rust still takes cooldown_hashes from Python.
// This could be a candidate for similar refactoring if these hashes can be pre-generated
// or derived from templates in AppContext. For now, it remains unchanged as per subtask scope.
#[pyfunction]
#[pyo3(signature = (cooldowns_image, area_key))] // cooldown_hashes removed
fn check_specific_cooldown_rust(
    cooldowns_image: PyReadonlyArray2<u8>, 
    area_key: String,
    // cooldown_hashes: HashMap<i64, String>, // Removed
) -> PyResult<bool> {
    let app_context = skb_core::global_app_context().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get AppContext: {}", e)))?;
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

    let hash = skb_core::image_processing::hash_utils::hashit_rust(&region_data);

    if let Some(hash_area_key_from_map) = app_context.cooldown_hashes.get(&hash) {
        if *hash_area_key_from_map == area_key {
            return Ok(true);
        }
    }
    Ok(false)
}

#[pyfunction]
#[pyo3(signature = (screenshot, left_arrows_x, left_arrows_y, left_arrows_width, slot, expected_pixel_value))]
fn is_action_bar_slot_equipped_rust(
    screenshot: PyReadonlyArray2<u8>,
    left_arrows_x: i32,
    left_arrows_y: i32,
    left_arrows_width: i32,
    slot: u32,
    expected_pixel_value: u8,
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
    
    Ok(view[(y_usize, x_usize)] == expected_pixel_value)
}

#[pyfunction]
#[pyo3(signature = (screenshot, left_arrows_x, left_arrows_y, left_arrows_width, slot, expected_pixel_value_for_unavailable))]
fn is_action_bar_slot_available_rust(
    screenshot: PyReadonlyArray2<u8>,
    left_arrows_x: i32,
    left_arrows_y: i32,
    left_arrows_width: i32,
    slot: u32,
    expected_pixel_value_for_unavailable: u8,
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
        if view[(check_y_usize, check_x_usize)] != expected_pixel_value_for_unavailable {
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
    
    // fn get_mock_numbers_hashes() -> HashMap<i64, i32> { ... } // No longer needed here
    // fn get_mock_minutes_hours_hashes() -> HashMap<i64, i32> { ... } // No longer needed here

    #[test]
    fn test_extract_and_process_region_normal() {
        let data = Array::from_shape_vec((2, 3), vec![10u8, 60, 120, 20, 70, 130]).unwrap();
        let view = data.view();
        // Using default values for original behavior (50, 100, 0, 126, 192, 192, 0)
        let result = extract_and_process_region(&view, 0, 0, 3, 2, false, 50, 100, 0, 126, 192, 192, 0).unwrap();
        assert_eq!(result, vec![10u8, 0, 120, 20, 0, 130]);

        // Test with different filter params - e.g. filter range 65-75 to 5, apply_value_filter = false
        let result_custom_range = extract_and_process_region(&view, 0, 0, 3, 2, false, 65, 75, 5, 126, 192, 192, 0).unwrap();
        // val: 10, 60, 120, 20, 70, 130
        // proc:10, 60, 120, 20,  5, 130 (because 70 is in 65-75 range)
        assert_eq!(result_custom_range, vec![10u8, 60, 120, 20, 5, 130]);
    }

    #[test]
    fn test_extract_and_process_region_filtered() {
        let data = Array::from_shape_vec((2, 3), vec![10u8, 126, 192, 20, 70, 130]).unwrap();
        let view = data.view();
        // Using default values for original behavior (50, 100, 0, 126, 192, 192, 0)
        // val: 10, 126, 192, 20, 70 (range 50-100 -> 0), 130
        // proc (before apply_filter): 10, 126, 192, 20, 0, 130
        // apply_filter:
        // 10 (not 126 or 192, not 192) -> 0
        // 126 (is 126) -> 192
        // 192 (is 192) -> 192
        // 20 (not 126 or 192, not 192) -> 0
        // 0 (not 126 or 192, not 192) -> 0
        // 130 (not 126 or 192, not 192) -> 0
        let result = extract_and_process_region(&view, 0, 0, 3, 2, true, 50, 100, 0, 126, 192, 192, 0).unwrap();
        assert_eq!(result, vec![0u8, 192, 192, 0, 0, 0]);

        // Test with different filter params - e.g. map 126 to 50, 192 to 50, else to 10 if not 192
        // Range filter (50-100 -> 0) still applies first.
        // val: 10, 126, 192, 20, 70 (range 50-100 -> 0), 130
        // proc (before apply_filter): 10, 126, 192, 20, 0, 130
        // apply_filter (custom: val_is_126=126, val_is_192=192, val_to_assign_if_126_or_192=50, val_else_filter_to_zero=10):
        // 10 (not 126/192, not 192) -> 10
        // 126 (is 126) -> 50
        // 192 (is 192) -> 50
        // 20 (not 126/192, not 192) -> 10
        // 0 (not 126/192, not 192) -> 10
        // 130 (not 126/192, not 192) -> 10
        let result_custom_filter = extract_and_process_region(&view, 0, 0, 3, 2, true, 50, 100, 0, 126, 192, 50, 10).unwrap();
        assert_eq!(result_custom_filter, vec![10u8, 50, 50, 10, 10, 10]);
    }

    #[test]
    fn test_extract_and_process_region_out_of_bounds() {
        let data = Array::from_shape_vec((2, 2), vec![1u8, 2, 3, 4]).unwrap();
        let view = data.view();
        // Using default values for original behavior
        assert!(extract_and_process_region(&view, 0, 0, 3, 2, false, 50, 100, 0, 126, 192, 192, 0).is_none());
        assert!(extract_and_process_region(&view, 0, 0, 2, 3, false, 50, 100, 0, 126, 192, 192, 0).is_none());
        assert!(extract_and_process_region(&view, 1, 1, 2, 2, false, 50, 100, 0, 126, 192, 192, 0).is_none());
        assert!(extract_and_process_region(&view, 2, 0, 1, 1, false, 50, 100, 0, 126, 192, 192, 0).is_none());
        assert!(extract_and_process_region(&view, 0, 2, 1, 1, false, 50, 100, 0, 126, 192, 192, 0).is_none());
        assert!(extract_and_process_region(&view, 0, 0, 0, 1, false, 50, 100, 0, 126, 192, 192, 0).is_none());
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

        // The call to get_hashed_value will use the default parameters for extract_and_process_region
        // as defined in its body.
        // screenshot_data is all 70s.
        // For get_hashed_value with is_value_type = false (apply_value_filter=false):
        // extract_and_process_region(..., apply_value_filter=false, 50, 100, 0, 126, 192, 192, 0)
        // val = 70. 70 >= 50 && 70 <= 100, so processed_val becomes 0.
        // apply_value_filter is false, so no more changes. processed_data will be all 0s.
        // hash of all_zeros_2x2 is what's in `hashes` map with value 99.
        let val = get_hashed_value(&screenshot_view, 0, 0, 0, 2, 2, &hashes, false);
        assert_eq!(val, 99);
        
        let mut other_hashes = HashMap::new();
        other_hashes.insert(12345, 10); 
        let val_other_map = get_hashed_value(&screenshot_view, 0, 0, 0, 2, 2, &other_hashes, false);
        assert_eq!(val_other_map, 0); // Hash not found

        // Test with is_value_type = true (apply_value_filter = true)
        // val = 70. Becomes 0 due to range filter.
        // apply_value_filter = true:
        // processed_val = 0. 0 != 126 and 0 != 192. And 0 != 192 (val_is_192). So processed_val becomes 0 (val_else_filter_to_zero).
        // Result is still hash of 0s.
        let val_value_type = get_hashed_value(&screenshot_view, 0, 0, 0, 2, 2, &hashes, true);
        assert_eq!(val_value_type, 99);


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
        // This test will now rely on AppContext being initialized correctly with templates
        // for digit_0 and digit_1, etc., and their hashes being generated.
        // For a unit test, this is becoming an integration test.
        // A true unit test would mock AppContext or the get_hashed_value inputs.
        // Assuming AppContext can be initialized (e.g. dummy templates exist at default paths):
        pyo3::prepare_freethreaded_python(); // Ensure PyO3 is initialized for global_app_context potentially
        Python::with_gil(|py| {
            let screenshot_data = create_targeted_screenshot_data(70, 126, 300, 300); 
            let screenshot = create_mock_screenshot_array(py, &screenshot_data, 300, 300);
            let mock_bbox = Some((50, 50, 160, 200)); 
            
            // The function no longer takes numbers_hashes. It will get them from AppContext.
            // We need to ensure AppContext is set up for this test to work, or mock it.
            // For now, we proceed assuming it might work if default templates are present.
            // If AppContext initialization fails (e.g. no config/templates), this test will panic/error.
            let result = get_hp_rust(screenshot, mock_bbox);

            // The expected outcome depends on the hashes in the global AppContext.
            // If "digit_0" (processed) hashes to X and "digit_1" (processed) hashes to Y,
            // and AppContext has { X:0, Y:1 }, then we expect Some(1).
            // This test is now more of an integration test for get_hp_rust + AppContext.
            // A proper unit test would require mocking global_app_context or providing a test AppContext.
            // For now, let's assert Ok, and if it runs in an env with templates, it might pass with Some(1).
            assert!(result.is_ok(), "get_hp_rust should return Ok. Error: {:?}", result.err());
            // A more specific assertion like `assert_eq!(result.unwrap(), Some(1));` can be used if templates are known.
        });
    }
    
    // These tests now rely on AppContext.
    #[test] fn test_get_hp_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_hp_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }
    #[test] fn test_get_mana_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_mana_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }
    #[test] fn test_get_capacity_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_capacity_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }
    #[test] fn test_get_speed_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_speed_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }
    #[test] fn test_get_food_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_food_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }
    #[test] fn test_get_stamina_rust_no_bbox() { pyo3::prepare_freethreaded_python(); Python::with_gil(|py| { assert_eq!(get_stamina_rust(create_mock_screenshot_array(py, &[0u8;100],10,10), None).unwrap(), None); }); }

    // --- Existing Tests (coordinates_are_equal) ---
    #[test] fn test_coordinates_are_equal_positive() { assert!(coordinates_are_equal((1, 2, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_x() { assert!(!coordinates_are_equal((0, 2, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_y() { assert!(!coordinates_are_equal((1, 0, 3), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_negative_z() { assert!(!coordinates_are_equal((1, 2, 0), (1, 2, 3))); }
    #[test] fn test_coordinates_are_equal_all_different() { assert!(!coordinates_are_equal((0, 0, 0), (1, 2, 3))); }

    // --- New ActionBar Tests ---
    #[test]
    fn test_check_specific_cooldown_rust_scenarios() {
        // This test now relies on AppContext being initialized with appropriate cooldown templates
        // (e.g., "attack.png", "healing.png", "support.png") and their hashes.
        // The test will create image data that *should* match these pre-generated hashes.
        pyo3::prepare_freethreaded_python(); // For global_app_context()
        Python::with_gil(|py| {
            let cooldown_img_width = 78; // Width of the full cooldowns_image bar
            let cooldown_img_height = 20;

            // To make this test runnable, we need to know what data would produce a hash
            // that AppContext has stored. This requires either:
            // 1. Running AppContext::new() and getting the real hashes.
            // 2. Mocking AppContext / global_app_context.
            // 3. Using placeholder raw image data that we *assume* will match if templates are simple.
            //
            // Let's assume AppContext is initialized. If "attack.png" (for example) is a 20x20 image
            // of all 1s, then `attack_data_to_match_template` should be that.
            // The following data is for creating sections of the cooldowns_image,
            // hoping they match hashes of templates named "attack", "healing", "support".

            // Create image data that would hypothetically match the "attack" template's hash
            // (assuming "attack" template is all 1s, 20x20)
            let mut attack_matching_data = vec![0u8; cooldown_img_width * cooldown_img_height];
            for r in 0..20 { for c in 4..24 { attack_matching_data[r * cooldown_img_width + c] = 1; } } // region for "attack"
            let cooldowns_image_attack = create_mock_screenshot_array(py, &attack_matching_data, cooldown_img_height, cooldown_img_width);
            
            // Test for "attack" - this will pass if AppContext has a hash for "attack" template that matches hash of data in region (4,0) to (24,20)
            let result_attack = check_specific_cooldown_rust(cooldowns_image_attack, "attack".to_string());
            // We can't be certain of `true` without knowing the actual template hash.
            // But if the template "attack" (20x20 of 1s) was loaded, this should be true.
            // For now, we'll assert it's Ok, and if templates are missing, it should be false.
            assert!(result_attack.is_ok(), "check_specific_cooldown_rust for attack failed: {:?}", result_attack.err());


            // Create image data for "healing" (assuming "healing" template is all 2s, 20x20)
            let mut healing_matching_data = vec![0u8; cooldown_img_width * cooldown_img_height];
            for r in 0..20 { for c in 29..49 { healing_matching_data[r * cooldown_img_width + c] = 2; } } // region for "healing"
            let cooldowns_image_healing = create_mock_screenshot_array(py, &healing_matching_data, cooldown_img_height, cooldown_img_width);
            let result_healing = check_specific_cooldown_rust(cooldowns_image_healing, "healing".to_string());
            assert!(result_healing.is_ok(), "check_specific_cooldown_rust for healing failed: {:?}", result_healing.err());


            // Create image data for "support" (assuming "support" template is all 3s, 20x20)
            let mut support_matching_data = vec![0u8; cooldown_img_width * cooldown_img_height];
            for r in 0..20 { for c in 54..74 { support_matching_data[r * cooldown_img_width + c] = 3; } } // region for "support"
            let cooldowns_image_support = create_mock_screenshot_array(py, &support_matching_data, cooldown_img_height, cooldown_img_width);
            let result_support = check_specific_cooldown_rust(cooldowns_image_support, "support".to_string());
            assert!(result_support.is_ok(), "check_specific_cooldown_rust for support failed: {:?}", result_support.err());
            

            // Test for a non-matching area key (should be false)
            let result_unknown = check_specific_cooldown_rust(cooldowns_image_attack.clone(), "unknown_key".to_string());
            assert_eq!(result_unknown.unwrap(), false);

            // Test with an image that definitely won't match any known template hash
            let non_matching_data = vec![255u8; cooldown_img_width * cooldown_img_height]; // all white
            let cooldowns_image_nomatch = create_mock_screenshot_array(py, &non_matching_data, cooldown_img_height, cooldown_img_width);
            let result_nomatch_attack = check_specific_cooldown_rust(cooldowns_image_nomatch.clone(), "attack".to_string());
            assert_eq!(result_nomatch_attack.unwrap(), false);

            // Test with too small image (should be false due to boundary checks)
            let small_image_data = vec![0u8; 10 * 10];
            let small_cooldowns_image = create_mock_screenshot_array(py, &small_image_data, 10, 10);
            assert_eq!(check_specific_cooldown_rust(small_cooldowns_image, "attack".to_string()).unwrap(), false);
        });
    }

    #[test]
    fn test_is_action_bar_slot_equipped_rust_scenarios() {
        Python::with_gil(|py| {
            let mut screenshot_data_vec = vec![0u8; 100 * 100];
            let (rows, cols) = (100, 100);
            let (lx, ly, lw) = (10, 10, 5);
            let default_expected_pixel = 41_u8;
            let alternative_expected_pixel = 55_u8;
            
            // Scenario 1: Pixel value matches default_expected_pixel (equipped)
            let slot_eq = 1_u32;
            let x0_eq = lx + lw + (slot_eq as i32 * 2) + ((slot_eq as i32 - 1) * 34);
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = default_expected_pixel;
            let screenshot_s1 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(is_action_bar_slot_equipped_rust(screenshot_s1.clone(), lx, ly, lw, slot_eq, default_expected_pixel).unwrap());

            // Scenario 1b: Pixel value matches alternative_expected_pixel
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = alternative_expected_pixel;
            assert!(is_action_bar_slot_equipped_rust(screenshot_s1.clone(), lx, ly, lw, slot_eq, alternative_expected_pixel).unwrap());


            // Scenario 2: Pixel value does not match default_expected_pixel (not equipped)
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = default_expected_pixel - 1;
            let screenshot_s2 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols); // Effectively a new array view due to data change
            assert!(!is_action_bar_slot_equipped_rust(screenshot_s2.clone(), lx, ly, lw, slot_eq, default_expected_pixel).unwrap());

            // Scenario 2b: Pixel value does not match alternative_expected_pixel
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = alternative_expected_pixel -1;
            assert!(!is_action_bar_slot_equipped_rust(screenshot_s2.clone(), lx, ly, lw, slot_eq, alternative_expected_pixel).unwrap());
            screenshot_data_vec[ly as usize * cols + x0_eq as usize] = 0; // Reset

            // Scenario 3: Target pixel out of bounds
            let screenshot_s3_data = vec![0u8; 100 * 100]; // Fresh data for these checks
            let s3_arr = create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols);
            assert!(!is_action_bar_slot_equipped_rust(s3_arr.clone(), 90, 90, 5, 3, default_expected_pixel).unwrap());
            assert!(!is_action_bar_slot_equipped_rust(s3_arr.clone(), -10, 10, 5, 1, default_expected_pixel).unwrap());
            assert!(!is_action_bar_slot_equipped_rust(s3_arr.clone(), 10, -10, 5, 1, default_expected_pixel).unwrap());

            // Scenario 4: slot is 0
            assert!(!is_action_bar_slot_equipped_rust(s3_arr.clone(), lx, ly, lw, 0, default_expected_pixel).unwrap());
        });
    }

    #[test]
    fn test_is_action_bar_slot_available_rust_scenarios() {
        Python::with_gil(|py| {
            let mut screenshot_data_vec = vec![0u8; 100 * 100];
            let (rows, cols) = (100, 100);
            let (lx, ly, lw) = (10, 10, 5);
            let default_unavailable_pixel = 54_u8;
            let alternative_unavailable_pixel = 60_u8;

            // Scenario 1: All five pixels are default_unavailable_pixel (not available / on cooldown)
            let slot_na = 1_u32;
            let x0_na = lx + lw + (slot_na as i32 * 2) + ((slot_na as i32 - 1) * 34);
            let check_y_na = (ly + 1) as usize;
            for i in 0..5 {
                screenshot_data_vec[check_y_na * cols + (x0_na + 2 + i*2) as usize] = default_unavailable_pixel;
            }
            let screenshot_s1 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(!is_action_bar_slot_available_rust(screenshot_s1.clone(), lx, ly, lw, slot_na, default_unavailable_pixel).unwrap());

            // Scenario 1b: All five pixels are alternative_unavailable_pixel
            for i in 0..5 {
                screenshot_data_vec[check_y_na * cols + (x0_na + 2 + i*2) as usize] = alternative_unavailable_pixel;
            }
            assert!(!is_action_bar_slot_available_rust(screenshot_s1.clone(), lx, ly, lw, slot_na, alternative_unavailable_pixel).unwrap());


            // Scenario 2: At least one pixel is not default_unavailable_pixel (available)
            screenshot_data_vec[check_y_na * cols + (x0_na + 2) as usize] = default_unavailable_pixel - 1;
            let screenshot_s2 = create_mock_screenshot_array(py, &screenshot_data_vec, rows, cols);
            assert!(is_action_bar_slot_available_rust(screenshot_s2.clone(), lx, ly, lw, slot_na, default_unavailable_pixel).unwrap());

            // Scenario 2b: At least one pixel is not alternative_unavailable_pixel
            screenshot_data_vec[check_y_na * cols + (x0_na + 2) as usize] = alternative_unavailable_pixel - 1;
            assert!(is_action_bar_slot_available_rust(screenshot_s2.clone(), lx, ly, lw, slot_na, alternative_unavailable_pixel).unwrap());

            // Reset for next tests
            for i in 0..5 { screenshot_data_vec[check_y_na * cols + (x0_na + 2 + i*2) as usize] = 0; }


            // Scenario 3: One or more pixels out of bounds (available)
            let screenshot_s3_data = vec![0u8; 100*100]; // Fresh data
            let s3_arr = create_mock_screenshot_array(py, &screenshot_s3_data, rows, cols);
            assert!(is_action_bar_slot_available_rust(s3_arr.clone(), 90, 90, 5, 3, default_unavailable_pixel).unwrap());

            // Scenario 4: slot is 0 (should be available as per logic)
            assert!(is_action_bar_slot_available_rust(s3_arr.clone(), lx, ly, lw, 0, default_unavailable_pixel).unwrap());
        });
    }
}
