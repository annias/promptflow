from promptflow.src.state import State


def main(state: State):
    """
    Initialize a grid for conway's game of life
    """
    # imports
    import numpy as np
    import random

    # get the grid size
    grid_size: int = int(state.snapshot["grid_size"])
    # initialize the grid
    grid = np.zeros((grid_size, grid_size))
    # set the initial state
    for i in range(grid_size):
        for j in range(grid_size):
            grid[i, j] = random.randint(0, 1)
    # save the grid
    state.snapshot["grid"] = np.tostring(grid)
    state.snapshot["grid_size"] = str(grid_size)

    return True
