"""
The GUI part of the agent.
"""

import arcade

SPRITE_SCALING = 2.5
#MOVEMENT_SPEED = 5

class Agent():

    def __init__(self):
        
        self.player_list = None
        self.player_sprite = None
        self.player = None
        self.setup()

    def setup(self):
        """ Set up the player sprites and initialize the variables. """
        self.player = arcade.AnimatedWalkingSprite()
        self.loadTextures()

        # Starting position of the player
        self.player.center_x = 50
        self.player.center_y = 1500
        self.player.scale = 2
        
    def getSpriteList(self):
        return self.player_list
    
    def getSprite(self):
        return self.player_sprite
    
    def getAgent(self):
        return self.player
    
    def setChange(self, key1, MOVEMENT_SPEED):
        if key1 == arcade.key.UP:
            self.player.change_y = MOVEMENT_SPEED
        elif key1 == arcade.key.DOWN:
            self.player.change_y = -MOVEMENT_SPEED
        elif key1 == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key1 == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED
       # print(self.player.change_x)
       # print(self.player.change_y)
         
            
    def loadTextures(self):
        character_scale = 2.5;
        self.player.stand_right_textures = []
        self.player.stand_right_textures.append(arcade.load_texture("gfx/Agent/walk_right/0.png",
                                                                    scale=character_scale))
        self.player.stand_left_textures = []
        self.player.stand_left_textures.append(arcade.load_texture("gfx/Agent/walk_left/0.png",
                                                                   scale=character_scale))

        self.player.walk_right_textures = []

        self.player.walk_right_textures.append(arcade.load_texture("gfx/Agent/walk_right/0.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("gfx/Agent/walk_right/1.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("gfx/Agent/walk_right/2.png",
                                                                   scale=character_scale))
        self.player.walk_right_textures.append(arcade.load_texture("gfx/Agent/walk_right/3.png",
                                                                   scale=character_scale))

        self.player.walk_left_textures = []
        self.player.walk_left_textures.append(arcade.load_texture("gfx/Agent/walk_left/0.png",
                                                                  scale=character_scale))
        self.player.walk_left_textures.append(arcade.load_texture("gfx/Agent/walk_left/1.png",
                                                                  scale=character_scale))
        self.player.walk_left_textures.append(arcade.load_texture("gfx/Agent/walk_left/2.png",
                                                                  scale=character_scale))
        self.player.walk_left_textures.append(arcade.load_texture("gfx/Agent/walk_left/3.png",
                                                                  scale=character_scale))

        self.player.walk_up_textures = []
        self.player.walk_up_textures.append(arcade.load_texture("gfx/Agent/walk_up/0.png",
                                                                  scale=character_scale))
        self.player.walk_up_textures.append(arcade.load_texture("gfx/Agent/walk_up/1.png",
                                                                  scale=character_scale))
        self.player.walk_up_textures.append(arcade.load_texture("gfx/Agent/walk_up/2.png",
                                                                  scale=character_scale))
        self.player.walk_up_textures.append(arcade.load_texture("gfx/Agent/walk_up/3.png",
                                                                  scale=character_scale))

        self.player.walk_down_textures = []
        self.player.walk_down_textures.append(arcade.load_texture("gfx/Agent/walk_down/0.png",
                                                                  scale=character_scale))
        self.player.walk_down_textures.append(arcade.load_texture("gfx/Agent/walk_down/1.png",
                                                                  scale=character_scale))
        self.player.walk_down_textures.append(arcade.load_texture("gfx/Agent/walk_down/2.png",
                                                                  scale=character_scale))
        self.player.walk_down_textures.append(arcade.load_texture("gfx/Agent/walk_down/3.png",
                                                                  scale=character_scale))

        self.player.texture_change_distance = 20
