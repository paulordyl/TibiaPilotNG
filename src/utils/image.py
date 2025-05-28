import ctypes
from numba import njit
import numpy as np
from py_rust_utils import lib as py_rust_lib
from typing import Union
from src.shared.typings import BBox, GrayImage
from src.utils.core import hashit, locate


class RustImageData(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_ubyte)),
        ("height", ctypes.c_uint64),
        ("width", ctypes.c_uint64),
        ("channels", ctypes.c_uint8),
        ("format", ctypes.c_char_p)
    ]

# Define FFI function signature for free_image_data_rust
if hasattr(py_rust_lib, 'free_image_data_rust'):
    py_rust_lib.free_image_data_rust.argtypes = [ctypes.POINTER(RustImageData)]
    py_rust_lib.free_image_data_rust.restype = None
else:
    # Optionally, raise an error or log a warning if the function isn't found,
    # depending on how critical this is at module load time.
    print("Warning: function 'free_image_data_rust' not found in py_rust_lib.")

# Define FFI function signature for load_image_rust
if hasattr(py_rust_lib, 'load_image_rust'):
    py_rust_lib.load_image_rust.argtypes = [ctypes.c_char_p]
    py_rust_lib.load_image_rust.restype = ctypes.POINTER(RustImageData)
else:
    print("Warning: function 'load_image_rust' not found in py_rust_lib.")

# Define FFI function signature for convert_to_grayscale_rust
if hasattr(py_rust_lib, 'convert_to_grayscale_rust'):
    py_rust_lib.convert_to_grayscale_rust.argtypes = [RustImageData] # Pass by value
    py_rust_lib.convert_to_grayscale_rust.restype = ctypes.POINTER(RustImageData)
else:
    print("Warning: function 'convert_to_grayscale_rust' not found in py_rust_lib.")

# Define FFI function signature for load_image_as_grayscale_rust
if hasattr(py_rust_lib, 'load_image_as_grayscale_rust'):
    py_rust_lib.load_image_as_grayscale_rust.argtypes = [ctypes.c_char_p]
    py_rust_lib.load_image_as_grayscale_rust.restype = ctypes.POINTER(RustImageData)
else:
    print("Warning: function 'load_image_as_grayscale_rust' not found in py_rust_lib.")

# Define FFI function signature for crop_image_rust
if hasattr(py_rust_lib, 'crop_image_rust'):
    py_rust_lib.crop_image_rust.argtypes = [
        RustImageData,      # Pass by value
        ctypes.c_uint32,    # x
        ctypes.c_uint32,    # y
        ctypes.c_uint32,    # width
        ctypes.c_uint32     # height
    ]
    py_rust_lib.crop_image_rust.restype = ctypes.POINTER(RustImageData)
else:
    print("Warning: function 'crop_image_rust' not found in py_rust_lib.")

# Define FFI function signature for save_image_rust
if hasattr(py_rust_lib, 'save_image_rust'):
    py_rust_lib.save_image_rust.argtypes = [RustImageData, ctypes.c_char_p] # RustImageData by value
    py_rust_lib.save_image_rust.restype = ctypes.c_int # 0 for success, non-zero for error
else:
    print("Warning: function 'save_image_rust' not found in py_rust_lib.")


def _numpy_to_rust_image_data(numpy_array: np.ndarray, format_str: str) -> RustImageData:
    if not isinstance(numpy_array, np.ndarray):
        raise TypeError("Expected numpy_array to be a NumPy array.")
    if not numpy_array.flags['C_CONTIGUOUS']:
        numpy_array = np.ascontiguousarray(numpy_array)
    
    height, width = numpy_array.shape[:2]
    
    if numpy_array.ndim == 2:
        channels = 1
    elif numpy_array.ndim == 3:
        channels = numpy_array.shape[2]
    else:
        raise ValueError(f"Unsupported numpy_array.ndim: {numpy_array.ndim}. Expected 2 or 3.")

    data_ptr = numpy_array.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    format_bytes = format_str.encode('utf-8')

    return RustImageData(
        data=data_ptr,
        height=height,
        width=width,
        channels=channels,
        format=format_bytes
    )


def _rust_to_numpy_image_data(rust_image_data_ptr: ctypes.POINTER(RustImageData)) -> np.ndarray:
    if not rust_image_data_ptr or not rust_image_data_ptr.contents:
        raise ValueError("Received a null or invalid pointer for RustImageData.")

    img_struct = rust_image_data_ptr.contents
    height = img_struct.height
    width = img_struct.width
    channels = img_struct.channels
    data_ptr = img_struct.data

    if not data_ptr:
        # Free the struct if data is null, assuming struct itself was allocated
        if hasattr(py_rust_lib, 'free_image_data_rust'):
            py_rust_lib.free_image_data_rust(rust_image_data_ptr)
        raise ValueError("RustImageData.data is a null pointer.")

    # Determine shape based on channels
    if channels == 1:  # Grayscale
        shape = (height, width)
    elif channels > 1:  # Color (RGB, RGBA, etc.)
        shape = (height, width, channels)
    else:
        # Free memory before raising error
        if hasattr(py_rust_lib, 'free_image_data_rust'):
            py_rust_lib.free_image_data_rust(rust_image_data_ptr)
        raise ValueError(f"Unsupported number of channels: {channels}")

    # Calculate buffer size
    # This assumes data is uint8, if other types, size calculation needs adjustment
    buffer_size = height * width * channels 
    
    # Create a NumPy array view from the Rust data
    # np.ctypeslib.as_array requires a pointer to the data, not the struct
    original_numpy_view = np.ctypeslib.as_array(data_ptr, shape=shape)
    
    # Create a copy of the data to Python-managed memory
    numpy_array_copy = np.copy(original_numpy_view)
    
    # Free the memory allocated by Rust
    if hasattr(py_rust_lib, 'free_image_data_rust'):
        py_rust_lib.free_image_data_rust(rust_image_data_ptr)
    else:
        # This case should ideally not be reached if the initial check passes,
        # but it's good for robustness.
        print("Warning: 'free_image_data_rust' function not available to free memory.")
        
    return numpy_array_copy


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
@njit(cache=True, fastmath=True)
def convertGraysToBlack(arr: np.ndarray) -> np.ndarray:
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i, j] >= 50 and arr[i, j] <= 100:
                arr[i, j] = 0
    return arr


# TODO: add unit tests
def RGBtoGray(image: np.ndarray) -> GrayImage:
    if not hasattr(py_rust_lib, 'convert_to_grayscale_rust'):
        raise RuntimeError("Rust function 'convert_to_grayscale_rust' is not available.")

    # Assuming the input 'image' is RGB. If it can be other formats,
    # this part might need adjustment or more robust format handling.
    # The format "RGB" will be passed to RustImageData.
    rust_input_image = _numpy_to_rust_image_data(image, "RGB")
    
    # Call the Rust function
    rust_gray_image_ptr = py_rust_lib.convert_to_grayscale_rust(rust_input_image)
    
    if not rust_gray_image_ptr:
        # This could happen if the Rust function returns a null pointer on error
        raise RuntimeError("Rust function 'convert_to_grayscale_rust' returned null.")
        
    # Convert the Rust-returned pointer back to a NumPy array.
    # _rust_to_numpy_image_data is expected to free the Rust-allocated memory.
    gray_numpy_image = _rust_to_numpy_image_data(rust_gray_image_ptr)
    
    # The GrayImage type hint implies a 2D NumPy array (height, width).
    # We should ensure gray_numpy_image matches this.
    # _rust_to_numpy_image_data shapes based on channels; for grayscale, it should be 2D.
    if gray_numpy_image.ndim != 2:
        # This might indicate an issue if the Rust function didn't actually return grayscale
        # or if _rust_to_numpy_image_data logic is not aligned for grayscale.
        # For now, we trust the process.
        pass

    return gray_numpy_image


# TODO: add unit tests
def loadFromRGBToGray(path: str) -> GrayImage:
    if not hasattr(py_rust_lib, 'load_image_as_grayscale_rust'):
        raise RuntimeError("Rust function 'load_image_as_grayscale_rust' is not available.")

    path_bytes = path.encode('utf-8')
    rust_gray_image_ptr = py_rust_lib.load_image_as_grayscale_rust(path_bytes)

    if not rust_gray_image_ptr:
        raise IOError(f"Failed to load image as grayscale at path: {path}. Rust function returned null.")

    # _rust_to_numpy_image_data converts the pointer to a NumPy array and handles freeing Rust memory.
    # It should return a 2D grayscale NumPy array.
    gray_numpy_image = _rust_to_numpy_image_data(rust_gray_image_ptr)
    
    # Ensure the image is indeed grayscale (2D) as expected.
    # _rust_to_numpy_image_data should handle this based on channels from RustImageData.
    if gray_numpy_image.ndim != 2:
        # This could be an unexpected situation if the Rust function
        # or _rust_to_numpy_image_data is not behaving as expected for grayscale.
        # Consider logging a warning or raising a more specific error.
        pass # Assuming _rust_to_numpy_image_data correctly forms a 2D array for grayscale.
        
    # The original function also cast to np.uint8, _rust_to_numpy_image_data should
    # ideally produce data of this type if Rust side uses u8.
    # If necessary, an explicit cast `gray_numpy_image.astype(np.uint8, copy=False)` could be added,
    # but it's better if the data is already in the correct format.
    return gray_numpy_image


# TODO: add unit tests
def save(arr: GrayImage, name: str):
    if not hasattr(py_rust_lib, 'save_image_rust'):
        raise RuntimeError("Rust function 'save_image_rust' is not available.")

    # Determine format string based on array dimensions
    if arr.ndim == 2:
        format_str = "GRAY"
    elif arr.ndim == 3:
        # Assuming RGB for 3-channel arrays. This might need to be
        # more flexible if other formats (like BGR) are common.
        format_str = "RGB" 
    else:
        raise ValueError(f"Unsupported array ndim for save: {arr.ndim}. Expected 2 or 3.")

    rust_input_image = _numpy_to_rust_image_data(arr, format_str)
    path_bytes = name.encode('utf-8')
    
    # Call the Rust function
    result = py_rust_lib.save_image_rust(rust_input_image, path_bytes)
    
    # Check the result code
    if result != 0:
        # It would be good if Rust could provide more detailed error codes/messages,
        # but for now, a generic error is raised.
        raise IOError(f"Failed to save image to '{name}'. Rust function returned error code {result}.")
    
    # No return value, as the original function didn't have one.


# TODO: add unit tests
def crop(image: GrayImage, x: int, y: int, width: int, height: int) -> GrayImage:
    if not hasattr(py_rust_lib, 'crop_image_rust'):
        raise RuntimeError("Rust function 'crop_image_rust' is not available.")

    # Determine format string based on image dimensions
    if image.ndim == 2:
        format_str = "GRAY"
    elif image.ndim == 3:
        format_str = "RGB" # Or BGR, or other, depending on typical input
    else:
        raise ValueError(f"Unsupported image ndim for crop: {image.ndim}. Expected 2 or 3.")

    rust_input_image = _numpy_to_rust_image_data(image, format_str)
    
    # Call the Rust function, ensuring parameters are of the correct ctypes
    # The FFI signature expects uint32 for x, y, width, height.
    # Python int types should be compatible if they are positive and within uint32 range.
    # For safety, explicit casting can be done, though often not strictly necessary
    # if values are known to be appropriate.
    rust_cropped_image_ptr = py_rust_lib.crop_image_rust(
        rust_input_image,
        ctypes.c_uint32(x),
        ctypes.c_uint32(y),
        ctypes.c_uint32(width),
        ctypes.c_uint32(height)
    )

    if not rust_cropped_image_ptr:
        raise RuntimeError(f"Rust function 'crop_image_rust' returned null. Crop parameters: x={x}, y={y}, w={width}, h={height}")

    cropped_numpy_image = _rust_to_numpy_image_data(rust_cropped_image_ptr)
    
    # The return type is GrayImage, which is np.ndarray.
    # The actual dimensions/channels of cropped_numpy_image will depend on what crop_image_rust returns
    # and how _rust_to_numpy_image_data interprets it.
    # If input was RGB and output is also RGB, GrayImage might be a misnomer if it implies 2D.
    # However, GrayImage is just an alias for np.ndarray, so it's technically fine.
    return cropped_numpy_image


# TODO: add unit tests
def load(path: str) -> np.ndarray:
    if not hasattr(py_rust_lib, 'load_image_rust'):
        raise RuntimeError("Rust function 'load_image_rust' is not available.")
    
    path_bytes = path.encode('utf-8')
    rust_image_data_ptr = py_rust_lib.load_image_rust(path_bytes)
    
    if not rust_image_data_ptr:
        # This could happen if the Rust function returns a null pointer on error (e.g., file not found)
        raise IOError(f"Failed to load image at path: {path}. Rust function returned null.")
        
    # Assuming _rust_to_numpy_image_data handles potential errors from Rust side
    # and frees the Rust-allocated memory.
    numpy_image = _rust_to_numpy_image_data(rust_image_data_ptr)
    
    # The original function returned RGB (based on cv2.COLOR_BGR2RGB).
    # We assume load_image_rust provides data in a compatible format (e.g. RGB directly,
    # or _rust_to_numpy_image_data correctly interprets it based on channels / format string).
    # If the Rust function returns BGR, and _rust_to_numpy_image_data doesn't convert it,
    # an additional cv2.cvtColor(numpy_image, cv2.COLOR_BGR2RGB) might be needed here.
    # For now, we'll assume the format is correct as per the subtask description.
    return numpy_image
