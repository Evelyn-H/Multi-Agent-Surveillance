from typing import Tuple, List
import math
import numpy as np
import vectormath as vmath

from .util import Position
from . import pathfinding
import simulation


class AgentView:
    """
    Implements a wrapper around an agent that only exposes things that can be
    known when another agent sees it
    """

    def __init__(self, agent):
        self._agent = agent

    @property
    def ID(self):
        return self._agent.ID

    @property
    def location(self):
        return Position(self._agent.location)

    @property
    def heading(self):
        return self._agent.heading

    @property
    def is_guard(self):
        return isinstance(self._agent, simulation.agent.GuardAgent)

    @property
    def is_intruder(self):
        return isinstance(self._agent, simulation.agent.IntruderAgent)

# TODO: ---------------------------------------------------------------

# vision of structures (targets, towers, gates, walls)
#    # if there is a line of vision, then walls and gates can be seen from <= 10 meters distance
#    # towers can be seen from <= 18 meters away
#    # guards on towers can only be seen within normal ranges

# vision when on towers (sentry towers aren't implemented yet)
#    # if on tower, then view_range between 2 and 15 meters
#    # if on tower, then view_angle = 30
#    # if entering/leaving a tower, then vision_range = 0 for 3 seconds

# decreased vision due to turning
#    # if turning > 45 degrees/second, then vision_range = 0 while turning + 0.5 seconds afterwards

# ---------------------------------------------------------------------


class MapView(pathfinding.Graph):
    """
    Basically implements a fog-of-war
    """

    def __init__(self, map):
        # private copy of the full map
        self._map = map

        # fog-of-war map
        self.fog = np.zeros((self._map.size[0], self._map.size[1]), dtype=np.bool)  # self._map.size?

    @property
    def size(self):
        return self._map.size

    @property
    def width(self):
        return self._map.size[0]

    @property
    def height(self):
        return self._map.size[1]

    def _reveal_all(self):
        self.fog = np.ones((self._map.size[0], self._map.size[1]), dtype=np.bool)

    def _is_tile_visible_from(self, x0, y0, x, y):
        # line code taken from:
        # https://github.com/encukou/bresenham
        def line(x0, y0, x1, y1):
            dx = x1 - x0
            dy = y1 - y0

            xsign = 1 if dx > 0 else -1
            ysign = 1 if dy > 0 else -1

            dx = abs(dx)
            dy = abs(dy)

            if dx > dy:
                xx, xy, yx, yy = xsign, 0, 0, ysign
            else:
                dx, dy = dy, dx
                xx, xy, yx, yy = 0, ysign, xsign, 0

            D = 2 * dy - dx
            y = 0

            for x in range(dx + 1):
                yield x0 + x * xx + y * yx, y0 + x * xy + y * yy
                if D >= 0:
                    y += 1
                    D -= 2 * dx
                D += 2 * dy

        for x_line, y_line in line(x0, y0, x, y):
            # reached the last tile, so it's visible
            if x == x_line and y == y_line:
                return True
            # if any tile along the way is a wall then the check failed
            if self._map.is_wall(x_line, y_line):
                return False

    # see-through-walls version:    0.2 ms / call
    # same but without numpy:       0.4 ms / call
    # proper version:               0.6 ms / call
    def _reveal_visible(self, x0: int, y0: int, radius: float, view_angle: float, heading: float):
        offset = int(math.ceil(radius)) + 1
        for x in range(x0 - offset, x0 + offset):
            for y in range(y0 - offset, y0 + offset):
                # bounds check
                if not self._map.in_bounds(x, y):
                    continue
                # distance check
                if (x - x0)**2 + (y - y0)**2 > radius**2:
                    continue
                # angle check
                angle = math.atan2(y0 - y, x0 - x) * 180 / np.pi
                angle = (angle + heading + 90 + 180) % 360 - 180
                if angle > view_angle / 2 or angle < -view_angle / 2:
                    continue
                # visibility check
                if not self._is_tile_visible_from(x0, y0, x, y):
                    continue
                # tile is visible!
                self.fog[x][y] = True

    def is_revealed(self, x: int, y: int):
        if 0 <= x < self._map.size[0] and 0 <= y < self._map.size[1]:
            return self.fog[x][y]
        else:
            return True

    # vvvv pathfinding methods vvvv
    def is_passable(self, node):
        if not self._map.in_bounds(*node):
            return False
        if self.is_revealed(*node) and self._map.is_wall(*node):
            return False
        # we're good!
        return True

    def neighbors(self, node):
        """ Implements abstract method `neighbors` from `Graph` """
        (x, y) = node

        corners = []

        top = self.is_passable((x, y + 1))
        right = self.is_passable((x + 1, y))
        bottom = self.is_passable((x, y - 1))
        left = self.is_passable((x - 1, y))

        if top and left:
            corners.append((x - 1, y + 1))
        if top and right:
            corners.append((x + 1, y + 1))
        if bottom and left:
            corners.append((x - 1, y - 1))
        if bottom and right:
            corners.append((x + 1, y - 1))

        nodes = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)] + corners
        nodes = filter(self.is_passable, nodes)

        return nodes

    def cost(self, from_node, to_node):
        """ Implements abstract method `cost` from `Graph` """
        x1, y1 = from_node
        x2, y2 = to_node

        # diagonal
        if (x2 - x1 + y2 - y1) % 2 == 0:
            multiplier = 2**0.5
        # straight
        else:
            multiplier = 1

        # double cost for "invisible" tiles
        if self.is_revealed(*to_node):
            return 1 * multiplier
        else:
            return 1 * multiplier

    def find_path(self, from_node: Tuple[float, float], to_node: Tuple[float, float]) -> List[Tuple[float, float]]:
        def heuristic(from_node, to_node):
            (x0, y0) = from_node
            (x1, y1) = to_node
            D = 1  # NESW cost
            D2 = 2**0.5  # diagonal cost
            dx = abs(x0 - x1)
            dy = abs(y0 - y1)
            return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

        # make start and goal positions into `int`s
        from_node = (int(from_node[0]), int(from_node[1]))
        to_node = (int(to_node[0]), int(to_node[1]))

        def pathify(path):
            if not path:
                return None
            return list(map(lambda node: vmath.Vector2(node[0] + 0.5, node[1] + 0.5), path))

        # already at target location
        if from_node == to_node:
            return pathify([from_node])

        # target isn't passable
        if not self.is_passable(to_node):
            # try the neighbours, sorted by distance from the start
            n = self.neighbors(to_node)
            n = sorted(n, key=lambda node: heuristic(from_node, node))
            n = filter(self.is_passable, n)
            n = list(n)
            # do we have a valid neighbor?
            if len(n) > 0:
                # if so go there instead
                to_node = n[0]
            else:
                # else we just return no path and skip the A* search
                return pathify(None)

        came_from, cost_so_far = pathfinding.a_star_search(self, from_node, to_node, heuristic)
        path = pathfinding.reconstruct_path(came_from, from_node, to_node)
        # map the path from tile coordinates to agent coordinates

        return pathify(path)

    # vvvv copy methods from map.Map vvvv

    def is_wall(self, x: int, y: int) -> bool:
        return self._map.is_wall(x, y)
