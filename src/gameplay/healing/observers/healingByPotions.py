from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.repositories.actionBar.core import slotIsAvailable
from ...typings import Context
from ..utils.potions import matchHpHealing


tasksOrchestrator = TasksOrchestrator()


# TODO: add unit tests
def healingByPotions(context: Context):
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    if context['healing']['potions']['firstHealthPotion']['enabled']:
        # if matchHpHealing(context['healing']['potions']['firstHealthPotion'], context['ng_statusBar']) and slotIsAvailable(context['ng_screenshot'], context['healing']['potions']['firstHealthPotion']['slot']):
        if matchHpHealing(context['healing']['potions']['firstHealthPotion'], context['ng_statusBar']):
            tasksOrchestrator.setRootTask(context, UseHotkeyTask(
                context['healing']['potions']['firstHealthPotion']['hotkey'], delayAfterComplete=1))
            return