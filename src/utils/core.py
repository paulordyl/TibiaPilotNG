import dxcam
from farmhash import FarmHash64
import numpy as np
from typing import Callable, Union, List # Added List
from src.shared.typings import BBox, GrayImage
import ctypes
from src.utils.image import RustImageData, _numpy_to_rust_image_data, _rust_to_numpy_image_data, py_rust_lib


class MatchResult(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int32),
        ("y", ctypes.c_int32),
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("confidence", ctypes.c_float)
    ]


class MatchResultArray(ctypes.Structure):
    _fields_ = [
        ("results", ctypes.POINTER(MatchResult)),
        ("count", ctypes.c_size_t)
    ]

# FFI Function Signatures

# locate_template_rust
if hasattr(py_rust_lib, 'locate_template_rust'):
    py_rust_lib.locate_template_rust.argtypes = [RustImageData, RustImageData, ctypes.c_float]
    py_rust_lib.locate_template_rust.restype = ctypes.POINTER(MatchResult)
else:
    print("Warning: function 'locate_template_rust' not found in py_rust_lib.")

# free_match_result_rust
if hasattr(py_rust_lib, 'free_match_result_rust'):
    py_rust_lib.free_match_result_rust.argtypes = [ctypes.POINTER(MatchResult)]
    py_rust_lib.free_match_result_rust.restype = None
else:
    print("Warning: function 'free_match_result_rust' not found in py_rust_lib.")

# locate_all_templates_rust
if hasattr(py_rust_lib, 'locate_all_templates_rust'):
    py_rust_lib.locate_all_templates_rust.argtypes = [RustImageData, RustImageData, ctypes.c_float]
    py_rust_lib.locate_all_templates_rust.restype = MatchResultArray # Returned by value
else:
    print("Warning: function 'locate_all_templates_rust' not found in py_rust_lib.")

# free_match_result_array_rust
if hasattr(py_rust_lib, 'free_match_result_array_rust'):
    py_rust_lib.free_match_result_array_rust.argtypes = [MatchResultArray] # Passed by value
    py_rust_lib.free_match_result_array_rust.restype = None
else:
    print("Warning: function 'free_match_result_array_rust' not found in py_rust_lib.")

# convert_bgra_to_grayscale_rust
if hasattr(py_rust_lib, 'convert_bgra_to_grayscale_rust'):
    py_rust_lib.convert_bgra_to_grayscale_rust.argtypes = [RustImageData] # Pass by value
    py_rust_lib.convert_bgra_to_grayscale_rust.restype = ctypes.POINTER(RustImageData)
else:
    print("Warning: function 'convert_bgra_to_grayscale_rust' not found in py_rust_lib.")


camera = dxcam.create(device_idx=0, output_idx=1, output_color='BGRA')
latestScreenshot = None


# TODO: add unit tests
def cacheObjectPosition(func: Callable) -> Callable:
    lastX = None
    lastY = None
    lastW = None
    lastH = None
    lastImgHash = None

    def inner(screenshot):
        nonlocal lastX, lastY, lastW, lastH, lastImgHash
        if lastX != None and lastY != None and lastW != None and lastH != None:
            if hashit(screenshot[lastY:lastY + lastH, lastX:lastX + lastW]) == lastImgHash:
                return (lastX, lastY, lastW, lastH)
        res = func(screenshot)
        if res is None:
            return None
        lastX = res[0]
        lastY = res[1]
        lastW = res[2]
        lastH = res[3]
        lastImgHash = hashit(
            screenshot[lastY:lastY + lastH, lastX:lastX + lastW])
        return res
    return inner


# TODO: add unit tests
def hashit(arr: np.ndarray) -> int:
    return FarmHash64(np.ascontiguousarray(arr))


# TODO: add unit tests
def locate(compareImage: GrayImage, img: GrayImage, confidence: float = 0.85, type=None) -> Union[BBox, None]:
    # The 'type' argument is now unused, can be removed or ignored.
    # For compatibility, it's kept but not used. Defaulting to None to signify it's not used.

    if not hasattr(py_rust_lib, 'locate_template_rust') or not hasattr(py_rust_lib, 'free_match_result_rust'):
        # Fallback to original cv2 logic or raise error if functions are missing
        # For this migration, we'll raise an error as cv2 will be removed.
        raise RuntimeError("Rust FFI functions for locate are not available and cv2 fallback is removed.")

    # 1. Convert NumPy arrays to RustImageData
    # Assuming GrayImage means ndim=2, so format is "GRAY"
    # If not, this needs more robust format detection like in image.py's crop/save
    format_haystack = "GRAY" if compareImage.ndim == 2 else "RGB" # Basic check
    format_needle = "GRAY" if img.ndim == 2 else "RGB" # Basic check
    
    rust_haystack = _numpy_to_rust_image_data(compareImage, format_haystack)
    rust_needle = _numpy_to_rust_image_data(img, format_needle)

    # 2. Call the FFI function
    match_result_ptr = py_rust_lib.locate_template_rust(rust_haystack, rust_needle, ctypes.c_float(confidence))

    # 3. Process the result
    if match_result_ptr: # Check if the pointer is not NULL
        try:
            match_data = match_result_ptr.contents
            # Ensure width and height from match_data are used, as these might be from the needle.
            # The original python code returned len(img[0]), len(img) which are needle's width and height.
            # So, match_data.width and match_data.height should correspond to this.
            bbox: BBox = (match_data.x, match_data.y, match_data.width, match_data.height)
            # 4. Free Rust-allocated memory
            py_rust_lib.free_match_result_rust(match_result_ptr)
            return bbox
        except ValueError: # Handles potential null pointer access if .contents fails on bad ptr
            if match_result_ptr: # Only free if pointer was not initially null
                 py_rust_lib.free_match_result_rust(match_result_ptr)
            return None # Or raise an error
    else:
        return None


# TODO: add unit tests
def locateMultiple(compareImg: GrayImage, img: GrayImage, confidence: float = 0.85) -> List[BBox]:
    if not hasattr(py_rust_lib, 'locate_all_templates_rust') or not hasattr(py_rust_lib, 'free_match_result_array_rust'):
        raise RuntimeError("Rust FFI functions for locateMultiple are not available and cv2 fallback is removed.")

    # 1. Convert NumPy arrays to RustImageData
    format_haystack = "GRAY" if compareImg.ndim == 2 else "RGB"
    format_needle = "GRAY" if img.ndim == 2 else "RGB"
    
    rust_haystack = _numpy_to_rust_image_data(compareImg, format_haystack)
    rust_needle = _numpy_to_rust_image_data(img, format_needle)

    # 2. Call the FFI function
    # This returns MatchResultArray by value
    match_array_struct = py_rust_lib.locate_all_templates_rust(rust_haystack, rust_needle, ctypes.c_float(confidence))

    resultList: List[BBox] = []
    # 3. Process the result
    if match_array_struct.results: # Check if the pointer to results is not NULL
        try:
            for i in range(match_array_struct.count):
                match_data = match_array_struct.results[i]
                # Ensure width and height are from the match_data (i.e., needle's dimensions)
                bbox: BBox = (match_data.x, match_data.y, match_data.width, match_data.height)
                resultList.append(bbox)
        finally: # Ensure memory is freed even if an error occurs during list processing
            # 4. Free Rust-allocated memory
            py_rust_lib.free_match_result_array_rust(match_array_struct)
    else: # If results pointer is NULL, still need to call free for the (empty) array structure if Rust expects it
          # Or if Rust guarantees results is null ONLY IF count is 0 and no allocation happened for the array itself,
          # then freeing might be conditional. Assuming Rust always allocates the MatchResultArray struct and its .results
          # pointer, which might be null if count is 0. The free function should handle this.
        py_rust_lib.free_match_result_array_rust(match_array_struct)


    return resultList


# TODO: add unit tests
def getScreenshot() -> GrayImage:
    global camera, latestScreenshot
    # Ensure FFI functions are available
    if not hasattr(py_rust_lib, 'convert_bgra_to_grayscale_rust'):
        raise RuntimeError("Rust FFI function convert_bgra_to_grayscale_rust is not available.")
    # _rust_to_numpy_image_data (which calls free_image_data_rust) must also be available from imports.
    if _numpy_to_rust_image_data is None or _rust_to_numpy_image_data is None:
        raise RuntimeError("Helper functions for Rust data conversion are not available.")

    screenshot_raw = camera.grab() # This is a BGRA numpy array from dxcam
    
    if screenshot_raw is None:
        # Return the previous screenshot if grab fails
        return latestScreenshot

    # 1. Convert BGRA NumPy array to RustImageData
    # DXCam returns BGRA, so "BGRA" is the format string.
    # The `screenshot_raw` is a NumPy array.
    rust_bgra_image = _numpy_to_rust_image_data(screenshot_raw, "BGRA")

    # 2. Call the FFI function for BGRA to Grayscale conversion
    rust_gray_image_ptr = py_rust_lib.convert_bgra_to_grayscale_rust(rust_bgra_image)

    # 3. Convert the result back to a NumPy array (and free Rust memory)
    if rust_gray_image_ptr:
        latestScreenshot = _rust_to_numpy_image_data(rust_gray_image_ptr)
        return latestScreenshot
    else:
        # Handle error: if Rust conversion fails and returns null
        # Log an error or raise an exception. For now, return previous screenshot.
        # This case might indicate an issue with the Rust conversion.
        # Consider logging: print("Error: Rust BGRA to Grayscale conversion failed.")
        return latestScreenshot # Fallback to previous screenshot
