from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask
from src.gameplay.core.tasks.useSpellHealHotkey import UseSpellHealHotkeyTask
from src.repositories.actionBar.core import hasCooldownByName
from src.wiki.spells import spells
from ...typings import Context


tasksOrchestrator = TasksOrchestrator()


# TODO: add unit tests
def healingBySpells(context: Context):
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
    if context['healing']['spells']['criticalHealing']['enabled']:
        if context['ng_statusBar']['hpPercentage'] <= context['healing']['spells']['criticalHealing']['hpPercentageLessThanOrEqual'] and context['ng_statusBar']['mana'] >= spells[context['healing']['spells']['lightHealing']['spell']]['manaNeeded'] and not hasCooldownByName(context['ng_screenshot'], context['healing']['spells']['criticalHealing']['spell']):
            tasksOrchestrator.setRootTask(
                context, UseHotkeyTask(context['healing']['spells']['criticalHealing']['hotkey']))
            return
    if context['healing']['spells']['lightHealing']['enabled']:
        if context['ng_statusBar']['hpPercentage'] <= context['healing']['spells']['lightHealing']['hpPercentageLessThanOrEqual'] and context['ng_statusBar']['mana'] >= spells[context['healing']['spells']['lightHealing']['spell']]['manaNeeded'] and not hasCooldownByName(context['ng_screenshot'], context['healing']['spells']['lightHealing']['spell']):
            tasksOrchestrator.setRootTask(
                context, UseSpellHealHotkeyTask(context['healing']['spells']['lightHealing']['hotkey']))
            return
    if context['healing']['spells']['utura']['enabled']:
        if context['ng_statusBar']['mana'] >= spells['utura']['manaNeeded'] and not hasCooldownByName(context['ng_screenshot'], 'utura'):
            tasksOrchestrator.setRootTask(
                context, UseHotkeyTask(context['healing']['spells']['utura']['hotkey']))
            return
    if context['healing']['spells']['uturaGran']['enabled']:
        if context['ng_statusBar']['mana'] >= spells['utura gran']['manaNeeded'] and not hasCooldownByName(context['ng_screenshot'], 'utura gran'):
            tasksOrchestrator.setRootTask(
                context, UseHotkeyTask(context['healing']['spells']['uturaGran']['hotkey']))
