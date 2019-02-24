from simulation.util import Position
from simulation.communication import Message, MarkerType, NoiseEvent
from simulation.agent import GuardAgent, IntruderAgent
import random

class SimpleGuard(GuardAgent):
    def setup(self):
        self.turn(45)

    def on_noise(self, noise: NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: Message) -> None:
        """ Message handler, will be called before `on_tick` """
        ...

    def on_collide(self) -> None:
        """ Collision handler """
        self.turn(20 * (1 if random.random() < 0.5 else -1))
        self.move(5)

    def on_tick(self) -> None:
        """ Agent logic goes here """
        # simple square patrol
        if self.turn_remaining() == 0 and self.move_remaining() == 0:
            self.turn(90)
            self.move(20)
