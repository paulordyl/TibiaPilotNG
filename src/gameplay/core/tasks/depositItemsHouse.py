from src.repositories.inventory.core import images
from ...typings import Context
from .common.vector import VectorTask
from .closeContainer import CloseContainerTask
from .dragItemsToFloor import DragItemsToFloorTask
from .openBackpack import OpenBackpackTask
from .scrollToItem import ScrollToItemTask
from .setNextWaypoint import SetNextWaypointTask
from .expandBackpack import ExpandBackpackTask

class DepositItemsHouseTask(VectorTask):
    def __init__(self):
        super().__init__()
        self.name = 'depositItemsHouse'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.isRootTask = True

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            OpenBackpackTask(context['ng_backpacks']['main']).setParentTask(self).setRootTask(self),
            ExpandBackpackTask(context['ng_backpacks']['main']).setParentTask(self).setRootTask(self),
            ScrollToItemTask(images['containersBars'][context['ng_backpacks']['main']], images['slots'][context['ng_backpacks']['loot']]).setParentTask(self).setRootTask(self),
            OpenBackpackTask(context['ng_backpacks']['loot']).setParentTask(self).setRootTask(self),
            DragItemsToFloorTask(images['containersBars'][context['ng_backpacks']['loot']]).setParentTask(self).setRootTask(self),
            CloseContainerTask(images['containersBars'][context['ng_backpacks']['loot']]).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context
