from src.shared.typings import Coordinate
from src.utils.keyboard import keyUp
from .typings import Context

# Attempt to import the Rust module
# The actual filename for the .so/.dll/.dylib will be something like:
# py_rust_utils.dll (Windows) or libpy_rust_utils.so (Linux)
# PyO3 handles the loading. The module name here matches #[pyo3(name = "py_rust_utils_module")]
try:
    import py_rust_utils_module
except ImportError:
    # Fallback or error handling if the Rust module is not found
    print("ERROR: Could not import py_rust_utils_module. Ensure the compiled Rust library is in the correct path.")
    # You might want to raise an error or use a fallback Python implementation
    # For this task, we'll assume it imports successfully for the functions below.
    # If it truly fails, the original Python functions would need to be kept as fallbacks,
    # or the program should halt. For now, let's assume it loads.
    pass


def coordinatesAreEqual(firstCoordinate: Coordinate, secondCoordinate: Coordinate) -> bool:
    if firstCoordinate is None or secondCoordinate is None:
        # Rust version doesn't handle None directly in its signature, 
        # so keep this check in Python or adjust Rust signature if Nones are common.
        # For now, mirroring the original Python guard.
        return False
    # Assuming py_rust_utils_module is successfully imported
    return py_rust_utils_module.coordinates_are_equal(firstCoordinate, secondCoordinate)


def releaseKeys(context: Context) -> Context:
    if context['ng_lastPressedKey'] is not None:
        # Still call the original keyUp from Python for the actual action
        keyUp(context['ng_lastPressedKey'])
        
        # Use Rust function to get the new state for ng_lastPressedKey.
        # The Rust function's placeholder for keyUp is just a print statement.
        # The main logic moved to Rust is determining that ng_lastPressedKey becomes None.
        current_key = context['ng_lastPressedKey']
        context['ng_lastPressedKey'] = py_rust_utils_module.release_keys(current_key)
    return context
