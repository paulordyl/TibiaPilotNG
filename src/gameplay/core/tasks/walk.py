import src.gameplay.utils as gameplayUtils
from src.repositories.radar.core import getBreakpointTileMovementSpeed, getTileFrictionByCoordinate
from src.repositories.skills.core import getSpeed
from src.shared.typings import Coordinate
from src.utils.coordinate import getDirectionBetweenCoordinates
from src.utils.keyboard import keyDown, press
from ...typings import Context
from ...utils import releaseKeys
from .common.base import BaseTask


class WalkTask(BaseTask):
    def __init__(self, context: Context, coordinate: Coordinate, passinho=False):
        super().__init__()
        self.name = 'walk'
        charSpeed = getSpeed(context['ng_screenshot'])
        tileFriction = getTileFrictionByCoordinate(coordinate)
        movementSpeed = getBreakpointTileMovementSpeed(
            charSpeed, tileFriction)
        self.delayOfTimeout = (movementSpeed * 2) / 1000
        # TODO: fix passinho with char speed
        self.delayBeforeStart = (movementSpeed * 2) / 1000 if passinho == True else 0
        self.shouldTimeoutTreeWhenTimeout = True
        self.walkpoint = coordinate

    # TODO: add unit tests
    def shouldIgnore(self, context: Context) -> bool:
        if context['ng_radar']['lastCoordinateVisited'] is None:
            return True
        return not gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], context['ng_radar']['lastCoordinateVisited'])

    # TODO: add unit tests
    def do(self, context: Context) -> bool:
        direction = getDirectionBetweenCoordinates(
            context['ng_radar']['coordinate'], self.walkpoint)
        if direction is None:
            return context
        futureDirection = None
        if self.parentTask and len(self.parentTask.tasks) > 1:
            if self.parentTask.currentTaskIndex + 1 < len(self.parentTask.tasks):
                futureDirection = getDirectionBetweenCoordinates(
                    self.walkpoint, self.parentTask.tasks[self.parentTask.currentTaskIndex + 1].walkpoint)
        if direction != futureDirection:
            if context['ng_lastPressedKey'] is not None:
                context = releaseKeys(context)
            else:
                press(direction)
            return context
        if direction != context['ng_lastPressedKey']:
            if len(self.parentTask.tasks) > 2:
                keyDown(direction)
                context['ng_lastPressedKey'] = direction
            else:
                press(direction)
            return context
        if len(self.parentTask.tasks) == 1 and context['ng_lastPressedKey'] is not None:
            context = releaseKeys(context)
        return context

    # TODO: add unit tests
    def did(self, context: Context) -> bool:
        return gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], self.walkpoint)

    # TODO: add unit tests
    def onInterrupt(self, context: Context) -> Context:
        return releaseKeys(context)

    # TODO: add unit tests
    def onTimeout(self, context: Context) -> Context:
        return releaseKeys(context)
