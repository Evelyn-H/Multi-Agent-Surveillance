from typing import Dict, List
import math
import random
from enum import Enum
import numpy as np
import vectormath as vmath
import json_tricks as jt

import simulation.logger
import simulation.vision
from .environment import Map
from .agent import Agent, AgentID, GuardAgent, IntruderAgent
from .util import Position


class World:
    """
    Main class that manages the whole simulation
    """

    # amount of times `on_tick` is called per second
    TICK_RATE = 20
    # time elapsed for each call to `on_tick`
    TIME_PER_TICK = 1.0 / TICK_RATE

    # for generating agent ID's
    next_agent_ID: AgentID = 1

    def __init__(self, map: Map):
        self.map: Map = map
        self.agents: Dict[AgentID, Agent] = dict()

        self.noises: List['NoiseEvent'] = []
        # to keep track of past noise events
        self.old_noises: List['NoiseEvent'] = []

        # to keep track of how many ticks have passed:
        self.time_ticks = 0

        # bit hacky, but eh
        # reset agent ID counter
        World.next_agent_ID = 1

    @classmethod
    def generate_agent_ID(cls) -> AgentID:
        ID = cls.next_agent_ID
        cls.next_agent_ID += 1
        return ID

    def save_map(self, name) -> None:
        data = {'map': self.map.to_dict()}

        filename = f'saves/{name}.map.json'
        with open(filename, mode='w') as file:
            jt.dump(data, file, indent=4)

    def save_agents(self, name) -> None:
        data = {'agents': [agent.__class__.__name__ for ID, agent in self.agents.items()]}

        filename = f'saves/{name}.agents.json'
        with open(filename, mode='w') as file:
            jt.dump(data, file, indent=4)

    def to_file(self, name, save_agents=True) -> None:
        self.save_map(name)
        if save_agents:
            self.save_agents(name)

    @classmethod
    def load_map(cls, name) -> 'World':
        filename = f'saves/{name}.map.json'
        with open(filename, mode='r') as file:
            data = jt.load(file)

        m = Map.from_dict(data['map'])
        return World(m)

    def load_agents(self, name) -> None:
        filename = f'saves/{name}.agents.json'
        with open(filename, mode='r') as file:
            data = jt.load(file)

        # add agents
        import importlib
        for agent_name in data['agents']:
            # get class by string
            agent_class = getattr(importlib.import_module("ai.agents"), agent_name)
            # and add it to the world
            self.add_agent(agent_class)

    @classmethod
    def from_file(cls, name, load_agents=True) -> 'World':
        world = cls.load_map(name)
        if load_agents:
            world.load_agents(name)
        return world

    def add_agent(self, agent_type):
        agent = agent_type()
        self.agents[agent.ID] = agent

    def add_noise(self, noise: 'NoiseEvent'):
        noise.time = self.time_ticks
        self.noises.append(noise)

    @property
    def guards(self):
        return {ID: agent for ID, agent in self.agents.items() if isinstance(agent, GuardAgent)}

    @property
    def intruders(self):
        return {ID: agent for ID, agent in self.agents.items() if isinstance(agent, IntruderAgent)}

    def transmit_message(self, message):
        self.agents[message.target]._message_queue_in.append(message)

    def _collision_check(self):
        def collision_point(x, y):
            x, y = int(math.floor(x)), int(math.floor(y))
            if self.map.is_wall(x, y):
                return vmath.Vector2(x, y) + (0.5, 0.5)
            else:
                return None

        def circle_collision(x, y, r=0.5):
            x, y = int(math.floor(x)), int(math.floor(y))
            if self.map.is_wall(x, y):
                center = vmath.Vector2(x, y) + (0.5, 0.5)
                if (agent.location - center).length < (r + width / 2):
                    return center + (agent.location - center).as_length(r + width / 2)

        for ID, agent in self.agents.items():
            # do a quick bounds check first so they stay on the map
            if agent.location.x < 0:
                agent.location.x = 0
            if agent.location.y < 0:
                agent.location.y = 0
            if agent.location.x >= self.map.width:
                agent.location.x = self.map.width - 0.01
            if agent.location.y >= self.map.height:
                agent.location.y = self.map.height - 0.01

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

    def _capture_check(self) -> bool:
        """
        return: Whether or not all the intruders have been captured
        """
        # see if any intruders will be captured now
        for ID_intruder, intruder in self.intruders.items():
            for ID_guard, guard in self.guards.items():
                guard_x, guard_y = int(guard.location.x), int(guard.location.y)
                intruder_x, intruder_y = int(intruder.location.x), int(intruder.location.y)

                if (intruder.location - guard.location).length <= 0.5 and \
                        guard.map._is_tile_visible_from(guard_x, guard_y, intruder_x, intruder_y):
                    intruder.on_captured()

        # check if all intruders are captured
        return all((intruder.is_captured for ID, intruder in self.intruders.items()))

    def _target_check(self) -> bool:
        """
        return: Whether or not all of the intruders have reached the target
        """
        # see if any intruders will reach the target now
        for ID_intruder, intruder in self.intruders.items():
            if (intruder.location - intruder.target).length < 1: 
                if intruder.ticks_in_target == 0.0:
                    if (intruder.ticks_since_target * self.TIME_PER_TICK) >= 3.0 or \
                            intruder.times_visited_target == 0.0:
                        intruder.times_visited_target += 1.0

                    intruder.ticks_since_target = 0.0

                intruder.ticks_in_target += 1.0

            else:
                if intruder.ticks_in_target > 0.0:
                    intruder.ticks_since_target += 1.0
                    intruder.ticks_in_target = 0.0

                elif intruder.ticks_since_target > 0.0:
                    intruder.ticks_since_target += 1.0

            # win type 1: the intruder has been in the target area for 3 seconds
            if (intruder.ticks_in_target * self.TIME_PER_TICK) >= 3.0:
                intruder.on_reached_target()

            # win type 2: the intruder has visited the target area twice with at least 3 seconds inbetween
            elif intruder.times_visited_target >= 2.0:
                intruder.on_reached_target()

        # check if any intruders has reached the target
        return any((intruder.reached_target for ID, intruder in self.intruders.items()))

    def setup(self):
        patrolling_areas = self.create_patrolling_areas()
        idx_pa = 0
        idx_st = 0

        for ID, agent in self.agents.items():
            agent.setup(world=self)
            if agent.type == 'PatrollingGuard':
                agent.setup_patrol_route(patrolling_areas[idx_pa % len(patrolling_areas)])
                idx_pa += 1
            elif agent.type == 'CameraGuard':
                agent.place_in_tower(self.map.towers[idx_st])
                idx_st += 1

    def create_patrolling_areas(self):
        patrolling_guards = []
        patrolling_areas = []

        for ID, agent in self.agents.items():
            if agent.type == 'PatrollingGuard':
                patrolling_guards.append(agent)

        x_cuts = int(np.floor(np.sqrt(len(patrolling_guards))))
        y_cuts = x_cuts
        if x_cuts ** 2 < len(patrolling_guards):
            if x_cuts ** 2 < (x_cuts + 1) * x_cuts <= len(patrolling_guards):
                y_cuts = x_cuts + 1

        map_x_length, map_y_length = self.map.size
        offset = 1.5
        for x in range(x_cuts):
            for y in range(y_cuts):
                bl_corner = (x/x_cuts * map_x_length + offset, y/y_cuts * map_y_length + offset)
                tr_corner = ((x + 1)/x_cuts * map_x_length - offset, (y + 1)/y_cuts * map_y_length - offset)
                patrolling_areas.append((bl_corner, tr_corner))

        return patrolling_areas

    def tick(self) -> bool:
        """
        Execute one tick / frame
        return: Whether or not the simulation is finished
        """
        # reset noise list
        self.old_noises.extend(self.noises)
        self.noises = []
        # emit random noise
        self.emit_random_noise()

        # find all events for every agent and then run the agent code
        for ID, agent in self.agents.items():
            # check if we can see any other agents
            visible_agents = []
            for other_ID, other_agent in self.agents.items():
                if other_ID == ID:
                    continue
                d = other_agent.location - agent.location
                angle_diff = abs((-math.degrees(math.atan2(d.y, d.x)) + 90 - agent.heading + 180) % 360 - 180)

                if (d.length < other_agent.visibility_range and d.length <= agent.view_range and
                        angle_diff <= agent.view_angle) or d.length <= 1.0:
                    # create a new `AgentView` event
                    visible_agents.append(simulation.vision.AgentView(other_agent))

            perceived_noises = []
            for noise in self.noises:
                distance = (noise.location - agent.location).length
                if distance < noise.radius and noise.source != agent:
                    perceived_noises.append(PerceivedNoise(noise, agent))
            if perceived_noises:
                agent.log("perceived noises at", [noise.perceived_angle for noise in perceived_noises])

            # and run the agent code
            agent.tick(seen_agents=visible_agents, noises=perceived_noises)
        self._collision_check()

        all_captured = self._capture_check()

        if all_captured:
            # we're done
            simulation.logger.set_outcome(False, self.time_ticks * self.TIME_PER_TICK)
            print('The guards won!')
            return True

        all_reached_target = self._target_check()
        if all_reached_target:
            # we're done
            simulation.logger.set_outcome(True, self.time_ticks * self.TIME_PER_TICK)
            print('The intruders won!')
            return True

        # and up the counter
        self.time_ticks += 1

        if all_captured:
            # we're done
            return True
        # keep going...
        return False

    def emit_random_noise(self):
        # Rate parameter for one 25m^2 is 0.1 per minute -> divide by 60 to get the events per second
        # Scale up the rate parameter to map size 6*(map_size/25)*2=64 (amount of 25m^2 squares in the map)
        # I know, that the map size should be dynamic
        event_rate = 0.1
        random_events_per_second = (event_rate / 60) * (self.map.size[0] * self.map.size[1] / 25)
        chance_to_emit = random_events_per_second * self.TIME_PER_TICK
        if random.uniform(0, 1) < chance_to_emit:
            # emit an event here
            x = random.randint(0, self.map.size[0] - 1)
            y = random.randint(0, self.map.size[1] - 1)

            noise_event = NoiseEvent(Position(x, y))
            self.add_noise(noise_event)


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

    def __init__(self, location: Position, source=None, radius=5 / 2) -> None:
        self.time = 0
        self.location = location
        self.source = source
        self.radius = radius


class PerceivedNoise:
    """Similar to a NoiseEvent, but tied to an observer"""

    def __init__(self, noise: NoiseEvent, observer: Agent):
        self._noise = noise
        self._observer = observer

    @property
    def perceived_angle(self):
        """
        Calculates the perceived angle towards the noise from the perspective of the `target_pos`
        This also adds the uncertainty as described in the booklet
        """

        diff = self._noise.location - self._observer.location
        if diff.length > 1e-5:
            angle = vmath.Vector2(0, 1).angle(diff, unit='deg')
            true_angle = angle if diff.x > 0 else -angle
        else:
            true_angle = 0

        uncertainty = 10
        return random.gauss(true_angle, uncertainty)
