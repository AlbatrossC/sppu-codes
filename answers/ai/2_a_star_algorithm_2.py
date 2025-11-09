# Easy version

import heapq

def astar(grid, start, goal):
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rows = len(grid)
    cols = len(grid[0])

    start_g = 0
    start_f = h(start, goal)
    open_list = [(start_f, start_g, start, [])]  # (f, g, position, path)
    visited = set()

    while open_list:
        f, g, current, path = heapq.heappop(open_list)

        if current in visited:
            continue
        visited.add(current)
        path = path + [current]

        if current == goal:
            return path

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x, y = current[0] + dx, current[1] + dy

            if 0 <= x < rows and 0 <= y < cols and grid[x][y] == 0:
                new_g = g + 1
                new_f = new_g + h((x, y), goal)
                heapq.heappush(open_list, (new_f, new_g, (x, y), path))
    return None


# --- Input Section ---
r, c = map(int, input("Rows Cols: ").split())
grid = [list(map(int, input().split())) for _ in range(r)]
sx, sy = map(int, input("Start (r c): ").split())
gx, gy = map(int, input("Goal (r c): ").split())

path = astar(grid, (sx, sy), (gx, gy))
print("Path:" if path else "No path found", path)
