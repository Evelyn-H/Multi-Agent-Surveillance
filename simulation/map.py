from typing import List, Tuple


class Position:
    """docstring for Position."""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y


class Tower:
    def __init__(self, pos: Position):
        self.pos: Position = pos


class Map:
    """Stores info about the map"""

    def __init__(self, size: Tuple[int, int], targets: List[Position]=None, structures=None, towers: List[Tower]=None) -> None:
        # metadata about the map
        self.size: Tuple[int, int] = size
        self.targets: List[Position] = targets if targets else []

        # info about tiles
        self._vision_modifier: List[List[float]] = [[1.0] * size[1]] * size[0]

        # structures and stuff on the map
        # TODO: decide on structure implementation (see github issue #3)
        self.structures = structures if structures else []
        self.towers: List[Tower] = towers if towers else []
