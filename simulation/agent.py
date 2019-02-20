from typing import NewType
from .communication import Message, MarkerType, NoiseEvent


AgentID = NewType('AgentID', int)


class Agent:
    """Class to be subclassed by specific agent implementations."""

    def __init__(self) -> None:
        self.move_speed = 1.4
        self.view_range = 6.0
        self.view_angle = 45.0

    def send_message(self, target: AgentID, message: Message) -> None:
        ...

    def leave_marker(self, type: MarkerType) -> None:
        ...

    def move(self, direction: float, speed: float=None, sprint: bool=False):
        speed = speed if speed else self._move_speed
        ...

    # to be overridden:
    def on_noise(self, noise: NoiseEvent) -> None:
        ...

    def on_message(self, message: Message) -> None:
        ...

    def on_tick(self) -> None:
        ...
