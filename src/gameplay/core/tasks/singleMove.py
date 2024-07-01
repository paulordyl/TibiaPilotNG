from ...typings import Context
from .common.vector import VectorTask
from .move import Move
from .setNextWaypoint import SetNextWaypointTask


class SingleMoveTask(VectorTask):
    def __init__(self, direction: str):
        super().__init__()
        self.name = 'singleMove'
        self.delayBeforeStart = 1
        self.delayAfterComplete = 1
        self.isRootTask = True
        self.direction = direction

    # TODO: add unit tests
    def onBeforeStart(self, context: Context) -> Context:
        self.tasks = [
            Move(self.direction).setParentTask(self).setRootTask(self),
            SetNextWaypointTask().setParentTask(self).setRootTask(self),
        ]
        return context
