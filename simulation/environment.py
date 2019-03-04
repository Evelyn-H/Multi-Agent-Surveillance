import numpy as np
from typing import List, Tuple

from .util import Position

class Gate:
    """
    Superclass for doors and windows and such,
    represents a generally unpassable block that can be opened by interating with it
    """

    def __init__(self) -> None:
        ...

    @property
    def is_open(self) -> bool:
        ...

    def open(self) -> None:
        ...

    def close(self) -> None:
        ...


class Map:
    """Stores info about the map"""

    def __init__(self,
                 size: Tuple[int, int],
                 targets: List[Position]=None,
                 gates=None,
                 towers: List[Position]=None,
                 markers: List['world.Marker']=None,
                 #Prehaps replace with Noise elements 
                 noise: List['world.NoiseEvent']=None) -> None:

        # metadata about the map
        self.size: Tuple[int, int] = size

        # info about tiles
        self.walls = np.zeros((size[0], size[1]), dtype=np.bool)
        self.vision_modifier: List[List[float]] = np.ones((size[0], size[1]), dtype=np.float32)

        # structures and stuff on the map
        self.noise: List['world.NoiseEvent'] = noise if noise else []
        self.targets: List[Position] = targets if targets else []
        self.towers: List[Position] = towers if towers else []
        self.gates: List[Gate] = gates if gates else []
        self.markers: List['world.Marker'] = markers if markers else []

    def in_bounds(self, x: int, y: int) -> bool:
        return x >= 0 and y >= 0 and x < self.size[0] and y < self.size[1]

    def add_target(self, x: int, y: int):
        self.targets.append(Position(x, y))

    def remove_target(self, x: int, y: int):
        for i, target in enumerate(self.targets):
            if abs(target.x - x) + abs(target.y - y) <= 2:
                del self.targets[i]

    def add_tower(self, x: int, y: int):
        self.towers.append(Position(x, y))

    def remove_tower(self, x: int, y: int):
        for i, tower in enumerate(self.towers):
            if abs(tower.x - x) + abs(tower.y - y) <= 2:
                del self.towers[i]

    def set_wall(self, x: int, y: int, value=True):
        if self.in_bounds(x, y):
            self.walls[x][y] = True if value else False

    def is_wall(self, x: int, y: int) -> bool:
        if self.in_bounds(x, y):
            return self.walls[x][y]
        else:
            return True

    def set_wall_rectangle(self, x0, y0, x1, y1, value=True):
        # make sure values are in the right order
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        # add horizontal wall
        for x in range(x0, x1 + 1):
            self.set_wall(x, y0, value)
            self.set_wall(x, y1, value)
        # add vertical wall
        for y in range(y0, y1 + 1):
            self.set_wall(x0, y, value)
            self.set_wall(x1, y, value)

    def set_vision(self, x: int, y: int, value=0.5):
        if self.in_bounds(x, y):
            self.vision_modifier[x][y] = max(0, min(value, 1.0))

    def set_vision_area(self, x0, y0, x1, y1, value=0.5):
        # make sure values are in the right order
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        self.vision_modifier[x0:x1 + 1, y0:y1 + 1] = max(0, min(value, 1.0))
