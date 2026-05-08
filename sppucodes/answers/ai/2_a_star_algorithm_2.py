# EASY VERSION

import heapq

def astar(grid, start, goal):
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rows = len(grid)
    cols = len(grid[0])
    open_list = [(h(start, goal), 0, start, [start])] # f, g, pos, path
    visited = set()

    while open_list:
        f, g, cur, path = heapq.heappop(open_list)
        if cur in visited:
            continue
        visited.add(cur)

        if cur == goal:
            return path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            x = cur[0] + dx
            y = cur[1] + dy
            if 0 <= x < rows and 0 <= y < cols and grid[x][y] == 0:
                new_g = g + 1
                new_f = new_g + h((x, y), goal)
                node = (new_f, new_g, (x, y), path + [(x, y)]) # f, g, pos, path
                heapq.heappush(open_list, node)
    return None


rows = int(input("Rows: "))
cols = int(input("Cols: "))

grid = []
for i in range(rows):
    row = list(map(int, input(f"Row {i+1}: ").split()))
    if len(row) == cols:
        grid.append(row)
    else:
        print("Error: Row must have", cols, "numbers")

sx = int(input("Start row: "))
sy = int(input("Start col: "))
gx = int(input("Goal row: "))
gy = int(input("Goal col: "))

path = astar(grid, (sx, sy), (gx, gy))

if path:
    print("Path:", path)
else:
    print("No path.")
