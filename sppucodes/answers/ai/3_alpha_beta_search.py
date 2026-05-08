# Print the 3x3 Board
def print_board(b):
    for i in range(0, 9, 3):
        print(b[i:i+3])
    print()


# Check Winner
def check_winner(b):
    wins = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),   # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),   # Columns
        (0, 4, 8), (2, 4, 6)               # Diagonals
    ]
    for x, y, z in wins:
        if b[x] == b[y] == b[z] != " ":
            return b[x]
    return None


# Evaluate Board
def evaluate(b):
    winner = check_winner(b)
    if winner == "X":
        return 1
    elif winner == "O":
        return -1
    return 0


# Alpha-Beta Pruning
def alpha_beta(b, depth, alpha, beta, maximizing):
    winner = check_winner(b)
    if winner or " " not in b or depth == 0:
        return evaluate(b)

    if maximizing:
        best_score = -1000
        for i in range(9):
            if b[i] == " ":
                b[i] = "X"
                score = alpha_beta(b, depth - 1, alpha, beta, False)
                b[i] = " "
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        return best_score
    else:
        best_score = 1000
        for i in range(9):
            if b[i] == " ":
                b[i] = "O"
                score = alpha_beta(b, depth - 1, alpha, beta, True)
                b[i] = " "
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
        return best_score


# Find Best Move for AI
def best_move(b):
    best_val = -1000
    move = -1
    for i in range(9):
        if b[i] == " ":
            b[i] = "X"
            val = alpha_beta(b, 9, -1000, 1000, False)
            b[i] = " "
            if val > best_val:
                best_val = val
                move = i
    return move


# Main Game Loop
board = [" "] * 9
print("Tic Tac Toe using Alpha-Beta Pruning (X = AI, O = You)\n")

while True:
    print_board(board)

    # Human Move
    move = int(input("Enter your move (0–8): "))
    if board[move] != " ":
        print("Invalid move! Try again.")
        continue
    board[move] = "O"

    if check_winner(board) or " " not in board:
        break

    # AI Move
    ai_move = best_move(board)
    board[ai_move] = "X"
    print(f"AI chose: {ai_move}\n")

    if check_winner(board) or " " not in board:
        break


# Game Over
print_board(board)
winner = check_winner(board)

if winner:
    print(f"Winner: {winner}")
else:
    print("It's a draw!")
