# based on code taken from: https://www.redblobgames.com/pathfinding/a-star/implementation.html

from abc import ABCMeta, abstractmethod
import heapq


class Graph(metaclass=ABCMeta):
    """Interface that graphs must implement so A* can traverse them"""

    @abstractmethod
    def neighbors(self, node):
        pass

    @abstractmethod
    def cost(self, from_node, to_node):
        pass


class PriorityQueue():
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def dijkstra_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    try:
        while current != start:
            path.append(current)
            current = came_from[current]
    except KeyError as e:
        # no path found
        return None

    path.append(start)  # optional
    path.reverse()  # optional
    return path


def a_star_search(graph, start, goal, heuristic):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                h = heuristic(goal, next)
                # make priority a tuple to break ties based on h if the total cost + h is the same
                priority = (new_cost + h, h)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far
