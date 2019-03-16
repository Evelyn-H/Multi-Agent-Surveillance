import numpy as np
from typing import List, Tuple, Dict

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

    def to_dict(self) -> Dict:
        return {
            'size': self.size,
            # objects on map
            'targets': [[t.x, t.y] for t in self.targets],
            'towers': [[t.x, t.y] for t in self.towers],
            'gates': self.gates,
            'markers': self.markers,
            # np arrays
            'walls': self.walls,
            'vision_modifier': self.vision_modifier,
        }

    @classmethod
    def from_dict(self, data) -> 'Map':
        m = Map(data['size'], data['targets'], data['gates'], data['towers'], data['markers'])
        m.targets = list(map(lambda x: Position(x[0], x[1]), m.targets))
        m.towers = list(map(lambda x: Position(x[0], x[1]), m.towers))
        m.walls = data['walls']
        m.vision_modifier = data['vision_modifier']
        return m

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

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


class MapGenerator:
    @classmethod
    def random(cls, size):
        m = Map(size=size)

        # percentage of wall tiles to add
        wall_ratio = 0.02
        # percentage of low vision tiles to add
        low_vis_ratio = 0.02
        # number of targets and towers to add
        num_targets = 4
        num_towers = 10

        for _ in range(int(wall_ratio * m.size[0] * m.size[1])):
            x, y = np.random.randint(0, m.size[0], size=2)
            m.walls[x][y] = True

        for _ in range(int(low_vis_ratio * m.size[0] * m.size[1])):
            x, y = np.random.randint(0, m.size[0], size=2)
            m.vision_modifier[x][y] = np.random.rand() * 0.75 + 0.25

        for _ in range(num_targets):
            x, y = np.random.randint(0, m.size[0], size=2)
            m.targets.append(Position(x, y))

        for _ in range(num_towers):
            x, y = np.random.randint(0, m.size[0], size=2)
            m.towers.append(Position(x, y))

        # for _ in range(10):
        #     x, y = np.random.randint(0, m.size[0], size=2)
        #     m.markers.append(Marker(MarkerType.MAGENTA, Position(x, y)))

        return m

    @classmethod
    def blank(cls, size):
        return Map(size=size)

    @classmethod
    def maze(cls, size):
        from numpy.random import randint as rand

        # from: https://en.wikipedia.org/wiki/Maze_generation_algorithm#Python_code_example
        def maze_prims(width=81, height=51, complexity=.75, density=.75):
            # Only odd shapes
            shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
            # Adjust complexity and density relative to maze size
            complexity = int(complexity * (5 * (shape[0] + shape[1])))  # number of components
            density = int(density * ((shape[0] // 2) * (shape[1] // 2)))  # size of components
            # Build actual maze
            Z = np.zeros(shape, dtype=bool)
            # Fill borders
            Z[0, :] = Z[-1, :] = 1
            Z[:, 0] = Z[:, -1] = 1
            # Make aisles
            for i in range(density):
                x, y = rand(0, shape[1] // 2) * 2, rand(0, shape[0] // 2) * 2  # pick a random position
                Z[y, x] = 1
                for j in range(complexity):
                    neighbours = []
                    if x > 1:
                        neighbours.append((y, x - 2))
                    if x < shape[1] - 2:
                        neighbours.append((y, x + 2))
                    if y > 1:
                        neighbours.append((y - 2, x))
                    if y < shape[0] - 2:
                        neighbours.append((y + 2, x))
                    if len(neighbours):
                        y_, x_ = neighbours[rand(0, len(neighbours) - 1)]
                        if Z[y_, x_] == 0:
                            Z[y_, x_] = 1
                            Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                            x, y = x_, y_
            return Z

        z = maze_prims(size[0], size[1], complexity=1, density=1)
        # z = maze_prims(size[0] // 2, size[1] // 2, complexity=1, density=1)
        m = Map(size=size)
        for x in range(0, m.size[0]):
            for y in range(0, m.size[1]):
                if z[x, y]:
                    m.walls[x][y] = True
        # for x in range(0, m.size[0], 2):
            # for y in range(0, m.size[1], 2):
                # if z[x // 2, y // 2]:
                #     m.walls[x][y] = True
                #     m.walls[x + 1][y] = True
                #     m.walls[x][y + 1] = True
                #     m.walls[x + 1][y + 1] = True

        return m
