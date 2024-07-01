from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.repositories.actionBar.core import slotIsAvailable
from ...typings import Context
from ..utils.potions import matchManaHealing


tasksOrchestrator = TasksOrchestrator()


# TODO: add unit tests
def healingByMana(context: Context):
    if context['ng_statusBar']['hpPercentage'] <= context['healing']['potions']['firstHealthPotion']['hpPercentageLessThanOrEqual'] and context['healing']['potions']['firstHealthPotion']['enabled']:
        return
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    if context['healing']['potions']['firstManaPotion']['enabled']:
        # if matchManaHealing(context['healing']['potions']['firstManaPotion'], context['ng_statusBar']) and slotIsAvailable(context['ng_screenshot'], context['healing']['potions']['firstManaPotion']['slot']):
        if matchManaHealing(context['healing']['potions']['firstManaPotion'], context['ng_statusBar']):
            tasksOrchestrator.setRootTask(context, UseHotkeyTask(
                context['healing']['potions']['firstManaPotion']['hotkey'], delayAfterComplete=1))
            return
