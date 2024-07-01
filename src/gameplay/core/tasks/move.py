from src.utils.keyboard import press
from ...typings import Context
from .common.base import BaseTask


class Move(BaseTask):
    def __init__(self, direction: str):
        super().__init__()
        self.name = 'move'
        self.isRootTask = True
        self.direction = direction

    # TODO: add unit tests
    # TODO: improve this code
    def do(self, context: Context) -> bool:
        direction = None
        if self.direction == 'north':
            direction = 'up'
        if self.direction == 'south':
            direction = 'down'
        if self.direction == 'west':
            direction = 'left'
        if self.direction == 'east':
            direction = 'right'
        press(direction)
        return context
