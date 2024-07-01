import src.repositories.gameWindow.core as gameWindowCore
import src.repositories.gameWindow.slot as gameWindowSlot
from src.shared.typings import Waypoint
import src.utils.keyboard as keyboard
from ...typings import Context
from .common.base import BaseTask
from time import sleep

class UseShovelTask(BaseTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'useShovel'
        self.waypoint = waypoint

    def shouldIgnore(self, context: Context) -> bool:
        return gameWindowCore.isHoleOpen(
            context['gameWindow']['image'], gameWindowCore.images[context['ng_resolution']]['holeOpen'], context['ng_radar']['coordinate'], self.waypoint['coordinate'])

    def do(self, context: Context) -> Context:
        slot = gameWindowCore.getSlotFromCoordinate(
            context['ng_radar']['coordinate'], self.waypoint['coordinate'])
        sleep(0.2)
        keyboard.press(context['general_hotkeys']['shovel_hotkey'])
        sleep(0.2)
        gameWindowSlot.clickSlot(slot, context['gameWindow']['coordinate'])
        sleep(0.2)
        return context

    def did(self, context: Context) -> bool:
        return self.shouldIgnore(context)
