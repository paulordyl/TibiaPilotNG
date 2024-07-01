from src.gameplay.typings import Context
import src.gameplay.utils as gameplayUtils
from src.repositories.radar.typings import Coordinate
from ...typings import Context
from ..waypoint import generateFloorWalkpoints
from .common.vector import VectorTask
from .walk import WalkTask
from .attackMonstersBox import AttackMonstersBoxTask
from .lootMonstersBox import LootMonstersBoxTask
from .resetSpellIndex import ResetSpellIndexTask
from .clickInClosestCreature import ClickInClosestCreatureTask
from .walkToTargetCreature import WalkToTargetCreatureTask

class WalkToCoordinateTask(VectorTask):
    def __init__(self, coordinate: Coordinate, passinho=False):
        super().__init__()
        self.name = 'walkToCoordinate'
        self.coordinate = coordinate
        self.passinho = passinho
        self.isTrapped = False

    def shouldRestartAfterAllChildrensComplete(self, context: Context) -> bool:
        if self.isTrapped == True:
            return True
        if len(self.tasks) == 0:
            return True
        return not gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], self.coordinate)

    def onBeforeStart(self, context: Context) -> Context:
        self.calculateWalkpoint(context)
        return context

    def onBeforeRestart(self, context: Context) -> Context:
        return self.onBeforeStart(context)

    def onInterrupt(self, context: Context) -> Context:
        return gameplayUtils.releaseKeys(context)

    def onComplete(self, context: Context):
        return gameplayUtils.releaseKeys(context)

    # TODO: add unit tests
    def calculateWalkpoint(self, context: Context):
        nonWalkableCoordinates = context['ng_cave']['holesOrStairs'].copy()
        for monster in context['gameWindow']['monsters']:
            # TODO: func to check if coord is none
            if monster['coordinate'] is not None:
                hasNoneCoord = any(coord is None for coord in monster['coordinate'])
                if not hasNoneCoord:
                    nonWalkableCoordinates.append(monster['coordinate'])
        refillCheckerIndexPlayer = next((index for index, item in enumerate(context['ng_cave']['waypoints']['items']) if item['type'] == 'refillChecker'), None)
        if refillCheckerIndexPlayer is None or refillCheckerIndexPlayer is not None and context['ng_cave']['waypoints']['currentIndex'] < refillCheckerIndexPlayer:
            for player in context['gameWindow']['players']:
                # TODO: func to check if coord is none
                if player['coordinate'] is not None:
                    hasNoneCoord = any(coord is None for coord in player['coordinate'])
                    if not hasNoneCoord:
                        nonWalkableCoordinates.append(player['coordinate'])
        self.tasks = []
        walkpoints = generateFloorWalkpoints(
                context['ng_radar']['coordinate'], self.coordinate, nonWalkableCoordinates=nonWalkableCoordinates)
        if len(walkpoints) == 0 and not gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], self.coordinate):
            self.isTrapped = True
            if any(creature[0] != 'Unknown' for creature in context['ng_battleList']['creatures']):
                refillCheckerIndex = next((index for index, item in enumerate(context['ng_cave']['waypoints']['items']) if item['type'] == 'refillChecker'), None)
                if refillCheckerIndex is None or refillCheckerIndex is not None and context['ng_cave']['waypoints']['currentIndex'] < refillCheckerIndex:
                    self.tasks = [
                        AttackMonstersBoxTask().setParentTask(self).setRootTask(self),
                        LootMonstersBoxTask().setParentTask(self).setRootTask(self),
                        LootMonstersBoxTask().setParentTask(self).setRootTask(self),
                        LootMonstersBoxTask().setParentTask(self).setRootTask(self),
                        ResetSpellIndexTask().setParentTask(self).setRootTask(self),
                    ]
                else:
                    self.tasks = [
                        ClickInClosestCreatureTask().setParentTask(self).setRootTask(self.rootTask),
                        WalkToTargetCreatureTask().setParentTask(self).setRootTask(self.rootTask),
                    ]
        else:
            self.isTrapped = False
        for walkpoint in walkpoints:
            self.tasks.append(WalkTask(context, walkpoint, self.passinho).setParentTask(
                self).setRootTask(self.rootTask))
