import timeit
import arcade
import pyglet.gl as gl
import numpy as np
from simulation.world import World

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
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

    def setup(self):
        """ Set up the GUI """
        self.viewport = Viewport(-50 * ASPECT_RATIO, 250 * ASPECT_RATIO, -50, 250)

        arcade.set_background_color(arcade.color.BLACK)
        self.set_update_rate(1.0 / 60)

        self.shape_grid = None

        # for fps calculations
        self.t0 = timeit.default_timer()
        self.frame_t0 = timeit.default_timer()
        self.frame_count = 0
        self.fps = 0

    def build_grid(self):
        # prepare VBO for tiles
        points = []
        colors = []
        for x in range(self.world.map.size[0]):
            for y in range(self.world.map.size[1]):
                # default color
                color = (0.2, 0.2, 0.2)
                # vision modfier
                vision_modifier = self.world.map.vision_modifier[x][y]
                if vision_modifier < 1.0:
                    color = (0, vision_modifier * 0.75, 0)
                # wall
                if self.world.map.walls[x][y]:
                    color = (0.8, 0.8, 0.8)

                # arcade.draw_lrtb_rectangle_filled(x, x + 1, y + 1, y, color=tuple([int(255 * c) for c in color]))
                # shape = arcade.create_rectangle_filled(x, y, 1, 1, color=tuple([int(255 * c) for c in color]))
                points.extend([(x, y), (x + 1, y), (x, y + 1), (x, y + 1), (x + 1, y), (x + 1, y + 1)])
                colors.extend([tuple([int(255 * c) for c in color])] * 6)

        return arcade.create_line_generic_with_colors(points, colors, gl.GL_TRIANGLES)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.set_viewport(*self.viewport.as_tuple())

        if self.shape_grid is None:
            self.shape_grid = self.build_grid()

        # and render it
        with self.shape_grid.vao:
            self.shape_grid.program['Projection'] = arcade.get_projection().flatten()
        self.shape_grid.draw()

        # FPS timing stuff
        t = timeit.default_timer()
        self.frame_count += 1
        if t - self.t0 > 1:
            self.fps = self.frame_count / (t - self.t0)
            self.t0 = timeit.default_timer()
            self.frame_count = 0
            print(f"FPS: {self.fps:3.1f}", f"({(1 / self.fps) * 1000:3.2f}ms)")

        if t - self.frame_t0 > (1.0 / 60):
            print(f"Frame took too long: {(t - self.frame_t0) * 1000:3.2f}ms")
        self.frame_t0 = t
        # arcade.draw_text(f"FPS: {self.fps:3.1f}", 8, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        ...

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.viewport.zoom(direction=scroll_y, factor=1.2)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        move_amount = 0.1
        if key == arcade.key.UP or key == arcade.key.W:
            self.viewport.move(0, move_amount)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.viewport.move(0, -move_amount)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.viewport.move(-move_amount, 0)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.viewport.move(move_amount, 0)

    def update(self, delta_time):
        """ Update ALL the things! """
        ...


class Viewport:
    def __init__(self, left, right, bottom, top):
        self.bottom_left = np.array((left, bottom), dtype=np.float32)
        self.top_right = np.array((right, top), dtype=np.float32)

    def as_tuple(self):
        return (self.bottom_left[0], self.top_right[0], self.bottom_left[1], self.top_right[1])

    def center(self):
        return np.array(((self.bottom_left[0] + self.top_right[0]) / 2, (self.bottom_left[1] + self.top_right[1]) / 2))

    def width(self):
        return self.top_right[0] - self.bottom_left[0]

    def height(self):
        return self.top_right[1] - self.bottom_left[1]

    def zoom(self, direction=1, factor=1.2):
        center = self.center()
        factor = factor if direction < 0 else (1 / factor)

        self.bottom_left = (self.bottom_left - center) * factor + center
        self.top_right = (self.top_right - center) * factor + center

        print(self)

    def move(self, move_x, move_y):
        """`move_x` and `move_y` represent a percentage of the screen size"""
        offset = np.array((move_x * self.width(), move_y * self.height()))
        self.bottom_left += offset
        self.top_right += offset

    def __str__(self):
        return f"Viewport: (x0,y0)={self.bottom_left}, (x1,y1)={self.top_right}"
