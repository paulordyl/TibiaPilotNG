try:
    from nptyping import NDArray
except Exception:
    NDArray = None

from typing import Any, List, Tuple, Union


BBox = Tuple[int, int, int, int]
Coordinate = Tuple[int, int, int]
CoordinateList = List[Coordinate]
CreatureCategory = str
CreatureCategoryOrUnknown = Union[CreatureCategory, 'unknown']
Direction = Union['up', Union['down', Union['left', 'right']]]
# Use Any if NDArray is not available at runtime
if NDArray is None:
    GrayImage = Any
    GrayVector = Any
else:
    GrayImage = NDArray[Any, Any]
    GrayVector = NDArray[Any, Any]

GrayPixel = int
Slot = Tuple[int, int]
SlotWidth = 32 | 64
Waypoint = Any
WaypointList = List[Waypoint]
XYCoordinate = Tuple[int, int]
XYCoordinateList = List[Coordinate]