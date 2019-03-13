import arcade
from gui import renderer
from simulation.world import World
from simulation.environment import Map, MapGenerator
from ai import agents

if __name__ == '__main__':

    i = input('Load save? ')
    # load from file
    if i:
        names = i.split()
        if len(names) > 1:
            world = World.load_map(names[0])
            world.load_agents(names[1])
        else:
            world = World.from_file(names[0], load_agents=True)
    # or build a new map
    else:
        m = MapGenerator.maze(size=(51, 51))

        world = World(m)

        world.add_agent(agents.SimpleGuard)
        world.add_agent(agents.SimpleGuard)
        world.add_agent(agents.PathfindingGuard)

    # initialise the world
    world.setup()

    # world.to_file('test.json')

    # init the GUI
    window = renderer.GUI(world)

    # and run everything
    arcade.run()
