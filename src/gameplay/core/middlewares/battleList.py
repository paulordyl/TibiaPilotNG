from src.repositories.battleList.core import getCreatures, isAttackingSomeCreature
from src.repositories.battleList.extractors import getContent
from ...typings import Context


# TODO: add unit tests
def setBattleListMiddleware(context: Context) -> Context:
    context['ng_battleList']['creatures'] = getCreatures(
        getContent(context['ng_screenshot']))
    context['ng_cave']['isAttackingSomeCreature'] = isAttackingSomeCreature(
        context['ng_battleList']['creatures'])
    return context
