import time
from src.gameplay.typings import Context
from src.repositories.inventory.core import images
from src.shared.typings import GrayImage
from src.utils.core import locate
from src.utils.mouse import drag, rightClick
from ...typings import Context
from .common.base import BaseTask
from src.repositories.gameWindow.slot import getSlotPosition

# TODO: check if item was moved on did. Is possible to check it by cap
class DragItemsToFloorTask(BaseTask):
    def __init__(self, containerBarImage: GrayImage):
        super().__init__()
        self.name = 'dragItemsToFloor'
        self.terminable = False
        self.containerBarImage = containerBarImage

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        containerBarPosition = locate(context['ng_screenshot'], self.containerBarImage, confidence=0.8)
        firstSlotImage = context['ng_screenshot'][containerBarPosition[1] + 18:containerBarPosition[1] + 18 + 32, containerBarPosition[0] + 10:containerBarPosition[0] + 10 + 32]
        isLootBackpackItem = locate(firstSlotImage, images['slots'][context['ng_backpacks']['loot']], confidence=0.8) is not None
        if isLootBackpackItem:
            rightClick((containerBarPosition[0] + 12, containerBarPosition[1] + 20))
            return context
        isNotEmptySlot = locate(firstSlotImage, images['slots']['empty']) is None
        if isNotEmptySlot:
            fromX, fromY = containerBarPosition[0] + 12, containerBarPosition[1] + 20
            slotPosition = getSlotPosition((7, 5), context['gameWindow']['coordinate'])
            drag((fromX, fromY), slotPosition)
            time.sleep(0.4)
            return context
        self.terminable = True
        return context
