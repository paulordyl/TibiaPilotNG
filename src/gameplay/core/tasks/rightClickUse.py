import src.repositories.gameWindow.core as gameWindowCore
import src.repositories.gameWindow.slot as gameWindowSlot
from src.shared.typings import Waypoint
from ...typings import Context
from .common.base import BaseTask
from time import sleep

class RightClickUseTask(BaseTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'rightClickUse'
        self.waypoint = waypoint

    def do(self, context: Context) -> Context:
        slot = gameWindowCore.getSlotFromCoordinate(
            context['ng_radar']['coordinate'], self.waypoint['coordinate'])
        sleep(0.2)
        gameWindowSlot.rightClickSlot(slot, context['gameWindow']['coordinate'])
        sleep(0.2)
        return context