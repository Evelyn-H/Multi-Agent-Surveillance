from typing import List, Dict
from .map import Map
from .agent import Agent, AgentID
from .util import Position


class World:
    """
    Main class that manages the whole simulation
    """

    def __init__(self, map: Map):
        self.map: Map = map
        self.agents: Dict[AgentID, Agent] = dict()

    def add_agent(self, agent):
        self.agents[agent.ID] = agent
