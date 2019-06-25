from typing import NewType, List, Tuple
from abc import ABCMeta, abstractmethod
import math
import vectormath as vmath
import random

from .util import Position
from . import vision
from . import world

# from profilehooks import profile

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    def __init__(self) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees, where 0 is up, -90 is left and 90 is right
        """
        # generate ID
        self.ID = world.World.generate_agent_ID()
        self.type = 'Agent'

        # placeholder reference to the `World` the agent is in
        self._world = None

        # pretty colours!
        self.color = (1.0, 1.0, 1.0)

        # movement stuff
        self.location: Position = None
        self.heading: float = 0
        self._last_heading: float = 0
        self.base_speed: float = 1.4
        self.move_speed: float = self.base_speed
        self.turn_speed: float = 180
        self.turn_speed_sprinting = 10
        self._can_sprint: bool = False
        self._sprint_rest_time = 10
        self._sprint_time = 5
        self.path = None
        self.is_captured = False
        
        # Guard agents interaction with towers
        self._in_tower = False
        self._interacting_with_tower = False
        self._tower_interaction_time = 3
        self._tower_start_time = 0

        # TODO: I would like to move these into the intruder agent since only the intruder should be able to sprint
        # Set the sprint cooldown to the tick that it started
        self._sprint_stop_time = -100000
        # Set the sprint time to the tick that the agent started sprinting
        self._sprint_start_time = 0

        # to keep track of movement commands and execute them in the background
        self._move_target: float = 0
        self._turn_target: float = 0

        # vision stuff
        self.map: vision.MapView = None
        self._last_tile: Tuple[int, int] = None
        self.tower_view_range: float = 15.0  # actually should be range between 2 and 15
        self.view_range: float = 6.0
        self.current_view_range: float = self.view_range
        self.visibility_range: float = self.tower_view_range  # self.view_range
        self.decreased_visibility_range: float = 1.0
        self.base_view_angle: float = 45.0
        self.view_angle: float = self.base_view_angle
        self.tower_view_angle: float = 30.0
        self._dec_vision_time = 0
        self._fast_turning: bool = False
        self._turn_blindness_time = 0

        # sound perception stuff
        self._is_deaf = False

        # for collision detection
        self._width = 0.9
        self._has_collided = False

        # communication stuff
        self._message_queue_in = []
        self._message_queue_out = []

    def setup(self, world):
        self._world = world

        # init mapview
        self.map = vision.MapView(self._world.map)

        # pick entry point
        start = self.on_pick_start()
        self.location = Position(start[0], start[1])

        # to track when to update the vision
        self._last_tile = (int(self.location.x), int(self.location.y))
        self._last_heading = self.heading

        # and finally run the custom agent setup code
        self.on_setup()

    def log(self, *args):
        print(f"logging (agent {self.ID}):", *args)

    def send_message(self, target: AgentID, message: str) -> None:
        if target == self.ID:
            print("Agent Warning: Can't send message to yourself")
            return

        self._message_queue_out.append(
            world.Message(self.ID, target, message)
        )

    def leave_marker(self, type: 'world.MarkerType') -> None:
        ...

    @property
    def time_ticks(self):
        return self._world.time_ticks

    @property
    def time_seconds(self):
        return self._world.time_ticks * self._world.TIME_PER_TICK

    def turn(self, target_angle: float):
        """ Turn relative to current heading """
        self._turn_target = self.heading + target_angle

    def turn_to(self, target_angle: float):
        """ Turn towards absolute heading """
        self._turn_target = target_angle

    def turn_to_point(self, target: vmath.Vector2):
        diff = target - self.location
        if diff.length > 1e-5:
            # try:
            angle = vmath.Vector2(0, 1).angle(diff, unit='deg')
            self.turn_to(angle if diff.x > 0 else -angle)
        # except ZeroDivisionError as e:
        else:
            self.turn_to(self.heading)

    def set_movement_speed(self, speed):
        """ Set the movement speed of the agent and ensure, that it is within the allowed bounds"""
        # return true if still
        # Agent has to rest for 10 seconds after sprinting
        if speed < 0 or speed > 3:
            raise Exception("Tried to set movement speed out of bounds: " + speed + " for agent " + self)

        if self.is_resting:
            return

        if self.move_speed > self.base_speed >= speed:
            self._sprint_stop_time = self._world.time_ticks
            self.log("Stop Sprinting and start resting")

        if not self.is_sprinting and speed > self.base_speed:
            self._sprint_start_time = self._world.time_ticks
            self.log("Start sprinting")

        self.move_speed = speed
        # self._world tick rate and time per tick as a sprint time counter

    @property
    def is_resting(self):
        return (self._world.time_ticks - self._sprint_stop_time) < self._sprint_rest_time/self._world.TIME_PER_TICK

    @property
    def is_sprinting(self):
        return self.move_speed > self.base_speed

    # This should be called in each update of the agent method
    def _update_sprint(self):
        if not self._can_sprint:
            return

        if self.is_sprinting and (self._world.time_ticks - self._sprint_start_time) > self._sprint_time/self._world.TIME_PER_TICK:
            self._sprint_stop_time = self._world.time_ticks
            
        # Check, if the agent has rested for enough -> ensure, that rests when if can't sprint
        if self.is_resting:
            self.move_speed = 0
        
    def _update_tower_interaction(self):
        if not self._interacting_with_tower:
            # do nothing if we're not interacting
            return

        # is the interaction time over?
        if (self._world.time_ticks - self._tower_start_time) < (self._tower_interaction_time / self._world.TIME_PER_TICK):
            # nope, keep waiting...
            return

        # done interacting!
        self._interacting_with_tower = False

        # and we're no longer deaf
        self._is_deaf = False

        # set move speed and vision accordingly
        if self._in_tower:
            self.log("I'm in the tower and no longer blind")
            self.current_view_range = self.tower_view_range
            ...
            self.move_speed = 0
        else:
            self.current_view_range = self.view_range
            ...
            self.move_speed = self.base_speed

    def enter_tower(self) -> bool:
        if self._in_tower or self._interacting_with_tower:
            return False

        viable_towers = [tower_pos for tower_pos in self.map._map.towers if self.in_tower_range(tower_pos)]

        if len(viable_towers) < 1:
            return False

        tower_pos = viable_towers[0]  # just pick the first viable tower

        self._in_tower = True
        self._interacting_with_tower = True
        self._tower_start_time = self._world.time_ticks

        self._is_deaf = True
        self.view_angle = self.tower_view_angle
        self.current_view_range = 0.0
        self.move_speed = 0

        # Put agent on tower
        self.location = tower_pos + (self._width / 2, self._width / 2)
        return True

    def leave_tower(self):
        if not self._in_tower or self._interacting_with_tower:
            return False

        self._in_tower = False
        self._interacting_with_tower = True
        self._tower_start_time = self._world.time_ticks

        self._is_deaf = True
        self.view_angle = self.base_view_angle
        self.current_view_range = 0.0
        self.move_speed = 0

        # # Move the agent out of the tower range in the direction that he is heading
        # self.move(self._width * 1.2)
        return True

    def in_tower_range(self, tower):
        if (tower - self.location).length < self._width * 1.1:
            return True
        return False

    def move(self, distance):
        self._move_target = distance

    @property
    def turn_remaining(self) -> float:
        a = self._turn_target - self.heading
        a = (a + 180) % 360 - 180
        return 0 if math.isclose(a, 0.0, abs_tol=1e-6) else a

    @property
    def move_remaining(self) -> float:
        return 0 if math.isclose(self._move_target, 0.0, abs_tol=1e-6) else self._move_target

    def _process_movement(self):
        """ Executes the last movement command """
        # don't think this is needed
        # if self._interacting_with_tower:
        #     return

        self._update_sprint()

        turn_speed = self.turn_speed
        if self.is_sprinting:
            turn_speed = self.turn_speed_sprinting

        # process turning
        if not math.isclose(self._turn_target, self.heading):
            remaining = self.turn_remaining
            self.heading += math.copysign(min(world.World.TIME_PER_TICK * turn_speed, abs(remaining)), remaining)
            self.heading = (self.heading + 180) % 360 - 180

        # process walking/running
        if self._move_target != 0:
            distance = math.copysign(min(world.World.TIME_PER_TICK * self.move_speed, abs(self._move_target)), self._move_target)
            self.location.move(distance, angle=self.heading)
            self._move_target -= distance
        self.make_noise()

    def _update_vision(self, force=False) -> bool:
        current_tile = (int(self.location.x), int(self.location.y))
        current_x, current_y = current_tile

        # get the speed at which the agent will turn
        current_turn_speed = 0
        if not math.isclose(self._turn_target, self.heading):
            current_turn_speed = min(self.turn_speed, abs(self.turn_remaining) / world.World.TIME_PER_TICK)

        # agent is blind while turning >45 degrees/second + 0.5 seconds afterwards
        if current_turn_speed > 45:
            self._fast_turning = True
            self.current_view_range = 0.0
        elif self._fast_turning:
            if self._turn_blindness_time * world.World.TIME_PER_TICK < 0.5:
                self.current_view_range = 0.0
                self._turn_blindness_time += 1
            else:
                self.current_view_range = self.view_range
                self._fast_turning = False
                self._turn_blindness_time = 0

        vision_modifier = self.map.get_vision_modifier(current_x, current_y)

        # check if agent is settled in decreased vision area
        if vision_modifier < 1.0 and self._move_target != 0:
            if self._dec_vision_time * world.World.TIME_PER_TICK > 10:
                self.visibility_range = self.decreased_visibility_range
            self._dec_vision_time += 1
        else:
            self._dec_vision_time = 0
            self.visibility_range = self.tower_view_range  # self.view_range

        if force or self._last_tile != current_tile or abs(self.heading - self._last_heading) > 5 or self._in_tower:
            self._last_tile = current_tile
            self.map._reveal_visible(current_x, current_y, self.current_view_range*vision_modifier,
                                     self.view_angle, self.heading, self._in_tower)
            self._last_heading = self.heading
            return True
        return False

    def tick(self, seen_agents: List['vision.AgentView'], noises: List['world.PerceivedNoise']):
        # tower interaction
        self._update_tower_interaction()

        # process vision
        has_updated = self._update_vision(force=(self.time_ticks == 0))
        if has_updated:
            self.on_vision_update()

        # noises
        if not self._is_deaf and len(noises) > 0:
            self.on_noise(noises)

        # messages
        for message in self._message_queue_in:
            self.on_message(message)
        # reset the queue after it's been processed
        self._message_queue_in = []

        # collision
        if self._has_collided:
            self.on_collide()

        # and logic
        self.on_tick(seen_agents)

        # reset collision tracking
        self._has_collided = False

        # and execute movement commands
        self._process_movement()

        # send all messages in the out queue
        for message in self._message_queue_out:
            self._world.transmit_message(message)
        self._message_queue_out = []

    @abstractmethod
    def on_setup(self) -> None:
        pass

    @abstractmethod
    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        pass

    @abstractmethod
    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        pass

    @abstractmethod
    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, that checks, if there a noise event occurs and where it is perceived  """
        pass

    @abstractmethod
    def on_message(self, message: 'world.Message') -> None:
        """ Message handler, will be called before `on_tick` """
        pass

    @abstractmethod
    def on_collide(self) -> None:
        """ Collision handler """
        pass

    @abstractmethod
    def on_tick(self, seen_agents: List['vision.AgentView']) -> None:
        """ Agent logic goes here """
        pass

    def make_noise(self):
        event_rate = 0.1
        random_events_per_second = (event_rate / 60) * (self._world.map.size[0] * self._world.map.size[1] / 25)
        chance_to_emit = random_events_per_second * self._world.TIME_PER_TICK
        radius = 0
        if self.move_speed > 0:
            radius = 1 / 2
        if self.move_speed > 0.5:
            radius = 3 / 2
        if self.move_speed > 1:
            radius = 5 / 2
        if self.move_speed > 2:
            radius = 10 / 2
        if random.uniform(0, 1) < chance_to_emit:
            noise_event = world.NoiseEvent(Position(self.location.x, self.location.y), self, radius)
            self._world.add_noise(noise_event)


class GuardAgent(Agent):
    def __init__(self) -> None:
        super().__init__()

        self.type = 'GuardAgent'
        self.color = (0, 20, 65)  # mint-green
        self.view_range: float = 6.0

        self.other_guards = List['vision.AgentView']
        self.other_patrol_guards = List['vision.AgentView']

    def setup(self, world):
        super().setup(world)
        self.other_guards = [vision.AgentView(guard) for ID, guard in self._world.guards.items() if not ID == self.ID]
        self.other_patrol_guards = [ID for ID, guard in self._world.guards.items() if not ID == self.ID and guard.type == 'PatrollingGuard']


# TODO: implement sprinting
class IntruderAgent(Agent):
    def __init__(self) -> None:
        super().__init__()

        self.type = 'IntruderAgent'
        self.color = (1, 155, 0)  # orange
        self.view_range: float = 7.5
#        self.target = Position(vmath.Vector2((1.5, 1.5)))  # must be .5 (center of tile)

        # are we captured yet?
        self.is_captured = False

        # has the target been reached?
        self.reached_target = False
        self._prev_reached_target = False
        self.times_visited_target = 0.0
        self.ticks_in_target = 0.0
        self.ticks_since_target = 0.0

        self._can_sprint = True
        
    @property
    def target(self):
        return self._world.map.targets[0]

    @abstractmethod
    def on_captured(self) -> None:
        """ Called once when the agent is captured """
        pass

    @abstractmethod
    def on_reached_target(self) -> None:
        """ Called once the agent has reached its target """
        pass
