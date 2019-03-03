"""
Load a Tiled map file

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_tiled_map
"""

import time

import arcade

from .agentGui import Agent
from .mapGui import MapGui


SPRITE_SCALING = 2.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Tiled Map Example"
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 60
VIEWPORT_MARGIN_BOTTOM = 60
VIEWPORT_RIGHT_MARGIN = 270
VIEWPORT_LEFT_MARGIN = 270

# Physics
MOVEMENT_SPEED = 5

class GUI(arcade.Window):
    """ Main application class. """

    def __init__(self, map):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.

        # Sprite lists
        self.platform_list = None
        # Set up the player
        self.score = 0
        self.agent = Agent()
        
        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.game_over = False
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

    def setup(self):
        """ Set up the game and initialize the variables. """
        #Define all layers from the map
        platforms_layer_name = 'Platforms'
        background_layer_name = 'Background'
        bridge_layer_name = 'Bridge'
        paths_layer_name = 'Paths'
        pathDeco_layer_name = 'PathDeco'
        platformsDeco_layer_name = 'PlatformsDeco'
        wallDeco_layer_name = 'WallDeco'
        
#        map_name = "gfx/CollectionTest.tmx"
        map_name = "gfx/StressTest.tmx"

        # Read in the tiled map
        my_map = arcade.read_tiled_map(map_name, SPRITE_SCALING)

        # --- Walls ---
        # Grab the layer of items we can't move through
        map_array = my_map.layers_int_data[platforms_layer_name]
        

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE

        # --- Platforms ---
        self.platform_list = arcade.generate_sprites(my_map, platforms_layer_name, SPRITE_SCALING)

        # --- Coins ---
        self.background_list = arcade.generate_sprites(my_map, background_layer_name, SPRITE_SCALING)
        print(self.background_list)
        self.bridge_list = arcade.generate_sprites(my_map, bridge_layer_name, SPRITE_SCALING)
        self.path_list = arcade.generate_sprites(my_map, paths_layer_name, SPRITE_SCALING)
        self.pathDeco_list = arcade.generate_sprites(my_map, pathDeco_layer_name, SPRITE_SCALING)
        self.platformDeco_list = arcade.generate_sprites(my_map, platformsDeco_layer_name, SPRITE_SCALING)
        self.wallDeco_list = arcade.generate_sprites(my_map, wallDeco_layer_name, SPRITE_SCALING)

        # --- Other stuff
        # Set the background color
        if my_map.backgroundcolor:
            arcade.set_background_color(my_map.backgroundcolor)

        # Keep player from running through the platform_list layer
#        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
#                                                             self.platform_list,
#                                                              gravity_constant=GRAVITY)
        self.physics_engine = arcade.PhysicsEngineSimple(self.agent.getAgent(), self.platform_list)


        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        self.frame_count += 1

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.background_list.draw()
        self.path_list.draw()
        self.platform_list.draw()
        self.wallDeco_list.draw() 
        self.platformDeco_list.draw()
        self.pathDeco_list.draw()
        self.bridge_list.draw()
        if(self.agent.praise):
            self.agent.updatePraiseAnimation()
            self.agent.getPraiseSprite().draw()
        elif(self.agent.attack):
            self.agent.updateAttackAnimation()
            self.agent.getAttackSprite().draw()
        else: 
            self.agent.getAgent().draw()

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        if self.fps_message:
            arcade.draw_text(self.fps_message, self.view_left + 10, self.view_bottom + 40, arcade.color.BLACK, 14)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        distance = self.agent.getAgent().right
        output = f"Distance: {distance}"
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20, arcade.color.BLACK, 14)

        if self.game_over:
            arcade.draw_text("Game Over", self.view_left + 200, self.view_bottom + 200, arcade.color.BLACK, 30)

    """
    TODO: Extract Key listener into a different module (I don't know how to do that)
    """
    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.P:
            self.agent.praise = True
        if key == arcade.key.O:
            self.agent.attack = True
        self.agent.setChange(key, MOVEMENT_SPEED)
        
    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.P:
            self.agent.praise = False        
        if key == arcade.key.O:
            self.agent.attack = False
        self.agent.setChange(key, 0)


    def update(self, delta_time):
        """ Movement and game logic """
        self.agent.updateAnimation()
        
        if self.agent.getAgent().right >= self.end_of_map:
            self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.agent.getAgent().left < left_bndry:
            self.view_left -= left_bndry - self.agent.getAgent().left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.agent.getAgent().right > right_bndry:
            self.view_left += self.agent.getAgent().right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.agent.getAgent().top > top_bndry:
            self.view_bottom += self.agent.getAgent().top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.agent.getAgent().bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.agent.getAgent().bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)