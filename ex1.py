import ex1_check
import ex1_tests
import search
import utils
from types import SimpleNamespace


id = ["208173740"]

""" Rules """
BLANK = 0
WALL = 99
FLOOR = 98
AGENT = 1
GOAL = 2
LOCKED_DOORS = list(range(40, 50))  # [40,...,49]
PRESSURE_PLATES = list(range(20, 30))  # [20,...,29]
KEY_BLOCKS = list(range(10, 20))  # [10,...,19]

class PressurePlateProblem(search.Problem):
    """This class implements a pressure plate problem"""
    def __init__(self, initial):
        """Constructor needs the initial state.
        Sets the initial state and identifies the goal"""
        self.map = initial
        self.doors = set()
        self.goal_pos = None
        # Find agent and blocks
        agent_pos = None
        # Initialize blocks_pos as 10 elements with (-1,-1)
        blocks_pos = [(-1, -1)] * 10
        self.targets = {}
        
        for i, row in enumerate(self.map):
            for j, cell in enumerate(row):
                if cell == GOAL:
                    self.goal_pos = (j, i)
                if cell == AGENT:
                    agent_pos = (j, i)
                elif cell in KEY_BLOCKS:
                    # Insert just the (j,i) position at the index (cell-10)
                    blocks_pos[cell-10] = (j, i)
                elif cell in LOCKED_DOORS:
                    self.doors.add(cell)
                elif cell in PRESSURE_PLATES:
                    self.targets[cell] = (j, i)
        
        # Keep all 10 positions including unused ones
        initial_state = (agent_pos, tuple(blocks_pos))
        search.Problem.__init__(self, initial_state)
        
        # Pre-calculate corresponding plate for each key block
        self.block_to_plate = {i+10: i+20 for i in range(10)}
        # Pre-calculate corresponding key for each plate
        self.plate_to_block = {i+20: i+10 for i in range(10)}
        # Pre-calculate door to plate mapping
        self.door_to_plate = {i+40: i+20 for i in range(10)}

    def door_test(self, cell, blocks_pos):
        """
        Test if a door is open based on whether the corresponding pressure plate
        has the correct key block on it
        """
        if cell not in self.doors:
            return True
            
        plate = self.door_to_plate.get(cell)
        plate_pos = self.targets.get(plate)
        
        if not plate_pos:
            return False
            
        # Get the block that should be on this plate
        correct_block = self.plate_to_block.get(plate)
        
        # Check if the correct block is at the plate position
        if correct_block is not None and blocks_pos[correct_block-10] == plate_pos:
            return True
            
        return False

    def successor(self, state):
        """Generates the successor states returns [(action, achieved_states)]"""
        agent_pos, blocks_pos = state
        successors = []
        
        # Convert blocks_pos tuple to a dictionary for faster lookups
        block_dict = {}
        for i, pos in enumerate(blocks_pos):
            if pos != (-1, -1):
                block_dict[pos] = i + 10
                
        directions = [('U', (0, -1)), ('D', (0, 1)), ('L', (-1, 0)), ('R', (1, 0))]
        for action, (dx, dy) in directions:
            new_x = agent_pos[0] + dx
            new_y = agent_pos[1] + dy
            
            # Check boundaries
            if new_x < 0 or new_y < 0 or new_y >= len(self.map) or new_x >= len(self.map[0]):
                continue
                
            # Get cell type at the new position
            cell = self.map[new_y][new_x]
            
            # Check if cell is valid to move into
            if cell == WALL or cell in PRESSURE_PLATES:
                continue
                
            # Check if there's a locked door
            if cell in self.doors and not self.door_test(cell, blocks_pos):
                continue
                
            new_pos = (new_x, new_y)
            block_at_new_pos = block_dict.get(new_pos)
            
            # If there's a block at the new position
            if block_at_new_pos is not None:
                # Calculate where the block would move
                new_box_x = new_x + dx
                new_box_y = new_y + dy
                
                # Check boundaries for block's new position
                if new_box_x < 0 or new_box_y < 0 or new_box_y >= len(self.map) or new_box_x >= len(self.map[0]):
                    continue
                    
                # Get cell type at the block's new position
                cell1 = self.map[new_box_y][new_box_x]
                
                # Check if block can be moved to the new position
                if cell1 == WALL:
                    continue
                    
                # Check if there's already another block at the new position
                if (new_box_x, new_box_y) in block_dict:
                    continue
                    
                # Check if there's a locked door
                if cell1 in self.doors and not self.door_test(cell1, blocks_pos):
                    continue
                    
                # Check if the new position is a pressure plate
                if cell1 in PRESSURE_PLATES:
                    # Only allow the block to move onto its matching pressure plate
                    matching_plate = self.block_to_plate.get(block_at_new_pos)
                    if cell1 != matching_plate:
                        continue
                        
                # Don't move a block off its matching pressure plate
                matching_plate = self.block_to_plate.get(block_at_new_pos)
                if self.targets.get(matching_plate) == new_pos:
                    continue
                    
                # Create new state with moved block
                new_blocks_list = list(blocks_pos)
                new_blocks_list[block_at_new_pos-10] = (new_box_x, new_box_y)
                new_state = (new_pos, tuple(new_blocks_list))
                successors.append((action, new_state))
            else:
                # Simple agent movement with no block
                new_state = (new_pos, blocks_pos)
                successors.append((action, new_state))
                
        return successors
    
    def goal_test(self, state):
        """Test if the goal has been reached"""
        agent_pos, _ = state
        
        return agent_pos == self.goal_pos
    
    def h(self, node):
        """
        Heuristic function - Manhattan distance to goal
        with additional cost for doors that are not open
        """
        agent_pos, blocks_pos = node.state
        
        if self.goal_test(node.state):
            return 0
            
        # Basic Manhattan distance to goal
        base_distance = abs(agent_pos[0] - self.goal_pos[0]) + abs(agent_pos[1] - self.goal_pos[1])
        
        # Additional cost for each block not on its plate
        block_penalty = 0
        for i, block_pos in enumerate(blocks_pos):
            if block_pos == (-1, -1):
                continue
                
            block_id = i + 10
            matching_plate = self.block_to_plate.get(block_id)
            plate_pos = self.targets.get(matching_plate)
            
            if plate_pos and block_pos != plate_pos:
                # Calculate distance from block to its plate
                block_penalty += abs(block_pos[0] - plate_pos[0]) + abs(block_pos[1] - plate_pos[1])
        
        return base_distance + block_penalty
           
def create_pressure_plate_problem(game):
    return PressurePlateProblem(game)

if __name__ == '__main__':
    ex1_tests.main()