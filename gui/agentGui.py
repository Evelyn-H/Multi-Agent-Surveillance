"""
The GUI part of the agent.
"""

from random import randint

import arcade
from simulation.agentSim import AgentSim


SPRITE_SCALING = 2.5
#MOVEMENT_SPEED = 5

class Agent():

    def __init__(self):
        self.player = None
        self.playerpraise = None
        self.praise = False
        self.attack = False
        self.textureIndex = 0
        self.attackCounter = 0
        self.attackanimation = randint(0, 2)
        self.agentSim = AgentSim();
        self.setup()
  
    def setup(self):
        """ Set up the player sprites and initialize the variables. """
        self.player = arcade.AnimatedWalkingSprite()
        #Probably smart to put them in some kind of collection
        self.playerpraise = arcade.AnimatedTimeSprite()
        self.playerattack = arcade.AnimatedTimeSprite()
        self.playerattacks = [arcade.AnimatedTimeSprite()
                              ,arcade.AnimatedTimeSprite()
                              ,arcade.AnimatedTimeSprite()]

        self.loadTextures()

        # Starting position of the player
        self.player.center_x = 50
        self.player.center_y = 1500
        self.player.scale = 2
        self.playerpraise.scale = 2
        self.playerpraise.center_x = self.player.center_x    
        self.playerpraise.center_y = self.player.center_y    

    def getAgent(self):
        return self.player
    
    def updateAnimation(self):
        pos_x, pos_y = self.agentSim.getPosition()
        self.player.center_x = pos_x
        self.player.center_y = pos_y
        self.player.update_animation()
        self.player.update()


    def updatePraiseAnimation(self):
        self.player.change_x = 0
        self.player.change_y = 0
        self.playerpraise.center_x = self.player.center_x    
        self.playerpraise.center_y = self.player.center_y
        self.playerpraise.update_animation()
        self.playerpraise.update()

    
    def updateAttackAnimation(self):
        self.player.change_x = 0
        self.player.change_y = 0
        self.playerattack.center_x = self.player.center_x    
        self.playerattack.center_y = self.player.center_y
        if(self.attackCounter > 3):
            self.attackanimation = 0#randint(0, 2)
            self.attackCounter = 0
        self.playerattack = self.playerattacks[self.attackanimation]
        self.playerattack.update_animation()
        self.playerattack.update()
        self.attackCounter += 1


    def setChange(self, key1, MOVEMENT_SPEED):
        if (self.praise or self.attack):
            return
        if key1 == arcade.key.UP:
            self.player.change_y = MOVEMENT_SPEED
        elif key1 == arcade.key.DOWN:
            self.player.change_y = -MOVEMENT_SPEED
        elif key1 == arcade.key.LEFT:
            self.player.change_x = -MOVEMENT_SPEED
        elif key1 == arcade.key.RIGHT:
            self.player.change_x = MOVEMENT_SPEED
            
         
    def getPraiseSprite(self):
        return self.playerpraise                 
            
    def getAttackSprite(self):
        return self.playerattack

    def loadTextures(self):
        character_scale = 2;
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

        self.player.praise = []

        self.player.praise.append(arcade.load_texture("gfx/Agent/praise/0.png",
                                                                   scale=character_scale))
        self.player.praise.append(arcade.load_texture("gfx/Agent/praise/1.png",
                                                                   scale=character_scale))
        self.player.praise.append(arcade.load_texture("gfx/Agent/praise/2.png",
                                                                   scale=character_scale))
        for tex in self.player.praise:
            self.playerpraise.append_texture(tex)

        for i in range(0,3): 
            self.player.attack = []

            self.player.attack.append(arcade.load_texture("gfx/Agent/attack/" + str(i) + "0.png",
                                                                   scale=character_scale))
            self.player.attack.append(arcade.load_texture("gfx/Agent/attack/" + str(i) + "1.png",
                                                                   scale=character_scale))
            self.player.attack.append(arcade.load_texture("gfx/Agent/attack/" + str(i) + "2.png",
                                                                   scale=character_scale))
            for tex in self.player.attack:
                self.playerattacks[i].append_texture(tex)

        self.player.texture_change_distance = 20
