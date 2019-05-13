import numpy as np
from simulation.world import World
from simulation import logger


def load_world(files):
    names = files.split()
    if len(names) > 1:
        world = World.load_map(names[0])
        world.load_agents(names[1])
    else:
        world = World.from_file(names[0], load_agents=True)

    return world


def main():
    files = input('file name(s)? ')

    if not files:
        print('Please specify a file...')
        return

    total_runs = int(input('how many runs? '))
    intruder_wins = 0
    times = []

    for run in range(total_runs):
        print(f"\n ======== Run {run+1}  ======== ")

        # load world and agents
        world = load_world(files)

        # initialise the world
        world.setup()

        # and run until the end
        is_finished = False
        while not is_finished:
            is_finished = world.tick()

        # process results
        print(f"Won by: {'intruders' if logger.intruder_win else 'guards'}")
        print(f'Time taken: {logger.time_taken}')
        if logger.intruder_win:
            intruder_wins += 1
        times.append(logger.time_taken)

    # aggregate data
    print()
    print(f'Intruder win percentage: {intruder_wins / total_runs * 100}')
    print('Time taken (5-number summary):', np.percentile(times, [0, 25, 50, 75, 100]))


if __name__ == '__main__':
    main()
