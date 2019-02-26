import arcade

from . import renderer


class Editor(renderer.WindowComponent):
    def setup(self):
        # running or not
        self.enabled = False
        # input controls
        self.start_pos = None  # start location of mouse dragging

    def on_draw(self):
        if self.enabled:
            arcade.draw_text("EDITING MODE", 8, self.parent.SCREEN_HEIGHT - 24 - 18, arcade.color.MAGENTA, 16)

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
            self.parent.world.map.add_wall(*self.start_pos, *end_pos)
            self.start_pos = None
            # invalidate map VBO to force rebuild
            self.parent.mapview.tiles_vbo = None
            return True
