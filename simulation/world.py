from typing import List, Dict
import math
import random
from enum import Enum
import vectormath as vmath
import threading 
import datetime 


from .environment import Map
from .agent import Agent, AgentID
from .util import Position
from pickle import NONE


class World:
    """
    Main class that manages the whole simulation
    """

    # amount of times `on_tick` is called per second
    TICK_RATE = 20
    # time elapsed for each call to `on_tick`
    TIME_PER_TICK = 1.0 / TICK_RATE

    def __init__(self, map: Map):
        self.map: Map = map
        self.agents: Dict[AgentID, Agent] = dict()
        #Kick off random noises
        nextEmit = self.nextRandomNoiseTime()
        timer = threading.Timer(nextEmit*60, self.emitRandomNoise)
        timer.start() 

        # to keep track of how many ticks have passed:
        self.time = 0

        
    def add_agent(self, agent):
        agent._world = self
        self.agents[agent.ID] = agent

    def transmit_message(self, message):
        self.agents[message.target]._message_queue_in.append(message)

    def _collision_check(self):
        def collision_point(x, y):
            x, y = int(math.floor(x)), int(math.floor(y))
            if self.map.is_wall(x, y):
                return vmath.Vector2(x, y) + (0.5, 0.5)
            else:
                return None

        for ID, agent in self.agents.items():
            # get some values we'll need
            width = agent._width
            x = agent.location.x
            y = agent.location.y

            # offset vector for collision resolution
            push = vmath.Vector2(0, 0)

            # left
            collision = collision_point(x - width / 2, y)
            if collision is not None:
                push.x += collision.x + (0.5 + width / 2) - agent.location.x
                agent._has_collided |= True
            # right
            collision = collision_point(x + width / 2, y)
            if collision is not None:
                push.x += collision.x - (0.5 + width / 2) - agent.location.x
                agent._has_collided |= True
            # bottom
            collision = collision_point(x, y - width / 2)
            if collision is not None:
                push.y += collision.y + (0.5 + width / 2) - agent.location.y
                agent._has_collided |= True
            # top
            collision = collision_point(x, y + width / 2)
            if collision is not None:
                push.y += collision.y - (0.5 + width / 2) - agent.location.y
                agent._has_collided |= True

            # and apply resolution vector
            agent.location += push

            def circle_collision(x, y, r=0.5):
                x, y = int(math.floor(x)), int(math.floor(y))
                if self.map.is_wall(x, y):
                    center = vmath.Vector2(x, y) + (0.5, 0.5)
                    if (agent.location - center).length < (r + width / 2):
                        return center + (agent.location - center).as_length(r + width / 2)

            collision = circle_collision(x - width / 2, y - width / 2)
            if collision is not None:
                agent.location.x = collision.x
                agent.location.y = collision.y
                agent._has_collided |= True

            collision = circle_collision(x - width / 2, y + width / 2)
            if collision is not None:
                agent.location.x = collision.x
                agent.location.y = collision.y
                agent._has_collided |= True

            collision = circle_collision(x + width / 2, y - width / 2)
            if collision is not None:
                agent.location.x = collision.x
                agent.location.y = collision.y
                agent._has_collided |= True

            collision = circle_collision(x + width / 2, y + width / 2)
            if collision is not None:
                agent.location.x = collision.x
                agent.location.y = collision.y
                agent._has_collided |= True

    def setup(self):
        for ID, agent in self.agents.items():
            agent.setup()

    def tick(self):
        """ Execute one tick / frame """
        for ID, agent in self.agents.items():
            agent.tick(noises=[])
        self._collision_check()
        
        # and up the counter
        self.time += 1
        
    """Compute the next time of an noise event occuring"""
    def nextRandomNoiseTime(self):
        #Rate parameter for one 25m^2 is 0.1 
        #This can be scaled up to 200m^2 by assuming, that when a noise event 
        #is emitted the location is chosen uniformly random. 
        #Hence we can set the rate parameter to 0.1*(200/25)*2=64 (amount of 25m^2 squares in the map)
        rateParameter = 6.4;
        return -math.log(1.0 - random.random()) / rateParameter

    def emitRandomNoise(self, fps):
        #Rate parameter for one 25m^2 is 0.1 per minute -> divide by 60 to get the events per second
        #Scale up the rate parameter to map size 6*(map_size/25)*2=64 (amount of 25m^2 squares in the map)
        #I know, that the map size should be dynamic
        random_events_per_second = (0.1/60)*((self.map.size[0]/25)+(self.map.size[1]/25))
        chance_to_emit = random_events_per_second / fps
        if(random.uniform(0, 1) < chance_to_emit):
            #emit an event here
            posx = random.randint(0,200)
            posy = random.randint(0,200)
            print("Noise at (",posx,",",posy,")")


class MarkerType(Enum):
    """The different types of markers used for indirect communication"""
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    MAGENTA = 5


class Marker:
    def __init__(self, type: MarkerType, location: Position):
        self.type = type
        self.location = location


class Message:
    """Encapsulates a single message"""

    def __init__(self, source, target, message: str) -> None:
        self.source: 'AgentID' = source
        self.target: 'AgentID' = target
        self.message: str = message


class NoiseEvent:
    """ This should be a singleton (How do I do that in python)
        Encapsulates a single noise event"""
    def __init__(self, location: Position) -> None:
        self.location = location
        self.source = None
            
    def perceived_angle(self, target_pos: Position):
        """
        Calculates the perceived angle towards the noise from the perspective of the `target_pos`
        This also adds the uncertainty as described in the booklet
        """
        ...
