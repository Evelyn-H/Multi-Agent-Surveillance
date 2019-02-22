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

    next_ID = 1

    @classmethod
    def generate_new_ID(cls):
        ID = Agent.next_ID
        Agent.next_ID += 1
        return ID

    def __init__(self, location: Position, heading: float=0) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees (counterclockwise), where 0 is up, -90 is left and 90 is right
        """
        self.ID = Agent.generate_new_ID()

        self.location: Position = location
        self.heading: float = heading
        self.move_speed: float = 1.4
        self.view_range: float = 6.0
        self.view_angle: float = 45.0
        self.turn_speed: float = 180

        # private variables
        self._move_target: float = 0
        self._turn_target: float = 0

    def send_message(self, target: AgentID, message: Message) -> None:
        ...

    def leave_marker(self, type: MarkerType) -> None:
        ...

    def turn(self, target_angle: float):
        self._turn_target = target_angle

    def move(self, distance):
        self._move_target = distance

    def turn_remaining(self) -> float:
        return self._turn_target - self.heading

    def move_remaining(self) -> float:
        ...

    def _process_movement(self):
        """ Executes the last movement command """
        # process turning
        if not math.isclose(self._turn_target, self.heading):
            remaining = self.turn_remaining()
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


# TODO: implement sentry tower
class GuardAgent(Agent):
    def __init__(self, location: Position, heading: float=0) -> None:
        super().__init__(location, heading)
        self.view_range: float = 6.0


# TODO: implement sprinting
class IntruderAgent(Agent):
    def __init__(self, location: Position, heading: float=0) -> None:
        super().__init__(location, heading)
        self.view_range: float = 7.5
