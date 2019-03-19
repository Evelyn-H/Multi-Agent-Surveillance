import timeit
# from profilehooks import profile

import arcade
import pyglet
import numpy as np
import vectormath as vmath

from simulation.world import World


class GUI(arcade.Window):
    """ Our custom Window Class"""

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 960
    ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
    SCREEN_TITLE = "Multi Agent Surveillance"

    def __init__(self, world: World) -> None:
        # Call the parent class initializer
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.SCREEN_TITLE)

        # set up key polling handler
        # this way we can poll `self.keys` to check input states outside of the event handlers
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        # save the world ;)
        assert world is not None
        self.world = world

        # background golor
        arcade.set_background_color(arcade.color.BLACK)

        # make sure `update` is called 60 times per second
        self.set_update_rate(1.0 / 60)

        # for running the simulation at the right speed,
        # independent of the GUI framerate and tracking the turns per second
        self.game_speed = 1
        self.is_paused = True
        self.tick_time = 0
        self.tick_count = 0
        self.tps = 0

        # for fps calculations
        self.t0 = timeit.default_timer()
        self.frame_t0 = timeit.default_timer()
        self.frame_count = 0
        self.fps = 0
        # editor

        from . import console
        from . import editor
        from . import mapviewer

        # and init all the `WindowComponent`s
        self.console = console.Console(self)
        self.editor = editor.Editor(self)
        self.mapview = mapviewer.MapViewer(self)

        # components will be called in this order
        self.components = [
            self.console,
            self.editor,
            self.mapview,
        ]

        # setup all components
        for c in self.components:
            c.setup()

        def toggle_paused(x):
            self.is_paused = not self.is_paused

        self.console.register_command('pause', toggle_paused)

    def update(self, dt):
        if self.is_paused:
            return

        # make sure we run at the right tick rate
        self.tick_time += dt
        while self.tick_time >= self.world.TIME_PER_TICK / self.game_speed:
            # subtract the `TIME_PER_TICK` when we run a tick
            self.tick_time -= self.world.TIME_PER_TICK / self.game_speed
            # and increase the `tick_count`
            self.tick_count += 1

            # update the simulation
            self.world.tick()

            #check if a noise should be emitted
            self.world.emit_random_noise(self.fps)

            # update all components
            for c in self.components:
                c.update(dt)

    def on_draw(self):
        arcade.start_render()

        # draw all components
        # (in reverse order to make sure the 'top' ones are drawn last)
        for c in self.components[::-1]:
            c.on_draw()

        # FPS timing stuff
        t = timeit.default_timer()
        self.frame_count += 1
        # update fps once a second
        if t - self.t0 > 1:
            self.fps = self.frame_count / (t - self.t0)
            self.tps = self.tick_count / (t - self.t0)
            self.t0 = timeit.default_timer()
            self.frame_count = 0
            self.tick_count = 0
            # print(f"FPS: {self.fps:3.1f}", f"({(1 / self.fps) * 1000:3.2f}ms)")

        # print a message if a frame takes more than 20ms
        # if t - self.frame_t0 > 0.02:
            # print(f"Frame took too long: {(t - self.frame_t0) * 1000:3.2f}ms")
        self.frame_t0 = t

        fps_text = f"FPS: {self.fps:3.1f}  TPS: {self.tps:3.1f} ({self.game_speed}x){' PAUSED' if self.is_paused else ''}"

        arcade.draw_lrtb_rectangle_filled(
            0, 8 + 12 * len(fps_text) + 6,
            self.SCREEN_HEIGHT, self.SCREEN_HEIGHT - 30,
            color=(0, 0, 0, 192)
        )

        # show the fps on the screen
        arcade.draw_text(
            fps_text,
            8, self.SCREEN_HEIGHT - 24, arcade.color.WHITE, 16
        )

    def on_key_press(self, key, modifiers):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_key_press(key, modifiers):
                return

        # game speed and pausing
        if key == arcade.key.PLUS or key == arcade.key.NUM_ADD:
            self.game_speed *= 2
        elif key == arcade.key.MINUS or key == arcade.key.NUM_SUBTRACT:
            self.game_speed /= 2
        elif key == arcade.key.SPACE:
            self.is_paused = not self.is_paused

    def on_mouse_motion(self, x, y, dx, dy):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_mouse_motion(x, y, dx, dy):
                break

    def on_mouse_press(self, x, y, button, modifiers):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_mouse_press(x, y, button, modifiers):
                break

    def on_mouse_release(self, x, y, button, modifiers):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_mouse_release(x, y, button, modifiers):
                break

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_mouse_drag(x, y, dx, dy, button, modifiers):
                break

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # handle input in all components,
        # only propagate as long as they return false
        for c in self.components:
            if c.on_mouse_scroll(x, y, scroll_x, scroll_y):
                break


class WindowComponent:
    def __init__(self, parent: arcade.Window):
        self.parent = parent

    def setup(self):
        pass

    def update(self, dt):
        pass

    def on_draw(self):
        pass

    def on_key_press(self, key, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        pass


class Viewport:
    """ Utility class for easy zooming and panning """

    def __init__(self, center_x, center_y, width, height):
        self.center = vmath.Vector2(center_x, center_y)
        self.width = width
        self.height = height
        # self.bottom_left = np.array((left, bottom), dtype=np.float32)
        # self.top_right = np.array((right, top), dtype=np.float32)

    @property
    def left(self):
        return self.center.x - self.width / 2

    @property
    def right(self):
        return self.center.x + self.width / 2

    @property
    def bottom(self):
        return self.center.y - self.height / 2

    @property
    def top(self):
        return self.center.y + self.height / 2

    @property
    def bottom_left(self):
        return (self.left, self.bottom)

    @property
    def top_right(self):
        return (self.right, self.top)

    def as_tuple(self):
        return (self.left, self.right, self.bottom, self.top)

    def zoom(self, direction=1, factor=1.2):
        factor = factor if direction < 0 else (1 / factor)

        # make sure we zoom around the center and not the corner of the screen
        # self.bottom_left = (self.bottom_left - self.center) * factor + self.center
        # self.top_right = (self.top_right - self.center) * factor + self.center
        self.width *= factor
        self.height *= factor

    def move(self, move_x, move_y):
        """`move_x` and `move_y` represent a percentage of the screen size"""
        self.center.x += move_x * self.width
        self.center.y += move_y * self.height
        # self.lock(-100, 300, 0, 200)

    def lock(self, left, right, bottom, top):
        if left and self.left < left:
            self.center.x += left - self.left
        if right and self.right > right:
            self.center.x += right - self.right
        if bottom and self.bottom < bottom:
            self.center.y += bottom - self.bottom
        if top and self.top > top:
            self.center.y += top - self.top

    def __str__(self):
        return f"Viewport: center={self.center}, (width, height)=({self.width}, {self.height})"
