from typing import Union
from src.repositories.gameWindow.creatures import hasTargetToCreature
from .core.tasks.attackClosestCreature import AttackClosestCreatureTask
from .typings import Context


# TODO: add unit tests
def resolveCavebotTasks(context: Context) -> Union[AttackClosestCreatureTask, None]:
    currentTask = context['ng_tasksOrchestrator'].getCurrentTask(context)
    if context['ng_cave']['isAttackingSomeCreature']:
        if context['ng_cave']['targetCreature'] is None:
            return context
        if hasTargetToCreature(
                context['gameWindow']['monsters'], context['ng_cave']['targetCreature'], context['ng_radar']['coordinate']) == False:
            if context['ng_cave']['closestCreature'] is None:
                return context
            context['ng_tasksOrchestrator'].setRootTask(
                context, AttackClosestCreatureTask())
            return context
        if currentTask is None or context['ng_tasksOrchestrator'].rootTask.name != 'attackClosestCreature':
            context['ng_tasksOrchestrator'].setRootTask(
                context, AttackClosestCreatureTask())
        return context
    if context['ng_cave']['closestCreature'] is None:
        return context
    context['ng_tasksOrchestrator'].setRootTask(
        context, AttackClosestCreatureTask())
    return context


# TODO: add unit tests
def shouldAskForCavebotTasks(context: Context) -> bool:
    if context['way'] != 'ng_cave':
        return False
    currentTask = context['ng_tasksOrchestrator'].getCurrentTask(context)
    if currentTask is None:
        return True
    return (currentTask.name not in ['dropFlasks', 'lootCorpse', 'moveDown', 'moveUp', 'singleMove', 'rightClickDirection', 'refillChecker', 'singleWalk', 'refillChecker', 'useRopeWaypoint', 'useShovelWaypoint', 'rightClickUseWaypoint', 'openDoor', 'useLadderWaypoint'])
