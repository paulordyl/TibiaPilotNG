from src.utils.array import getNextArrayIndex
from ...typings import Context
from ..waypoint import resolveGoalCoordinate
from .common.base import BaseTask


class SetNextWaypointTask(BaseTask):
    def __init__(self):
        super().__init__()
        self.name = 'setNextWaypoint'

    # TODO: add unit tests
    def do(self, context: Context) -> Context:
        nextWaypointIndex = getNextArrayIndex(
            context['ng_cave']['waypoints']['items'], context['ng_cave']['waypoints']['currentIndex'])
        context['ng_cave']['waypoints']['currentIndex'] = nextWaypointIndex
        currentWaypoint = context['ng_cave']['waypoints']['items'][context['ng_cave']
                                                                ['waypoints']['currentIndex']]
        context['ng_cave']['waypoints']['state'] = resolveGoalCoordinate(
            context['ng_radar']['coordinate'], currentWaypoint)
        return context
