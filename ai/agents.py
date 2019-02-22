from simulation.util import Position
from simulation.communication import Message, MarkerType, NoiseEvent
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def __init__(self, location: Position, heading: float=0) -> None:
        super().__init__(location, heading)

    def on_noise(self, noise: NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    def on_message(self, message: Message) -> None:
        """ Message handler, will be called before `on_tick` """
        ...

    def on_tick(self) -> None:
        """ Agent logic goes here """
        ...
