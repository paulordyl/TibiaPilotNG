from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.repositories.actionBar.core import slotIsAvailable, slotIsEquipped
from ...typings import Context

tasksOrchestrator = TasksOrchestrator()

# TODO: add unit tests
def swapAmulet(context: Context):
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    if context['healing']['highPriority']['swapAmulet']['enabled'] == False:
        return
    currentTaskName = context['ng_tasksOrchestrator'].getCurrentTaskName(context)
    if currentTaskName in ['depositGold', 'refill', 'buyBackpack', 'selectChatTab', 'travel']:
        return
    tankAmuletSlotIsEquipped = slotIsEquipped(context['ng_screenshot'], context['healing']['highPriority']['swapAmulet']['tankAmulet']['slot'])
    tankAmuletSlotIsAvailable = slotIsAvailable(context['ng_screenshot'], context['healing']['highPriority']['swapAmulet']['tankAmulet']['slot'])
    if context['ng_statusBar']['hpPercentage'] <= context['healing']['highPriority']['swapAmulet']['tankAmulet']['hpPercentageLessThanOrEqual']:
        if not tankAmuletSlotIsEquipped and tankAmuletSlotIsAvailable:
            tasksOrchestrator.setRootTask(context, UseHotkeyTask(
                context['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'], delayAfterComplete=2))
        return
    mainAmuletSlotIsEquipped = slotIsEquipped(context['ng_screenshot'], context['healing']['highPriority']['swapAmulet']['mainAmulet']['slot'])
    mainAmuletSlotIsAvailable = slotIsAvailable(context['ng_screenshot'], context['healing']['highPriority']['swapAmulet']['mainAmulet']['slot'])
    if context['ng_statusBar']['hpPercentage'] > context['healing']['highPriority']['swapAmulet']['mainAmulet']['hpPercentageGreaterThan']:
        if not mainAmuletSlotIsEquipped and mainAmuletSlotIsAvailable:
            tasksOrchestrator.setRootTask(context, UseHotkeyTask(
                context['healing']['highPriority']['swapAmulet']['mainAmulet']['hotkey'], delayAfterComplete=2))
        return
    if context['healing']['highPriority']['swapAmulet']['tankAmuletAlwaysEquipped']:
        if not tankAmuletSlotIsEquipped and tankAmuletSlotIsAvailable:
            tasksOrchestrator.setRootTask(context, UseHotkeyTask(
                context['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'], delayAfterComplete=2))
        return
    if tankAmuletSlotIsEquipped:
        tasksOrchestrator.setRootTask(context, UseHotkeyTask(
            context['healing']['highPriority']['swapAmulet']['tankAmulet']['hotkey'], delayAfterComplete=2))
        return
    if mainAmuletSlotIsEquipped:
        tasksOrchestrator.setRootTask(context, UseHotkeyTask(
            context['healing']['highPriority']['swapAmulet']['mainAmulet']['hotkey'], delayAfterComplete=2))
