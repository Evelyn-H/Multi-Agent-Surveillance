import arcade
from gui import renderer
from simulation.world import World
from simulation.environment import Map, MapGenerator
from simulation.util import Position
from ai import agents

if __name__ == '__main__':
    # init agents and stuff here
    m = MapGenerator.random((200, 200))

    world = World(m)

    world.add_agent(agents.SimpleGuard)
    world.add_agent(agents.PathfindingGuard)
    world.add_agent(agents.SimpleGuard)

    # initialise the world
    world.setup()

    # init the GUI
    window = renderer.GUI(world)

    # and run everything
    arcade.run()
