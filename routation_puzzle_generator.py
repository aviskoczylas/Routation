import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from shapely.geometry import Point
import random
from collections import deque
#TODO
#1: implement a heuristic to decrease runtime
#then push to github
#: implement the solver in c++ to go even faster


show_each_step = 0
num_bad_holes = 3
num_red_pieces = 0
randomize_num_holes_and_pieces = True
min_sol_steps = 15
max_sol_steps = 99
num_rows = 3
num_cols = 3

write_to_file = 1
puzzle_num = 19  #only matters if writing to file
gears = [np.array([0,0,0,0]),
         np.array([1,0,0,0]),
         np.array([1,0,0,0]),
         np.array([1,0,0,0]),
         np.array([1,1,0,0]),
         np.array([0,1,1,0]),
         np.array([1,0,1,0]),
         np.array([1,1,1,0]),#this one is the real question mark
         np.array([1,1,1,0])]

#the board is defined in order up, right, down, left
directions = {
  "top": [0,2],
  "right": [1,3],
  "bottom": [2,0],
  "left": [3,1]
}

def plot_grid(grid, holes, num_moves, save):
    fig, ax = plt.subplots()
    radius = 0.6
    gear_data = []
    gear_colors = ["blue","orange"]
    gear_num = 1
    for row_idx, row in enumerate(grid):
        for col_idx, vals in enumerate(row):
            gear_data.append((Point(col_idx, -row_idx).buffer(radius), row_idx, col_idx, vals))
            if row_idx != 0 and col_idx != 0 and row_idx != grid.shape[0]-1 and col_idx != grid.shape[1]-1:
                plt.text(col_idx, -row_idx, gear_num, fontsize=14, horizontalalignment='center', verticalalignment='center')
                ax.add_patch(Circle((col_idx, -row_idx), radius-0.01, color = gear_colors[(row_idx+col_idx)%2]))
                gear_num += 1

    for i in range(len(gear_data)):
        for j in range(i + 1, len(gear_data)):
            if gear_data[i][1]+1==gear_data[j][1] and gear_data[i][2]==gear_data[j][2]:#if gear i is above gear j
                val_compare = directions["bottom"]
            elif gear_data[i][1]-1==gear_data[j][1] and gear_data[i][2]==gear_data[j][2]:#if gear i is below gear j
                val_compare = directions["top"]
            elif gear_data[i][2]+1==gear_data[j][2] and gear_data[i][1]==gear_data[j][1]:#if gear i is to the left of gear j
                val_compare = directions["right"]
            elif gear_data[i][2]-1==gear_data[j][2] and gear_data[i][1]==gear_data[j][1]:#if gear i is to the right of gear j
                val_compare = directions["left"]
            else:
                continue
            gear_i = gear_data[i][3][val_compare[0]]
            gear_j = gear_data[j][3][val_compare[1]]
            overlap = gear_data[i][0].intersection(gear_data[j][0])

            if gear_i == 0:
                assert(gear_j == 0 or gear_j == 1)
                if gear_j == 0:
                    color = "white"
                else:
                    color = gear_colors[(gear_data[j][1]+gear_data[j][2])%2]
            elif gear_i == 1:
                assert(gear_j == 0)
                color = gear_colors[(gear_data[i][1]+gear_data[i][2])%2]
            elif gear_i == 2:
                assert(gear_j == 2)
                color = "red"
            elif gear_i == 3:
                assert(gear_j == 3)
                color = "chartreuse"
            else:
                assert(False)
            for poly in [overlap]:
                x, y = poly.exterior.xy
                ax.fill(x, y, color=color)
    plot_holes(holes)
    plt.title(f"{num_moves} moves minimum", fontsize = 15)
    plt.tight_layout()
    plt.gca().tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    plt.xlim([0.25,3.75])
    plt.ylim([-3.75,-0.25])

    if save:
        plt.savefig(f"sample_puzzles/puzzle{puzzle_num}.png")
    plt.show()

def plot_holes(holes):
    for row, col, dir in holes:
        if (row, col, dir) == destination:
            color = 'chartreuse'
        else:
            color = 'k'
        if dir == "top":
            row-=0.5
        elif dir == "right":
            col+=0.5
        elif dir == "bottom":
            row+=0.5
        elif dir == "left":
            col-=0.5
        else:
            assert(False)
        plt.scatter(col, -row, s=100, color = color)

def display_move_history(move_history, grid):
    gear_nums = {}
    gear_num = 1
    for row in range(1,grid.shape[0]-1):
        for col in range(1,grid.shape[1]-1):
            gear_nums[(row, col)] = gear_num
            gear_num+=1
    for row, col, dir in move_history:
        if dir == 1:
            direction = "clockwise"
        elif dir == -1:
            direction = "counterclockwise"
        else:
            assert(False)
        gear_num = gear_nums[(row, col)]
        print(f"rotate gear {gear_num} {direction}.")
        if write_to_file:
            with open(f"sample_solutions/sol{puzzle_num}.txt", "a") as file:
                file.write(f"rotate gear {gear_num} {direction}.\n")


def generate_random_grid(num_rows, num_cols, gears):
    grid = np.zeros((num_rows+2, num_cols+2, 4))
    taken_spots = [(0,0)]
    spot = (0,0)
    for gear in gears:
        sampled_spots = []
        while spot in taken_spots or placement_invalid(grid, rotated_gear, spot):
            spot = (random.choice(range(1,num_rows+1)), random.choice(range(1,num_cols+1)))
            rotated_gear = np.roll(gear, random.choice([0,1,2,3]))
            if spot not in sampled_spots:
                sampled_spots.append(spot)
                if len(sampled_spots) >= num_rows*num_cols:
                    return generate_random_grid(num_rows, num_cols, gears)
            else:
                continue
        taken_spots.append(spot)
        grid[spot] = rotated_gear
    return grid

def placement_invalid(grid, gear, spot):
    row = spot[0]
    col = spot[1]
    if gear[0] ==1 and grid[row-1,col][2]==1:
            return True
    if gear[1] ==1 and grid[row,col+1][3]==1:
            return True
    if gear[2] ==1 and grid[row+1,col][0]==1:
            return True
    if gear[3] ==1 and grid[row,col-1][1]==1:
            return True
    return False

def add_pieces(grid, pieces):
    for row,col,dir in pieces:
        if (row,col,dir) == green:
            val = 3
        else:
            val = 2
        if dir == "top":
            grid[row][col][0] = val
            grid[row-1][col][2] = val
        elif dir == "right":
            grid[row][col][1] = val
            grid[row][col+1][3] = val
        elif dir == "bottom":
            grid[row][col][2] = val
            grid[row+1][col][0] = val
        elif dir == "left":
            grid[row][col][3] = val
            grid[row][col-1][1] = val
    return grid

def generate_piece_and_hole_locations(grid, num_bad_holes, num_red_pieces):
    valid_piece_spots = []
    for row in range(grid.shape[0] - 1):
        for col in range(grid.shape[1] - 1):
            if col != 0 and grid[row][col][2] == 0 and grid[row+1][col][0] == 0:
                valid_piece_spots.append((row, col, "bottom"))
            if row != 0 and grid[row][col][1] == 0 and grid[row][col+1][3] == 0:
                valid_piece_spots.append((row, col, "right"))
    if len(valid_piece_spots) < num_red_pieces + 1:
        return (None, None)#not enough open spots
    chosen_piece_spots = random.sample(valid_piece_spots, num_red_pieces + 1)
    red_pieces = chosen_piece_spots[:-1]
    global green
    green = chosen_piece_spots[-1]
    pieces = red_pieces + [green]
    valid_hole_spots = []
    for row in range(grid.shape[0] - 1):
        for col in range(grid.shape[1] - 1):
            if col != 0 and (row,col,"bottom") not in chosen_piece_spots:
                valid_hole_spots.append((row, col, "bottom"))
            if row != 0 and (row,col,"right") not in chosen_piece_spots:
                valid_hole_spots.append((row, col, "right"))
    chosen_hole_spots = random.sample(valid_hole_spots, num_bad_holes + 1)
    bad_holes = chosen_hole_spots[:-1]
    global destination
    destination = chosen_hole_spots[-1]
    holes = bad_holes + [destination]

    grid = add_pieces(grid, pieces)
    return (grid, holes)

def rotate_gear(grid, row, col, direction):
    #direction = 1 is clockwise, -1 is counterclockwise
    #first, turn the gear itself
    assert(row != 0 and col != 0 and row != grid.shape[0]-1 and col != grid.shape[1]-1)
    new_grid = np.copy(grid)
    vals = grid[row, col, :] 
    idx = (np.arange(len(vals)) - direction) % len(vals)
    new_grid[row, col, :] = vals[idx]
    #then, update all 4 surrounding gears.
    new_grid[row+1][col][0] = (0 if new_grid[row][col][2]==1 else new_grid[row][col][2]) #gear below
    new_grid[row][col-1][1] = (0 if new_grid[row][col][3]==1 else new_grid[row][col][3]) #gear at left
    new_grid[row-1][col][2] = (0 if new_grid[row][col][0]==1 else new_grid[row][col][0]) #gear above
    new_grid[row][col+1][3] = (0 if new_grid[row][col][1]==1 else new_grid[row][col][1]) #gear at right
    return new_grid

def gear_locked(grid, row, col):
    return (grid[row-1][col][2]==1 or
            grid[row][col+1][3]==1 or
            grid[row+1][col][0]==1 or
            grid[row][col-1][1]==1)

def solution_satisfied(grid, destination):
    if grid[destination[0]][destination[1]][directions[destination[2]][0]] == 3:
        return True
    return False

def piece_fell(grid, holes, destination):
    for hole in holes:
        val_at_hole = grid[hole[0]][hole[1]][directions[hole[2]][0]]
        if val_at_hole == 2:
            return True
        if val_at_hole == 3:
            if hole != destination:
                return True
    return False

def solve_grid(grid):
    q = deque([(grid, [])])    
    checked_grids = {grid.tobytes()}
    rotations = [1,-1]
    while q:
        current_grid, move_history = q.popleft()
        if solution_satisfied(current_grid, destination):
            return current_grid, move_history
        if len(move_history) >= max_sol_steps:
            continue
        for row in range(1, grid.shape[0] - 1):
            for col in range(1, grid.shape[1] - 1):
                if gear_locked(current_grid, row, col):
                    continue
                for direction in rotations:
                    new_grid = rotate_gear(current_grid, row, col, direction)
                    new_grid_bytes = new_grid.tobytes()
                    if (new_grid_bytes not in checked_grids) and not piece_fell(new_grid, holes, destination):
                        new_move_history = move_history + [(row, col, direction)]
                        checked_grids.add(new_grid_bytes)
                        q.append((new_grid, new_move_history))
    # if this point is reached, there is no valid solution.
    return (None, None)

solve_num = 0
while True:
    if randomize_num_holes_and_pieces:
        num_bad_holes = random.choice([0,1,2,3,4,5])
        num_red_pieces = random.choice([0,1,2,3,4,5])
    solve_num +=1
    grid = generate_random_grid(num_rows, num_cols, gears)
    grid, holes = generate_piece_and_hole_locations(grid, num_bad_holes, num_red_pieces)
    attempts = 0
    while grid is None:
        if attempts > 100:
            num_bad_holes = random.choice([0,1,2,3,4,5])
            num_red_pieces = random.choice([0,1,2,3,4,5])
        attempts +=1
        grid = generate_random_grid(num_rows, num_cols, gears)
        grid, holes = generate_piece_and_hole_locations(grid, num_bad_holes, num_red_pieces)
    if solution_satisfied(grid, destination):
        continue #ignore a grid that's already solved.

    #at this point, i have a valid grid with holes - solve it.
    print(f"Solve attempt {solve_num}")
    sol_grid, move_history = solve_grid(grid)
    if sol_grid is not None:
        if len(move_history) >= min_sol_steps:
            break   
        else:
            print(f"Solution was too short: only {len(move_history)} steps")
    else:
        print("No valid solution for this one")
print("grid = ",repr(grid))
print("holes = ",holes)
plot_grid(grid, holes, len(move_history), write_to_file)
if show_each_step:
    for row, col, direction in move_history:
        grid = rotate_gear(grid, row, col, direction)
        plot_grid(grid, holes, len(move_history), 0)
else:
    display_move_history(move_history, sol_grid)
    plot_grid(sol_grid, holes, len(move_history), 0)
print("move_history = ", move_history)

