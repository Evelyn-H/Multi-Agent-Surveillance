from enum import Enum


class MarkerType(Enum):
    """The different types of markers used for indirect communication"""
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    MAGENTA = 5


class Message:
    """Encapsulates a single message"""

    def __init__(self, message: str) -> None:
        self.message: str = message
