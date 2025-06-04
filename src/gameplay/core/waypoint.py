import tcod
from src.repositories.radar.config import walkableFloorsSqms
from src.shared.typings import Coordinate, CoordinateList
from src.utils.coordinate import getAvailableAroundCoordinates, getClosestCoordinate, getPixelFromCoordinate
from .typings import Checkpoint
from src.utils.config_manager import get_config


# TODO: add unit tests
def generateFloorWalkpoints(coordinate: Coordinate, goalCoordinate: Coordinate, nonWalkableCoordinates: CoordinateList = []) -> CoordinateList:
    pixelCoordinate = getPixelFromCoordinate(coordinate)
    radar_x_offset = get_config('pathfinding.radar_x_offset', 53)
    radar_y_offset_start = get_config('pathfinding.radar_y_offset_start', 54)
    radar_y_offset_end = get_config('pathfinding.radar_y_offset_end', 55)

    xFromTheStartOfRadar = pixelCoordinate[0] - radar_x_offset
    xFromTheEndOfRadar = pixelCoordinate[0] + radar_x_offset
    yFromTheStartOfRadar = pixelCoordinate[1] - radar_y_offset_start
    yFromTheEndOfRadar = pixelCoordinate[1] + radar_y_offset_end

    # Calculate derived dimensions for checks, ensuring they are positive
    derived_x_dim = radar_x_offset * 2
    derived_y_dim = radar_y_offset_start + radar_y_offset_end -1 # Example: 54+55 = 109. Max index is 108 if size is 109.

    copiedWalkableFloorSqms = walkableFloorsSqms[coordinate[2]][
        yFromTheStartOfRadar:yFromTheEndOfRadar, xFromTheStartOfRadar:xFromTheEndOfRadar].copy()
    for nonWalkableCoordinate in nonWalkableCoordinates:
        if nonWalkableCoordinate[2] == coordinate[2]:
            nonWalkableCoordinateInPixelX, nonWalkableCoordinateInPixelY = getPixelFromCoordinate(nonWalkableCoordinate)
            leX = nonWalkableCoordinateInPixelX - xFromTheStartOfRadar
            leY = nonWalkableCoordinateInPixelY - yFromTheStartOfRadar
            # Ensure derived_x_dim and derived_y_dim are correctly calculated for boundary checks
            if leX >= 0 and leX <= derived_x_dim and leY >= 0 and leY <= derived_y_dim : # Adjusted boundary
                copiedWalkableFloorSqms[leY, leX] = 0

    x = goalCoordinate[0] - coordinate[0] + radar_x_offset
    y = goalCoordinate[1] - coordinate[1] + radar_y_offset_start

    astar_diagonal_cost = get_config('pathfinding.astar_diagonal_cost', 0)
    # The start point for AStar.get_path is relative to the sliced copiedWalkableFloorSqms
    # So, it should be (radar_y_offset_start, radar_x_offset) if these are 0-indexed midpoints of the slice
    start_y_astar = radar_y_offset_start
    start_x_astar = radar_x_offset

    return [[coordinate[0] + x_path - radar_x_offset,
             coordinate[1] + y_path - radar_y_offset_start, coordinate[2]]
            for y_path, x_path in tcod.path.AStar(copiedWalkableFloorSqms, cost=astar_diagonal_cost).get_path(start_y_astar, start_x_astar, y, x)]

# TODO: add unit tests
def resolveFloorCoordinate(_, nextCoordinate: Coordinate) -> Checkpoint:
    return {
        'goalCoordinate': nextCoordinate,
        'checkInCoordinate': nextCoordinate,
    }


# TODO: add types
# TODO: add unit tests
def resolveMoveDownCoordinate(_, waypoint) -> Checkpoint:
    checkInCoordinate = None
    offset = get_config('pathfinding.move_action_offset', 2)
    if waypoint['options']['direction'] == 'north':
        checkInCoordinate = [waypoint['coordinate'][0], waypoint['coordinate'][1] - offset, waypoint['coordinate'][2] + 1]
    elif waypoint['options']['direction'] == 'south':
        checkInCoordinate = [waypoint['coordinate'][0], waypoint['coordinate'][1] + offset, waypoint['coordinate'][2] + 1]
    elif waypoint['options']['direction'] == 'east':
        checkInCoordinate = [waypoint['coordinate'][0] + offset, waypoint['coordinate'][1], waypoint['coordinate'][2] + 1]
    else: # west
        checkInCoordinate = [waypoint['coordinate'][0] - offset, waypoint['coordinate'][1], waypoint['coordinate'][2] + 1]
    return {
        'goalCoordinate': waypoint['coordinate'],
        'checkInCoordinate': checkInCoordinate,
    }


# TODO: add types
# TODO: add unit tests
def resolveMoveUpCoordinate(_, waypoint) -> Checkpoint:
    checkInCoordinate = None
    offset = get_config('pathfinding.move_action_offset', 2)
    if waypoint['options']['direction'] == 'north':
        checkInCoordinate = [waypoint['coordinate'][0], waypoint['coordinate'][1] - offset, waypoint['coordinate'][2] - 1]
    elif waypoint['options']['direction'] == 'south':
        checkInCoordinate = [waypoint['coordinate'][0], waypoint['coordinate'][1] + offset, waypoint['coordinate'][2] - 1]
    elif waypoint['options']['direction'] == 'east':
        checkInCoordinate = [waypoint['coordinate'][0] + offset, waypoint['coordinate'][1], waypoint['coordinate'][2] - 1]
    else: # west
        checkInCoordinate = [waypoint['coordinate'][0] - offset, waypoint['coordinate'][1], waypoint['coordinate'][2] - 1]
    return {
        'goalCoordinate': waypoint['coordinate'],
        'checkInCoordinate': checkInCoordinate,
    }


# TODO: add unit tests
def resolveUseShovelWaypointCoordinate(coordinate, nextCoordinate: Coordinate) -> Checkpoint:
    availableAroundCoordinates = getAvailableAroundCoordinates(
        nextCoordinate, walkableFloorsSqms[nextCoordinate[2]])
    closestCoordinate = getClosestCoordinate(
        coordinate, availableAroundCoordinates)
    checkInCoordinate = [nextCoordinate[0], nextCoordinate[1], nextCoordinate[2] + 1]
    return {
        'goalCoordinate': closestCoordinate,
        'checkInCoordinate': checkInCoordinate,
    }


# TODO: add unit tests
def resolveUseRopeWaypointCoordinate(_, nextCoordinate: Coordinate) -> Checkpoint:
    return {
        'goalCoordinate': [nextCoordinate[0], nextCoordinate[1], nextCoordinate[2]],
        'checkInCoordinate': [nextCoordinate[0], nextCoordinate[1] + 1, nextCoordinate[2] - 1],
    }


# TODO: add unit tests
def resolveUseHoleCoordinate(_, nextCoordinate: Coordinate) -> Checkpoint:
    return {
        'goalCoordinate': nextCoordinate,
        'checkInCoordinate': [nextCoordinate[0], nextCoordinate[1], nextCoordinate[2] + 1],
    }


# TODO: add unit tests
def resolveGoalCoordinate(coordinate: Coordinate, waypoint):
    if waypoint['type'] == 'useRope':
        return resolveUseRopeWaypointCoordinate(coordinate, waypoint['coordinate'])
    if waypoint['type'] == 'useShovel':
        return resolveUseShovelWaypointCoordinate(coordinate, waypoint['coordinate'])
    if waypoint['type'] == 'moveDown':
        return resolveMoveDownCoordinate(coordinate, waypoint)
    if waypoint['type'] == 'moveUp':
        return resolveMoveUpCoordinate(coordinate, waypoint)
    if waypoint['type'] == 'useHole':
        return resolveUseHoleCoordinate(coordinate, waypoint['coordinate'])
    return resolveFloorCoordinate(coordinate, waypoint['coordinate'])
