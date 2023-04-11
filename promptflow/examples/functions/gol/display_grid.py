from promptflow.src.state import State


def main(state: State):
    """
    Display the game of life grid grid
    """
    # imports
    import numpy as np

    # get the grid size
    grid_size: int = int(state.snapshot["grid_size"])
    # get the grid
    grid: np.ndarray = np.fromstring(state.snapshot["grid"]).reshape(
        (grid_size, grid_size)
    )
    # print the grid
    print(grid)

    return True
