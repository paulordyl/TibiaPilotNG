from ...typings import Context
from .common.vector import VectorTask
from .clickInClosestCreature import ClickInClosestCreatureTask
from .walkToTargetCreature import WalkToTargetCreatureTask
from src.repositories.gameWindow.creatures import getNearestCreaturesCount
import src.utils.keyboard as keyboard

class AttackClosestCreatureTask(VectorTask):
    def __init__(self):
        super().__init__()
        self.name = 'attackClosestCreature'
        self.isRootTask = True
        self.runTimesWithoutCloseMonster = 0

    def shouldManuallyComplete(self, context: Context) -> bool:
        nearestCreaturesCount = getNearestCreaturesCount(context['gameWindow']['monsters'])

        if nearestCreaturesCount == 0:
            self.runTimesWithoutCloseMonster = self.runTimesWithoutCloseMonster + 1
        else:
            self.runTimesWithoutCloseMonster = 0

        if self.runTimesWithoutCloseMonster >= 70:
            keyboard.press('esc')
            return True

        return False

    # TODO: task should have like 5 retries until all tree is destroyed
    def onBeforeStart(self, context: Context) -> Context:
        if context['ng_cave']['runToCreatures'] == True:
            self.tasks = [
                ClickInClosestCreatureTask().setParentTask(self).setRootTask(self),
                WalkToTargetCreatureTask().setParentTask(self).setRootTask(self),
            ]
        else:
            self.tasks = [
                ClickInClosestCreatureTask().setParentTask(self).setRootTask(self),
            ]
        return context
