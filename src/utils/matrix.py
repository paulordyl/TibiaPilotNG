import ctypes # Added
import numpy as np # Added
from src.shared.typings import GrayImage
from src.utils.image import RustImageData, _numpy_to_rust_image_data, py_rust_lib # Added


# FFI Function Signature Setup for check_matrix_rules_rust
if hasattr(py_rust_lib, 'check_matrix_rules_rust'):
    py_rust_lib.check_matrix_rules_rust.argtypes = [
        RustImageData,                          # matrix_image_data
        RustImageData,                          # other_image_data
        ctypes.POINTER(ctypes.c_uint8),         # ignorable_values_ptr
        ctypes.c_size_t                         # ignorable_values_len
    ]
    py_rust_lib.check_matrix_rules_rust.restype = ctypes.c_bool
else:
    print("Warning: FFI function 'check_matrix_rules_rust' not found in py_rust_lib.")
    # Or raise an error. For consistency with other modules, a warning is used.


def hasMatrixInsideOther(matrix: GrayImage, other: GrayImage) -> bool:
    # Ensure FFI function is available
    if not hasattr(py_rust_lib, 'check_matrix_rules_rust'):
        raise RuntimeError("Rust FFI function 'check_matrix_rules_rust' is not available.")
    
    # _numpy_to_rust_image_data must also be available from imports.
    if _numpy_to_rust_image_data is None:
        raise RuntimeError("Helper function '_numpy_to_rust_image_data' for Rust data conversion is not available.")

    # 1. Define ignorable values
    # These were previously hardcoded in the loop condition.
    ignorable_np = np.array([0, 29, 57, 91, 113, 152, 170, 192], dtype=np.uint8)
    ignorable_ptr = ignorable_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
    ignorable_len = len(ignorable_np)

    # 2. Convert input matrices to RustImageData
    # Assuming GrayImage is typically uint8 and 2D (single channel).
    # The _numpy_to_rust_image_data function handles details of data pointer and dimensions.
    # Using "GRAY" as format implies 1 channel for RustImageData.
    rust_matrix_data = _numpy_to_rust_image_data(matrix, "GRAY")
    rust_other_data = _numpy_to_rust_image_data(other, "GRAY")

    # 3. Call the FFI function
    result = py_rust_lib.check_matrix_rules_rust(
        rust_matrix_data,
        rust_other_data,
        ignorable_ptr,
        ctypes.c_size_t(ignorable_len)
    )
    
    return result
