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
        return context['ng_cave']['targetCreature'] is not None

    def do(self, context: Context) -> Context:
        if context['ng_cave']['isAttackingSomeCreature'] == False:
            # TODO: find another way (maybe click in battle)
            # attack by mouse click when there are players on screen or ignorable creatures
            if context['gameWindow']['players'] or context['ng_targeting']['hasIgnorableCreatures']:
                if context['ng_cave'] and context['ng_cave']['closestCreature'] and context['ng_cave']['closestCreature']['windowCoordinate']:
                    mouse.rightClick(context['ng_cave']['closestCreature']['windowCoordinate'])
                return context
            keyboard.press('space')

        return context