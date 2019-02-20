from typing import List
from .map import Map
from .agent import Agent


class World:
    """
    Main class that manages the whole simulation
    """

    def __init__(self, map: Map, agents: List[Agent]):
        self.map: Map = map
        self.agents: List[Agent] = agents
