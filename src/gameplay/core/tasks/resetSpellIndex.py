from .common.base import BaseTask
from ...typings import Context

class ResetSpellIndexTask(BaseTask):
  def __init__(self):
      super().__init__()
      self.name = 'resetSpellIndex'

  def shouldIgnore(self, context: Context) -> bool:
      if context['ng_lastUsedSpellLoot'] is None:
          return True
      else:
          return False

  def do(self, context: Context) -> Context:
      context['ng_lastUsedSpellLoot'] = None
      for index, _ in enumerate(context['ng_comboSpells']['items']):
        context['ng_comboSpells']['items'][index]['currentSpellIndex'] = 0

      return context