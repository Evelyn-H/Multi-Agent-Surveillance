import timeit
from typing import Dict, List, Tuple
import collections

import arcade
import pyglet
import pyglet.gl as gl

import numpy as np
from simulation.world import World
from simulation.agent import Agent
from . import editor

# from profilehooks import profile


class GUI(arcade.Window):
    """ Our custom Window Class"""

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 960
    ASPECT_RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
    SCREEN_TITLE = "Multi Agent Surveillance"

    AGENT_RADIUS = 1.5

    def __init__(self, world: World) -> None:
        """ Initializer """
        # Call the parent class initializer
        super().__init__(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.SCREEN_TITLE)

        # set up key polling handler
        # this way we can poll `self.keys` to check input states outside of the event handlers
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        # save the world ;)
        assert world is not None
        self.world = world

    def setup(self):
        """ Set up the GUI """
        self.viewport = Viewport(-50 * self.ASPECT_RATIO, 250 * self.ASPECT_RATIO, -50, 250)

        arcade.set_background_color(arcade.color.BLACK)
        self.set_update_rate(1.0 / 60)

        # variables to store rendering objects
        self.tiles_vbo = None
        self.map_items = None

        # agent sprite objects
        self.agent_sprites = arcade.SpriteList()
        # map from `Agent`s to `Sprite`s
        self.agent_sprite_map: Dict[Agent, arcade.Sprite] = {}
        for ID, agent in self.world.agents.items():
            sprite = arcade.Sprite("gui/agent.png", scale=(1 / 64) * self.AGENT_RADIUS)
            sprite.color = tuple((int(255 * c) for c in agent.color))
            # add it to the sprite list
            self.agent_sprites.append(sprite)
            # and add it to a dict so we can get the sprite for a given agent
            self.agent_sprite_map[agent] = sprite

        # agent trails
        self.agent_trails: Dict[Agent, List[Tuple[float, float]]] = {}
        for ID, agent in self.world.agents.items():
            self.agent_trails[agent] = collections.deque(maxlen=self.world.TICK_RATE * 100)
            self.agent_trails[agent].append((agent.location.x, agent.location.y))

        # editor
        self.editor = editor.Editor(self)

        # for running the simulation at the right speed,
        # independent of the GUI framerate and tracking the turns per second
        self.game_speed = 1
        self.tick_time = 0
        self.tick_count = 0
        self.tps = 0

        # for fps calculations
        self.t0 = timeit.default_timer()
        self.frame_t0 = timeit.default_timer()
        self.frame_count = 0
        self.fps = 0

    def update_agent_sprites(self):
        for ID, agent in self.world.agents.items():
            sprite = self.agent_sprite_map[agent]
            sprite.center_x = agent.location.x
            sprite.center_y = agent.location.y
            sprite.angle = -agent.heading

    def update(self, dt):
        """ Update ALL the things! """
        # make sure we run at the right tick rate
        self.tick_time += dt
        while self.tick_time >= self.world.TIME_PER_TICK / self.game_speed:
            # subtract the `TIME_PER_TICK` when we run a tick
            self.tick_time -= self.world.TIME_PER_TICK / self.game_speed
            # and increase the `tick_count`
            self.tick_count += 1

            # update the simulation
            self.world.tick()
            # update agent sprites to match
            self.update_agent_sprites()

            # agent trails
            for ID, agent in self.world.agents.items():
                self.agent_trails[agent].append((agent.location.x, agent.location.y))

    # @profile
    def build_grid(self):
        # prepare VBO for tiles
        # init arrays
        points = []
        colors = []
        # add background
        w = self.world.map.size[0]
        h = self.world.map.size[1]
        points.extend(((0, 0), (w, 0), (0, h), (0, h), (w, 0), (w, h)))
        bg_color = (0.2, 0.2, 0.2, 1.0)
        colors.extend([tuple((int(255 * c) for c in bg_color))] * 6)
        # for each tile...
        for x in range(self.world.map.size[0]):
            for y in range(self.world.map.size[1]):
                # vision modfier
                vision_modifier = self.world.map.vision_modifier[x][y]
                if self.world.map.walls[x][y]:
                    color = (0.8, 0.8, 0.8)
                elif vision_modifier < 1.0:
                    color = (0, vision_modifier * 0.75, 0)
                # wall
                else:
                    # nothing here to draw
                    continue

                # add tile to array
                points.extend(((x, y), (x + 1, y), (x, y + 1), (x, y + 1), (x + 1, y), (x + 1, y + 1)))
                colors.extend([tuple((int(255 * c) for c in color))] * 6)

        # and build VBO object
        self.tiles_vbo = arcade.create_line_generic_with_colors(points, colors, gl.GL_TRIANGLES)

    def build_map_items(self):
        shape_list = arcade.ShapeElementList()
        # targets (blue)
        for target in self.world.map.targets:
            shape_list.append(arcade.create_rectangle_filled(target.x - 0.5, target.y - 0.5, 2, 2, color=(0, 0, 255)))

        # towers (red)
        for tower in self.world.map.towers:
            shape_list.append(arcade.create_rectangle_filled(tower.pos.x - 0.5, tower.pos.y - 0.5, 2, 2, color=(255, 0, 0)))

        # communication markers (circles)
        for marker in self.world.map.markers:
            shape_list.append(arcade.create_ellipse_filled(marker.location.x - 0.5, marker.location.y - 0.5, 1, 1, color=(255, 0, 255)))

        # TODO: self.gates

        self.map_items = shape_list

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.set_viewport(*self.viewport.as_tuple())

        # build map VBO if necessary
        if self.tiles_vbo is None:
            self.build_grid()

        # render main map tiles
        # fix projection each frame
        with self.tiles_vbo.vao:
            self.tiles_vbo.program['Projection'] = arcade.get_projection().flatten()
        # and draw
        self.tiles_vbo.draw()

        # render stuff on top of the map
        if self.map_items is None:
            self.build_map_items()
        # fix projection each frame
        with self.map_items.program:
            self.map_items.program['Projection'] = arcade.get_projection().flatten()
        # and draw
        self.map_items.draw()

        # draw agents
        self.agent_sprites.draw()

        # draw agent trails
        for ID, agent in self.world.agents.items():
            arcade.draw_line_strip(self.agent_trails[agent], color=[int(255 * c) for c in agent.color])

        # change to pixel viewport for text and menu drawing
        self.set_viewport(0, self.SCREEN_WIDTH, 0, self.SCREEN_HEIGHT)

        # editor
        if self.editor.enabled:
            self.editor.on_draw()

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
        # show the fps on the screen
        arcade.draw_text(f"FPS: {self.fps:3.1f}  TPS: {self.tps:3.1f} (x{self.game_speed})", 8, self.SCREEN_HEIGHT - 24, arcade.color.WHITE, 16)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        if self.editor.enabled:
            self.editor.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed"""
        # editor controls
        if self.editor.enabled:
            self.editor.on_mouse_press(x, y, button, modifiers)
        # normal controls
        else:
            ...

    def on_mouse_release(self, x, y, button, modifiers):
        """ Called when a mouse button is released"""
        # editor controls
        if self.editor.enabled:
            self.editor.on_mouse_release(x, y, button, modifiers)
        # normal controls
        else:
            ...

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.viewport.move(-dx / self.SCREEN_WIDTH, -dy / self.SCREEN_HEIGHT)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """ Called when the scroll wheel is used """
        # map zooming
        self.viewport.zoom(direction=scroll_y, factor=1.2)
        # editor controls
        if self.editor.enabled:
            self.editor.on_mouse_scroll(x, y, scroll_x, scroll_y)
        # normal controls
        else:
            ...

    def on_key_press(self, key, modifiers):
        """ Called when a key is pressed """
        # map panning
        move_amount = 0.1
        if key == arcade.key.UP or key == arcade.key.W:
            self.viewport.move(0, move_amount)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.viewport.move(0, -move_amount)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.viewport.move(-move_amount, 0)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.viewport.move(move_amount, 0)
        # Force rebuild VBOs
        elif key == arcade.key.B:
            self.build_grid()
            self.build_map_items()
        # toggle editing mode
        elif key == arcade.key.E:
            self.editor.enabled = not self.editor.enabled
        elif key == arcade.key.PLUS or key == arcade.key.NUM_ADD:
            self.game_speed *= 2
        elif key == arcade.key.MINUS or key == arcade.key.NUM_SUBTRACT:
            self.game_speed /= 2

        # editor controls
        if self.editor.enabled:
            self.editor.on_key_press(key, modifiers)

    def screen_to_map(self, x, y, round=True):
        """ Maps screen coordinates in the current viewport to coordinates in the game map """
        x = np.interp(x, (0, self.SCREEN_WIDTH), (self.viewport.bottom_left[0], self.viewport.top_right[0]))
        y = np.interp(y, (0, self.SCREEN_HEIGHT), (self.viewport.bottom_left[1], self.viewport.top_right[1]))
        if round:
            return (int(x), int(y))
        else:
            return (x, y)


class Viewport:
    """ Utility class for easy zooming and panning """

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

        # make sure we zoom around the center and not the corner of the screen
        self.bottom_left = (self.bottom_left - center) * factor + center
        self.top_right = (self.top_right - center) * factor + center

    def move(self, move_x, move_y):
        """`move_x` and `move_y` represent a percentage of the screen size"""
        offset = np.array((move_x * self.width(), move_y * self.height()))
        self.bottom_left += offset
        self.top_right += offset

    def __str__(self):
        return f"Viewport: (x0,y0)={self.bottom_left}, (x1,y1)={self.top_right}"
