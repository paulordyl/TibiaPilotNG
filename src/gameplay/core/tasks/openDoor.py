from src.shared.typings import Waypoint
from ...typings import Context
from .common.base import BaseTask
import src.gameplay.utils as gameplayUtils
import src.repositories.gameWindow.core as gameWindowCore
import src.repositories.gameWindow.slot as gameWindowSlot
from time import sleep

class OpenDoorTask(BaseTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'openDoor'
        self.isRootTask = True
        self.waypoint = waypoint
        self.withoutSlot = False

    def shouldRestart(self, _: Context) -> bool:
        if self.withoutSlot == True:
            self.withoutSlot = False
            return True
        else:
            return False

    # TODO: add unit tests
    def shouldIgnore(self, context: Context) -> bool:
        if not gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], self.waypoint['coordinate']):
            return True
        else:
            return False

    def onIgnored(self, context: Context) -> Context:
        # TODO: func to check if coord is none
        if context['ng_radar']['coordinate'] is None:
            return context
        if any(coord is None for coord in context['ng_radar']['coordinate']):
            return context
        slot = gameWindowCore.getSlotFromCoordinate(
            context['ng_radar']['coordinate'], self.waypoint['coordinate'])
        sleep(0.2)
        if slot is None:
            self.withoutSlot = True
            return context
        gameWindowSlot.rightClickSlot(slot, context['gameWindow']['coordinate'])
        sleep(0.2)
        return context

    def onComplete(self, context: Context) -> Context:
        return context
