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
            3: 'Target Location',
            4: 'Sentry Tower',
            5: 'Door',
            6: 'Window',
        }

        # start coordinate for mouse dragging
        self.start_pos = None  # start location of mouse dragging

        # commands
        self.parent.console.register_command('save', lambda x: self.parent.world.to_file(x))
        self.parent.console.register_command('save_map', lambda x: self.parent.world.save_map(x))
        self.parent.console.register_command('save_agents', lambda x: self.parent.world.save_agents(x))

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
                color = arcade.color.MAGENTA if i == self.current_mode else arcade.color.WHITE
                arcade.draw_text(f"  {i}: {name}", 8, line(i + 3), color, 16)

    def on_key_press(self, key, modifiers):
        # toggle editing mode
        if key == arcade.key.E:
            self.enabled = not self.enabled
            return True

        # change editor mode
        if self.enabled and (key >= arcade.key.KEY_1 and key <= arcade.key.KEY_9):
            m = int(chr(key))
            if m in self.modes:
                self.current_mode = m

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.enabled:
            return False

        if button == arcade.MOUSE_BUTTON_LEFT:
            # resolve input according to which mode we're in
            # walls or low visibility area
            if self.current_mode == 1 or self.current_mode == 2:
                # store current point for dragging
                self.start_pos = self.parent.mapview.screen_to_map(x, y)
                return True


    def on_mouse_release(self, x, y, button, modifiers):
        if not self.enabled:
            return False

        if button == arcade.MOUSE_BUTTON_LEFT:
            # add wall at the point that was clicked
            end_pos = self.parent.mapview.screen_to_map(x, y)
            # check if control is being held
            ctrl_held = (modifiers & arcade.key.MOD_CTRL)
            # resolve input according to which mode we're in
            # walls
            if self.current_mode == 1:
                # are we removing or adding a wall?
                # add/remove wall
                value = False if ctrl_held else True
                self.parent.world.map.set_wall_rectangle(*self.start_pos, *end_pos, value)
            # low vision area
            elif self.current_mode == 2:
                value = 1.0 if ctrl_held else 0.5
                self.parent.world.map.set_vision_area(*self.start_pos, *end_pos, value)
            # target location
            elif self.current_mode == 3:
                # remove
                if ctrl_held:
                    self.parent.world.map.remove_target(*end_pos)
                # add
                else:
                    self.parent.world.map.add_target(*end_pos)
            # sentry tower
            elif self.current_mode == 4:
                # remove
                if ctrl_held:
                    self.parent.world.map.remove_tower(*end_pos)
                # add
                else:
                    self.parent.world.map.add_tower(*end_pos)

            # and reset start pos for next input
            self.start_pos = None
            # invalidate map VBO to force rebuild
            self.parent.mapview.tiles_vbo = None
            self.parent.mapview.map_items = None
            return True
