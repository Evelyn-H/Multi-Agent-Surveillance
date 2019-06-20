import numpy as np
from simulation.world import World
from simulation import logger
import winsound
import pickle
from ai import agents


def load_world(files, ia, sa):
    names = files.split()
    if len(names) > 1:
        world = World.load_map(names[0])
        world.load_agents(names[1])
    else:
        world = World.from_file(names[0], load_agents=True)
        
    world.clear_agents()
    for i in range(1, ia+1):   
        world.add_agent(agents.PathfindingIntruder)

    for s in range(1, sa+1):
        world.add_agent(agents.PatrollingGuard)
    
    return world


def main():
    files = input('file name(s)? ')

    if not files:
        print('Please specify a file...')
        return

    total_runs = int(input('how many runs? '))
    intruder_wins = 0
    times = []
    for sa in range(1,6):
        for ia in range(1,6):
            intruder_wins = 0
            times = []
            for run in range(total_runs):
                print(f"\n ======== Run {run+1}  ======== ")
        
                # load world and agents
                world = load_world(files, ia, sa)
        
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
            print(str(sa) + ' Surveilance agents, ' + str(ia) + ' Intruders')
            print(f'Intruder win percentage: {intruder_wins / total_runs * 100}')
            print('Time taken (5-number summary):', np.percentile(times, [0, 25, 50, 75, 100]))
            logFile = open("log.txt", "a")
            logFile.write(str(sa) + ' Surveilance agents, ' + str(ia) + ' Intruders\n')
            logFile.write(f'Intruder win percentage: {intruder_wins / total_runs * 100}\n')
            logFile.write('Time taken (5-number summary):')
            logFile.write('[')
            logFile.write(', '.join(map(str, np.percentile(times, [0, 25, 50, 75, 100]))))
            logFile.write(']\n\n')
            logFile.close()             
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    while True:
        winsound.Beep(frequency, duration)

if __name__ == '__main__':
    main()
