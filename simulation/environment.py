import numpy as np
from typing import List, Tuple

from .util import Position

class Tower:
    """
    Represents a single tower (one tile wide)
    """

    def __init__(self, pos: Position):
        self.pos: Position = pos


class Gate:
    """
    Superclass for doors and windows and such,
    represents a generally unpassable block that can be opened by interating with it
    """

    def __init__(self) -> None:
        ...

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
                 towers: List[Tower]=None,
                 markers: List['world.Marker']=None) -> None:

        # metadata about the map
        self.size: Tuple[int, int] = size
        self.targets: List[Position] = targets if targets else []

        # info about tiles
        self.vision_modifier: List[List[float]] = np.ones((size[0], size[1]), dtype=np.float32)

        # structures and stuff on the map
        self.walls = np.zeros((size[0], size[1]), dtype=np.bool)
        self.gates: List[Gate] = gates if gates else []
        self.towers: List[Tower] = towers if towers else []
        self.markers: List['world.Marker'] = markers if markers else []

    def set_wall(self, x: int, y: int):
        if x >= 0 and y >= 0 and x < self.size[0] and y < self.size[1]:
            self.walls[x][y] = True

    def is_wall(self, x: int, y: int) -> bool:
        if x >= 0 and y >= 0 and x < self.size[0] and y < self.size[1]:
            return self.walls[x][y]
        else:
            return True

    def add_wall(self, x0, y0, x1, y1):
        # make sure values are in the right order
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        # add horizontal wall
        for x in range(x0, x1 + 1):
            self.set_wall(x, y0)
            self.set_wall(x, y1)
        # add vertical wall
        for y in range(y0, y1 + 1):
            self.set_wall(x0, y)
            self.set_wall(x1, y)
