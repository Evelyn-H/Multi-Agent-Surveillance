import random

from simulation import world
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def setup(self):
        """ Agent setup """
        self.turn(45)

    def on_noise(self, noise: world.NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        print(f'agent {message.target} received message from agent {message.source} on tick {self.current_time}: {message.message}')

    def on_collide(self) -> None:
        """ Collision handler """
        self.turn(20 * (1 if random.random() < 0.5 else -1))
        self.move(5)

    def on_tick(self) -> None:
        """ Agent logic goes here """
        # simple square patrol
        if self.turn_remaining == 0 and self.move_remaining == 0:
            self.turn(90)
            self.move(20)
            if self.ID != 1:
                self.send_message(1, "I just turned!")


class PathfindingGuard(GuardAgent):
    def setup(self):
        """ Agent setup """
        self.path = None

    def on_noise(self, noise: world.NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """

    def on_collide(self) -> None:
        """ Collision handler """
        # recalculate path
        if self.turn_remaining == 0 and self.move_remaining == 0:
            self.path = self.map.find_path(self.location, (100, 100))

    def on_tick(self) -> None:
        """ Agent logic goes here """
        if not self.path:
            self.path = self.map.find_path(self.location, (100, 100))

        if self.move_remaining == 0:
            next_pos = self.path[0]
            self.turn_to_point(next_pos)
            # if self.turn_remaining == 0:
            self.move((next_pos - self.location).length)
            self.path = self.path[1:]
