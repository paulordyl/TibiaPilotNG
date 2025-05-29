from numba import njit
import numpy as np
from typing import List, Union
from src.shared.typings import Coordinate, CoordinateList, XYCoordinate
import ctypes
from py_rust_utils import lib as py_rust_lib


# FFI Function Signature Setup
if hasattr(py_rust_lib, 'find_closest_coordinate_rust'):
    py_rust_lib.find_closest_coordinate_rust.argtypes = [
        ctypes.c_double,                        # target_x
        ctypes.c_double,                        # target_y
        ctypes.POINTER(ctypes.c_double),        # coords_data
        ctypes.c_size_t                         # num_coords
    ]
    py_rust_lib.find_closest_coordinate_rust.restype = ctypes.c_ssize_t # index or -1
else:
    print("Warning: FFI function 'find_closest_coordinate_rust' not found in py_rust_lib.")
    # Or raise an error, or set a flag to fallback if that's desired.
    # For now, a warning is fine as per previous patterns.


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
        # Or return coordinate? Or None? Or specific error for no valid closest?
        # For now, raising ValueError as SciPy might also error on empty inputs for cdist.
        raise ValueError("Input 'coordinates' list cannot be empty.")

    if not hasattr(py_rust_lib, 'find_closest_coordinate_rust'):
        # Fallback to original SciPy logic or raise an error if the FFI function is missing.
        # For this migration, we'll raise a RuntimeError as SciPy will be removed.
        raise RuntimeError("Rust FFI function 'find_closest_coordinate_rust' is not available.")

    target_x = float(coordinate[0])
    target_y = float(coordinate[1])
    # We ignore target_z for distance calculation as per original logic.

    # Convert list of tuples to a flat NumPy array for FFI
    # The Rust side expects [x1, y1, z1, x2, y2, z2, ...]
    # Ensure it's float64 to match ctypes.c_double
    coords_np = np.array(coordinates, dtype=np.float64)
    if not coords_np.flags['C_CONTIGUOUS']:
        coords_np = np.ascontiguousarray(coords_np, dtype=np.float64)
    
    coords_ptr = coords_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    num_coords = len(coordinates)

    closest_idx = py_rust_lib.find_closest_coordinate_rust(
        ctypes.c_double(target_x),
        ctypes.c_double(target_y),
        coords_ptr,
        ctypes.c_size_t(num_coords)
    )

    if closest_idx < 0:
        # Rust function indicates an error (e.g., -1 if num_coords was 0, though we check above)
        # or some other internal issue.
        raise RuntimeError(f"Rust function 'find_closest_coordinate_rust' returned error code: {closest_idx}")
    
    # closest_idx is a valid index
    return coordinates[closest_idx]


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
