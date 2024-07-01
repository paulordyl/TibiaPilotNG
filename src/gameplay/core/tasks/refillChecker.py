from src.repositories.actionBar.core import getSlotCount
from src.repositories.skills.core import getCapacity
from src.shared.typings import Waypoint
from src.utils.array import getNextArrayIndex
from ...typings import Context
from .common.base import BaseTask


class RefillCheckerTask(BaseTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'refillChecker'
        self.delayAfterComplete = 1
        self.isRootTask = True
        self.waypoint = waypoint

    # TODO: add unit tests
    def shouldIgnore(self, context: Context) -> bool:
        quantityOfHealthPotions = getSlotCount(context['ng_screenshot'], context['healing']['potions']['firstHealthPotion']['slot'])
        if quantityOfHealthPotions is None:
            return False
        quantityOfManaPotions = getSlotCount(context['ng_screenshot'], context['healing']['potions']['firstManaPotion']['slot'])
        if quantityOfManaPotions is None:
            return False
        capacity = getCapacity(context['ng_screenshot'])
        if capacity is None:
            return False
        hasEnoughHealthPotions = True if self.waypoint['options']['healthEnabled'] == False else quantityOfHealthPotions > self.waypoint[
            'options']['minimumAmountOfHealthPotions']
        hasEnoughManaPotions = quantityOfManaPotions > self.waypoint[
            'options']['minimumAmountOfManaPotions']
        hasEnoughCapacity = capacity > self.waypoint['options']['minimumAmountOfCap']
        return hasEnoughHealthPotions and hasEnoughManaPotions and hasEnoughCapacity

    # TODO: add unit tests
    def onIgnored(self, context: Context) -> Context:
        # TODO: add function to get waypoint by label
        labelIndexes = [index for index, waypoint in enumerate(
            context['ng_cave']['waypoints']['items']) if waypoint['label'] == self.waypoint['options']['waypointLabelToRedirect']]
        if len(labelIndexes) == 0:
            # TODO: raise error
            return context
        context['ng_cave']['waypoints']['currentIndex'] = labelIndexes[0]
        context['ng_cave']['waypoints']['state'] = None
        return context

    # TODO: add unit tests
    def onComplete(self, context: Context) -> Context:
        nextWaypointIndex = getNextArrayIndex(
            context['ng_cave']['waypoints']['items'], context['ng_cave']['waypoints']['currentIndex'])
        context['ng_cave']['waypoints']['currentIndex'] = nextWaypointIndex
        context['ng_cave']['waypoints']['state'] = None
        return context
