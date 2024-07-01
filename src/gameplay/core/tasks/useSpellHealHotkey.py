from src.utils.keyboard import press
from ...typings import Context
from .common.base import BaseTask

class UseSpellHealHotkeyTask(BaseTask):
    def __init__(self, hotkey: str, delayBeforeStart: int = 1):
        super().__init__()
        self.name = 'useSpellHealHotkey'
        self.delayBeforeStart = delayBeforeStart
        self.hotkey = hotkey

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        currentTaskName = context['ng_tasksOrchestrator'].getCurrentTaskName(context)
        if currentTaskName == 'attackClosestCreature':
            if context['healCount'] <= 2:
                press(self.hotkey)
        else:
            press(self.hotkey)
        return context

    def onComplete(self, context: Context) -> Context:
        context['healCount'] = context['healCount'] + 1

        return context