import arcade
from gui import renderer
from simulation.world import World
from simulation.map import Map

if __name__ == '__main__':
    # init agents and stuff here
    map = Map(size=(200, 200))
    agents = []
    world = World(map, agents)

    # and run the GUI
    window = renderer.GUI(world)
    window.setup()
    arcade.run()
