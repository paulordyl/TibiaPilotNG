use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use numpy::{PyArrayDyn, PyReadonlyArrayDyn, PyArray2, PyReadonlyArray2, PyReadonlyArray3, PyReadwriteArray2, Ix2, IxDyn, IntoPyArray, PyArrayMethods};
use image::{DynamicImage, ImageBuffer, Rgb, Rgba, Luma, ImageError, GenericImageView, Luma as ImageLuma}; // Added ImageLuma for GrayImage
use std::path::Path;
use std::ffi::CStr; // For Tesseract lang string

// Assuming rustesseract is added to Cargo.toml
// For example: rustesseract = "0.8"
// And Tesseract OCR (libtesseract-dev) is installed on the system.
extern crate rustesseract;
use rustesseract::Tesseract;
use once_cell::sync::Lazy; // For global resource manager
use std::collections::HashMap; // For storing templates and hashes
use image::GrayImage; // Specific type for grayscale

// Assuming skb_core::AppError is defined in the crate root (e.g., src/lib.rs or a specific error module)
// For this file to compile correctly, `crate::AppError` must be resolvable.
use crate::AppError;
// If AppError is in a sub-module like `crate::errors::AppError`, adjust the path.
// Example placeholder for AppError if not available directly via `crate::AppError`
// #[derive(Debug)] pub enum AppError { ImageProcessingError(String), IoError(std::io::Error), Other(String), ConfigError(String) }
// impl std::fmt::Display for AppError { fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result { write!(f, "{:?}", self) } }
// impl std::error::Error for AppError {}
// impl From<std::io::Error> for AppError { fn from(e: std::io::Error) -> Self { AppError::IoError(e) } }

// Placeholder for BBox struct if not defined elsewhere (e.g. from matching.rs)
type BBox = (i32, i32, u32, u32); // (x, y, width, height)


// === Global Resource Manager (Simplified) ===
struct GlobalResources {
    arrow_left: DynamicImage,
    arrow_right: DynamicImage,
    cooldown_templates: HashMap<String, DynamicImage>,
    cooldown_group_hashes: HashMap<String, Vec<i64>>,
    group_cooldown_rois: HashMap<String, (u32, u32, u32, u32)>,

    // Resources for skills
    skills_icon_template: DynamicImage,
    numbers_hashes: HashMap<i64, i32>, // Hash -> Value for HP, Mana, Cap, Speed
    minutes_or_hours_hashes: HashMap<i64, i32>, // Hash -> Value for Food, Stamina (time)
    // ROIs for skills relative to the top-left of the skills_icon_template match
    // skill_name -> (offset_x, offset_y, width, height)
    skill_rois: HashMap<String, (u32, u32, u32, u32)>,
}

impl GlobalResources {
    fn new() -> Self {
        let placeholder_luma_img = ImageBuffer::from_pixel(1, 1, ImageLuma([0u8]));
        let placeholder_dynamic_img = DynamicImage::ImageLuma8(placeholder_luma_img.clone());
        
        let mut cooldown_templates = HashMap::new();
        cooldown_templates.insert("exori".to_string(), placeholder_dynamic_img.clone());

        let mut cooldown_group_hashes = HashMap::new();
        cooldown_group_hashes.insert("attack".to_string(), vec![12345, 67890]);
        cooldown_group_hashes.insert("healing".to_string(), vec![11111, 22222]);
        cooldown_group_hashes.insert("support".to_string(), vec![33333, 44444]);

        let mut group_cooldown_rois = HashMap::new();
        group_cooldown_rois.insert("attack".to_string(), (0, 0, 20, 20));
        group_cooldown_rois.insert("healing".to_string(), (22, 0, 20, 20));
        group_cooldown_rois.insert("support".to_string(), (44, 0, 20, 20));

        // Skills resources - placeholders
        let skills_icon_template = placeholder_dynamic_img.clone(); // Replace with actual skills icon template
        
        let mut numbers_hashes = HashMap::new();
        numbers_hashes.insert(111, 100); // Example: hash_of_100_hp_image -> 100
        numbers_hashes.insert(222, 200); // Example: hash_of_200_mana_image -> 200

        let mut minutes_or_hours_hashes = HashMap::new();
        minutes_or_hours_hashes.insert(333, 60); // Example: hash_of_60_stamina_image -> 60 (minutes)
        
        let mut skill_rois = HashMap::new();
        // These ROIs are relative to the top-left of the found skills_icon_template
        // (offsetX, offsetY, width, height)
        // Values need to be determined from the game UI.
        skill_rois.insert("hp".to_string(), (30, 5, 40, 10));       // Example ROI for HP value
        skill_rois.insert("mana".to_string(), (30, 20, 40, 10));    // Example ROI for Mana value
        skill_rois.insert("capacity".to_string(), (30, 35, 40, 10)); // Example ROI for Capacity
        skill_rois.insert("speed".to_string(), (30, 50, 40, 10));   // Example ROI for Speed
        skill_rois.insert("food".to_string(), (30, 65, 40, 10));    // Example ROI for Food (time)
        skill_rois.insert("stamina".to_string(), (30, 80, 40, 10)); // Example ROI for Stamina (time)

        GlobalResources {
            arrow_left: placeholder_dynamic_img.clone(),
            arrow_right: placeholder_dynamic_img.clone(),
            cooldown_templates,
            cooldown_group_hashes,
            group_cooldown_rois,
            skills_icon_template,
            numbers_hashes,
            minutes_or_hours_hashes,
            skill_rois,
        }
    }
}

static GLOBAL_RESOURCES: Lazy<GlobalResources> = Lazy::new(GlobalResources::new);

// Helper to convert PyReadonlyArray2 to GrayImage (Luma8)
fn py_to_gray_image(py_array: PyReadonlyArray2<u8>) -> PyResult<GrayImage> {
    let array = py_array.as_array();
    let (height, width) = (array.shape()[0] as u32, array.shape()[1] as u32);
    let data_slice = array.to_slice().ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get slice from numpy array"))?;
    ImageBuffer::from_raw(width, height, data_slice.to_vec())
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create GrayImage from numpy array"))
}


// Conversion from skb_core's AppError to PyErr
impl From<AppError> for PyErr {
    fn from(err: AppError) -> PyErr {
        // Customize this based on how AppError is structured
        PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("AppError: {}", err))
    }
}

// Conversion from image::ImageError to PyErr
impl From<ImageError> for PyErr {
    fn from(err: ImageError) -> PyErr {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("ImageError: {}", err))
    }
}


// === Helper Functions for Image Conversion ===

fn py_array_dyn_to_dynamic_image(py_array: PyReadonlyArrayDyn<u8>) -> PyResult<DynamicImage> {
    let array = py_array.as_array();
    let dims = array.shape();
    let data_slice = array.to_slice().ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get slice from numpy array's underlying data"))?;
    let data_vec = data_slice.to_vec();

    match dims.len() {
        2 => { // Grayscale HxW
            let (height, width) = (dims[0] as u32, dims[1] as u32);
            ImageBuffer::<Luma<u8>, Vec<u8>>::from_raw(width, height, data_vec)
                .map(DynamicImage::ImageLuma8)
                .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create Grayscale image from 2D numpy array"))
        }
        3 => { // Color HxWxChannels
            let (height, width, channels) = (dims[0] as u32, dims[1] as u32, dims[2] as u32);
            match channels {
                3 => { // RGB
                    ImageBuffer::<Rgb<u8>, Vec<u8>>::from_raw(width, height, data_vec)
                        .map(DynamicImage::ImageRgb8)
                        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create RGB image from 3D numpy array"))
                }
                4 => { // RGBA
                    ImageBuffer::<Rgba<u8>, Vec<u8>>::from_raw(width, height, data_vec)
                        .map(DynamicImage::ImageRgba8)
                        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create RGBA image from 3D numpy array"))
                }
                _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Unsupported channel count in 3D array: {}", channels))),
            }
        }
        _ => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Unsupported array dimensions: {}. Expected 2 (HxW) or 3 (HxWxC).", dims.len()))),
    }
}

fn py_array2_to_dynamic_image_luma(py_array: PyReadonlyArray2<u8>) -> PyResult<DynamicImage> {
    let array = py_array.as_array();
    let (height, width) = (array.shape()[0] as u32, array.shape()[1] as u32);
    let data_slice = array.to_slice().ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get slice from PyReadonlyArray2"))?;
    let data_vec = data_slice.to_vec();
    ImageBuffer::<Luma<u8>, Vec<u8>>::from_raw(width, height, data_vec)
        .map(DynamicImage::ImageLuma8)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create Grayscale image from 2D numpy array"))
}

// For convert_bgra_to_grayscale, prompt specified PyReadonlyArray2<u8> but also "4 channels".
// This is conflicting. A HxW PyArray2 cannot have 4 channels directly.
// It could be H x (W*4) or Python side ensures a 1D view of H*W*4 data is cast to this 2D type.
// A more type-safe PyO3 signature would be PyReadonlyArray3<u8> (HxWx4) or PyReadonlyArrayDyn<u8>.
// I will use PyReadonlyArray3<u8> as it's unambiguous for HxWx4.
fn py_array3_bgra_to_dynamic_image_rgba(py_array: PyReadonlyArray3<u8>) -> PyResult<DynamicImage> {
    let array = py_array.as_array(); // This is ArrayView3<u8>
    let dims = array.shape(); // (height, width, channels)
    
    if dims[2] != 4 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Input array for BGRA conversion must have 4 channels, got {}", dims[2])
        ));
    }
    let height = dims[0] as u32;
    let width = dims[1] as u32;

    let data_slice = array.to_slice().ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get slice for BGRA array"))?;
    let mut bgra_data = data_slice.to_vec();

    // Swap B and R channels to convert BGRA to RGBA
    for chunk in bgra_data.chunks_exact_mut(4) {
        chunk.swap(0, 2); // BGRA -> RGBA
    }

    ImageBuffer::<Rgba<u8>, Vec<u8>>::from_raw(width, height, bgra_data)
        .map(DynamicImage::ImageRgba8)
        .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to create RGBA image from BGRA numpy array data"))
}


fn dynamic_image_to_py_array_dyn(py: Python, img: &DynamicImage) -> PyResult<Py<PyArrayDyn<u8>>> {
    let (height, width) = img.dimensions();
    let py_array = match img {
        DynamicImage::ImageLuma8(buf) => {
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize]))
        }
        DynamicImage::ImageLumaA8(buf) => {
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize, 2]))
        }
        DynamicImage::ImageRgb8(buf) => {
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize, 3]))
        }
        DynamicImage::ImageRgba8(buf) => {
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize, 4]))
        }
        DynamicImage::ImageBgr8(buf) => { // image crate >= 0.24
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize, 3]))
        }
        DynamicImage::ImageBgra8(buf) => { // image crate >= 0.24
            PyArrayDyn::from_slice(py, buf.as_raw(), IxDyn(&[height as usize, width as usize, 4]))
        }
        _ => { // Convert to a common format like RGBA8 if not directly supported
            let rgba_img = img.to_rgba8();
            PyArrayDyn::from_slice(py, rgba_img.as_raw(), IxDyn(&[height as usize, width as usize, 4]))
        }
    };
    Ok(py_array.to_owned(py)) // into_pyarray creates a copy
}

fn dynamic_image_to_py_array2_luma(py: Python, img: &DynamicImage) -> PyResult<Py<PyArray2<u8>>> {
    let gray_img = img.to_luma8(); // This creates a new ImageBuffer (grayscale)
    let (height, width) = gray_img.dimensions();
    let data_vec = gray_img.into_raw(); // Consumes gray_img
    Ok(PyArray2::from_vec(py, data_vec, Ix2(height as usize, width as usize)).to_owned(py))
}


// === PyO3 Functions ===

#[pyfunction]
fn locate_template(
    py: Python,
    haystack: PyReadonlyArray2<u8>, 
    needle: PyReadonlyArray2<u8>,   
    confidence: f32,
) -> PyResult<Option<(i32, i32, u32, u32)>> {
    let haystack_img = py_array2_to_dynamic_image_luma(haystack)?;
    let needle_img = py_array2_to_dynamic_image_luma(needle)?;

    // Call the existing Rust logic from skb_core::image_processing::matching
    match crate::image_processing::matching::locate_template_on_image(&haystack_img, &needle_img, confidence) {
        Ok(Some((x, y, w, h))) => Ok(Some((x, y, w as u32, h as u32))),
        Ok(None) => Ok(None),
        Err(e) => Err(e.into()), 
    }
}

#[pyfunction]
fn locate_all_templates(
    py: Python,
    haystack: PyReadonlyArray2<u8>, 
    needle: PyReadonlyArray2<u8>,   
    confidence: f32,
) -> PyResult<Vec<(i32, i32, u32, u32)>> {
    let haystack_img = py_array2_to_dynamic_image_luma(haystack)?;
    let needle_img = py_array2_to_dynamic_image_luma(needle)?;
    let default_max_overlap = 0.3; 

    match crate::image_processing::matching::locate_all_templates_on_image(&haystack_img, &needle_img, confidence, default_max_overlap) {
        Ok(results) => Ok(results), 
        Err(e) => Err(e.into()),
    }
}

#[pyfunction]
fn convert_bgra_to_grayscale(py: Python, bgra_image_array3: PyReadonlyArray3<u8>) -> PyResult<Py<PyArray2<u8>>> {
    // Changed signature to PyReadonlyArray3<u8> for clarity (HxWx4 for BGRA)
    let dynamic_img = py_array3_bgra_to_dynamic_image_rgba(bgra_image_array3)?; // BGRA to RGBA DynamicImage
    dynamic_image_to_py_array2_luma(py, &dynamic_img) // RGBA to Luma PyArray2
}

#[pyfunction]
fn hash_image_data(image_array: PyReadonlyArray2<u8>) -> PyResult<u64> {
    let data_slice = image_array.as_slice()?;
    Ok(farmhash::hash64(data_slice))
}

#[pyfunction]
fn load_image(py: Python, path: String) -> PyResult<Py<PyArrayDyn<u8>>> {
    let img = image::io::Reader::open(path)?.decode()?;
    dynamic_image_to_py_array_dyn(py, &img)
}

#[pyfunction]
fn convert_to_grayscale(py: Python, image_array_dyn: PyReadonlyArrayDyn<u8>) -> PyResult<Py<PyArray2<u8>>> {
    let dynamic_img = py_array_dyn_to_dynamic_image(image_array_dyn)?;
    dynamic_image_to_py_array2_luma(py, &dynamic_img)
}

#[pyfunction]
fn load_image_as_grayscale(py: Python, path: String) -> PyResult<Py<PyArray2<u8>>> {
    let img = image::io::Reader::open(path)?.decode()?; 
    dynamic_image_to_py_array2_luma(py, &img)
}

#[pyfunction]
fn crop_image(
    py: Python,
    image_array_dyn: PyReadonlyArrayDyn<u8>,
    x: u32,
    y: u32,
    width: u32,
    height: u32,
) -> PyResult<Py<PyArrayDyn<u8>>> {
    let mut dynamic_img = py_array_dyn_to_dynamic_image(image_array_dyn)?; // mut for crop_imm
    if x + width > dynamic_img.width() || y + height > dynamic_img.height() {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Crop dimensions out of bounds"));
    }
    let cropped_img = dynamic_img.crop_imm(x, y, width, height);
    dynamic_image_to_py_array_dyn(py, &cropped_img)
}

#[pyfunction]
fn save_image(_py: Python, image_array_dyn: PyReadonlyArrayDyn<u8>, path: String) -> PyResult<()> {
    // _py is not used here, but often good practice to keep it if other helpers might need it.
    let dynamic_img = py_array_dyn_to_dynamic_image(image_array_dyn)?;
    dynamic_img.save(path)?; 
    Ok(())
}

#[pyfunction]
fn coordinates_are_equal(first_coordinate: (i32, i32, i32), second_coordinate: (i32, i32, i32)) -> bool {
    first_coordinate == second_coordinate
}

#[pyfunction]
fn release_keys(_py: Python, last_pressed_key: Option<String>) -> PyResult<Option<String>> {
    if let Some(key) = last_pressed_key {
        println!("Rust: keyUp({}) would be called here (from python_utils.rs).", key);
    }
    Ok(None)
}

#[pymodule]
fn rust_utils_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(coordinates_are_equal, m)?)?;
    m.add_function(wrap_pyfunction!(release_keys, m)?)?;
    m.add_function(wrap_pyfunction!(locate_template, m)?)?;
    m.add_function(wrap_pyfunction!(locate_all_templates, m)?)?;
    m.add_function(wrap_pyfunction!(convert_bgra_to_grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(hash_image_data, m)?)?;
    m.add_function(wrap_pyfunction!(load_image, m)?)?;
    m.add_function(wrap_pyfunction!(convert_to_grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(load_image_as_grayscale, m)?)?;
    m.add_function(wrap_pyfunction!(crop_image, m)?)?;
    m.add_function(wrap_pyfunction!(save_image, m)?)?;
    m.add_function(wrap_pyfunction!(filter_grays_to_black, m)?)?;
    m.add_function(wrap_pyfunction!(perform_ocr_on_slot_image, m)?)?;
    m.add_function(wrap_pyfunction!(has_cooldown_by_name, m)?)?;
    m.add_function(wrap_pyfunction!(check_cooldown_status, m)?)?;
    m.add_function(wrap_pyfunction!(get_action_bar_roi, m)?)?;
    m.add_function(wrap_pyfunction!(is_slot_equipped, m)?)?;
    m.add_function(wrap_pyfunction!(is_slot_available, m)?)?;
    // Skills functions
    m.add_function(wrap_pyfunction!(get_skills_icon_roi, m)?)?;
    m.add_function(wrap_pyfunction!(get_hp, m)?)?;
    m.add_function(wrap_pyfunction!(get_mana, m)?)?;
    m.add_function(wrap_pyfunction!(get_capacity, m)?)?;
    m.add_function(wrap_pyfunction!(get_speed, m)?)?;
    m.add_function(wrap_pyfunction!(get_food, m)?)?;
    m.add_function(wrap_pyfunction!(get_stamina, m)?)?;
    Ok(())
}

// Notes for successful compilation as part of skb_core:
// 1. `crate::AppError` must be defined and accessible.
//    If it's in `src/lib.rs` as `pub enum AppError { ... }`, `use crate::AppError;` is correct.
//    If it's in `src/errors.rs` as `pub enum AppError { ... }` and `src/lib.rs` has `pub mod errors;`,
//    then `use crate::errors::AppError;` would be needed.
//
// 2. `crate::image_processing::matching::locate_template_on_image` and `locate_all_templates_on_image`
//    must exist and have compatible signatures.
//
// 3. `Cargo.toml` for `skb_core` must include:
//    [dependencies]
//    pyo3 = { version = "0.20", features = ["extension-module", "numpy"] } # Or your current pyo3 version
//    numpy = "0.20" # Or version compatible with pyo3's numpy feature
//    image = { version = "0.24", features = ["png", "jpeg", "bmp", "gif"] } # Ensure necessary image format features
//    farmhash = "1.1.1" # Or version from py_rust_utils
//
// 4. The `[lib]` section in `skb_core/Cargo.toml` should define the crate as a `cdylib`:
//    [lib]
//    name = "skb_core" # Or your desired library name
//    crate-type = ["cdylib", "rlib"] # cdylib for Python, rlib for Rust usage
//
// 5. The `python_utils.rs` file should be part of the library, declared in `skb_core/src/lib.rs`:
//    pub mod python_utils;
//    (and `pub use python_utils::rust_utils_module;` if you want to re-export the PyO3 module function directly)

// The helper `py_array3_bgra_to_dynamic_image_rgba` now expects `PyReadonlyArray3<u8>` (HxWx4) for BGRA data.
// This means the Python call to `convert_bgra_to_grayscale` must pass a NumPy array with 3 dimensions.
// If the original C-FFI `convert_bgra_to_grayscale_rust` indeed took a 2D array for BGRA data,
// it implies some specific data layout (e.g., flattened, or H x W*4) that would need to be
// handled carefully in the conversion. `PyReadonlyArray3<u8>` is more standard for HxWx4 images.
// The prompt's original signature `convert_bgra_to_grayscale(bgra_image: PyReadonlyArray2<u8>)`
// with the comment "assuming BGRA input has 4 channels" is ambiguous for a 2D array type.
// I've opted for the clearer `PyReadonlyArray3<u8>`. If strict adherence to `PyReadonlyArray2<u8>`
// for 4-channel data is required, the `py_array_dyn_to_dynamic_image` would need to infer
// BGRA from a 2D shape, which is non-standard (e.g. by checking if width is multiple of 4).
// Or, the Python side would have to pass a view of the array that makes it 2D.
// For now, `PyReadonlyArray3<u8>` is the most robust interpretation of "BGRA with 4 channels".

// === Rust function for image filtering (from previous step) ===

#[pyfunction]
fn filter_grays_to_black(mut image_array: PyReadwriteArray2<u8>) -> PyResult<()> {
    let mut array = image_array.as_array_mut();
    // Iterate over the array and modify pixel values in place.
    // This uses ndarray's indexed iteration.
    for val in array.iter_mut() {
        if *val >= 50 && *val <= 100 {
            *val = 0;
        }
    }
    Ok(())
}

// === New Rust function for OCR ===

#[pyfunction]
fn perform_ocr_on_slot_image(slot_image_array: PyReadonlyArray2<u8>) -> PyResult<Option<i32>> {
    let array = slot_image_array.as_array();
    let (height, width) = (array.shape()[0] as u32, array.shape()[1] as u32);
    let data_slice = array.to_slice().ok_or_else(|| 
        PyErr::new::<pyo3::exceptions::PyValueError, _>("Failed to get slice from slot_image_array")
    )?;

    // Initialize Tesseract
    // TODO: Consider if Tesseract instance can be cached/reused if this function is called frequently.
    // For now, initialize per call. Path to Tesseract data might be needed if not in standard location.
    let mut ht = match Tesseract::new(None, Some("eng")) {
        Ok(t) => t,
        Err(e) => {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to initialize Tesseract: {}", e)));
        }
    };

    // Set Page Segmentation Mode (PSM) - 7 assumes a single text line.
    // This matches the config used in the Python version.
    // `rustesseract` might not expose PSM directly in `new`.
    // It might be available via `set_variable` or might need to be part of tesseract config files.
    // For `rustesseract` 0.8, direct PSM setting via a simple function call isn't obvious from docs.
    // It might pick up `tessedit_pageseg_mode` if set as an environment variable or in a Tesseract config file.
    // Or, we might need to use lower-level C API via `leptonica_plumbing` if `rustesseract` doesn't expose it.
    // For now, we proceed without explicit PSM setting here, relying on Tesseract's default or external config.
    // If `rustesseract` has `set_page_seg_mode`, it would be used here.
    // Example: ht.set_page_seg_mode(rustesseract::PageSegMode::PsmSingleLine); (This is hypothetical)

    // It seems `rustesseract`'s `set_image` takes a path. To use in-memory data,
    // we might need to save to a temporary file, or use a different binding/method if available.
    // `Tesseract::set_image_from_mem` seems to be what we need.
    // It expects `&[u8]` image data, width, height, and bytes_per_pixel.
    // For a grayscale image (Luma<u8>), bytes_per_pixel is 1.

    // Set the image data for Tesseract
    // The `set_image_from_mem` function in `rustesseract` expects raw pixel data.
    if let Err(e) = ht.set_image_from_mem(data_slice, width as i32, height as i32, 1) { // 1 byte per pixel for Luma8
        return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Tesseract: failed to set image from memory: {}", e)));
    }
    
    // Perform OCR
    if let Err(e) = ht.recognize() {
         return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Tesseract: recognition failed: {}", e)));
    }

    // Get text. `get_text` returns Result<String, String_>. `String_` is from `leptonica-sys`.
    let text_result = ht.get_text();
    match text_result {
        Ok(ocr_text_cstr) => {
            // The text from `rustesseract::Tesseract::get_text` is a CString-like object from leptonica_plumbing.
            // It needs to be converted to a Rust String.
            // Assuming `ocr_text_cstr` is `leptonica_plumbing::string::String_` which can be dereferenced to `CStr`.
            let ocr_text_str = match ocr_text_cstr.as_c_str().to_str() {
                 Ok(s) => s,
                 Err(_) => return Ok(None), // Or error if text is not valid UTF-8
            };

            // Clean the text: remove non-digits and whitespace
            let cleaned_text: String = ocr_text_str.chars().filter(|c| c.is_digit(10)).collect();

            if cleaned_text.is_empty() {
                Ok(None)
            } else {
                match cleaned_text.parse::<i32>() {
                    Ok(num) => Ok(Some(num)),
                    Err(_) => Ok(None), // Failed to parse, treat as no number found
                }
            }
        }
        Err(e) => {
            // e might be leptonica_plumbing::string::String_ if that's the error type
            // For simplicity, convert to a generic error message.
             Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Tesseract: failed to get text: {:?}", e) // Adjust formatting based on actual error type
            ))
        }
    }
}


// === Cooldown Detection Logic ===

fn extract_cooldown_area_internal(
    full_screenshot_dyn: &DynamicImage, // Changed to DynamicImage to use matching
    res: &GlobalResources
) -> PyResult<Option<DynamicImage>> {
    // Use locate_template_on_image from matching.rs (assumed to take DynamicImage)
    // Confidence for arrow location, can be high.
    let confidence = 0.8; 

    let left_arrow_bbox = crate::image_processing::matching::locate_template_on_image(
        full_screenshot_dyn,
        &res.arrow_left, // This is a DynamicImage
        confidence,
    )
    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Error locating left arrow: {}", e)))?
    .map(|(_x, _y, _w, _h)| (_x, _y as u32, _w, _h)); // Convert y to u32 for consistency if needed by BBox type

    let right_arrow_bbox = crate::image_processing::matching::locate_template_on_image(
        full_screenshot_dyn,
        &res.arrow_right, // This is a DynamicImage
        confidence,
    )
    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Error locating right arrow: {}", e)))?
    .map(|(_x, _y, _w, _h)| (_x, _y as u32, _w, _h));

    if let (Some(left_pos), Some(right_pos)) = (left_arrow_bbox, right_arrow_bbox) {
        let y_start = left_pos.1 + 37; // y-coordinate from BBox tuple
        let height = 22; // Fixed height
        let x_start = left_pos.0 as u32; // x-coordinate from BBox tuple (assuming it's i32, cast to u32)
        // Ensure right_pos.0 is greater than left_pos.0 before calculating width
        if right_pos.0 <= left_pos.0 {
             return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Right arrow is not to the right of left arrow."));
        }
        let width = (right_pos.0 - left_pos.0) as u32;

        // Boundary checks for cropping
        if x_start + width > full_screenshot_dyn.width() || y_start + height > full_screenshot_dyn.height() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Cooldown area crop region out of screenshot bounds."));
        }
        
        let cropped_area = full_screenshot_dyn.crop_imm(x_start, y_start, width, height);
        Ok(Some(cropped_area))
    } else {
        Ok(None) // Arrows not found
    }
}

#[pyfunction]
fn has_cooldown_by_name(screenshot_array: PyReadonlyArray2<u8>, name: String) -> PyResult<bool> {
    let full_screenshot_gray = py_array2_to_dynamic_image_luma(screenshot_array)?; // To DynamicImage Luma8
    let res = &GLOBAL_RESOURCES; // Access global resources

    if let Some(cooldown_area_img) = extract_cooldown_area_internal(&full_screenshot_gray, res)? {
        if let Some(cooldown_template) = res.cooldown_templates.get(&name) {
            // Confidence for cooldown template matching
            let confidence = 0.8; 
            match crate::image_processing::matching::locate_template_on_image(
                &cooldown_area_img,
                cooldown_template,
                confidence,
            ) {
                Ok(Some(pos)) => {
                    // pos is (x, y, width, height) relative to cooldown_area_img
                    // Python logic: listOfCooldownsImage[20:21, cooldownImagePosition[0]:cooldownImagePosition[0] + cooldownImagePosition[2]][0][0] == 255
                    // This means check pixel at (pos.0, 20) in cooldown_area_img
                    let check_x = pos.0 as u32;
                    let check_y = 20u32; // Fixed Y offset from Python code

                    if check_x < cooldown_area_img.width() && check_y < cooldown_area_img.height() {
                        // Convert DynamicImage to GrayImage to use get_pixel easily
                        let cooldown_area_gray = cooldown_area_img.to_luma8();
                        let pixel_value = cooldown_area_gray.get_pixel(check_x, check_y).0[0];
                        Ok(pixel_value == 255)
                    } else {
                        Ok(False) // Cooldown found but check point is out of bounds (should not happen if template is smaller than area)
                    }
                }
                Ok(None) => Ok(False), // Template not found
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Error during template matching for cooldown {}: {}", name, e))),
            }
        } else {
            Ok(False) // Cooldown template name not found in resources
        }
    } else {
        Ok(False) // Cooldown area not found
    }
}

// === Action Bar Slot Status Logic ===

#[pyfunction]
fn get_action_bar_roi(screenshot_array: PyReadonlyArray2<u8>) -> PyResult<Option<(i32, i32, u32, u32)>> {
    let full_screenshot_dyn = py_array2_to_dynamic_image_luma(screenshot_array)?;
    let res = &GLOBAL_RESOURCES;
    let confidence = 0.8;

    match crate::image_processing::matching::locate_template_on_image(
        &full_screenshot_dyn,
        &res.arrow_left, // Assuming this is the primary anchor for the ROI
        confidence,
    ) {
        Ok(Some(bbox)) => Ok(Some(bbox)), // bbox is (i32, i32, u32, u32)
        Ok(None) => Ok(None),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Error locating left arrow for ROI: {}", e))),
    }
}

#[pyfunction]
fn is_slot_equipped(
    screenshot_array: PyReadonlyArray2<u8>, 
    slot: u32, 
    bar_x: i32, // X-coordinate of the located left arrow (action bar anchor)
    bar_y: i32, // Y-coordinate of the located left arrow
    left_arrow_width: u32
) -> PyResult<bool> {
    let screenshot = screenshot_array.as_array();
    // Logic based on the structure: bar_x + left_arrow_width gives start of slots area
    // Each slot is 34px wide, with 2px spacing.
    // Slot index `slot` is 1-based in Python, convert to 0-based for calculation if necessary,
    // but u32 from Python implies it's already 0-indexed or handled by caller.
    // Assuming `slot` is 0-indexed for direct use here.
    // The Python code used `(slot * 2) + ((slot - 1) * 34)` for 1-indexed slot.
    // If slot is 0-indexed: (slot_idx * 2) + (slot_idx * 34) = slot_idx * 36
    // If slot is 1-indexed (as in Python code): ((slot-1) * 36)
    // Let's assume Python passes 0-indexed slot for u32, or adjusts.
    // For PyO3, u32 usually means direct non-negative integer.
    // The original Python `slot` arg was 1-indexed. If we maintain that for the PyO3 interface:
    if slot == 0 { return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Slot number should be 1-indexed.")); }
    let slot_idx = slot - 1;

    // Calculate the X offset for the specific slot's check pixel
    // This is a simplified placeholder for the pixel check.
    // The original FFI is_action_bar_slot_equipped_rust had specific logic.
    // Example: Check a pixel roughly in the middle of the slot.
    let slot_start_x = bar_x as u32 + left_arrow_width + (slot_idx * 36); // Each slot area including spacing
    let check_x = slot_start_x + 17; // Mid-point of a 34px slot part
    
    // Y-coordinate for check pixel (e.g., middle of the slot height)
    // Action bar slot height is 34px.
    let check_y = bar_y as u32 + 17; // Mid-point vertically

    if check_x >= screenshot.shape()[1] as u32 || check_y >= screenshot.shape()[0] as u32 {
        // print!("Slot check coordinates out of bounds");
        return Ok(false); // Or raise error
    }

    let pixel_value = screenshot[[check_y as usize, check_x as usize]];
    
    // Placeholder logic: if pixel is not very dark, assume it's equipped.
    // This needs to be replaced with the actual logic from the old Rust FFI function.
    Ok(pixel_value > 30) // Example threshold
}

#[pyfunction]
fn is_slot_available(
    screenshot_array: PyReadonlyArray2<u8>, 
    slot: u32, 
    bar_x: i32, 
    bar_y: i32, 
    left_arrow_width: u32
) -> PyResult<bool> {
    let screenshot = screenshot_array.as_array();
    if slot == 0 { return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Slot number should be 1-indexed.")); }
    let slot_idx = slot - 1;

    // Calculate the X offset for the specific slot's check pixel
    let slot_start_x = bar_x as u32 + left_arrow_width + (slot_idx * 36);
    let check_x = slot_start_x + 17; // Mid-point of a 34px slot
    
    // Y-coordinate (e.g., specific location for cooldown indicator)
    // The Python code for cooldowns checks a pixel at y=20 relative to the cooldown area.
    // Slot availability might be a different check (e.g., not red, not gray number).
    // Let's use a y-offset within the slot, e.g., top part for a color check.
    let check_y = bar_y as u32 + 5; // Example: check near the top of the slot

    if check_x >= screenshot.shape()[1] as u32 || check_y >= screenshot.shape()[0] as u32 {
        // print!("Slot availability check coordinates out of bounds");
        return Ok(true); // Default to available if out of bounds, or handle as error
    }

    let pixel_value = screenshot[[check_y as usize, check_x as usize]];

    // Placeholder logic: if pixel is not a typical cooldown color (e.g., red or dark gray),
    // it's available. This is highly dependent on the game's UI.
    // Example: assume cooldown makes pixel < 100 (dark/gray) or a specific red color.
    // For simplicity, if it's not very dark, assume available.
    Ok(pixel_value > 50) // Example: not too dark, so not a number, not a dark overlay
}

// === Skills Reading Logic ===

#[pyfunction]
fn get_skills_icon_roi(screenshot_array: PyReadonlyArray2<u8>) -> PyResult<Option<BBox>> {
    let full_screenshot_dyn = py_array2_to_dynamic_image_luma(screenshot_array)?;
    let res = &GLOBAL_RESOURCES;
    let confidence = 0.8; // Confidence for skills icon template matching

    match crate::image_processing::matching::locate_template_on_image(
        &full_screenshot_dyn,
        &res.skills_icon_template,
        confidence,
    ) {
        Ok(Some(bbox)) => Ok(Some(bbox)), // bbox is (i32, i32, u32, u32)
        Ok(None) => Ok(None),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Error locating skills icon: {}", e))),
    }
}

/// Internal helper to extract a specific skill region, hash it, and return the hash.
fn rust_extract_and_hash_skill_region(
    screenshot_dyn: &DynamicImage,
    skills_icon_bbox: BBox, // (x, y, w, h) of the found main skills icon
    skill_roi_key: &str,    // e.g., "hp", "mana"
    res: &GlobalResources,
) -> PyResult<Option<i64>> {
    if let Some(relative_roi) = res.skill_rois.get(skill_roi_key) {
        let (roi_offset_x, roi_offset_y, roi_width, roi_height) = *relative_roi;

        // Calculate absolute coordinates for the skill value region
        let absolute_roi_x = skills_icon_bbox.0 as u32 + roi_offset_x;
        let absolute_roi_y = skills_icon_bbox.1 as u32 + roi_offset_y;

        // Boundary check
        if absolute_roi_x + roi_width > screenshot_dyn.width() || absolute_roi_y + roi_height > screenshot_dyn.height() {
            // eprintln!("Skill ROI for {} is out of bounds.", skill_roi_key);
            return Ok(None); // Or return an error
        }

        let skill_value_region_dyn = screenshot_dyn.crop_imm(
            absolute_roi_x,
            absolute_roi_y,
            roi_width,
            roi_height,
        );
        
        let skill_value_luma = skill_value_region_dyn.to_luma8();
        let data_slice = skill_value_luma.as_raw();
        let hash = farmhash::hash64(data_slice);
        Ok(Some(hash))
    } else {
        // eprintln!("Skill ROI key {} not found in GlobalResources.", skill_roi_key);
        Ok(None) // Skill ROI definition not found
    }
}

// Macro to generate skill getter functions
macro_rules! generate_skill_getter {
    ($func_name:ident, $skill_key:expr, $hash_map_field:ident) => {
        #[pyfunction]
        fn $func_name(
            screenshot_array: PyReadonlyArray2<u8>,
            skills_icon_bbox: BBox, // (x, y, w, h) of the located skills icon
        ) -> PyResult<Option<i32>> {
            let screenshot_dyn = py_array2_to_dynamic_image_luma(screenshot_array)?;
            let res = &GLOBAL_RESOURCES;

            match rust_extract_and_hash_skill_region(&screenshot_dyn, skills_icon_bbox, $skill_key, res)? {
                Some(hash) => {
                    if let Some(value) = res.$hash_map_field.get(&hash) {
                        Ok(Some(*value))
                    } else {
                        Ok(None) // Hash not found in the specific map
                    }
                }
                None => Ok(None), // Region extraction or hashing failed
            }
        }
    };
}

// Generate PyO3 functions for each skill
generate_skill_getter!(get_hp, "hp", numbers_hashes);
generate_skill_getter!(get_mana, "mana", numbers_hashes);
generate_skill_getter!(get_capacity, "capacity", numbers_hashes);
generate_skill_getter!(get_speed, "speed", numbers_hashes);
// Assuming food and stamina might use a different hash map or representation (e.g. time)
// If they use the same numbers_hashes for numerical values:
generate_skill_getter!(get_food, "food", minutes_or_hours_hashes); // Or numbers_hashes if direct number
generate_skill_getter!(get_stamina, "stamina", minutes_or_hours_hashes);

#[pyfunction]
fn check_cooldown_status(screenshot_array: PyReadonlyArray2<u8>, group_name: String) -> PyResult<bool> {
    let full_screenshot_gray = py_array2_to_dynamic_image_luma(screenshot_array)?;
    let res = &GLOBAL_RESOURCES;

    if let Some(cooldown_area_img) = extract_cooldown_area_internal(&full_screenshot_gray, res)? {
        if let Some(roi_coords) = res.group_cooldown_rois.get(&group_name) {
            let (x, y, w, h) = *roi_coords;
            if x + w > cooldown_area_img.width() || y + h > cooldown_area_img.height() {
                 return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("ROI for group {} exceeds cooldown area bounds.", group_name)));
            }
            let group_roi_img_dyn = cooldown_area_img.crop_imm(x, y, w, h);
            
            // Convert to GrayImage (Luma8) to get raw bytes for hashing
            let group_roi_luma = group_roi_img_dyn.to_luma8();
            let data_slice = group_roi_luma.as_raw();
            let current_hash = farmhash::hash64(data_slice);

            if let Some(valid_hashes) = res.cooldown_group_hashes.get(&group_name) {
                Ok(valid_hashes.contains(&current_hash))
            } else {
                Ok(False) // Group name not found in hash definitions
            }
        } else {
            Ok(False) // ROI for group name not defined
        }
    } else {
        Ok(False) // Cooldown area not found
    }
}
