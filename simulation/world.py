from typing import List, Dict
import math
from enum import Enum
import vectormath as vmath

from .environment import Map
from .agent import Agent, AgentID
from .util import Position


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

        # to keep track of how many ticks have passed:
        self.time_ticks = 0

    def add_agent(self, agent_type):
        agent = agent_type()
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
            agent.setup(world=self)

    def tick(self):
        """ Execute one tick / frame """
        for ID, agent in self.agents.items():
            agent.tick(noises=[])
        self._collision_check()

        # and up the counter
        self.time_ticks += 1


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
    """Encapsulates a single noise event"""

    def __init__(self, location: Position) -> None:
        self._location = location

    def perceived_angle(self, target_pos: Position):
        """
        Calculates the perceived angle towards the noise from the perspective of the `target_pos`
        This also adds the uncertainty as described in the booklet
        """
        ...
