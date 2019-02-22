from typing import NewType, List
from abc import ABCMeta, abstractmethod
import math
from .communication import Message, MarkerType, NoiseEvent
from .util import Position

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    # amount of times `on_tick` is called per second
    TICK_RATE = 20
    # time elapsed for each call to `on_tick`
    TIME_PER_TICK = 1.0 / TICK_RATE

    def __init__(self, location: Position, heading: float=0) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees (counterclockwise), where 0 is up, -90 is left and 90 is right
        """
        self.location: Position = location
        self.heading: float = heading
        self.move_speed: float = 1.4
        self.sprint_speed: float = 3.0
        self.view_range: float = 6.0
        self.view_angle: float = 45.0
        self.turn_speed: float = 180.0

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
        if not math.isclose(self._turn_target, self.heading):
            remaining = self._turn_target - self.heading
            self.heading += math.copysign(min(Agent.TIME_PER_TICK * self.turn_speed, math.abs(remaining)), remaining)
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
