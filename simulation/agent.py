from typing import NewType, List
from abc import ABCMeta, abstractmethod
import math
from .communication import Message, MarkerType, NoiseEvent
from .util import Position
from . import world

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    next_ID = 1

    @classmethod
    def generate_new_ID(cls):
        ID = Agent.next_ID
        Agent.next_ID += 1
        return ID

    def __init__(self, location: Position, heading: float=0, color=None) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees (counterclockwise), where 0 is up, -90 is left and 90 is right
        """
        self.ID = Agent.generate_new_ID()

        # pretty colours!
        self.color = color if color else (1.0, 1.0, 1.0)

        # movement stuff
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
        """ Turn relative to current heading """
        self._turn_target = self.heading + target_angle

    def turn_to(self, target_angle: float):
        """ Turn towards absolute heading """
        self._turn_target = target_angle

    def move(self, distance):
        self._move_target = distance

    def turn_remaining(self) -> float:
        return self._turn_target - self.heading

    def move_remaining(self) -> float:
        return self._move_target

    def _process_movement(self):
        """ Executes the last movement command """
        # process turning
        if not math.isclose(self._turn_target, self.heading):
            remaining = self.turn_remaining()
            self.heading += math.copysign(min(world.World.TIME_PER_TICK * self.turn_speed, abs(remaining)), remaining)
        # process walking/running
        if self._move_target > 0:
            distance = math.copysign(min(world.World.TIME_PER_TICK * self.move_speed, abs(self._move_target)), self._move_target)
            self.location.move(distance, angle=self.heading)
            self._move_target -= distance

    def tick(self, noises: List[NoiseEvent], messages: List[Message]):
        for noise in noises:
            self.on_noise(noise)

        for message in messages:
            self.on_message(message)

        self.on_tick()

        self._process_movement()

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def on_noise(self, noise: NoiseEvent) -> None:
        """ Noise handler, will be called before `on_tick` """
        pass

    @abstractmethod
    def on_message(self, message: Message) -> None:
        """ Message handler, will be called before `on_tick` """
        pass

    @abstractmethod
    def on_tick(self) -> None:
        """ Agent logic goes here """
        pass


# TODO: implement sentry tower
class GuardAgent(Agent):
    def __init__(self, location: Position, heading: float=0, color=None) -> None:
        color = color if color else (0.0, 1.0, 0.0)
        super().__init__(location, heading, color)
        self.view_range: float = 6.0


# TODO: implement sprinting
class IntruderAgent(Agent):
    def __init__(self, location: Position, heading: float=0, color=None) -> None:
        color = color if color else (1.0, 0.0, 0.0)
        super().__init__(location, heading, color)
        self.view_range: float = 7.5
