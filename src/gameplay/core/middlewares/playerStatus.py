from src.repositories.skills.core import getHp, getMana
from src.repositories.statusBar.core import getManaPercentage, getHpPercentage
from ...typings import Context


# TODO: add unit tests
def setMapPlayerStatusMiddleware(context: Context) -> Context:
    context['ng_statusBar']['hp'] = getHp(context['ng_screenshot'])
    context['ng_statusBar']['hpPercentage'] = getHpPercentage(context['ng_screenshot'])
    context['ng_statusBar']['mana'] = getMana(context['ng_screenshot'])
    context['ng_statusBar']['manaPercentage'] = getManaPercentage(context['ng_screenshot'])
    return context
