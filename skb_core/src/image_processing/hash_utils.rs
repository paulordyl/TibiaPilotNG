use farmhash::FarmHasher;
use std::hash::Hasher;
// Note: ArrayView related imports are removed as we'll use &[u8] and dimensions.

/// Computes a FarmHash for a given byte slice.
pub fn hashit_rust(data: &[u8]) -> i64 {
    let mut hasher = FarmHasher::default();
    hasher.write(data);
    hasher.finish() as i64
}

/// Extracts and processes a region from image data.
/// The input image_data is assumed to be a flat byte array for a 1-channel (e.g., grayscale) image.
pub fn extract_and_process_region(
    image_data: &[u8],
    image_width: u32,
    image_height: u32,
    region_x: usize,      // Top-left x of the region
    region_y: usize,      // Top-left y of the region
    region_width: usize,  // Width of the region to extract
    region_height: usize, // Height of the region to extract
    apply_value_filter: bool,
    filter_range_low: u8,
    filter_range_high: u8,
    value_to_filter_to_zero_for_range: u8,
    val_is_126: u8,
    val_is_192: u8,
    val_to_assign_if_126_or_192: u8,
    val_else_filter_to_zero: u8,
) -> Option<Vec<u8>> {
    if region_width == 0 || region_height == 0 {
        return None;
    }
    // Convert u32 image dimensions to usize for checks
    let image_width_usize = image_width as usize;
    let image_height_usize = image_height as usize;

    if region_y.saturating_add(region_height) > image_height_usize ||
       region_x.saturating_add(region_width) > image_width_usize ||
       region_y >= image_height_usize || region_x >= image_width_usize {
        return None;
    }

    let mut processed_data = Vec::with_capacity(region_width * region_height);
    for r_offset in 0..region_height { // y-offset within the region
        for c_offset in 0..region_width { // x-offset within the region
            let current_y = region_y + r_offset;
            let current_x = region_x + c_offset;

            // Calculate index in the flat image_data array
            let index = (current_y * image_width_usize + current_x) as usize;
            if index >= image_data.len() {
                // This should not happen if boundary checks above are correct
                return None;
            }
            let val = image_data[index];
            let mut processed_val = val;

            if val >= filter_range_low && val <= filter_range_high {
                processed_val = value_to_filter_to_zero_for_range;
            }

            if apply_value_filter {
                if processed_val == val_is_126 || processed_val == val_is_192 {
                    processed_val = val_to_assign_if_126_or_192;
                } else if processed_val != val_is_192 {
                    processed_val = val_else_filter_to_zero;
                }
            }
            processed_data.push(processed_val);
        }
    }
    Some(processed_data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hashit_rust_basic() {
        let data1 = b"hello world";
        let data2 = b"hello world!";
        let hash1 = hashit_rust(data1);
        let hash2 = hashit_rust(data2);
        assert_ne!(hash1, hash2, "Different data should produce different hashes.");

        // Known value test (if you have a pre-calculated farmhash::hash64 value)
        // For example, if farmhash::hash64(b"test") is known:
        // let known_hash = farmhash::hash64(b"test") as i64; // Calculate outside or use a constant
        // assert_eq!(hashit_rust(b"test"), known_hash, "Hash does not match known value.");
        // Using a specific value obtained by running farmhash::hash64(b"test_string")
        assert_eq!(hashit_rust(b"test_string"), 6890505999018069720_i64);
    }

    #[test]
    fn test_hashit_rust_empty() {
        let data_empty = b"";
        let hash_empty = hashit_rust(data_empty);
        // Hash of empty string is consistent
        assert_eq!(hash_empty, 229007098906703908_i64);
    }

    #[test]
    fn test_extract_and_process_region_simple_extraction() {
        let image_data: Vec<u8> = vec![
            10, 20, 30, 40,
            50, 60, 70, 80,
            90,100,110,120,
        ]; // 4x3 image
        let image_width = 4;
        let image_height = 3;

        // Extract 2x2 region from (1,1) -> values should be 60, 70, 100, 110
        // No filters applied yet.
        let params_no_filter = (false, 0,0,0,0,0,0,0); // apply_filter and dummy filter values

        let result = extract_and_process_region(
            &image_data, image_width, image_height,
            1, 1, 2, 2, // region x,y,w,h
            params_no_filter.0, params_no_filter.1, params_no_filter.2, params_no_filter.3,
            params_no_filter.4, params_no_filter.5, params_no_filter.6, params_no_filter.7
        ).unwrap();
        assert_eq!(result, vec![60, 70, 100, 110]);
    }

    #[test]
    fn test_extract_and_process_region_filtering_range() {
        let image_data: Vec<u8> = vec![10, 55, 90, 105]; // 4x1 image
        let image_width = 4;
        let image_height = 1;

        // Filter: range 50-100 to 0. apply_value_filter=false.
        // Expected: 10, 0, 0, 105
        let result = extract_and_process_region(
            &image_data, image_width, image_height,
            0, 0, 4, 1, // Full image
            false, // apply_value_filter
            50, 100, 0, // filter_range_low, high, value_to_filter_to_zero_for_range
            0,0,0,0 // dummy values for other filter params
        ).unwrap();
        assert_eq!(result, vec![10, 0, 0, 105]);
    }

    #[test]
    fn test_extract_and_process_region_filtering_apply_value_filter() {
        // Values: 10, 60 (becomes 0 by range), 126, 192, 150 (not 126 or 192, not 192 -> 0)
        let image_data: Vec<u8> = vec![10, 60, 126, 192, 150];
        let image_width = 5;
        let image_height = 1;

        // Params from default value_type_filter_params
        let filter_range_low = 50;
        let filter_range_high = 100;
        let value_to_filter_to_zero_for_range = 0;
        let val_is_126 = 126;
        let val_is_192 = 192;
        let val_to_assign_if_126_or_192 = 192;
        let val_else_filter_to_zero = 0;

        // Apply value filter: true
        // 10 -> (not in range 50-100) -> 10. Then (apply_filter: 10!=126, 10!=192. 10!=192 -> 0) -> 0
        // 60 -> (in range 50-100) -> 0. Then (apply_filter: 0!=126, 0!=192. 0!=192 -> 0) -> 0
        // 126 -> (not in range) -> 126. Then (apply_filter: 126==126 -> 192) -> 192
        // 192 -> (not in range) -> 192. Then (apply_filter: 192==192 -> 192) -> 192
        // 150 -> (not in range) -> 150. Then (apply_filter: 150!=126, 150!=192. 150!=192 -> 0) -> 0
        // Expected: 0, 0, 192, 192, 0
        let result = extract_and_process_region(
            &image_data, image_width, image_height,
            0, 0, 5, 1, // Full image
            true, // apply_value_filter
            filter_range_low, filter_range_high, value_to_filter_to_zero_for_range,
            val_is_126, val_is_192, val_to_assign_if_126_or_192, val_else_filter_to_zero
        ).unwrap();
        assert_eq!(result, vec![0, 0, 192, 192, 0]);
    }

    #[test]
    fn test_extract_and_process_region_out_of_bounds() {
        let image_data: Vec<u8> = vec![1, 2, 3, 4]; // 2x2 image
        let image_width = 2;
        let image_height = 2;
        let params_no_filter = (false,0,0,0,0,0,0,0);

        assert!(extract_and_process_region(&image_data, image_width, image_height, 0, 0, 3, 2, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region width out of bounds");
        assert!(extract_and_process_region(&image_data, image_width, image_height, 0, 0, 2, 3, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region height out of bounds");
        assert!(extract_and_process_region(&image_data, image_width, image_height, 1, 1, 2, 2, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region x+width out of bounds");
        assert!(extract_and_process_region(&image_data, image_width, image_height, 2, 0, 1, 1, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region x out of bounds");
        assert!(extract_and_process_region(&image_data, image_width, image_height, 0, 2, 1, 1, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region y out of bounds");
    }

    #[test]
    fn test_extract_and_process_region_zero_dimension_region() {
        let image_data: Vec<u8> = vec![1, 2, 3, 4]; // 2x2 image
        let image_width = 2;
        let image_height = 2;
        let params_no_filter = (false,0,0,0,0,0,0,0);

        assert!(extract_and_process_region(&image_data, image_width, image_height, 0, 0, 0, 2, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region width is 0");
        assert!(extract_and_process_region(&image_data, image_width, image_height, 0, 0, 2, 0, params_no_filter.0, params_no_filter.1,params_no_filter.2,params_no_filter.3,params_no_filter.4,params_no_filter.5,params_no_filter.6,params_no_filter.7).is_none(), "Region height is 0");
    }
}
