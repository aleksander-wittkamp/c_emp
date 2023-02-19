import copy

class Grid:
    grid_key = {}

    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)

    def draw(self):
        for i in range(16):
            for j in range(12):
                self.grid_key[self.grid[j][i]].draw(i, j)