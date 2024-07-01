from src.utils.keyboard import press
from ...typings import Context
from .common.base import BaseTask
from src.utils.core import getScreenshot
from src.repositories.radar.core import getClosestWaypointIndexFromCoordinate, getCoordinate
from ..waypoint import resolveGoalCoordinate

class MoveUp(BaseTask):
    def __init__(self, context, direction: str):
        super().__init__()
        self.name = 'moveUp'
        self.isRootTask = True
        self.direction = direction
        self.floorLevel = context['ng_radar']['coordinate'][2] - 1

    # TODO: add unit tests
    # TODO: improve this code
    def do(self, context: Context) -> bool:
        direction = None
        if self.direction == 'north':
            direction = 'up'
        if self.direction == 'south':
            direction = 'down'
        if self.direction == 'west':
            direction = 'left'
        if self.direction == 'east':
            direction = 'right'
        press(direction)
        return context

    # TODO: add unit tests
    def onComplete(self, context: Context) -> Context:
        context['ng_screenshot'] = getScreenshot()
        context['ng_radar']['coordinate'] = getCoordinate(
            context['ng_screenshot'], previousCoordinate=context['ng_radar']['previousCoordinate'])
        if context['ng_radar']['coordinate'][2] != self.floorLevel:
            context['ng_cave']['waypoints']['currentIndex'] = getClosestWaypointIndexFromCoordinate(
                context['ng_radar']['coordinate'], context['ng_cave']['waypoints']['items'])
            currentWaypoint = context['ng_cave']['waypoints']['items'][context['ng_cave']
                                                                ['waypoints']['currentIndex']]
            context['ng_cave']['waypoints']['state'] = resolveGoalCoordinate(
                context['ng_radar']['coordinate'], currentWaypoint)
        return context
