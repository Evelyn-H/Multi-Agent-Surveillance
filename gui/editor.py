import arcade

class Editor:
    def __init__(self, window: arcade.Window):
        self.window = window
        # running or not
        self.enabled = False

        # input controls
        self.start_pos = None  # start location of mouse dragging

    def on_draw(self):
        """ Draw everything """
        arcade.draw_text("EDITING MODE", 8, self.window.SCREEN_HEIGHT - 24 - 18, arcade.color.MAGENTA, 16)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        ...

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # add wall at the point that was clicked
            self.start_pos = self.window.screen_to_map(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        """ Called when a mouse button is released"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # add wall at the point that was clicked
            end_pos = self.window.screen_to_map(x, y)
            self.window.world.map.add_wall(*self.start_pos, *end_pos)
            self.start_pos = None
            # invalidate map VBO to force rebuild
            self.window.tiles_vbo = None

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """ Called when the scroll wheel is used """
        ...

    def on_key_press(self, key, modifiers):
        """ Called when a key is pressed """
        ...
