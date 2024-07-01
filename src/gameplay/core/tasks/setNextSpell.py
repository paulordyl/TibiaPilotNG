from ...typings import Context
from .common.base import BaseTask
from src.repositories.actionBar.core import hasCooldownByName
from src.utils.array import getNextArrayIndex
from time import time
from src.utils.core import getScreenshot

class SetNextSpellTask(BaseTask):
    def __init__(self, spell: str):
        super().__init__()
        self.name = 'setNextSpell'
        self.spell = spell

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        curScreen = context['ng_screenshot'] = getScreenshot()
        hasCooldown = hasCooldownByName(curScreen, self.spell)
        if hasCooldown:
            comboSpell = context['ng_comboSpells']['items'][0]
            if comboSpell['enabled'] == False:
                return context
            nextIndex = getNextArrayIndex(
                comboSpell['spells'], comboSpell['currentSpellIndex'])
            # TODO: improve indexes without using context
            context['ng_comboSpells']['items'][0]['currentSpellIndex'] = nextIndex
            context['ng_comboSpells']['lastUsedSpell'] = self.spell
            context['ng_lastUsedSpellLoot'] = self.spell
            context['ng_comboSpells']['lastUsedSpellAt'] = time()
            context['healCount'] = 0

        return context
