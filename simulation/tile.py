from typing import List, Tuple

""" If there is some kind of abstract class concept in python this could
    be a representation of all tiles that we need. """
"""Not sure if we need this at all when we can load the maps as in the gui package"""
class Tile:

    def __init__(self, center_x: float, center_y: float, size: float) -> None:
        self.center_x: float = center_x
        self.center_y: float = center_y
        self.size: float = size
        # A tile can have additional different properties like walkable etc. 
        #TBD some individual properties in either subclass implementations in the constructor or with getters and setters
        
    """ Extract this into the map class where a collection/list/matrix of tiles can be returned"""    
    def getTile(self):
        return self
    
    """ Return the position of a tile. Not sure, if this is neccesary when we have the get tile method """
    def getPosition(self):
        return self.center_x, self.center_y
    
    def getSize(self):
        return self.size
    