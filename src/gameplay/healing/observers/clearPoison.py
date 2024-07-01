from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.repositories.actionBar.core import hasCooldownByName
from src.wiki.spells import spells
from ...typings import Context

tasksOrchestrator = TasksOrchestrator()

# TODO: add unit tests
def clearPoison(context: Context):
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    if not context['clear_stats']['poison']:
        return
    if context['statsBar']['poison'] is not None and context['statsBar']['poison'] == False:
        return
    if hasCooldownByName(context['ng_screenshot'], 'exana pox'):
        return
    if context['ng_statusBar']['mana'] < spells['exana pox']['manaNeeded']:
        return
    tasksOrchestrator.setRootTask(
        context, UseHotkeyTask(context['clear_stats']['poison_hotkey'], delayAfterComplete=1))
