from enum import Enum
from .util import Position


class MarkerType(Enum):
    """The different types of markers used for indirect communication"""
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    MAGENTA = 5


class Marker:
    def __init__(self, type: MarkerType, location: Position):
        self.type = type
        self.location = location


class Message:
    """Encapsulates a single message"""

    def __init__(self, message: str) -> None:
        self.message: str = message


class NoiseEvent:
    """Encapsulates a single noise event"""

    def __init__(self, location: Position) -> None:
        self._location = location

    def perceived_angle(self, target_pos: Position):
        """
        Calculates the perceived angle towards the noise from the perspective of the `target_pos`
        This also adds the uncertainty as described in the booklet
        """
        ...
