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
        m = MapGenerator.random(size=(51, 51))

        world = World(m)

<<<<<<< Upstream, based on branch 'master' of https://github.com/Evelyn-H/Multi-Agent-Surveillance.git
        world.add_agent(agents.SimpleGuard)
        world.add_agent(agents.SimpleGuard)
        world.add_agent(agents.SimpleGuard)
        world.add_agent(agents.PathfindingIntruder)
        world.add_agent(agents.PathfindingIntruder)
=======
    for _ in range(10):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.towers.append(Position(x, y))

    for _ in range(10):
        x, y = np.random.randint(0, map.size[0], size=2)
        map.markers.append(Marker(MarkerType.MAGENTA, Position(x, y)))
    world = World(map)

    world.add_agent(agents.SimpleGuard(Position(40, 40), map=map, color=(1.0, 1.0, 0)))
    world.add_agent(agents.PathfindingGuard(Position(60, 40), map=map, color=(1.0, 1.0, 0)))
    world.add_agent(agents.SimpleGuard(Position(80, 40), map=map))
>>>>>>> 1866a51 Poisson distribution for random noise

    # initialise the world
    world.setup()

    # world.to_file('test.json')

    # init the GUI
    window = renderer.GUI(world)

    # and run everything
    arcade.run()
