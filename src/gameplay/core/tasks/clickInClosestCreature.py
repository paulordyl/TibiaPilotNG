import src.utils.keyboard as keyboard
import src.utils.mouse as mouse
from ...typings import Context
from .common.base import BaseTask

class ClickInClosestCreatureTask(BaseTask):
    def __init__(self):
        super().__init__()
        self.name = 'clickInClosestCreature'
        self.delayOfTimeout = 1

    def shouldIgnore(self, context: Context) -> bool:
        return context.get('ng_cave', {}).get('targetCreature') is not None

    def do(self, context: Context) -> Context:
        if context.get('ng_cave', {}).get('isAttackingSomeCreature', False) == False:
            # attack by mouse click when there are players on screen or ignorable creatures
            if context.get('gameWindow', {}).get('players') or context.get('ng_targeting', {}).get('hasIgnorableCreatures'):
                closest = context.get('ng_cave', {}).get('closestCreature')
                if closest and closest.get('windowCoordinate'):
                    keyboard.keyDown('alt')
                    mouse.leftClick(closest['windowCoordinate'])
                    keyboard.keyUp('alt')
                return context
            keyboard.press('space')

        return context

    def did(self, context: Context) -> bool:
        # Consider the task done when the bot is attacking some creature
        return bool(context.get('ng_cave', {}).get('isAttackingSomeCreature', False))