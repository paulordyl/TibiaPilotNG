# Minimal tcod shim to satisfy pathfinding usage in tests.
class path:
    class AStar:
        def __init__(self, map_, *args, **kwargs):
            self.map = map_

        def get_path(self, start_y, start_x, goal_y, goal_x):
            # Return a trivial path containing only the goal coordinate.
            return [(goal_y, goal_x)]
