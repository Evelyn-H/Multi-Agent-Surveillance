import numpy as np
from typing import List, Tuple
from .util import Position
from .communication import Marker


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
                 markers: List[Marker]=None) -> None:

        # metadata about the map
        self.size: Tuple[int, int] = size
        self.targets: List[Position] = targets if targets else []

        # info about tiles
        self.vision_modifier: List[List[float]] = np.ones((size[0], size[1]), dtype=np.float32)

        # structures and stuff on the map
        self.walls = np.zeros((size[0], size[1]), dtype=np.bool)
        self.gates: List[Gate] = gates if gates else []
        self.towers: List[Tower] = towers if towers else []
        self.markers: List[Marker] = markers if markers else []
