from src.shared.typings import Waypoint
from ...typings import Context
from .common.vector import VectorTask
from .openDoor import OpenDoorTask
from .singleMove import SingleMoveTask
from src.utils.coordinate import getDirectionBetweenCoordinates
from .setNextWaypoint import SetNextWaypointTask
from src.repositories.radar.core import getClosestWaypointIndexFromCoordinate, getCoordinate
import src.gameplay.utils as gameplayUtils
from src.utils.core import getScreenshot
from ..waypoint import resolveGoalCoordinate

class OpenDoorWaypointTask(VectorTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'openDoorWaypoint'
        self.isRootTask = True
        self.waypoint = waypoint

    def onBeforeStart(self, context: Context) -> Context:
        direction = getDirectionBetweenCoordinates(
            context['ng_radar']['coordinate'], self.waypoint['coordinate'])
        
        if direction == 'up':
            direction = 'north'
        if direction == 'down':
            direction = 'south'
        if direction == 'left':
            direction = 'west'
        if direction == 'right':
            direction = 'east'
                
        if direction is not None:
            battleListPlayers = context['gameWindow']['players']
            if battleListPlayers and len(battleListPlayers) > 0:
                battleListPlayersCoordinates = [player['coordinate'] for player in battleListPlayers]
                playerInCoordinate = self.waypoint['coordinate'] in battleListPlayersCoordinates
                if playerInCoordinate:
                    self.tasks = [
                        SingleMoveTask(direction).setParentTask(self).setRootTask(self),
                        SingleMoveTask(direction).setParentTask(self).setRootTask(self),
                    ]
                    return context
            self.tasks = [
                SingleMoveTask(direction).setParentTask(self).setRootTask(self),
                OpenDoorTask(self.waypoint).setParentTask(self).setRootTask(self),
            ]
        else:
            self.tasks = [
                SetNextWaypointTask().setParentTask(self).setRootTask(self),
            ]
        return context
    
    def onComplete(self, context: Context) -> Context:
        context['ng_screenshot'] = getScreenshot()
        context['ng_radar']['coordinate'] = getCoordinate(
            context['ng_screenshot'], previousCoordinate=context['ng_radar']['previousCoordinate'])
        if not gameplayUtils.coordinatesAreEqual(context['ng_radar']['coordinate'], self.waypoint['coordinate']):
            context['ng_cave']['waypoints']['currentIndex'] = getClosestWaypointIndexFromCoordinate(
                context['ng_radar']['coordinate'], context['ng_cave']['waypoints']['items'])
            currentWaypoint = context['ng_cave']['waypoints']['items'][context['ng_cave']
                                                                ['waypoints']['currentIndex']]
            context['ng_cave']['waypoints']['state'] = resolveGoalCoordinate(
                context['ng_radar']['coordinate'], currentWaypoint)

        return context
