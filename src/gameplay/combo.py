from src.gameplay.comboSpells.core import comboSpellDidMatch
from src.gameplay.core.tasks.orchestrator import TasksOrchestrator
from src.repositories.actionBar.core import hasCooldownByName
from src.repositories.gameWindow.creatures import getNearestCreaturesCount
from src.wiki.spells import spells
from .core.tasks.useComboHotkey import UseComboHotkeyTask
from .typings import Context


tasksOrchestrator = TasksOrchestrator()


# TODO: do not execute algorithm when has no combo spells
# TODO: add unit tests
# TODO: check if spell is casted, if not try cast again
def comboSpells(context: Context):
    if context['ng_statusBar']['mana'] is None or context['ng_comboSpells']['enabled'] == False:
        return
    currentTask = tasksOrchestrator.getCurrentTask(context)
    if currentTask is not None:
        if currentTask.status == 'completed':
            tasksOrchestrator.reset()
        else:
            tasksOrchestrator.do(context)
            return
    nearestCreaturesCount = getNearestCreaturesCount(
        context['gameWindow']['monsters'])
    if nearestCreaturesCount == 0:
        return
    if context['ng_statusBar']['hpPercentage'] <= context['healing']['potions']['firstHealthPotion']['hpPercentageLessThanOrEqual']:
        return
    if context['ng_statusBar']['manaPercentage'] <= 30:
        return
    for key, comboSpell in enumerate(context['ng_comboSpells']['items']):
        if comboSpell['enabled'] == False:
            continue
        if comboSpellDidMatch(comboSpell, nearestCreaturesCount):
            spell = comboSpell['spells'][comboSpell['currentSpellIndex']]
            # TODO: JUST COMBO WHEN CAITING WITH PALADIN (NOT FOR NOW)
            if context['ng_cave']['isAttackingSomeCreature'] == False:
                return
            if context['ng_statusBar']['mana'] < spells[spell['name']]['manaNeeded']:
                return
            # TODO: ADD SPELL CATEGORY IN WIKI
            if spell['name'] in ['utito tempo', 'utamo tempo']:
                if hasCooldownByName(context['ng_screenshot'], 'support'):
                    return
            else:
                if hasCooldownByName(context['ng_screenshot'], 'attack'):
                    return
            if hasCooldownByName(context['ng_screenshot'], spell['name']):
                return
            # TODO: verify if spell hotkey slot is available
            tasksOrchestrator.setRootTask(
                context, UseComboHotkeyTask(spell['hotkey'], spell['name']))
            return
