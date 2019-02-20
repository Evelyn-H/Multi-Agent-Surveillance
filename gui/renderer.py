import timeit
import arcade
from simulation.world import World

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "Sprite Collect Coins Example"


class GUI(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self, world: World) -> None:
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # save the world ;)
        assert world is not None
        self.world = world

        # for fps calculations
        self.t0 = timeit.default_timer()
        self.frame_count = 0
        self.fps = 0

        arcade.set_background_color(arcade.color.BLACK)
        self.set_update_rate(1.0 / 60)

    def setup(self):
        """ Set up the GUI and initialize the variables. """
        ...

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()

        # draw tiles
        for x in range(self.world.map.size[0]):
            for y in range(self.world.map.size[1]):
                # default color
                color = (0.2, 0.2, 0.2)
                # vision modfier
                vision_modifier = self.world.map.vision_modifier[x][y]
                if vision_modifier < 1.0:
                    color = (1, 1, vision_modifier * 0.75)
                # wall
                if self.world.map.walls[x][y]:
                    color = (0.8, 0.8, 0.8)

                arcade.draw_lrtb_rectangle_filled(x, x + 1, y + 1, y, color=tuple([int(255 * c) for c in color]))

        # FPS timing stuff
        t = timeit.default_timer()
        self.frame_count += 1
        if t - self.t0 > 1:
            self.fps = self.frame_count / (t - self.t0)
            self.t0 = timeit.default_timer()
            self.frame_count = 0

        arcade.draw_text(f"FPS: {self.fps:3.1f}", 8, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        ...

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        vp = self.get_viewport()
        if scroll_y == -1:
            new_vp = tuple((x * 0.5 for x in vp))
        if scroll_y == 1:
            new_vp = tuple((x * 2 for x in vp))
        self.set_viewport(*new_vp)
        print(self.get_viewport())

    def update(self, delta_time):
        """ Update ALL the things! """
        ...
