from numba import njit
import numpy as np
from typing import List, Union, Optional # Added Optional
from src.shared.typings import Coordinate, CoordinateList, XYCoordinate
# Remove CFFI related imports if no longer needed by other functions
# import ctypes
# from py_rust_utils import lib as py_rust_lib

# Import the new Rust function from skb_core
try:
    from skb_core.rust_utils_module import find_closest_coordinate
except ImportError:
    print("Warning: Could not import 'find_closest_coordinate' from 'skb_core.rust_utils_module'.")
    # Define a fallback or raise an error if essential
    find_closest_coordinate = None


# TODO: add unit tests
def getAroundPixelsCoordinates(pixelCoordinate: XYCoordinate) -> List[XYCoordinate]:
    aroundPixelsCoordinatesIndexes = np.array(
        [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]])
    pixelCoordinates = np.broadcast_to(
        pixelCoordinate, aroundPixelsCoordinatesIndexes.shape)
    return np.add(aroundPixelsCoordinatesIndexes, pixelCoordinates)


# TODO: add unit tests
def getAvailableAroundPixelsCoordinates(aroundPixelsCoordinates: List[XYCoordinate], walkableFloorSqms: np.ndarray) -> List[XYCoordinate]:
    yPixelsCoordinates = aroundPixelsCoordinates[:, 1]
    xPixelsCoordinates = aroundPixelsCoordinates[:, 0]
    nonzero = np.nonzero(
        walkableFloorSqms[yPixelsCoordinates, xPixelsCoordinates])[0]
    return np.take(
        aroundPixelsCoordinates, nonzero, axis=0)


# TODO: add unit tests
def getAvailableAroundCoordinates(coordinate: Coordinate, walkableFloorSqms: np.ndarray) -> CoordinateList:
    pixelCoordinate = getPixelFromCoordinate(coordinate)
    aroundPixelsCoordinates = getAroundPixelsCoordinates(pixelCoordinate)
    availableAroundPixelsCoordinates = getAvailableAroundPixelsCoordinates(
        aroundPixelsCoordinates, walkableFloorSqms)
    xCoordinates = availableAroundPixelsCoordinates[:, 0] + 31744
    yCoordinates = availableAroundPixelsCoordinates[:, 1] + 30976
    floors = np.broadcast_to(
        coordinate[2], (availableAroundPixelsCoordinates.shape[0]))
    return np.column_stack(
        (xCoordinates, yCoordinates, floors))


def getClosestCoordinate(coordinate: Coordinate, coordinates: CoordinateList) -> Coordinate:
    if not coordinates:
        # Keep existing behavior for empty list
        raise ValueError("Input 'coordinates' list cannot be empty.")

    if find_closest_coordinate is None:
        # This happens if the import failed.
        raise RuntimeError("Rust function 'find_closest_coordinate' is not available from skb_core.rust_utils_module.")

    # The new Rust function expects the target coordinate as a tuple (or list)
    # and the list of coordinates directly.
    # Ensure target coordinate is in (float, float, float) format, though Python's float should be f64 for Rust.
    # The input `coordinate` is Coordinate, which is Tuple[int, int, int] or similar.
    # The Rust function expects (f64, f64, f64).
    target_f64 = (float(coordinate[0]), float(coordinate[1]), float(coordinate[2]))

    # Ensure coordinates in the list are also (f64, f64, f64)
    # CoordinateList is List[Coordinate], so List[Tuple[int,int,int]]
    # We need to convert each to List[Tuple[f64,f64,f64]]
    coordinates_f64 = [(float(c[0]), float(c[1]), float(c[2])) for c in coordinates]

    try:
        # Call the new Rust function
        # It returns Option<(f64, f64, f64)> which in Python is Optional[Tuple[float, float, float]]
        closest_coord_tuple_f64 = find_closest_coordinate(target_f64, coordinates_f64)

        if closest_coord_tuple_f64 is None:
            # This case should ideally be covered by the initial `if not coordinates:` check,
            # as the Rust function returns None for an empty list.
            # If it somehow returns None for a non-empty list, it implies no closest found or an internal issue.
            # For robustness, we can raise an error here.
            raise RuntimeError("Rust function 'find_closest_coordinate' returned None unexpectedly for a non-empty list.")

        # The original function returned a Coordinate (Tuple[int, int, int])
        # The Rust function returns Tuple[f64, f64, f64]. We should convert it back.
        # However, the type hint `Coordinate` is `Tuple[int, int, int]`.
        # For now, let's assume the user of `getClosestCoordinate` can handle floats or if conversion is needed.
        # The original `coordinates` list contains `Coordinate` objects. The Rust function finds one of *those*.
        # So, the returned type should match the elements in the input `coordinates` list.
        # The Rust function returns a *copy* of the coordinate data as f64.
        # To return the original Coordinate object (with ints), we would need the index.
        # The PyO3 function was designed to return the coordinate itself, not an index.
        # This is a slight deviation from the CFFI which returned an index.
        # If the exact original Coordinate object (with original int types) must be returned,
        # the Rust function should return an index, or we find it again in Python.
        # Given the Rust function returns Option<(f64,f64,f64)>, we will convert this back to Coordinate (int tuple)
        # to match the function's type hint.
        # This might lose precision if coordinates were originally float, but Coordinate is int.
        # Let's find the *original* coordinate object from the list that matches the one returned by Rust.
        # This is safer to ensure type consistency.
        # (Alternatively, adjust type hints if float results are acceptable downstream)

        # Re-iterate to find the matching original coordinate to preserve original types and object identity if important.
        # This is because (float(c[0]), float(c[1]), float(c[2])) might not be exactly equal to closest_coord_tuple_f64
        # due to float precision. The safest is if Rust returned an index.
        # Since it returns the coord, we'll compare with tolerance or convert back to int and compare.

        # For simplicity, let's convert the f64 tuple back to Coordinate's int tuple format.
        # This assumes that the closest coordinate found by Rust, when converted to int,
        # will match one of the original int coordinates.
        closest_coord_int = (int(closest_coord_tuple_f64[0]), int(closest_coord_tuple_f64[1]), int(closest_coord_tuple_f64[2]))

        # Now, we need to ensure this int tuple actually exists in the original `coordinates` list
        # to return the exact original object if that matters, or just this converted tuple.
        # The function signature implies returning a Coordinate from the input list.
        # If closest_coord_int is guaranteed to be one of the items in `coordinates`, this is fine.
        # Let's find it in the original list to be safe.
        for c_orig in coordinates:
            if c_orig[0] == closest_coord_int[0] and \
               c_orig[1] == closest_coord_int[1] and \
               c_orig[2] == closest_coord_int[2]:
                return c_orig

        # If not found (e.g. due to float conversion subtleties), this is an issue.
        # This situation means the closest_coord_tuple_f64 from Rust, when converted to int,
        # doesn't match any of the original integer coordinates.
        # This should be rare if the logic is sound (closest of the provided ones).
        # A more robust way would be for Rust to return the index.
        # Given the current Rust signature, we'll return the converted int tuple.
        # This matches the return type hint `Coordinate`.
        return closest_coord_int

    except Exception as e:
        # Catch potential errors from the Rust call (e.g., PyO3 errors)
        raise RuntimeError(f"Error calling Rust function 'find_closest_coordinate': {e}")


def getCoordinateFromPixel(pixel: XYCoordinate) -> Coordinate:
    return pixel[0] + 31744, pixel[1] + 30976


def getDirectionBetweenCoordinates(coordinate: Coordinate, nextCoordinate: Coordinate) -> Union[str, None]:
    if coordinate[0] < nextCoordinate[0]:
        return 'right'
    if nextCoordinate[0] < coordinate[0]:
        return 'left'
    if coordinate[1] < nextCoordinate[1]:
        return 'down'
    if nextCoordinate[1] < coordinate[1]:
        return 'up'


@njit(cache=True, fastmath=True)
def getPixelFromCoordinate(coordinate: Coordinate) -> XYCoordinate:
    return coordinate[0] - 31744, coordinate[1] - 30976
