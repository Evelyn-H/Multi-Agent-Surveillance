import arcade

from . import renderer


class Editor(renderer.WindowComponent):
    def setup(self):
        # running or not
        self.enabled = False

        # input modes
        self.current_mode = 1
        self.modes = {
            1: 'Walls',
            2: 'Low Vision Area',
            3: 'Target Area',
            4: 'Sentry Tower',
            5: 'Door',
            6: 'Window',
        }

        # start coordinate for mouse dragging
        self.start_pos = None  # start location of mouse dragging

    def on_draw(self):
        def line(i):
            return self.parent.SCREEN_HEIGHT - 24 - 18 * (i + 2)

        if self.enabled:
            arcade.draw_lrtb_rectangle_filled(
                0, 8 + 12 * 20 + 6,
                self.parent.SCREEN_HEIGHT - 24 - 18 * 1 + 4, self.parent.SCREEN_HEIGHT - 24 - 18 * 11 - 6,
                color=(0, 0, 0, 192)
            )

            arcade.draw_text("EDITING MODE", 8, line(0), arcade.color.MAGENTA, 16)

            arcade.draw_text("Editor Controls:", 8, line(2), arcade.color.WHITE, 16)

            for i, name in self.modes.items():
                arcade.draw_text(f"  {i}: {name}", 8, line(i + 3), arcade.color.WHITE, 16)

    def on_key_press(self, key, modifiers):
        # toggle editing mode
        if key == arcade.key.E:
            self.enabled = not self.enabled
            return True

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.enabled:
            return False

        if button == arcade.MOUSE_BUTTON_LEFT:
            # add wall at the point that was clicked
            self.start_pos = self.parent.mapview.screen_to_map(x, y)
            return True

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.enabled:
            return False

        if button == arcade.MOUSE_BUTTON_LEFT:
            # add wall at the point that was clicked
            end_pos = self.parent.mapview.screen_to_map(x, y)
            # are we removing or adding a wall?
            value = not (modifiers & arcade.key.MOD_CTRL)
            # add/remove wall
            self.parent.world.map.set_wall_rectangle(*self.start_pos, *end_pos, value)
            # and reset start pos for next input
            self.start_pos = None
            # invalidate map VBO to force rebuild
            self.parent.mapview.tiles_vbo = None
            return True
