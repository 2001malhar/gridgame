import time
from collections import Counter

import numpy as np
from gridgame import *

def refresh():
    pass

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.

##############################################################################################################################

setup(GUI=False, render_delay_sec=0.1, gs=10)

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board.

# -1 indicates an empty cell
# 0 indicates a cell colored in the first color (indigo by default)
# 1 indicates a cell colored in the second color (taupe by default)
# 2 indicates a cell colored in the third color (veridian by default)
# 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.

# Each shape is represented as a list of three elements: a) the brush type (number between 0-8),
# b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

# For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute('export')

# <-- workaround to prevent PyGame window from closing after execute() is called, for when GUI set to True. Uncomment to enable.
# print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)


####################################################
# Timing your code's execution for the leaderboard.
####################################################
start = time.time()  # <- do not modify this.

##########################################
# Write all your code in the area below.
##########################################

grid_size = grid.shape[0]
colors_available = len(colors)

def move_brush(target_x, target_y, current_pos):
    commands = []
    current_x, current_y = current_pos
    while current_y < target_y:
        commands.append('s')
        current_y += 1
    while current_y > target_y:
        commands.append('w')
        current_y -= 1
    while current_x < target_x:
        commands.append('d')
        current_x += 1
    while current_x > target_x:
        commands.append('a')
        current_x -= 1
    return commands


def get_next_position(grid):
    grid_size = grid.shape[0]
    for y in range(grid_size):
        for x in range(grid_size):
            if grid[y, x] == -1:
                return x, y
    return None


def all_diagonal_cells_colored(grid, x, y):
    diagonal_offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

    for dx, dy in diagonal_offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[1] and 0 <= ny < grid.shape[0]:
            if grid[ny, nx] == -1:
                return False
    return True


def conflict_minimizing_fill():
    global shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done

    flattened = [item for row in grid for item in row]
    filtered = [num for num in flattened if num != -1]
    frequency = Counter(filtered)
    top_two = frequency.most_common(2)

    if len(top_two) >= 2:
        first_max, second_max = top_two[0][0], top_two[1][0]
    elif len(top_two) == 1:
        first_max = top_two[0][0]
        second_max = None
    else:
        first_max = second_max = None

    print(f"Primary color (most frequent): {first_max}")
    print(f"Secondary color (second most frequent): {second_max}")

    shape_zero_placed = False
    colors_used = set()

    next_preferred_color = first_max if first_max is not None else 1
    second_preferred_color = second_max if second_max is not None else 2

    all_colors = [0, 1, 2, 3]

    preferred_colors = [next_preferred_color]
    if second_preferred_color is not None and second_preferred_color != next_preferred_color:
        preferred_colors.append(second_preferred_color)

    remaining_colors = [color for color in all_colors if
                        color not in preferred_colors]

    color_order = preferred_colors + remaining_colors

    print(f"Color order: {color_order}")

    placement_stack = []

    attempted_shapes = {}

    def is_color_conflict(shape, position, color_index):
        shape_height = len(shape)
        shape_width = len(shape[0])
        x_start, y_start = position
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    x = x_start + j
                    y = y_start + i
                    adjacent_cells = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    for dx, dy in adjacent_cells:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < grid.shape[1] and 0 <= ny < grid.shape[0]:
                            neighbor_color = grid[ny][nx]
                            if neighbor_color == color_index:
                                return True
        return False

    def attempt_place_shape(shape_idx):
        nonlocal shape_zero_placed, next_preferred_color, second_preferred_color
        global currentShapeIndex, currentColorIndex, shapePos, grid, placedShapes, done

        if currentShapeIndex != shape_idx:
            execute('switchshape')
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                'export')
            while currentShapeIndex != shape_idx:
                execute('switchshape')
                shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                    'export')

        if not canPlace(grid, shapes[shape_idx], shapePos):
            x, y = tuple(shapePos)
            if (x, y) not in attempted_shapes:
                attempted_shapes[(x, y)] = set()
            attempted_shapes[(x, y)].add(shape_idx)
            return False

        for color in color_order:
            if not is_color_conflict(shapes[shape_idx], shapePos, color):
                if currentColorIndex != color:
                    while currentColorIndex != color:
                        execute('switchcolor')
                        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                            'export')
                execute('place')
                colors_used.add(color)
                placement_stack.append((shape_idx, color))
                refresh()

                if checkGrid(grid):
                    score = (grid_size ** 2) / len(placedShapes) if len(
                        placedShapes) > 0 else 0
                    done = True
                    return True

                if len(preferred_colors) >= 2:
                    next_preferred_color, second_preferred_color = second_preferred_color, next_preferred_color
                elif len(preferred_colors) == 1:
                    next_preferred_color = next_preferred_color
                return True
        return False

    shape_groups = [
        [3, 4],
        [5, 6],
        [7, 8],
        [2, 1],
        [0]
    ]

    while not done:
        position = get_next_position(grid)
        if position is None:
            done = True
            break
        x, y = position

        if (x, y) in attempted_shapes and len(attempted_shapes[(x, y)]) == len(
            shapes):
            while placement_stack:
                last_shape, last_color = placement_stack.pop()
                execute('undo')
                shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                    'export')
            desired_shape_index = 2
            if currentShapeIndex != desired_shape_index:
                while currentShapeIndex != desired_shape_index:
                    execute('switchshape')
                    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                        'export')
                    if currentShapeIndex == desired_shape_index:
                        break

            next_preferred_color = first_max if first_max is not None else 1
            second_preferred_color = second_max if second_max is not None else 2

            preferred_colors = [next_preferred_color]
            if second_preferred_color is not None and second_preferred_color != next_preferred_color:
                preferred_colors.append(second_preferred_color)
            remaining_colors = [color for color in all_colors if
                                color not in preferred_colors]
            color_order = preferred_colors + remaining_colors

            attempted_shapes.clear()
            continue

        move_commands = move_brush(x, y, shapePos)
        for cmd in move_commands:
            execute(cmd)
            shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = execute(
                'export')

        placed = False
        shape_zero_placed = False
        diagonals_colored = all_diagonal_cells_colored(grid, x, y)
        if diagonals_colored:
            placed = attempt_place_shape(0)
            if placed:
                continue
            else:
                shape_zero_placed = True

        if not placed:
            for shape_group in shape_groups:
                for shape_idx in shape_group:
                    placed = attempt_place_shape(shape_idx)
                    if placed:
                        break
                if placed:
                    break

        if not placed and not shape_zero_placed:
            placed = attempt_place_shape(0)
            if placed:
                continue
            else:
                shape_zero_placed = True

        if not placed and shape_zero_placed:
            continue

        if shape_zero_placed:
            shape_zero_placed = False

        if checkGrid(grid):
            done = True
            break

    execute('export')
    return grid, placedShapes, done


conflict_minimizing_fill()
# input()

########################################

# Do not modify any of the code below.

########################################

end = time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end - start))
