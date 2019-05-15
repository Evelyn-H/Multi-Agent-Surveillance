from typing import Tuple, List
import random
import vectormath as vmath

from simulation.util import Position
from simulation import world
from simulation.agent import GuardAgent, IntruderAgent


class SimpleGuard(GuardAgent):
    def on_setup(self):
        """ Agent setup """
        self.turn(45)

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

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
        # only try to chase intruders, not other guards
        seen_intruders = [a for a in seen_agents if a.is_intruder]
        if seen_intruders:
            # chase!
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
    def make_patrol_route(self) -> List['Position']:
        width = [1.5, self.map.width - 1.5]
        height = [1.5, self.map.height - 1.5]
        corner_points = [Position(vmath.Vector2(a, b)) for a in width for b in height]
        patrol_route = []

        for i in range(3):
            route_point = corner_points.pop(random.randint(0, len(corner_points) - 1))
            patrol_route.append(route_point)
        return patrol_route

    def on_setup(self):
        """ Agent setup """
        self.color = (0, 1, 1)  # cyan
        self.path = None
        self.patrol_route = self.make_patrol_route()
        self.patrol_idx = 0
        self.patrol_point = self.patrol_route[self.patrol_idx]
        self.seen_intruder = None
        self.chase = False
        print('Guard', self.ID, 'Patrolling Route:', self.patrol_route)

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

    def on_noise(self, noises: List['world.PerceivedNoise']) -> None:
        """ Noise handler, will be called before `on_tick` """
        self.turn_to(noises[0].perceived_angle)
        self.log(f"turned to: {noises[0].perceived_angle}")

    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        self.log(f'received message from agent {message.source} on tick {self.time_ticks}: {message.message}')

    def on_collide(self) -> None:
        """ Collision handler """
        pass

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        if (self.location - self.patrol_point).length < 0.5:
            self.log('I\'ve reached corner point', self.patrol_idx, 'of my patrolling route.')
            self.patrol_idx = (self.patrol_idx + 1) % len(self.patrol_route)
            self.patrol_point = self.patrol_route[self.patrol_idx]

        target = self.patrol_point if not self.chase else self.seen_intruder

        self.path = self.map.find_path(self.location, target)
        self.path = self.path and self.path[1:]

    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """
        # enter tower if possible
        if self.enter_tower():
            self.log("entered a tower!")

        # only try to chase intruders, not other guards
        seen_intruders = [a for a in seen_agents if a.is_intruder]

        if seen_intruders:
            self.seen_intruder = seen_intruders[0].location
            self.chase = True
        else:
            self.chase = False

        if self.path and self.move_remaining == 0:
            next_pos = self.path[0]
            self.turn_to_point(next_pos)
            self.move((next_pos - self.location).length)
            self.path = self.path[1:]


class CameraGuard(GuardAgent):
    
    def on_setup(self):
        """ Agent setup """
        self.base_speed = 0
        self.move_speed = 0
        self.view_range: float = 12.0
                
        self.color = (1, 0, 0)  # cyan
        self.seen_intruder = None
        print('Guard', self.ID, 'Camera guard')
        
    def on_message(self, message: world.Message) -> None:
        """ Message handler, will be called before `on_tick` """
        pass

    def on_collide(self) -> None:
        """ Collision handler """
        pass

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

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
        
        #Turn to an intruder as long as we see him and send a message to the other agents
        if seen_intruders:
            self.log("Intruder seen")
            target = seen_intruders[0].location
            self.turn_to_point(target)            
            #Send a message of the intruders location
        
        #Turn by a bit at each turn unless we precieved noise
        else:
            self.turn(45)


class PathfindingIntruder(IntruderAgent):
    def on_setup(self):
        """ Agent setup """
        self.path = None

    def on_pick_start(self) -> Tuple[float, float]:
        """ Must return a valid starting position for the agent """
        return (random.random() * self.map.width, random.random() * self.map.height)

    def on_captured(self) -> None:
        """ Called once when the agent is captured """
        self.log('I\'ve been captured... :(')

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
        self.log('I\'ve reached the target! :)')
        # pass

    def on_vision_update(self) -> None:
        """ Called when vision is updated """
        self.path = self.map.find_path(self.location, self.target)
        self.path = self.path and self.path[1:]  # remove starting node

    def on_tick(self, seen_agents) -> None:
        """ Agent logic goes here """

        if not self.path:
            # self.log('no path')
            pass

#        try:
#            self.set_movement_speed(3)
#        except:
#            self.log("Resting")
#            pass

        if self.path and self.move_remaining == 0:
            next_pos = self.path[0]
            self.turn_to_point(next_pos)
            # self.log(self.location, self.path[0], self.path[1], self.turn_remaining)
            # if self.turn_remaining == 0:
            self.move((next_pos - self.location).length)
            self.path = self.path[1:]
