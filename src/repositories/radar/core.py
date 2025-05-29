import ctypes # Added
from numba import njit
import numpy as np
from typing import Union
from src.shared.typings import Coordinate, GrayImage, GrayPixel, WaypointList
from src.utils.core import hashit, locate
# Assuming py_rust_lib is accessible from src.utils.image, 
# where it's initialized and other FFI functions are attached.
# This avoids re-loading the library in multiple places.
from src.utils.image import py_rust_lib # Added
from src.utils.coordinate import getCoordinateFromPixel, getPixelFromCoordinate
from .config import availableTilesFrictions, breakpointTileMovementSpeed, coordinates, dimensions, floorsImgs, floorsLevelsImgsHashes, floorsPathsSqms, nonWalkablePixelsColors, tilesFrictionsWithBreakpoints, walkableFloorsSqms
from .extractors import getRadarImage
from .locators import getRadarToolsPosition
from .typings import FloorLevel, TileFriction


# FFI Function Signature Setup 

# find_closest_waypoint_index_rust
if hasattr(py_rust_lib, 'find_closest_waypoint_index_rust'):
    py_rust_lib.find_closest_waypoint_index_rust.argtypes = [
        ctypes.c_double,                        # target_x
        ctypes.c_double,                        # target_y
        ctypes.c_int32,                         # target_z (floor level)
        ctypes.POINTER(ctypes.c_double),        # waypoints_data_ptr (flat array of x,y,z)
        ctypes.c_size_t                         # num_waypoints
    ]
    py_rust_lib.find_closest_waypoint_index_rust.restype = ctypes.c_ssize_t # index or -1
else:
    # Using print for warning, consistent with how it was done in src/utils/core.py
    print("Warning: FFI function 'find_closest_waypoint_index_rust' not found in py_rust_lib.")

# are_coordinates_close_rust
if hasattr(py_rust_lib, 'are_coordinates_close_rust'):
    py_rust_lib.are_coordinates_close_rust.argtypes = [
        ctypes.c_double,                        # x1
        ctypes.c_double,                        # y1
        ctypes.c_double,                        # x2
        ctypes.c_double,                        # y2
        ctypes.c_double                         # distance_tolerance
    ]
    py_rust_lib.are_coordinates_close_rust.restype = ctypes.c_bool
else:
    print("Warning: FFI function 'are_coordinates_close_rust' not found in py_rust_lib.")


# TODO: add unit tests
# TODO: add perf
# TODO: get by cached images coordinates hashes
def getCoordinate(screenshot: GrayImage, previousCoordinate: Coordinate = None) -> Coordinate | None:
    radarToolsPosition = getRadarToolsPosition(screenshot)
    if radarToolsPosition is None:
        return None
    radarImage = getRadarImage(screenshot, radarToolsPosition)
    radarHashedImg = hashit(radarImage)
    hashedCoordinate = coordinates.get(radarHashedImg, None)
    if hashedCoordinate is not None:
        return hashedCoordinate
    floorLevel = getFloorLevel(screenshot)
    if floorLevel is None:
        return None
    radarImage[52, 53] = 128
    radarImage[52, 54] = 128
    radarImage[53, 53] = 128
    radarImage[53, 54] = 128
    radarImage[54, 51] = 128
    radarImage[54, 52] = 128
    radarImage[55, 51] = 128
    radarImage[55, 52] = 128
    radarImage[54, 53] = 128
    radarImage[54, 54] = 128
    radarImage[55, 53] = 128
    radarImage[55, 54] = 128
    radarImage[54, 55] = 128
    radarImage[54, 56] = 128
    radarImage[55, 55] = 128
    radarImage[55, 56] = 128
    radarImage[56, 53] = 128
    radarImage[56, 54] = 128
    radarImage[57, 53] = 128
    radarImage[57, 54] = 128
    if previousCoordinate is not None:
        (previousCoordinateXPixel, previousCoordinateYPixel) = getPixelFromCoordinate(
            previousCoordinate)
        paddingSize = 5
        yStart = previousCoordinateYPixel - \
            (dimensions['halfHeight'] + paddingSize)
        yEnd = previousCoordinateYPixel + \
            (dimensions['halfHeight'] + 1 + paddingSize)
        xStart = previousCoordinateXPixel - \
            (dimensions['halfWidth'] + paddingSize)
        xEnd = previousCoordinateXPixel + \
            (dimensions['halfWidth'] + paddingSize)
        areaImgToCompare = floorsImgs[floorLevel][yStart:yEnd, xStart:xEnd]
        areaFoundImg = locate(areaImgToCompare, radarImage, confidence=0.9)
        if areaFoundImg:
            currentCoordinateXPixel = previousCoordinateXPixel - \
                paddingSize + areaFoundImg[0]
            currentCoordinateYPixel = previousCoordinateYPixel - \
                paddingSize + areaFoundImg[1]
            (currentCoordinateX, currentCoordinateY) = getCoordinateFromPixel(
                (currentCoordinateXPixel, currentCoordinateYPixel))
            return (currentCoordinateX, currentCoordinateY, floorLevel)
    imgCoordinate = locate(floorsImgs[floorLevel], radarImage, confidence=0.75)
    if imgCoordinate is None:
        return None
    xImgCoordinate = imgCoordinate[0] + dimensions['halfWidth']
    yImgCoordinate = imgCoordinate[1] + dimensions['halfHeight']
    xCoordinate, yCoordinate = getCoordinateFromPixel(
        (xImgCoordinate, yImgCoordinate))
    return (xCoordinate, yCoordinate, floorLevel)


# TODO: add unit tests
# TODO: add perf
def getFloorLevel(screenshot: GrayImage) -> FloorLevel | None:
    radarToolsPosition = getRadarToolsPosition(screenshot)
    if radarToolsPosition is None:
        return None
    left, top, width, height = radarToolsPosition
    left = left + width + 8
    top = top - 7
    height = 67
    width = 2
    floorLevelImg = screenshot[top:top + height, left:left + width]
    floorImgHash = hashit(floorLevelImg)
    if floorImgHash not in floorsLevelsImgsHashes:
        return None
    return floorsLevelsImgsHashes[floorImgHash]


# TODO: add unit tests
# TODO: add perf
def getClosestWaypointIndexFromCoordinate(coordinate: Coordinate, waypoints: WaypointList) -> Union[int, None]:
    if not hasattr(py_rust_lib, 'find_closest_waypoint_index_rust'):
        raise RuntimeError("Rust FFI function 'find_closest_waypoint_index_rust' is not available.")

    if not waypoints:
        return None

    target_x = float(coordinate[0])
    target_y = float(coordinate[1])
    target_z = int(coordinate[2]) # Assuming floor level is integer

    # Extract coordinates from waypoints and flatten
    # WaypointList is List[Dict[str, Any]], with waypoint['coordinate'] being (x,y,z)
    # Rust expects a flat array: [x1,y1,z1, x2,y2,z2, ...]
    flat_waypoints_data = []
    for waypoint in waypoints:
        wp_coord = waypoint['coordinate']
        flat_waypoints_data.extend([float(wp_coord[0]), float(wp_coord[1]), float(wp_coord[2])]) # Keep z as float for array type consistency
    
    if not flat_waypoints_data: # Should not happen if waypoints list was not empty, but good check
        return None

    waypoints_np = np.array(flat_waypoints_data, dtype=np.float64)
    # No need to check for C_CONTIGUOUS here if creating from a list of Python floats, 
    # np.array will make it contiguous by default.

    waypoints_ptr = waypoints_np.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    num_waypoints = len(waypoints) # Number of 3D waypoints

    closest_idx = py_rust_lib.find_closest_waypoint_index_rust(
        ctypes.c_double(target_x),
        ctypes.c_double(target_y),
        ctypes.c_int32(target_z), # Passed as int32 to Rust
        waypoints_ptr,
        ctypes.c_size_t(num_waypoints)
    )

    if closest_idx < 0:
        # Rust function indicates no suitable waypoint found or an error
        return None
    
    return closest_idx


# TODO: add perf
def getBreakpointTileMovementSpeed(charSpeed: int, tileFriction: TileFriction) -> int:
    tileFrictionNotFound = tileFriction not in tilesFrictionsWithBreakpoints
    if tileFrictionNotFound:
        closestTilesFrictions = np.flatnonzero(
            availableTilesFrictions > tileFriction)
        tileFriction = availableTilesFrictions[closestTilesFrictions[0]] if len(
            closestTilesFrictions) > 0 else 250
    availableBreakpointsIndexes = np.flatnonzero(
        charSpeed >= tilesFrictionsWithBreakpoints[tileFriction])
    if len(availableBreakpointsIndexes) == 0:
        return breakpointTileMovementSpeed[1]
    return breakpointTileMovementSpeed.get(availableBreakpointsIndexes[-1] + 1)


# TODO: add unit tests
# TODO: add perf
def getTileFrictionByCoordinate(coordinate: Coordinate) -> TileFriction:
    xOfPixelCoordinate, yOfPixelCoordinate = getPixelFromCoordinate(
        coordinate)
    floorLevel = coordinate[2]
    tileFriction = floorsPathsSqms[floorLevel,
                                   yOfPixelCoordinate, xOfPixelCoordinate]
    return tileFriction


# TODO: add unit tests
# TODO: add perf
def isCloseToCoordinate(currentCoordinate: Coordinate, possibleCloseCoordinate: Coordinate, distanceTolerance: int = 10) -> bool:
    if not hasattr(py_rust_lib, 'are_coordinates_close_rust'):
        raise RuntimeError("Rust FFI function 'are_coordinates_close_rust' is not available.")

    x1 = float(currentCoordinate[0])
    y1 = float(currentCoordinate[1])
    # z1 is ignored for 2D distance

    x2 = float(possibleCloseCoordinate[0])
    y2 = float(possibleCloseCoordinate[1])
    # z2 is ignored for 2D distance
    
    # Ensure distanceTolerance is also float for FFI call
    dt_float = float(distanceTolerance)

    return py_rust_lib.are_coordinates_close_rust(
        ctypes.c_double(x1),
        ctypes.c_double(y1),
        ctypes.c_double(x2),
        ctypes.c_double(y2),
        ctypes.c_double(dt_float)
    )


# TODO: add unit tests
# TODO: add perf
# TODO: 2 coordinates was tested. Is very hard too test all coordinates(16 floors * 2560 mapWidth * 2048 mapHeight = 83.886.080 pixels)
# NumbaWarning: Cannot cache compiled function "isCoordinateWalkable" as it uses dynamic globals (such as ctypes pointers and large global arrays)
def isCoordinateWalkable(coordinate: Coordinate) -> bool:
    (xOfPixel, yOfPixel) = getPixelFromCoordinate(coordinate)
    return (walkableFloorsSqms[coordinate[2], yOfPixel, xOfPixel]) == 1


# TODO: add unit tests
# TODO: add perf
def isNonWalkablePixelColor(pixelColor: GrayPixel) -> bool:
    return np.isin(pixelColor, nonWalkablePixelsColors)
