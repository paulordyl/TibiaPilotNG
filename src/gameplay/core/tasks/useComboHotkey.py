from ...typings import Context
from .common.vector import VectorTask
from .useHotkey import UseHotkeyTask
from .setNextSpell import SetNextSpellTask

class UseComboHotkeyTask(VectorTask):
    def __init__(self, hotkey: str, spellName: str):
        super().__init__()
        self.name = 'useComboHotkey'
        self.hotkey = hotkey
        self.isRootTask = True
        self.spellName = spellName

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
          UseHotkeyTask(self.hotkey, 0.1).setParentTask(self).setRootTask(self),
          SetNextSpellTask(self.spellName).setParentTask(self).setRootTask(self),
        ]
        return context
