import math
import vectormath as vmath


class Position(vmath.Vector2):
    """ small wrapper around `vectormath.Vector2` to add some functionality """

    def move(self, distance: float, angle: float):
        self.x += distance * math.sin(math.radians(angle))
        self.y += distance * math.cos(math.radians(angle))
