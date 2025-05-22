# PressurePlateProblem
In the ex1_check.py there will be the solve_problems function that will receive the problem matrix and which algorithm to use (either “gbfs” or “astar”). The problem matrix will be NxM tuple of tuples that each value will be an int that can be the following values: 
BLANK = 0
WALL = 99
FLOOR = 98 
AGENT = 1 
GOAL = 2
AGENT_ON_GOAL = 3 
LOCKED_DOORS = 40 ... 49 
PRESSED_PLATES = 30 ... 39 
PRESSURE_PLATES = 20 ... 29
KEY_BLOCKS = 10 ... 19
The agent has 4 possible actions:
•
Moving right – represented by “R” string
•
Moving left - represented by “L” string
•
Moving up - represented by “U” string
•
Moving down - represented by “D” string
Every action makes the agent move towards the desired direction if its applicable (either a floor tile or keyblock or an unlock door or the goal), otherwise it’s an invalid move and therefore won’t be checked.
Success: The agent finds a path to the goal. Failure: No possible path to the goal can be found or dead-end.
