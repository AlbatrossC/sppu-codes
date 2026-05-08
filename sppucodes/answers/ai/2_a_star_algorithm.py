import heapq

def astar(grid, start, goal):
    def heuristic(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]  # reverse path

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            neighbor = (current[0]+dx, current[1]+dy)
            if 0 <= neighbor[0] < len(grid) and 0 <= neighbor[1] < len(grid[0]):
                if grid[neighbor[0]][neighbor[1]] == 1:
                    continue  # obstacle
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

    return None  # no path found

rows = int(input("Enter number of rows in the grid: "))
cols = int(input("Enter number of columns in the grid: "))

grid = []
print("Enter the grid row by row (0 for free, 1 for obstacle):")
for i in range(rows):
    row = list(map(int, input(f"Row {i+1}: ").split()))
    if len(row) != cols:
        raise ValueError(f"Row must have exactly {cols} values.")
    grid.append(row)

start_row = int(input("Enter start row (0-indexed): "))
start_col = int(input("Enter start column (0-indexed): "))
goal_row = int(input("Enter goal row (0-indexed): "))
goal_col = int(input("Enter goal column (0-indexed): "))

start = (start_row, start_col)
goal = (goal_row, goal_col)

path = astar(grid, start, goal)

if path:
    print("Path found:", path)
else:
    print("No path exists from start to goal.")
    