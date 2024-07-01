import src.repositories.gameWindow.core as gameWindowCore
import src.repositories.gameWindow.slot as gameWindowSlot
from ...typings import Context
from .common.base import BaseTask
from time import sleep

class RightClickDirectionTask(BaseTask):
    def __init__(self, direction: str):
        super().__init__()
        self.name = 'rightClickDirection'
        self.direction = direction

    def do(self, context: Context) -> Context:
        clickCoord = list(context['ng_radar']['coordinate'])
        if self.direction == 'north':
            clickCoord[1] = clickCoord[1] - 1
        if self.direction == 'south':
            clickCoord[1] = clickCoord[1] + 1
        if self.direction == 'west':
            clickCoord[0] = clickCoord[0] + 1
        if self.direction == 'east':
            clickCoord[0] = clickCoord[0] - 1

        clickCoord = tuple(clickCoord)
        slot = gameWindowCore.getSlotFromCoordinate(
            context['ng_radar']['coordinate'], clickCoord)
        sleep(0.2)
        gameWindowSlot.rightClickSlot(slot, context['gameWindow']['coordinate'])
        sleep(0.2)
        return context
