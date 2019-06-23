from typing import Tuple, List
import random
import numpy as np
import vectormath as vmath

from simulation.util import Position
from simulation import world
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def __init__(self) -> None:
        super().__init__()
        self.type = 'SimpleGuard'

    def on_setup(self):
        """ Agent setup """
        self.turn(45)

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return 1 + random.random() * (self.map.width-2), 1 + random.random() * (self.map.height-2)

    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, will be called before `on_tick` """
        pass

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        self.log(f'received message from agent {message.source} on tick {self.time_ticks}: {message.message}')

    def on_collide(self) -> None:
        """ Collision handler """
        self.turn(20 * (1 if random.random() < 0.5 else -1))
        self.move(5)

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        pass

    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """
        # enter tower if possible
        if self.enter_tower():
            self.log("Entered a tower!")

        # only try to chase intruders, not other guards
        seen_intruders = [a for a in seen_agents if a.is_intruder]
        if seen_intruders:
            target = seen_intruders[0].location
            self.turn_to_point(target)
            self.move((target - self.location).length)
        else:
            # simple square patrol
            if self.turn_remaining == 0 and self.move_remaining == 0:
                self.turn(90)
                self.move(20)
                if self.ID != 1:
                    self.send_message(1, "I just turned!")


class PatrollingGuard(GuardAgent):
    def __init__(self) -> None:
        super().__init__()

        self.type = 'PatrollingGuard'
        self.color = (205, 95, 160)  # green

        self.patrol_route = None
        self.patrol_idx = 0
        self.patrol_point = None

        self.seen_intruder = None
        self.chase = False

    def on_setup(self):
        """ Agent setup """
        pass

    def setup_patrol_route(self, pa):
        self.patrol_route = [pa[0], pa[1], (pa[1][0], pa[0][1]), (pa[0][1], pa[1][0]), pa[0]]
        self.patrol_route = [Position(vmath.Vector2(patrol_point)) for patrol_point in self.patrol_route]
        print('Guard', self.ID, 'Patrolling guard, route:', self.patrol_route)

        self.patrol_point = self.patrol_route[self.patrol_idx]
        self.location = Position((pa[0][0] + np.abs(pa[0][0] - pa[1][0])*random.random(),
                                  pa[0][1] + np.abs(pa[0][1] - pa[1][1])*random.random()))

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return 1 + random.random() * (self.map.width-2), 1 + random.random() * (self.map.height-2)

    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, will be called before `on_tick` """
        self.turn_to(noises[0].perceived_angle)
        self.log(f"turned to: {noises[0].perceived_angle}")

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        if message.message[:9] == 'Intruder@':
            intruder = self._world.agents[int(message.message[9:])]
            if (self.location - intruder.location).length < 30:
                self.seen_intruder = intruder
        else:
            self.log(f'received message from agent {message.source} on tick {self.time_ticks}: {message.message}')

    def on_collide(self) -> None:
        """ Collision handler """
        pass

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        if (self.location - self.patrol_point).length <= 2:
            self.log('I\'ve reached corner point', self.patrol_idx, 'of my patrolling route.')
            self.patrol_idx = (self.patrol_idx + 1) % len(self.patrol_route)
            self.patrol_point = self.patrol_route[self.patrol_idx]

        target = self.patrol_point if not self.chase else self.seen_intruder.location
        self.path = self.map.find_path(self.location, target)
        self.path = self.path and self.path[1:]

    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """
        # enter tower if possible
        # if self.enter_tower():
        #     self.log("Entered a tower!")

        if self.seen_intruder is not None and self.seen_intruder.is_captured:
            self.seen_intruder = None

        # only try to chase intruders, not other guards
        seen_intruders = [a for a in seen_agents if a.is_intruder]

        self.chase = False
        if self.seen_intruder is not None and (self.location - self.seen_intruder.location).length > 0.05:
            self.chase = True

        for intruder in seen_intruders:
            if not intruder.is_captured:
                self.seen_intruder = intruder
                self.chase = True

        if self.path and self.move_remaining == 0:
            next_pos = self.path[0]
            self.turn_to_point(next_pos)
            self.move((next_pos - self.location).length)
            self.path = self.path[1:]


# TODO: add zoning for cameras (distribute cameras as evenly as possible over the map)
class CameraGuard(GuardAgent):
    def __init__(self) -> None:
        super().__init__()

        self.type = 'CameraGuard'
        self.color = (115, 55, 0)  # light-green
        self.seen_intruder = None
    
    def on_setup(self):
        """ Agent setup """
        self.base_speed = 0
        self.move_speed = 0
        # self.view_range: float = 15.0

        print('Guard', self.ID, 'Camera guard')

    def place_in_tower(self, location):
        self.location = location
        self.enter_tower()

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        pass

    def on_collide(self) -> None:
        """ Collision handler """
        pass

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return 1 + random.random() * (self.map.width-2), 1 + random.random() * (self.map.height-2)

    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, will be called before `on_tick` """
        self.turn_to(noises[0].perceived_angle)
        self.log(f"turned to: {noises[0].perceived_angle}")

    def on_vision_update(self) -> None:
        pass

    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """
        # Check, if the agent sees any intruders
        seen_intruders = [a for a in seen_agents if a.is_intruder]
        
        # Turn to an intruder as long as we see it and send a message to the other agents
        if seen_intruders:
            for intruder in seen_intruders:
                if not intruder.is_captured:
                    target = intruder.location
                    self.turn_to_point(target)
                    for guard_id in self.other_patrol_guards:
                        self.send_message(guard_id, 'Intruder@'+str(seen_intruders[0].ID))
                    break
        else:
            self.turn(10)  # turning faster will cause blindness

    def on_capture(self) -> None:
        """ Called once when the guard has captured an intruder """
        pass


class PathfindingIntruder(IntruderAgent):
    def __init__(self) -> None:
        super().__init__()
        self.type = 'PathfindingIntruder'

    def on_setup(self):
        """ Agent setup """

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        edge = random.randint(0,3)
        # Left wall
        if edge == 0:
            return 1, random.randint(1,self.map.height-1)
        # Right wall
        if edge == 1:
            return self.map.width-1, random.randint(1,self.map.height-1)
        # Left wall
        if edge == 2:
            return random.randint(1,self.map.width-1), self.map.height-1
        # Right wall
        if edge == 3:
            return random.randint(1,self.map.width-1), 1
                       
#        return 1 + random.random() * (self.map.width-2), 1 + random.random() * (self.map.height-2)

    def on_captured(self) -> None:
        """ Called once when the agent is captured """
        if not self.is_captured:
            self.is_captured = True
            self.log('I\'ve been captured... :(')

        self.move_speed = 0  # intruders that have been caught should stop moving

    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, will be called before `on_tick` """
        pass

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """

    def on_collide(self) -> None:
        """ Collision handler """
        pass

    def on_reached_target(self) -> None:
        """ Called once the intruder has reached its target """
        if not self.reached_target:
            self.reached_target = True
            self.log('I\'ve reached the target! :)')

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        self.path = self.map.find_path(self.location, self.target)
        self.path = self.path and self.path[1:]  # remove starting node


    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """
        if not self.path:
            # self.log('no path')
            pass

        # check if any guards in sight
        seen_guards = [a for a in seen_agents if a.is_guard]
        fleeing = True if seen_guards else False

        if not fleeing:
            if self.path and self.move_remaining == 0:
                next_pos = self.path[0]
                self.turn_to_point(next_pos)
                self.move((next_pos - self.location).length)
                self.path = self.path[1:]
        elif not self.is_captured:
            if self.move_remaining == 0:
                self.log('Fleeing '+str(self.heading)+' '+str(seen_guards[0].heading))
                d = 3
                a = 45

                if random.random() < 0.9 and self.heading != seen_guards[0].heading:
                    if self.heading < seen_guards[0].heading:
                        a = -a
                else:
                    a * ((-1)**random.randrange(2))

                self.turn(a)
                self.move(d)
