from typing import List, Dict
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
        def check_pos(x, y, width):
            return (
                self.map.is_wall(int(x - width / 2), int(y - width / 2)) or
                self.map.is_wall(int(x + width / 2), int(y - width / 2)) or
                self.map.is_wall(int(x - width / 2), int(y + width / 2)) or
                self.map.is_wall(int(x + width / 2), int(y + width / 2))
            )

        for ID, agent in self.agents.items():
            # is agent in a wall tile?
            width = 0.45
            while check_pos(agent.location.x, agent.location.y, width):
                agent.location.move(-0.01, agent.heading)

    def tick(self):
        """ Execute one tick / frame """
        for ID, agent in self.agents.items():
            agent.tick(noises=[], messages=[])
        self._collision_check()
