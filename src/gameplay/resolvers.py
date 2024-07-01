from typing import Union
from src.shared.typings import Waypoint
from .core.tasks.common.base import BaseTask
from .core.tasks.common.vector import VectorTask
from .core.tasks.depositGold import DepositGoldTask
from .core.tasks.depositItems import DepositItemsTask
from .core.tasks.depositItemsHouse import DepositItemsHouseTask
from .core.tasks.dropFlasks import DropFlasksTask
from .core.tasks.logout import LogoutTask
from .core.tasks.refill import RefillTask
from .core.tasks.buyBackpack import BuyBackpackTask
from .core.tasks.refillChecker import RefillCheckerTask
from .core.tasks.openDoorWaypoint import OpenDoorWaypointTask
from .core.tasks.singleWalk import SingleWalkTask
from .core.tasks.useRopeWaypoint import UseRopeWaypointTask
from .core.tasks.useShovelWaypoint import UseShovelWaypointTask
from .core.tasks.rightClickUseWaypoint import RightClickUseWaypointTask
from .core.tasks.useLadderWaypoint import UseLadderWaypointTask
from .core.tasks.walkToWaypoint import WalkToWaypointTask
from .core.tasks.travel import TravelTask
from .core.tasks.singleMove import SingleMoveTask
from .core.tasks.rightClickDirectionWaypoint import RightClickDirectionWaypointTask

# TODO: add unit tests
def resolveTasksByWaypoint(waypoint: Waypoint) -> Union[BaseTask, VectorTask]:
    if waypoint['type'] == 'depositGold':
        return DepositGoldTask()
    elif waypoint['type'] == 'travel':
        return TravelTask(waypoint)
    elif waypoint['type'] == 'depositItems':
        return DepositItemsTask(waypoint)
    elif waypoint['type'] == 'depositItemsHouse':
        return DepositItemsHouseTask()
    elif waypoint['type'] == 'dropFlasks':
        return DropFlasksTask()
    elif waypoint['type'] == 'logout':
        return LogoutTask()
    elif waypoint['type'] == 'moveDown':
        return SingleWalkTask(waypoint['type'], waypoint['options']['direction'])
    elif waypoint['type'] == 'moveUp':
        return SingleWalkTask(waypoint['type'], waypoint['options']['direction'])
    elif waypoint['type'] == 'singleMove':
        return SingleMoveTask(waypoint['options']['direction'])
    elif waypoint['type'] == 'rightClickDirection':
        return RightClickDirectionWaypointTask(waypoint['options']['direction'])
    elif waypoint['type'] == 'refill':
        return RefillTask(waypoint)
    elif waypoint['type'] == 'buyBackpack':
        return BuyBackpackTask(waypoint)
    elif waypoint['type'] == 'refillChecker':
        return RefillCheckerTask(waypoint)
    elif waypoint['type'] == 'openDoor':
        return OpenDoorWaypointTask(waypoint)
    elif waypoint['type'] == 'useRope':
        return UseRopeWaypointTask(waypoint)
    elif waypoint['type'] == 'useShovel':
        return UseShovelWaypointTask(waypoint)
    elif waypoint['type'] == 'rightClickUse':
        return RightClickUseWaypointTask(waypoint)
    elif waypoint['type'] == 'useLadder':
        return UseLadderWaypointTask(waypoint)
    elif waypoint['type'] == 'walk':
        return WalkToWaypointTask(waypoint['coordinate'], waypoint['ignore'], waypoint['passinho'])
