from ...typings import Context
from .common.base import BaseTask
from src.utils.keyboard import keyDown, keyUp
import src.repositories.gameWindow.slot as gameWindowSlot

class LootMonstersBoxTask(BaseTask):
    def __init__(self):
        super().__init__()
        self.name = 'lootMonstersBox'
        self.isRootTask = True
        self.delayBeforeStart = 0.4

    def shouldIgnore(self, context: Context) -> bool:
        if context['ng_lastUsedSpellLoot'] is None:
            return True
        else:
            return False

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        keyDown('shift')
        gameWindowSlot.rightClickSlot(
            [6, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 4], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [6, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 5], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [6, 6], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [7, 6], context['gameWindow']['coordinate'])
        gameWindowSlot.rightClickSlot(
            [8, 6], context['gameWindow']['coordinate'])
        keyUp('shift')
        return context