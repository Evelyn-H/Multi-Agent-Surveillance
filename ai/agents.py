from simulation.util import Position
from simulation.communication import Message, MarkerType, NoiseEvent
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def setup(self):
        ...

    def on_noise(self, noise: NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: Message) -> None:
        """ Message handler, will be called before `on_tick` """
        ...

    def on_tick(self) -> None:
        """ Agent logic goes here """
        # simple square patrol
        if self.turn_remaining() == 0 and self.move_remaining() == 0:
            self.turn(90)
            self.move(20)
