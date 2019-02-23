import math

class Position:
    """Simple class for (x,y) pairs"""

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y

    def move(self, distance: float, angle: float):
        self.x += distance * math.sin(math.radians(angle))
        self.y += distance * math.cos(math.radians(angle))
