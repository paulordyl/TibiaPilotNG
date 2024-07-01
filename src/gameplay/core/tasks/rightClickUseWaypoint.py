from src.shared.typings import Waypoint
from ...typings import Context
from .common.vector import VectorTask
from .rightClickUse import RightClickUseTask
from .setNextWaypoint import SetNextWaypointTask


class RightClickUseWaypointTask(VectorTask):
    def __init__(self, waypoint: Waypoint):
        super().__init__()
        self.name = 'rightClickUseWaypoint'
        self.isRootTask = True
        self.waypoint = waypoint

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            RightClickUseTask(self.waypoint).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context
