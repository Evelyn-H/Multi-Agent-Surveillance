from typing import NewType, List, Tuple
from abc import ABCMeta, abstractmethod
import math
import vectormath as vmath

from .util import Position
from . import vision
from . import world

# from profilehooks import profile

AgentID = NewType('AgentID', int)


class Agent(metaclass=ABCMeta):
    """Class to be subclassed by specific agent implementations."""

    next_ID: AgentID = 1

    @classmethod
    def generate_new_ID(cls) -> AgentID:
        ID: AgentID = Agent.next_ID
        Agent.next_ID += 1
        return ID

    def __init__(self) -> None:
        """
        `location`: (x, y) coordinates of the agent
        `heading`: heading of the agent in degrees, where 0 is up, -90 is left and 90 is right
        """
        # generate ID
        self.ID = Agent.generate_new_ID()

        # placeholder reference to the `World` the agent is in
        self._world = None

        # pretty colours!
        self.color = (1.0, 1.0, 1.0)

        # movement stuff
        self.location: Position = None
        self.heading: float = 0
        self.base_speed: float = 1.4
        self.move_speed: float = self.base_speed
        self.view_range: float = 6.0
        self.view_angle: float = 45.0
        self.turn_speed: float = 180
        self.turn_speed_sprinting = 10
        self._can_sprint: boolean = False
        self._sprint_rest_time = 10
        self._sprint_time = 5

        
        #I would like to move these into the intruder agent since only the intruder should be able to sprint
        #Set the sprint cooldown to the tick that it started
        self._sprint_stop_time = -100000
        #Set the sprint time to the tick that the agent started sprinting
        self._sprint_start_time = 0

        
        # to keep track of movement commands and execute them in the background
        self._move_target: float = 0
        self._turn_target: float = 0

        # vision stuff
        self.map: vision.MapView = None
        self._last_tile: Tuple[int, int] = None

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
        # start = (int(start.x), int(start.y))
        # # must be on the map
        # if start.x < 0 or start.x >= self.map.width or start.y < 0 or start.y >= self.map.height:
        #     raise Exception(f"Starting position for Agent {self.ID} is not on the map.")
        # # must be along the outer edge
        # if (start.x != 0 and start.x != self.map.width - 1) or (start.y != 0 and start.y != self.map.height - 1):
        #     raise Exception(f"Starting position for Agent {self.ID} is not along the outer edge.")
        # found a valid starting location!
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
        #return true if still 
        #Agent has to rest for 10 seconds after sprinting 
        if speed < 0 or speed > 3:
            raise Exception("Tried to set movement speed out of bounds: " + speed + " for agent " + self)
        
        if self.is_resting:
            return
        
        if self.move_speed > self.base_speed and speed <= self.base_speed:
            self._sprint_stop_time = self._world.time_ticks
            self.log("Stop Sprinting and start resting")
        
        if not self.is_sprinting and speed > self.base_speed:
            self._sprint_start_time = self._world.time_ticks
            self.log("Start sprinting")
            
        self.move_speed = speed
        #self._world tick rate and time per tick as a sprint time counter
        
    @property    
    def is_resting(self):
        return (self._world.time_ticks - self._sprint_stop_time) < self._sprint_rest_time/self._world.TIME_PER_TICK
    
    @property    
    def is_sprinting(self):
        return self.move_speed > self.base_speed
    
    #This should be called in each update of the agent method
    def _update_sprint(self):
        if not self._can_sprint:
            return 
        
        if self.is_sprinting and (self._world.time_ticks - self._sprint_start_time) > self._sprint_time/self._world.TIME_PER_TICK:
            self._sprint_stop_time = self._world.time_ticks        

        #Check, if the agent has rested for enough -> ensure, that rests when if can't sprint
        if self.is_resting:
            self.move_speed = 0
        
    
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

    def _update_vision(self, force=False) -> bool:
        current_tile = (int(self.location.x), int(self.location.y))
        if force or self._last_tile != current_tile or abs(self.heading - self._last_heading) > 5:
            self._last_tile = current_tile
            self.map._reveal_circle(current_tile[0], current_tile[1], self.view_range, self.view_angle, self.heading)
            self._last_heading = self.heading
            return True
        return False

    def tick(self, seen_agents: List['vision.AgentView'], noises: List['world.NoiseEvent']):
        # process vision
        has_updated = self._update_vision(force=(self.time_ticks == 0))
        if has_updated:
            self.on_vision_update()

        # noises
        for noise in noises:
            self.on_noise(noise)

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
    def on_noise(self, noise: 'world.NoiseEvent') -> None:
        """ Noise handler, will be called before `on_tick` """
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


# TODO: implement sentry tower
class GuardAgent(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.color = (0.0, 1.0, 0.0)
        self.view_range: float = 6.0

    def setup(self, world):
        super().setup(world)
        self.other_guards = [vision.AgentView(guard) for ID, guard in self._world.guards.items() if not ID == self.ID]


# TODO: implement sprinting
class IntruderAgent(Agent):
    def __init__(self) -> None:
        super().__init__()
        self.color = (1.0, 0.0, 0.0)
        self.view_range: float = 7.5
        
        # are we captured yet?
        self.is_captured = False
        self._prev_is_captured = False
        
        # has the target been reached
        self.reached_target = False
        self._prev_reached_target = False
        self.times_visited_target = 0.0
        self.ticks_in_target = 0.0
        self.ticks_since_target = 0.0

        self._can_sprint = True
        
    @abstractmethod
    def on_captured(self) -> None:
        """ Called once when the agent is captured """
        pass
    
    @abstractmethod
    def on_reached_target(self) -> None:
        """ Called once the agent has reached its target """
        pass

    def tick(self, seen_agents, noises):
        if self.is_captured:
            # make sure we only run the `on_captured` handler once
            if not self._prev_is_captured:
                self.on_captured()
                self._prev_is_captured = True

            # don't run any other agent code if we're captured
            return
        elif self.reached_target:
            # make sure we only run the `on_captured` handler once
            if not self._prev_reached_target:
                self.on_reached_target()
                self._prev_reached_target = True
            
            # don't run any other code - the intruder won
            return 
        else:
            # if we're not captured or have reached the target then just proceed as usual
            super().tick(seen_agents, noises)
