import arcade
from gui import renderer
from simulation.world import World
from simulation.environment import Map, MapGenerator
from ai import agents

if __name__ == '__main__':
    # init agents and stuff here
    m = MapGenerator.maze(size=(50, 50))

    world = World(m)

    world.add_agent(agents.SimpleGuard)
    world.add_agent(agents.SimpleGuard)
    world.add_agent(agents.PathfindingGuard)


    # world = World.from_file('test.json')

    # initialise the world
    world.setup()

    # world.to_file('test.json')

    # init the GUI
    window = renderer.GUI(world)

    # and run everything
    arcade.run()
