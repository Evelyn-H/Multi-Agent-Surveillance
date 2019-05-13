from typing import List, Dict, Any


# to log any sort of events
events: List[Dict[Any, Any]] = []
# outcome of the simulation
intruder_win = False
guard_win = False
time_taken = None  # in seconds


def reset():
    global events, result, intruder_win, guard_win, time_taken
    events = []
    result = None
    intruder_win = False
    guard_win = False
    time_taken = None


def new_event(event: Dict[Any, Any]):
    global events
    events.append(event)


def set_outcome(_intruder_win: bool, _time_taken):
    global intruder_win, guard_win, time_taken
    intruder_win = _intruder_win
    guard_win = not intruder_win
    # in seconds
    time_taken = _time_taken
