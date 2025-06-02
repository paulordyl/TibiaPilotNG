import random
from src.repositories.actionBar.core import getSlotCount
from src.shared.typings import Waypoint
from ...typings import Context
from .common.vector import VectorTask
from .buyItem import BuyItemTask
from .closeNpcTradeBox import CloseNpcTradeBoxTask
from .enableChat import EnableChatTask
from .say import SayTask
from .selectChatTab import SelectChatTabTask
from .setChatOff import SetChatOffTask
from .setNextWaypoint import SetNextWaypointTask
from src.gameplay.core.tasks.useHotkey import UseHotkeyTask

class RefillTask(VectorTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'refill'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.isRootTask = True
        self.waypoint = waypoint

    # TODO: add unit tests
    def onBeforeStart(self, context: Context) -> Context:
        healthPotionsAmount = getSlotCount(context['ng_screenshot'], context['healing']['potions']['firstHealthPotion']['slot'])
        manaPotionsAmount = getSlotCount(context['ng_screenshot'], context['healing']['potions']['firstManaPotion']['slot'])

        amountOfManaPotionsToBuy = max(
            0, self.waypoint['options']['manaPotion']['quantity'] - manaPotionsAmount)
        amountOfHealthPotionsToBuy = max(
            0, self.waypoint['options']['healthPotion']['quantity'] - healthPotionsAmount)
        self.tasks = [
            SelectChatTabTask('local chat').setParentTask(
                self).setRootTask(self),
            EnableChatTask().setParentTask(self).setRootTask(self),
            SayTask('hi').setParentTask(self).setRootTask(self),
            EnableChatTask().setParentTask(self).setRootTask(self),
            SayTask('potions' if self.waypoint['options']['houseNpcEnabled'] else 'trade').setParentTask(self).setRootTask(self),
            SetChatOffTask().setParentTask(self).setRootTask(self),
            BuyItemTask(self.waypoint['options']['manaPotion']['item'], amountOfManaPotionsToBuy).setParentTask(
                self).setRootTask(self),
            BuyItemTask(self.waypoint['options']['healthPotion']['item'], amountOfHealthPotionsToBuy, ignore=not self.waypoint['options']['healthPotionEnabled']).setParentTask(
                self).setRootTask(self),
            CloseNpcTradeBoxTask().setParentTask(self).setRootTask(self),
            UseHotkeyTask(context['healing']['potions']['firstManaPotion']['hotkey'], delayAfterComplete=random.uniform(0.8, 1.2)).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]

        default_random_delay_range = (0.2, 0.5)
        say_task_delay_range = (0.3, 0.6)

        # Apply delays
        self.tasks[0].delayAfterComplete = random.uniform(*default_random_delay_range) # SelectChatTabTask
        self.tasks[1].delayAfterComplete = random.uniform(*default_random_delay_range) # EnableChatTask
        self.tasks[2].delayAfterComplete = random.uniform(*say_task_delay_range)      # SayTask 'hi'
        self.tasks[3].delayAfterComplete = random.uniform(*default_random_delay_range) # EnableChatTask
        self.tasks[4].delayAfterComplete = random.uniform(*say_task_delay_range)      # SayTask 'potions' or 'trade'
        self.tasks[5].delayAfterComplete = random.uniform(*default_random_delay_range) # SetChatOffTask
        self.tasks[6].delayAfterComplete = random.uniform(*default_random_delay_range) # BuyItemTask mana
        self.tasks[7].delayAfterComplete = random.uniform(*default_random_delay_range) # BuyItemTask health
        self.tasks[8].delayAfterComplete = random.uniform(*default_random_delay_range) # CloseNpcTradeBoxTask
        # self.tasks[9] is UseHotkeyTask, already handled
        # self.tasks[10] is SetNextWaypointTask, can leave its default (0) or add a small one if desired
        # self.tasks[10].delayAfterComplete = random.uniform(0.1, 0.2)

        return context
