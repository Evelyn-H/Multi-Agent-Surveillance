from typing import Dict, List, Tuple
import collections
import arcade
import pyglet.gl as gl
import numpy as np

from simulation.agent import Agent

from . import renderer


class MapViewer(renderer.WindowComponent):

    AGENT_RADIUS = 1.5

    def setup(self):
        # get reference to `world` for less typing
        self.world = self.parent.world

        # self.viewport = renderer.Viewport(-50 * self.parent.ASPECT_RATIO, 250 * self.parent.ASPECT_RATIO, -50, 250)
        w = self.world.map.size[0]
        h = self.world.map.size[1]
        self.viewport = renderer.Viewport(w / 2, h / 2, w * 1.2 * self.parent.ASPECT_RATIO, w * 1.2)

        # variables to store rendering objects
        self.tiles_vbo = None
        self.map_items = None

        # fog-of-war
        # None: no fog-of-war
        # number: viewing what a certain agent sees
        self.fog = None

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

        # register commands
        self.parent.console.register_command('fow', lambda x: self.set_fog(int(x)))

        # to track mouse motion
        self.mouse_x = 0
        self.mouse_y = 0

    def set_fog(self, agent=None):
        if agent in self.world.agents:
            self.fog = agent
        else:
            self.fog = None
            # force redraw
            self.tiles_vbo = None

    def update_agent_sprites(self):
        for ID, agent in self.world.agents.items():
            sprite = self.agent_sprite_map[agent]
            sprite.center_x = agent.location.x
            sprite.center_y = agent.location.y
            sprite.angle = -agent.heading

    def build_grid(self):
        # prepare VBO for tiles
        # init arrays
        points = []
        colors = []
        # add background
        w = self.world.map.size[0]
        h = self.world.map.size[1]
        points.extend(((0, 0), (w, 0), (0, h), (0, h), (w, 0), (w, h)))
        bg_color = (0.2, 0.2, 0.2)
        colors.extend([tuple((int(255 * c) for c in bg_color))] * 6)
        # for each tile...
        for x in range(self.world.map.size[0]):
            for y in range(self.world.map.size[1]):

                # hacky fog-of-war rendering
                if self.fog and not self.world.agents[self.fog].map.is_revealed(x, y):
                    continue

                vision_modifier = self.world.map.vision_modifier[x][y]
                # wall
                if self.world.map.walls[x][y]:
                    color = (0.8, 0.8, 0.8)
                # vision modfier
                elif vision_modifier < 1.0:
                    color = (0, vision_modifier * 0.6, 0)
                # fog-of-war
                elif self.fog:
                    color = (0.4, 0.4, 0.4)
                # nothing here to draw
                else:
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
            shape_list.append(arcade.create_rectangle_filled(target.x + 0.5, target.y + 0.5, 2, 2, color=(0, 0, 255)))

        # towers (red)
        for tower in self.world.map.towers:
            shape_list.append(arcade.create_rectangle_filled(tower.x + 0.5, tower.y + 0.5, 2, 2, color=(255, 0, 0)))

        # communication markers (circles)
        for marker in self.world.map.markers:
            shape_list.append(arcade.create_ellipse_filled(marker.location.x + 0.5, marker.location.y + 0.5, 1, 1, color=(255, 0, 255)))

        # TODO: self.gates

        self.map_items = shape_list

    def screen_to_map(self, x, y, round=True):
        """ Maps screen coordinates in the current viewport to coordinates in the game map """
        x = np.interp(x, (0, self.parent.SCREEN_WIDTH), (self.viewport.bottom_left[0], self.viewport.top_right[0]))
        y = np.interp(y, (0, self.parent.SCREEN_HEIGHT), (self.viewport.bottom_left[1], self.viewport.top_right[1]))
        if round:
            return (int(x), int(y))
        else:
            return (x, y)

    def update(self, dt):
        # agent trails
        for ID, agent in self.world.agents.items():
            self.agent_trails[agent].append((agent.location.x, agent.location.y))

    def on_draw(self):
        self.parent.set_viewport(*self.viewport.as_tuple())

        # update agent sprites
        self.update_agent_sprites()

        # build map VBO if necessary
        if self.tiles_vbo is None or self.fog:
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

        # draw agent trails
        for ID, agent in self.world.agents.items():
            arcade.draw_line_strip(self.agent_trails[agent], color=[int(255 * c) for c in agent.color])

        # draw agents
        self.agent_sprites.draw()

        # change back to pixel viewport for the next WindowComponent
        self.parent.set_viewport(0, self.parent.SCREEN_WIDTH, 0, self.parent.SCREEN_HEIGHT)

        # print map position of the cursor
        location = self.screen_to_map(self.mouse_x, self.mouse_y, round=False)
        text = f"({location[0]:3.2f}, {location[1]:3.2f})"
        arcade.draw_lrtb_rectangle_filled(
            self.parent.SCREEN_WIDTH - 12 * len(text) - 6, self.parent.SCREEN_WIDTH,
            self.parent.SCREEN_HEIGHT, self.parent.SCREEN_HEIGHT - 24 - 6,
            color=(0, 0, 0, 192)
        )
        arcade.draw_text(text, self.parent.SCREEN_WIDTH - 12 * len(text), self.parent.SCREEN_HEIGHT - 24, arcade.color.WHITE, 16)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_key_press(self, key, modifiers):
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
        else:
            return False
        return True

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.viewport.move(-dx / self.parent.SCREEN_WIDTH, -dy / self.parent.SCREEN_HEIGHT)
            return True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # map zooming
        self.viewport.zoom(direction=scroll_y, factor=1.2)
        return True
