from typing import NewType, List, Tuple
from abc import ABCMeta, abstractmethod
import math
from .communication import Message, MarkerType, NoiseEvent
from .util import Position
from .vision import MapView
from . import world

# from profilehooks import profile

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    next_ID = 1

    @classmethod
    def generate_new_ID(cls):
        ID = Agent.next_ID
        Agent.next_ID += 1
        return ID

    def __init__(self, location: Position, heading: float=0, color=None, map=None) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees (counterclockwise), where 0 is up, -90 is left and 90 is right
        """
        # generate ID
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
        # to keep track of movement commands and execute them in the background
        self._move_target: float = 0
        self._turn_target: float = 0

        # vision stuff
        assert map is not None
        self.map: MapView = MapView(map)
        self._last_tile: Tuple[int, int] = (int(self.location.x), int(self.location.y))
        self._update_vision(force=True)

        # for collision detection
        self._width = 0.9
        self._has_collided = False

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
        if self._move_target != 0:
            distance = math.copysign(min(world.World.TIME_PER_TICK * self.move_speed, abs(self._move_target)), self._move_target)
            self.location.move(distance, angle=self.heading)
            self._move_target -= distance

    def _update_vision(self, force=False):
        current_tile = (int(self.location.x), int(self.location.y))
        if force or self._last_tile != current_tile:
            self._last_tile = current_tile
            self.map._reveal_circle(current_tile[0], current_tile[1], self.view_range)

    def tick(self, noises: List[NoiseEvent], messages: List[Message]):
        # process vision
        self._update_vision()

        # noises
        for noise in noises:
            self.on_noise(noise)

        # messages
        for message in messages:
            self.on_message(message)

        # collision
        if self._has_collided:
            self.on_collide()

        # and logic
        self.on_tick()

        # reset collision tracking
        self._has_collided = False
        # and execute movement commands
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
    def on_collide(self) -> None:
        """ Collision handler """
        pass

    @abstractmethod
    def on_tick(self) -> None:
        """ Agent logic goes here """
        pass


# TODO: implement sentry tower
class GuardAgent(Agent):
    def __init__(self, location: Position, heading: float=0, color=None, map: MapView=None) -> None:
        color = color if color else (0.0, 1.0, 0.0)
        super().__init__(location, heading, color, map)
        self.view_range: float = 6.0


# TODO: implement sprinting
class IntruderAgent(Agent):
    def __init__(self, location: Position, heading: float=0, color=None, map: MapView=None) -> None:
        color = color if color else (1.0, 0.0, 0.0)
        super().__init__(location, heading, color, map)
        self.view_range: float = 7.5
