from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.repositories.actionBar.core import hasCooldownByName
from src.wiki.spells import spells
from ...typings import Context

tasksOrchestrator = TasksOrchestrator()

# TODO: add unit tests
def autoHur(context: Context):
    if context['ng_statusBar']['hpPercentage'] <= context['healing']['potions']['firstHealthPotion']['hpPercentageLessThanOrEqual'] and context['healing']['potions']['firstHealthPotion']['enabled']:
        return
    if context['ng_statusBar']['manaPercentage'] <= 30 and context['healing']['potions']['firstManaPotion']['enabled']:
        return
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    if not context['auto_hur']['enabled']:
        return
    if context['statsBar']['hur'] is not None and context['statsBar']['hur'] == True:
        return
    if context['auto_hur']['pz'] == False and context['statsBar']['pz'] is not None and context['statsBar']['pz'] == True:
        return
    currentTaskName = context['ng_tasksOrchestrator'].getCurrentTaskName(context)
    if currentTaskName in ['attackClosestCreature', 'lootMonstersBox', 'refill', 'buyBackpack', 'useRopeWaypoint', 'useShovelWaypoint', 'rightClickUseWaypoint', 'openDoor', 'useLadderWaypoint']:
        return
    if hasCooldownByName(context['ng_screenshot'], 'support'):
        return
    if hasCooldownByName(context['ng_screenshot'], context['auto_hur']['spell']):
        return
    if context['ng_statusBar']['mana'] < spells[context['auto_hur']['spell']]['manaNeeded']:
        return
    tasksOrchestrator.setRootTask(
        context, UseHotkeyTask(context['auto_hur']['hotkey'], delayAfterComplete=1))
