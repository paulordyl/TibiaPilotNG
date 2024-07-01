import src.utils.keyboard as keyboard
from ...typings import Context
from .common.vector import VectorTask
from .attackClosestCreature import AttackClosestCreatureTask
from src.repositories.gameWindow.creatures import getNearestCreaturesCount
from .setNextWaypoint import SetNextWaypointTask

class AttackMonstersBoxTask(VectorTask):
    def __init__(self):
        super().__init__()
        self.name = 'attackMonstersBox'
        self.isRootTask = True
        self.runTimesWithoutCloseMonster = 0

    def shouldIgnore(self, context: Context) -> bool:
        hasMonsters = len(context['ng_battleList']['creatures']) > 0
        return not hasMonsters

    def shouldRestartAfterAllChildrensComplete(self, context: Context) -> bool:
        nearestCreaturesCount = getNearestCreaturesCount(context['gameWindow']['monsters'])

        if nearestCreaturesCount == 0:
            self.runTimesWithoutCloseMonster = self.runTimesWithoutCloseMonster + 1
        else:
            self.runTimesWithoutCloseMonster = 0

        if self.runTimesWithoutCloseMonster >= 70:
            keyboard.press('esc')
            return False

        if any(creature[0] != 'Unknown' for creature in context['ng_battleList']['creatures']):
            return True
        
        return False

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            AttackClosestCreatureTask().setParentTask(self).setRootTask(self),
        ]
        return context
    
    def onIgnored(self, context: Context) -> Context:
        context['ng_tasksOrchestrator'].setRootTask(
                context, SetNextWaypointTask())

        return context