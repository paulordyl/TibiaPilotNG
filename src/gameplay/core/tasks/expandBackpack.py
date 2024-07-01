from src.gameplay.typings import Context
from src.repositories.inventory.core import images
from src.utils.core import locate
from src.utils.mouse import drag
from ...typings import Context
from .common.base import BaseTask


# TODO: ignore when backpack already expanded
# TODO: check if backpack is expanded on did
# TODO: voltar terminable talvez, melhorar esse codigo
class ExpandBackpackTask(BaseTask):
    def __init__(self, backpack: str):
        super().__init__()
        self.name = 'expandBackpack'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        # self.terminable = False
        self.backpack = backpack

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        backpackBarImage = images['containersBars'][context['ng_backpacks']['main']]
        # TODO: locate should be done in right content position to avoid calculation in whole screen
        backpackBarPosition = locate(context['ng_screenshot'], backpackBarImage, confidence=0.8)
        if backpackBarPosition is None:
            return context
        croppedImage = context['ng_screenshot'][backpackBarPosition[1]:, backpackBarPosition[0]:]
        # TODO: locate should be done in right content position to avoid calculation in whole screen
        backpackBottomBarPosition = locate(croppedImage, images['containersBars']['backpack bottom'], confidence=0.8)
        backpackBottomBarPositionX = backpackBottomBarPosition[0] + backpackBarPosition[0]
        backpackBottomBarPositionY = backpackBottomBarPosition[1] + backpackBarPosition[1]
        yDifference = backpackBottomBarPositionY - backpackBarPosition[1] - 1
        scrollY = 208 - yDifference
        if scrollY <= 1:
            # self.terminable = True
            return context
        drag((backpackBottomBarPositionX, backpackBottomBarPositionY + 1), (backpackBottomBarPositionX, backpackBottomBarPositionY + scrollY))
        return context