from typing import List, Tuple


class Position:
    """docstring for Position."""

    def __init__(self, x: float , y: float) -> None:
        self.x: float = x
        self.y: float = y


class Tower:
    def __init__(self, pos: Position):
        self.pos: Position = pos


class Map:
    """Stores info about the map"""

    def __init__(self) -> None:
        # metadata about the map
        self._size: Tuple[int, int] = (..., ...)
        self._targets: List[Position] = [...]

        # info about tiles
        self._vision_modifier: List[List[float]] = [[...]]

        # structures and stuff on the map
        # TODO: decide on structure implementation (see github issue #3)
        self._structures = [...]
        self._towers: List[Tower] = [...]
