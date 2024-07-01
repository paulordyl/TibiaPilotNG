from src.shared.typings import Waypoint
from ...typings import Context
from .common.vector import VectorTask
from .rightClickUse import RightClickUseTask
from .setNextWaypoint import SetNextWaypointTask
from src.utils.core import getScreenshot
from src.repositories.radar.core import getClosestWaypointIndexFromCoordinate, getCoordinate
from ..waypoint import resolveGoalCoordinate

class UseLadderWaypointTask(VectorTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'useLadderWaypoint'
        self.isRootTask = True
        self.waypoint = waypoint

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            RightClickUseTask(self.waypoint).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context

    def onComplete(self, context: Context) -> Context:
        context['ng_screenshot'] = getScreenshot()
        context['ng_radar']['coordinate'] = getCoordinate(
            context['ng_screenshot'], previousCoordinate=context['ng_radar']['previousCoordinate'])
        if context['ng_radar']['coordinate'][2] != self.waypoint['coordinate'][2] - 1:
            context['ng_cave']['waypoints']['currentIndex'] = getClosestWaypointIndexFromCoordinate(
                context['ng_radar']['coordinate'], context['ng_cave']['waypoints']['items'])
            currentWaypoint = context['ng_cave']['waypoints']['items'][context['ng_cave']
                                                                ['waypoints']['currentIndex']]
            context['ng_cave']['waypoints']['state'] = resolveGoalCoordinate(
                context['ng_radar']['coordinate'], currentWaypoint)
        return context
