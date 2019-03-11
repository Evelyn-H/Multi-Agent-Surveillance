from typing import Tuple
import random

from simulation import world
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def on_setup(self):
        """ Agent setup """
        self.turn(45)

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

    def on_noise(self, noise: world.NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        self.log(f'received message from agent {message.source} on tick {self.time_ticks}: {message.message}')

    def on_collide(self) -> None:
        """ Collision handler """
        self.turn(20 * (1 if random.random() < 0.5 else -1))
        self.move(5)

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        pass

    def on_tick(self) -> None:
        """ Agent logic goes here """
        # simple square patrol
        if self.turn_remaining == 0 and self.move_remaining == 0:
            self.turn(90)
            self.move(20)
            if self.ID != 1:
                self.send_message(1, "I just turned!")


class PathfindingGuard(GuardAgent):
    def on_setup(self):
        """ Agent setup """
        self.color = (1, 1, 0)  # yellow
        self.path = None

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

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

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        self.path = self.map.find_path(self.location, (100, 100))
        self.path = self.path and self.path[1:]  # remove starting node

    def on_tick(self) -> None:
        """ Agent logic goes here """

        if self.path and self.move_remaining == 0:
            next_pos = self.path[0]
            self.turn_to_point(next_pos)
            # self.log(self.location, self.path[0], self.path[1], self.turn_remaining)
            # if self.turn_remaining == 0:
            self.move((next_pos - self.location).length)
            self.path = self.path[1:]
