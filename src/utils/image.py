import numpy as np
from typing import Union
from src.shared.typings import BBox, GrayImage
# hashit and locate are imported from core, which is already refactored.
from src.utils.core import hashit, locate 

# Attempt to import the new PyO3 module
try:
    from skb_core import rust_utils_module as skb_rust_utils
except ImportError:
    # Fallback or error handling if the module is not found.
    class MockRustUtils:
        def __getattr__(self, name):
            print(f"Attempted to call '{name}' on a non-existent skb_rust_utils module.")
            raise AttributeError(f"Rust function {name} is not available (skb_core.rust_utils_module not found).")
    skb_rust_utils = MockRustUtils()
    print("Warning: skb_core.rust_utils_module not found. Using a mock object. Ensure Rust library is compiled and in PYTHONPATH.")


# _numpy_to_rust_image_data and _rust_to_numpy_image_data are no longer needed
# as PyO3 handles data conversion directly with NumPy arrays.

# TODO: add types
# TODO: add unit tests
def cacheChain(imageList):
    def decorator(_):
        lastX = None
        lastY = None
        lastW = None
        lastH = None
        lastImageHash = None

        def inner(screenshot: GrayImage) -> Union[BBox, None]:
            nonlocal lastX, lastY, lastW, lastH, lastImageHash
            if lastX != None and lastY != None and lastW != None and lastH != None:
                copiedImage = screenshot[lastY:lastY +
                                         lastH, lastX:lastX + lastW]
                copiedImageHash = hashit(copiedImage)
                if copiedImageHash == lastImageHash:
                    return (lastX, lastY, lastW, lastH)
            for image in imageList:
                imagePosition = locate(screenshot, image)
                if imagePosition is not None:
                    (x, y, w, h) = imagePosition
                    lastX = x
                    lastY = y
                    lastW = w
                    lastH = h
                    lastImage = screenshot[lastY:lastY +
                                           lastH, lastX:lastX + lastW]
                    lastImageHash = hashit(lastImage)
                    return (x, y, w, h)
            return None
        return inner
    return decorator


# TODO: add unit tests
def convertGraysToBlack(arr: np.ndarray) -> np.ndarray:
    """
    Filters gray pixels (values between 50 and 100, inclusive) to black (0)
    using a Rust implementation. The modification is done in-place on the array.
    """
    if not isinstance(arr, np.ndarray):
        # Raise error or convert, depending on desired strictness.
        # The Rust function expects a PyReadwriteArray2<u8>.
        # For safety, let's ensure it's a NumPy array.
        raise TypeError("Input must be a NumPy array.")

    if arr.ndim != 2:
        raise ValueError("Input array must be 2-dimensional (grayscale).")

    # Ensure the array is of dtype uint8 and C-contiguous for the Rust function.
    # PyReadwriteArray2<u8> implies uint8.
    if arr.dtype != np.uint8:
        arr_converted = np.array(arr, dtype=np.uint8)
        # If original arr was not uint8, Rust function will modify arr_converted.
        # We need to decide if we copy back or modify original if types differ.
        # For simplicity, if dtype changes, we operate on the converted copy and return it.
        # However, the Rust function is designed for in-place on u8.
        # So, the Python wrapper should enforce u8 or make a u8 copy.
        # Let's assume the user intends to modify the passed array if it's already u8,
        # otherwise, they get a modified copy that is u8.
        # This behavior is a bit complex. For direct replacement of Numba's in-place behavior,
        # the input arr should ideally already be uint8.
        # Let's simplify: the function will attempt to modify in-place if possible,
        # but if a conversion is needed, the original array won't be modified if it wasn't uint8.
        # This matches the plan of "Python wrapper handles pre-processing".
        if not np.array_equal(arr, arr_converted): # Check if conversion changed values (e.g. float to int)
             print("Warning: input array was not uint8. A uint8 copy was made and will be modified.")
        arr = arr_converted # Work with the uint8 version.

    if not arr.flags['C_CONTIGUOUS']:
        # If not C-contiguous, PyO3 might handle it by creating a temporary copy for Rust,
        # but the in-place modification might not reflect on the original non-C-contiguous array.
        # It's safer to ensure it's C-contiguous.
        arr_c_contig = np.ascontiguousarray(arr)
        if arr_c_contig is not arr : # Check if ascontiguousarray actually made a copy
            print("Warning: input array was not C-contiguous. A C-contiguous copy was made and will be modified.")
        arr = arr_c_contig

    try:
        # skb_rust_utils.filter_grays_to_black modifies the array in-place and returns None.
        skb_rust_utils.filter_grays_to_black(arr) 
        return arr # Return the modified array
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.filter_grays_to_black: {e}. Ensure skb_core module is correctly built and imported.")
        # Fallback to original Numba logic if module/function not found, or raise error.
        # For this task, we raise to indicate the Rust path should be working.
        raise
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.filter_grays_to_black: {e}")
        # Decide on fallback or re-raise
        raise


# TODO: add unit tests
def RGBtoGray(image: np.ndarray) -> GrayImage:
    """Converts an RGB or RGBA image (NumPy array) to grayscale using Rust."""
    if not isinstance(image, np.ndarray):
        raise TypeError("Input must be a NumPy array.")
    # The Rust function `convert_to_grayscale` expects PyReadonlyArrayDyn<u8>.
    # It will handle different dimensions (2D grayscale, 3D RGB/RGBA).
    # Ensure C-contiguous and uint8 for PyO3.
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if not image.flags['C_CONTIGUOUS']:
        image = np.ascontiguousarray(image)
        
    try:
        return skb_rust_utils.convert_to_grayscale(image)
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.convert_to_grayscale: {e}.")
        raise
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.convert_to_grayscale: {e}")
        raise


# TODO: add unit tests
def loadFromRGBToGray(path: str) -> GrayImage:
    """Loads an image from path and converts it to grayscale using Rust."""
    try:
        # The Rust function `load_image_as_grayscale` returns Py<PyArray2<u8>>.
        gray_image = skb_rust_utils.load_image_as_grayscale(path)
        return gray_image
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.load_image_as_grayscale: {e}.")
        raise
    except Exception as e: # Catch potential errors from Rust (e.g., file not found PyIOError)
        print(f"An error occurred in skb_rust_utils.load_image_as_grayscale for path '{path}': {e}")
        raise IOError(f"Failed to load image as grayscale from '{path}'. Caused by: {e}")


# TODO: add unit tests
def save(arr: np.ndarray, name: str): # Changed type hint from GrayImage to generic np.ndarray
    """Saves a NumPy array as an image using Rust. Supports grayscale or color images."""
    if not isinstance(arr, np.ndarray):
        raise TypeError("Input must be a NumPy array.")
    # Rust function `save_image` expects PyReadonlyArrayDyn<u8>.
    # Ensure C-contiguous and uint8 for PyO3.
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)

    try:
        skb_rust_utils.save_image(arr, name)
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.save_image: {e}.")
        raise
    except Exception as e: # Catch potential errors from Rust (e.g., path error PyIOError)
        print(f"An error occurred in skb_rust_utils.save_image for path '{name}': {e}")
        raise IOError(f"Failed to save image to '{name}'. Caused by: {e}")


# TODO: add unit tests
def crop(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """Crops an image (NumPy array) using Rust."""
    if not isinstance(image, np.ndarray):
        raise TypeError("Input image must be a NumPy array.")
    # Rust function `crop_image` expects PyReadonlyArrayDyn<u8>.
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if not image.flags['C_CONTIGUOUS']:
        image = np.ascontiguousarray(image)
    
    # Ensure x, y, width, height are positive integers as expected by u32 in Rust.
    if not all(isinstance(val, int) and val >= 0 for val in [x, y, width, height]):
        raise ValueError("x, y, width, height must be non-negative integers.")

    try:
        return skb_rust_utils.crop_image(image, x, y, width, height)
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.crop_image: {e}.")
        raise
    except Exception as e: # Catch potential errors (e.g., crop dimensions out of bounds PyValueError)
        print(f"An error occurred in skb_rust_utils.crop_image: {e}")
        raise


# TODO: add unit tests
def load(path: str) -> np.ndarray:
    """Loads an image from path using Rust. Returns a NumPy array (color or grayscale)."""
    try:
        # Rust function `load_image` returns Py<PyArrayDyn<u8>>.
        return skb_rust_utils.load_image(path)
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.load_image: {e}.")
        raise
    except Exception as e: # Catch potential errors from Rust (e.g., file not found PyIOError)
        print(f"An error occurred in skb_rust_utils.load_image for path '{path}': {e}")
        raise IOError(f"Failed to load image from '{path}'. Caused by: {e}")
