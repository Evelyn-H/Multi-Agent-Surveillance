from typing import NewType

from .communication import MarkerType, Message
from .world import Noise


AgentID = NewType('AgentID', int)


class AgentSim:
    """Class to be subclassed by specific agent implementations."""
    

    def __init__(self) -> None:
        self._move_speed = 1.4
        self._view_range = 6.0
        self._view_angle = 45.0
        self.pos_x = 0;
        self.pos_y = 0;

    def getPosition(self):
        self.pos_x += 5;
        self.pos_y += 5;
        return self.pos_x, self.pos_y

    """
    def send_message(self, target: AgentID, message: Message) -> None:
        ...

    def leave_marker(self, type: MarkerType) -> None:
        ...

    # to be overridden:
    def on_noise(self, noise: Noise) -> None:
        ...

    def on_message(self, message: Message) -> None:
        ...

    def on_tick(self) -> None:
        ...
    """