from typing import Dict, Callable

import arcade

from . import renderer


class Console(renderer.WindowComponent):
    def setup(self):
        # console
        self.open = False
        self.text = ""
        self.out = ""

        # command list
        self.commands: Dict[str, Callable] = {}

        self.register_command('help', lambda _: 'Available commands:\n - ' + '\n - '.join((name for name, func in self.commands.items())))

    def register_command(self, name: str, func: Callable):
        self.commands[name] = func

    def println(self, line):
        self.out += line + "\n"

    def run_command(self, command: str):
        split = command.split(' ', maxsplit=1)
        if len(split) > 1:
            name, args = split
        else:
            name = split[0]
            args = ''

        args = args.split(' ')
        # check if function exists
        if name in self.commands:
            # call function and get output
            try:
                output = self.commands[name](*args)
            except Exception as e:
                print('console error:', repr(e))
                output = "Command cound not be executed"
                # raise e
            # and print output
            if output:
                self.println(f"{output}")
        else:
            self.println(f"Unrecognised command: {name}")

    def on_draw(self):
        if self.open:
            prompt = f"CONSOLE >> {self.text}_"

            lines_out = self.out.split('\n')

            arcade.draw_lrtb_rectangle_filled(
                0, 8 + 12 * 32 + 6,
                self.parent.SCREEN_HEIGHT - 24 - 18 * 1 + 4, self.parent.SCREEN_HEIGHT - 24 - 18 * 1 - 14 * (len(lines_out) + 1) - 12,
                color=(0, 0, 0, 192)
            )

            arcade.draw_text(prompt, 8, self.parent.SCREEN_HEIGHT - 24 - 18 * 2, arcade.color.WHITE, 16)
            for num, line in enumerate(lines_out):
                arcade.draw_text(f">> {line}", 8, self.parent.SCREEN_HEIGHT - 24 - 18 * 3 - 14 * (num), arcade.color.WHITE, 12)

    def on_key_press(self, key, modifiers):
        # toggle console
        if key == arcade.key.TAB:
            self.open = not self.open
            # reset the console
            if not self.open:
                self.open = False
                self.text = ""
                self.out = ""
            return True

        # typing and stuff
        if self.open:
            if (
                (key >= arcade.key.A and key <= arcade.key.Z) or
                (key >= arcade.key.KEY_0 and key <= arcade.key.KEY_9) or
                key == arcade.key.SPACE or
                key == arcade.key.UNDERSCORE
            ):
                self.text += chr(key)
            elif key == arcade.key.ENTER:
                self.run_command(self.text)
                self.text = ""
            elif key == arcade.key.BACKSPACE:
                self.text = self.text[0:-1]
            else:
                return False
            return True
