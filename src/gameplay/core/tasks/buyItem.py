from src.gameplay.typings import Context
import src.repositories.refill.core as refillCore
from ...typings import Context
from .common.base import BaseTask


# TODO: check if item was bought checking gold difference on did
# TODO: check if has necessary money to buy item. If not, an alert to user must be sent
class BuyItemTask(BaseTask):
    def __init__(self, itemName: str, itemQuantity: str, ignore=False):
        super().__init__()
        self.name = 'buyItem'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.itemName = itemName
        self.itemQuantity = itemQuantity
        self.ignore = ignore

    def shouldIgnore(self, _: Context) -> bool:
        if self.ignore == True:
            return True

        return self.itemQuantity <= 0

    def do(self, context: Context) -> Context:
        # TODO: split into multiple tasks
        refillCore.buyItem(context['ng_screenshot'],
                        self.itemName, self.itemQuantity)
        return context
