import arcade
import numpy as np
from gui import renderer
from simulation.world import World, Marker, MarkerType
from simulation.environment import Map
from simulation.util import Position
from ai import agents

if __name__ == '__main__':
    # init agents and stuff here
    map = Map(size=(200, 200))
    for _ in range(1000):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.walls[x][y] = True

    for _ in range(1000):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.vision_modifier[x][y] = np.random.rand() * 0.75 + 0.25

    for _ in range(4):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.targets.append(Position(x, y))

    for _ in range(10):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.towers.append(Position(x, y))

    for _ in range(10):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.markers.append(Marker(MarkerType.MAGENTA, Position(x, y)))

    world = World(map)

    world.add_agent(agents.SimpleGuard(Position(40, 40), map=map, color=(1.0, 1.0, 0)))
    world.add_agent(agents.SimpleGuard(Position(60, 40), map=map, color=(1.0, 1.0, 0)))
    world.add_agent(agents.SimpleGuard(Position(80, 40), map=map))

    # initialise the world
    world.setup()

    # init the GUI
    window = renderer.GUI(world)

    # and run everything
    arcade.run()
