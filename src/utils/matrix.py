import numpy as np
from src.shared.typings import GrayImage

# Attempt to import the new PyO3 function
try:
    from skb_core.rust_utils_module import check_matrix_rules
except ImportError:
    print("Warning: Could not import 'check_matrix_rules' from 'skb_core.rust_utils_module'.")
    # Define a fallback or raise an error if essential
    check_matrix_rules = None


def hasMatrixInsideOther(matrix: GrayImage, other: GrayImage) -> bool:
    if check_matrix_rules is None:
        # This happens if the import failed.
        raise RuntimeError("Rust function 'check_matrix_rules' is not available from skb_core.rust_utils_module.")

    # Ensure input arrays are np.uint8 as PyReadonlyArray2<u8> expects this.
    # GrayImage type hint usually implies np.ndarray of dtype=np.uint8.
    if not isinstance(matrix, np.ndarray) or matrix.dtype != np.uint8:
        matrix = np.array(matrix, dtype=np.uint8)
    if not isinstance(other, np.ndarray) or other.dtype != np.uint8:
        other = np.array(other, dtype=np.uint8)
    
    # Define ignorable values as a Python list of ints (u8 compatible)
    ignorable_values = [0, 29, 57, 91, 113, 152, 170, 192]

    try:
        # Call the new Rust function
        # It expects matrix, other_image (both PyReadonlyArray2<u8>), and ignorable_values (Vec<u8>)
        result = check_matrix_rules(matrix, other, ignorable_values)
        return result
    except Exception as e:
        # Catch potential errors from the Rust call (e.g., PyO3 errors, or if Rust panics)
        # Or specific PyO3 errors if identifiable, e.g. pyo3::exceptions::PyValueError
        print(f"Error calling Rust function 'check_matrix_rules': {e}")
        # Depending on policy, either re-raise, return a default (e.g. False), or handle specifically
        raise RuntimeError(f"Error in Rust 'check_matrix_rules': {e}")
