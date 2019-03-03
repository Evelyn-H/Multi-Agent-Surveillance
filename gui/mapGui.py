"""
The GUI part of the map.
"""

from simulation.map import Map


SPRITE_SCALING = 2.5

class MapGui():
    

    def __init__(self, map):
        self.tiledMap = map.getTiledMap()

        return
    
    def setup(self):
        return
    
    def loadTextures(self):
        platforms_layer_name = 'Platforms'
        background_layer_name = 'Background'
        bridge_layer_name = 'Bridge'
        paths_layer_name = 'Paths'
        pathDeco_layer_name = 'PathDeco'
        platformsDeco_layer_name = 'PlatformsDeco'
        wallDeco_layer_name = 'WallDeco'
        self.background_list = arcade.generate_sprites(self.tiledMap, background_layer_name, SPRITE_SCALING)        
 
    def getTextures(self):
        return self.background_list