import dxcam
import numpy as np
from typing import Callable, Union, List
from src.shared.typings import BBox, GrayImage
# Attempt to import the new PyO3 module
try:
    from skb_core import rust_utils_module as skb_rust_utils
except ImportError:
    # Fallback or error handling if the module is not found.
    # For this refactoring, we'll assume it will be available.
    # If you have an old FFI module name like `py_rust_utils` and want to try it as a fallback:
    # try:
    #     from py_rust_utils import lib as py_rust_lib_old_ffi
    #     # Further checks if this old FFI is what we expect or if it's truly the PyO3 module
    #     # This part can get complex if names are ambiguous.
    #     # For now, we rely on the new skb_core path.
    #     print("Warning: skb_core.rust_utils_module not found. Ensure the Rust library is compiled and accessible.")
    #     # You might want to define a mock skb_rust_utils here for linting/testing if needed
    #     class MockRustUtils:
    #         def __getattr__(self, name):
    #             raise NotImplementedError(f"Rust function {name} is not available (skb_core not found).")
    #     skb_rust_utils = MockRustUtils()
    # except ImportError:
    #     print("Critical: Neither skb_core.rust_utils_module nor py_rust_utils found.")
    #     # Define a mock skb_rust_utils to allow the rest of the file to be parsed for now.
    class MockRustUtils:
        def __getattr__(self, name):
            # This will raise an AttributeError if a function is called,
            # indicating the module isn't properly loaded.
            print(f"Attempted to call '{name}' on a non-existent skb_rust_utils module.")
            raise AttributeError(f"Rust function {name} is not available (skb_core.rust_utils_module not found).")
    skb_rust_utils = MockRustUtils()
    print("Warning: skb_core.rust_utils_module not found. Using a mock object. Ensure Rust library is compiled and in PYTHONPATH.")


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
    """
    Hashes a NumPy array using the Rust `hash_image_data` function.
    The input array `arr` is expected to be a 2D NumPy array (grayscale).
    """
    if not isinstance(arr, np.ndarray):
        # The PyO3 function will also perform type checking, but good to have it here.
        raise TypeError("Input must be a NumPy array.")
    if arr.ndim != 2:
        # The Rust function `hash_image_data` expects PyReadonlyArray2<u8>
        raise ValueError(f"Unsupported array ndim for hashit: {arr.ndim}. Expected 2 (grayscale).")
    
    # Ensure the array is C-contiguous and uint8, as PyO3 functions often expect this.
    # PyReadonlyArray2<u8> implies uint8.
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    if not arr.flags['C_CONTIGUOUS']:
        arr = np.ascontiguousarray(arr)
        
    try:
        return skb_rust_utils.hash_image_data(arr)
    except AttributeError as e:
        # This can happen if skb_rust_utils is the MockObject due to import failure
        print(f"Error calling skb_rust_utils.hash_image_data: {e}. Ensure skb_core module is correctly built and imported.")
        raise
    except Exception as e:
        # Catch other potential errors from the Rust call
        print(f"An error occurred in skb_rust_utils.hash_image_data: {e}")
        raise


# TODO: add unit tests
def locate(compareImage: GrayImage, img: GrayImage, confidence: float = 0.85, type=None) -> Union[BBox, None]:
    """
    Locates a template `img` within `compareImage` using Rust's `locate_template`.
    Inputs are expected to be grayscale NumPy arrays.
    The 'type' argument is unused.
    """
    # Ensure inputs are NumPy arrays, C-contiguous, and uint8
    # PyReadonlyArray2<u8> in Rust expects this.
    if not isinstance(compareImage, np.ndarray) or compareImage.dtype != np.uint8 or not compareImage.flags['C_CONTIGUOUS']:
        compareImage = np.ascontiguousarray(compareImage, dtype=np.uint8)
    if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or not img.flags['C_CONTIGUOUS']:
        img = np.ascontiguousarray(img, dtype=np.uint8)

    if compareImage.ndim != 2 or img.ndim != 2:
        raise ValueError("locate expects 2D grayscale images.")

    try:
        # The Rust function returns Option<(i32, i32, u32, u32)> which PyO3 converts to Python's None or a tuple.
        result = skb_rust_utils.locate_template(compareImage, img, confidence)
        return result # result is already BBox (tuple) or None
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.locate_template: {e}. Ensure skb_core module is correctly built and imported.")
        raise
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.locate_template: {e}")
        raise


# TODO: add unit tests
def locateMultiple(compareImg: GrayImage, img: GrayImage, confidence: float = 0.85) -> List[BBox]:
    """
    Locates all occurrences of a template `img` within `compareImg` using Rust's `locate_all_templates`.
    Inputs are expected to be grayscale NumPy arrays.
    """
    if not isinstance(compareImg, np.ndarray) or compareImg.dtype != np.uint8 or not compareImg.flags['C_CONTIGUOUS']:
        compareImg = np.ascontiguousarray(compareImg, dtype=np.uint8)
    if not isinstance(img, np.ndarray) or img.dtype != np.uint8 or not img.flags['C_CONTIGUOUS']:
        img = np.ascontiguousarray(img, dtype=np.uint8)

    if compareImg.ndim != 2 or img.ndim != 2:
        raise ValueError("locateMultiple expects 2D grayscale images.")

    try:
        # The Rust function returns Vec<(i32, i32, u32, u32)> which PyO3 converts to a Python list of tuples.
        result = skb_rust_utils.locate_all_templates(compareImg, img, confidence)
        return result # result is already List[BBox]
    except AttributeError as e:
        print(f"Error calling skb_rust_utils.locate_all_templates: {e}. Ensure skb_core module is correctly built and imported.")
        raise
    except Exception as e:
        print(f"An error occurred in skb_rust_utils.locate_all_templates: {e}")
        raise


# TODO: add unit tests
def getScreenshot() -> GrayImage:
    global camera, latestScreenshot
    screenshot_raw = camera.grab() # This is a BGRA numpy array from dxcam, typically HxWx4 uint8

    if screenshot_raw is None:
        return latestScreenshot # Return the previous screenshot if grab fails

    # Ensure screenshot_raw is a NumPy array, uint8, C-contiguous, and HxWx4
    if not isinstance(screenshot_raw, np.ndarray) or screenshot_raw.dtype != np.uint8:
        screenshot_raw = np.array(screenshot_raw, dtype=np.uint8)
    if not screenshot_raw.flags['C_CONTIGUOUS']:
        screenshot_raw = np.ascontiguousarray(screenshot_raw)

    if screenshot_raw.ndim == 3 and screenshot_raw.shape[2] == 4:
        try:
            # PyO3 function `convert_bgra_to_grayscale` expects PyReadonlyArray3<u8> (HxWx4)
            latestScreenshot = skb_rust_utils.convert_bgra_to_grayscale(screenshot_raw)
            return latestScreenshot
        except AttributeError as e:
            print(f"Error calling skb_rust_utils.convert_bgra_to_grayscale: {e}. Ensure skb_core module is correctly built and imported.")
            # Fallback to returning previous screenshot or raise error
            return latestScreenshot
        except Exception as e:
            print(f"An error occurred in skb_rust_utils.convert_bgra_to_grayscale: {e}")
            # Fallback
            return latestScreenshot
    elif screenshot_raw.ndim == 2: # Already grayscale? Unlikely from DXCam BGRA but handle defensively.
        latestScreenshot = screenshot_raw
        return latestScreenshot
    else:
        print(f"Warning: Unexpected screenshot format from DXCam. Shape: {screenshot_raw.shape}, dtype: {screenshot_raw.dtype}. Returning previous screenshot.")
        return latestScreenshot
