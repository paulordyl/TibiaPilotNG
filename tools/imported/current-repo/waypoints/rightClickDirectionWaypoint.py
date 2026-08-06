from ...typings import Context
from .common.vector import VectorTask
from .rightClickDirection import RightClickDirectionTask
from .setNextWaypoint import SetNextWaypointTask


class RightClickDirectionWaypointTask(VectorTask):
    def __init__(self, direction: str):
        super().__init__()
        self.name = 'rightClickDirectionWaypoint'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.isRootTask = True
        self.direction = direction

    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            RightClickDirectionTask(self.direction).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context
