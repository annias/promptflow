from promptflow.src.state import State


def main(state: State):
    """
    Main loop for conway's game of life
    """
    # imports
    import numpy as np

    # get the grid size
    grid_size: int = int(state.snapshot["grid_size"])
    # get the grid
    grid: np.ndarray = np.fromstring(state.snapshot["grid"]).reshape(
        (grid_size, grid_size)
    )
    # initialize the next grid
    next_grid = np.zeros((grid_size, grid_size))
    # loop through every cell in the grid
    for i in range(grid_size):
        for j in range(grid_size):
            # get the number of neighbors
            neighbors = (
                grid[i, (j - 1) % grid_size]
                + grid[i, (j + 1) % grid_size]
                + grid[(i - 1) % grid_size, j]
                + grid[(i + 1) % grid_size, j]
                + grid[(i - 1) % grid_size, (j - 1) % grid_size]
                + grid[(i - 1) % grid_size, (j + 1) % grid_size]
                + grid[(i + 1) % grid_size, (j - 1) % grid_size]
                + grid[(i + 1) % grid_size, (j + 1) % grid_size]
            )
            # apply the rules of the game
            if grid[i, j] == 1 and neighbors < 2:
                next_grid[i, j] = 0
            elif grid[i, j] == 1 and neighbors > 3:
                next_grid[i, j] = 0
            elif grid[i, j] == 0 and neighbors == 3:
                next_grid[i, j] = 1
            else:
                next_grid[i, j] = grid[i, j]
    # save the next grid
    state.snapshot["grid"] = next_grid.tostring()

    return True
