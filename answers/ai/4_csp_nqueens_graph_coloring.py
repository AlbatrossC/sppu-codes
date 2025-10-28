def print_board(board):
    for row in board:
        print(" ".join(row))
    print()

def is_safe(board, row, col, N):
    for i in range(row):
        for j in range(N):
            if board[i][j] == 'Q' and (j == col or abs(row - i) == abs(col - j)):
                return False
    return True

def solve(board, row, N):
    if row == N:
        print_board(board)
        return

    for col in range(N):
        if is_safe(board, row, col, N):
            board[row][col] = 'Q'
            solve(board, row + 1, N)
            board[row][col] = 'O'

N = int(input("Enter N: "))

board = []
for _ in range(N):
    row = ['O'] * N
    board.append(row)
    
solve(board, 0, N)
