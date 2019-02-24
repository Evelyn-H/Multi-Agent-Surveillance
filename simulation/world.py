from typing import List, Dict
import math
import vectormath as vmath
from .map import Map
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

    def add_agent(self, agent):
        self.agents[agent.ID] = agent

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

    def setup(self):
        for ID, agent in self.agents.items():
            agent.setup()

    def tick(self):
        """ Execute one tick / frame """
        for ID, agent in self.agents.items():
            agent.tick(noises=[], messages=[])
        self._collision_check()
