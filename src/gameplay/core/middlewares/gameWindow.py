from src.repositories.battleList.core import getBeingAttackedCreatureCategory
from src.repositories.chat.core import hasNewLoot
from src.repositories.gameWindow.config import gameWindowSizes
from src.repositories.gameWindow.core import getCoordinate, getImageByCoordinate
from src.repositories.gameWindow.creatures import getCreatures, getCreaturesByType, getDifferentCreaturesBySlots, getTargetCreature
from ...comboSpells.core import spellsPath
from ...typings import Context
from ..tasks.selectChatTab import SelectChatTabTask


# TODO: add unit tests
def setDirectionMiddleware(context: Context) -> Context:
    if context['ng_radar']['previousCoordinate'] is None:
        context['ng_radar']['previousCoordinate'] = context['ng_radar']['coordinate']

    if (context['ng_radar']['coordinate'] is not None and
            context['ng_radar']['previousCoordinate'] is not None):
        if (context['ng_radar']['coordinate'][0] != context['ng_radar']['previousCoordinate'][0] or
                context['ng_radar']['coordinate'][1] != context['ng_radar']['previousCoordinate'][1] or
                context['ng_radar']['coordinate'][2] != context['ng_radar']['previousCoordinate'][2]):

            comingFromDirection = None
            if context['ng_radar']['coordinate'][2] != context['ng_radar']['previousCoordinate'][2]:
                comingFromDirection = None
            elif (context['ng_radar']['coordinate'][0] != context['ng_radar']['previousCoordinate'][0] and
                context['ng_radar']['coordinate'][1] != context['ng_radar']['previousCoordinate'][1]):
                comingFromDirection = None
            elif context['ng_radar']['coordinate'][0] != context['ng_radar']['previousCoordinate'][0]:
                comingFromDirection = 'left' if context['ng_radar']['coordinate'][0] > context['ng_radar']['previousCoordinate'][0] else 'right'
            elif context['ng_radar']['coordinate'][1] != context['ng_radar']['previousCoordinate'][1]:
                comingFromDirection = 'top' if context['ng_radar']['coordinate'][1] > context['ng_radar']['previousCoordinate'][1] else 'bottom'
            
            context['ng_comingFromDirection'] = comingFromDirection

    # if context['gameWindow']['previousGameWindowImage'] is not None:
    #     context['gameWindow']['walkedPixelsInSqm'] = getWalkedPixels(context)

    context['gameWindow']['previousGameWindowImage'] = context['gameWindow']['image']
    context['ng_radar']['previousCoordinate'] = context['ng_radar']['coordinate']
    return context


# TODO: add unit tests
def setHandleLootMiddleware(context: Context) -> Context:
    currentTaskName = context['ng_tasksOrchestrator'].getCurrentTaskName(context)
    if (currentTaskName not in ['depositGold', 'refill', 'buyBackpack', 'selectChatTab', 'travel']):
        lootTab = context['ng_chat']['tabs'].get('loot')
        if lootTab is not None and not lootTab['isSelected']:
            context['ng_tasksOrchestrator'].setRootTask(
                context, SelectChatTabTask('loot'))
    if hasNewLoot(context['ng_screenshot']):
        if context['ng_cave']['previousTargetCreature'] is not None:
            context['loot']['corpsesToLoot'].append(
                context['ng_cave']['previousTargetCreature'])
            context['ng_cave']['previousTargetCreature'] = None
        # has spelled exori category
        if context['ng_comboSpells']['lastUsedSpell'] is not None and context['ng_comboSpells']['lastUsedSpell'] in ['exori', 'exori gran', 'exori mas']:
            spellPath = spellsPath.get(
                context['ng_comboSpells']['lastUsedSpell'], [])
            if len(spellPath) > 0:
                differentCreatures = getDifferentCreaturesBySlots(
                    context['gameWindow']['previousMonsters'], context['gameWindow']['monsters'], spellPath)
                for creature in differentCreatures:
                    context['loot']['corpsesToLoot'].append(creature)
            context['ng_comboSpells']['lastUsedSpell'] = None
            context['ng_comboSpells']['lastUsedSpellAt'] = None
    context['ng_cave']['targetCreature'] = getTargetCreature(
        context['gameWindow']['monsters'])
    if context['ng_cave']['targetCreature'] is not None:
        context['ng_cave']['previousTargetCreature'] = context['ng_cave']['targetCreature']
    return context


# TODO: add unit tests
def setGameWindowMiddleware(context: Context) -> Context:
    context['gameWindow']['coordinate'] = getCoordinate(
        context['ng_screenshot'], (gameWindowSizes[1080][0], gameWindowSizes[1080][1]))
    context['gameWindow']['image'] = getImageByCoordinate(
        context['ng_screenshot'], context['gameWindow']['coordinate'], (gameWindowSizes[1080][0], gameWindowSizes[1080][1]))
    return context


# TODO: add unit tests
def setGameWindowCreaturesMiddleware(context: Context) -> Context:
    context['ng_battleList']['beingAttackedCreatureCategory'] = getBeingAttackedCreatureCategory(
        context['ng_battleList']['creatures'])
    # TODO: func to check if coord is none
    if context['ng_radar']['coordinate'] is None:
        return context
    if any(coord is None for coord in context['ng_radar']['coordinate']):
        return context
    context['gameWindow']['creatures'] = getCreatures(
        context['ng_battleList']['creatures'], context['ng_comingFromDirection'], context['gameWindow']['coordinate'], context['gameWindow']['image'], context['ng_radar']['coordinate'], beingAttackedCreatureCategory=context['ng_battleList']['beingAttackedCreatureCategory'], walkedPixelsInSqm=context['gameWindow']['walkedPixelsInSqm'])
    if len(context['gameWindow']['creatures']) == 0:
        context['gameWindow']['monsters'] = []
        context['gameWindow']['players'] = []
        return context
    context['gameWindow']['monsters'] = getCreaturesByType(
        context['gameWindow']['creatures'], 'monster')
    context['gameWindow']['players'] = getCreaturesByType(
        context['gameWindow']['creatures'], 'player')
    return context
