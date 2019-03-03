import gui.DrawingTests2
#gui.DrawingTests2.main()

import arcade
from gui import DrawingTests2
#from gui import MapGui
#from simulation.world import World
from simulation.map import Map

if __name__ == '__main__':
    # init agents and stuff here
#    map = Map(size=(200, 200))
#    agents = []
#    world = World(map, agents)
    

    # Read in the tiled map
#    map_name = "gfx/CollectionTest.tmx"
    map_name = "gfx/StressTest.tmx"
    SPRITE_SCALING = 0.625
    tiled_map = arcade.read_tiled_map(map_name, SPRITE_SCALING)
    map = Map(tiled_map)

    # and run the GUI
    window = DrawingTests2.GUI(map)
    window.setup()
    arcade.run()
