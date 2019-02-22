from typing import NewType, List
from abc import ABCMeta, abstractmethod
from .communication import Message, MarkerType, NoiseEvent
from .util import Position

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    def __init__(self, location: Position, heading: float=0) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in radians (counterclockwise), where 0 is up
        """
        self.location: Position = location
        self.heading: float = heading
        self.move_speed: float = 1.4
        self.sprint_speed: float = 1.4
        self.view_range: float = 6.0
        self.view_angle: float = 45.0
        self.turn_speed: float = ...

        # private variables
        self._is_sprinting: bool = False
        self._move_target: float = 0
        self._turn_target: float = 0

    def send_message(self, target: AgentID, message: Message) -> None:
        ...

    def leave_marker(self, type: MarkerType) -> None:
        ...

    def turn(self, target_angle: float):
        self._turn_target = target_angle

    def move(self, distance, sprint: bool=False):
        if sprint:
            self._is_sprinting = True
        self._move_target = distance

    def _process_movement(self):
        """ Executes the last movement command """
        # process turning
        ...
        # process walking/running
        ...

    def tick(self, noises: List[NoiseEvent], messages: List[Message]):
        for noise in noises:
            self.on_noise(noise)

        for message in messages:
            self.on_message(message)

        self.on_tick()

        self._process_movement()

    @abstractmethod
    def on_noise(self, noise: NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        ...

    @abstractmethod
    def on_message(self, message: Message) -> None:
        """ Message handler, will be called before `on_tick` """
        ...

    @abstractmethod
    def on_tick(self) -> None:
        """ Agent logic goes here """
        ...
