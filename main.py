import arcade
import numpy as np
from gui import renderer
from simulation.world import World
from simulation.map import Map

if __name__ == '__main__':
    # init agents and stuff here
    map = Map(size=(200, 200))
    for _ in range(1000):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.walls[x][y] = True

    for _ in range(1000):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.vision_modifier[x][y] = np.random.rand() * 0.75 + 0.25

    agents = []
    world = World(map, agents)

    # and run the GUI
    window = renderer.GUI(world)
    window.setup()
    arcade.run()
