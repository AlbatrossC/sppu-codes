import heapq

def astar(grid, start, goal):
    # --- Heuristic (Manhattan Distance) ---
    def h(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rows, cols = len(grid), len(grid[0])
    open_list = [(h(start, goal), 0, start, [start])]  # (f, g, position, path)
    visited = set()

    while open_list:
        f, g, cur, path = heapq.heappop(open_list)
        if cur in visited:
            continue
        visited.add(cur)

        if cur == goal:
            return path

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:  # 4 directions
            x, y = cur[0] + dx, cur[1] + dy
            if 0 <= x < rows and 0 <= y < cols and grid[x][y] == 0:
                new_g = g + 1
                new_f = new_g + h((x, y), goal)
                heapq.heappush(open_list, (new_f, new_g, (x, y), path + [(x, y)]))
    return None


# --- Input Section ---
r, c = map(int, input("Rows Cols: ").split())
grid = [list(map(int, input().split())) for _ in range(r)]
sx, sy = map(int, input("Start (r c): ").split())
gx, gy = map(int, input("Goal (r c): ").split())

# --- Run A* ---
path = astar(grid, (sx, sy), (gx, gy))
print("Path:" if path else "No path found", path)
