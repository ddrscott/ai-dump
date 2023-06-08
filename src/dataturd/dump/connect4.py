import numpy as np

# Define the game board
board_rows = 6
board_cols = 7
board = np.zeros((board_rows, board_cols))

# Define the evaluation function for the minimax algorithm
def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, board_cols//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(board_rows):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(board_cols-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(board_cols):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(board_rows-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Score diagonal positive slope
    for r in range(board_rows-3):
        for c in range(board_cols-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score diagonal negative slope
    for r in range(board_rows-3):
        for c in range(board_cols-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

# Define the minimax algorithm
def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, 2))
    if maximizing_player:
        value = -np.Inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = np.Inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, 1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# Define helper functions for the minimax algorithm
def get_valid_locations(board):
    valid_locations = []
    for col in range(board_cols):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_valid_location(board, col):
    return board[board_rows-1][col] == 0

def get_next_open_row(board, col):
    for r in range(board_rows):
        if board[r][col] == 0:
            return r

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(board_cols-3):
        for r in range(board_rows):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Check vertical locations for win
    for c in range(board_cols):
        for r in range(board_rows-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Check positively sloped diagonals
    for c in range(board_cols-3):
        for r in range(board_rows-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Check negatively sloped diagonals
    for c in range(board_cols-3):
        for r in range(3, board_rows):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    return False

# Define a function to display the board in ASCII art and in bottom-up order
def display_board(board):
    padding = "      "
    print("\n")
    print(padding + "  1   2   3   4   5   6   7   ")
    for row in range(board_rows-1, -1, -1):
        row_str = padding + "|"
        for col in range(board_cols):
            if board[row][col] == 0:
                row_str += "   |"
            elif board[row][col] == 1:
                row_str += " X |"
            else:
                row_str += " O |"
        print(row_str)
        print(padding + "-" * (board_cols*4+1))
    print("\n")


def main():
# Play the game!
    game_over = False
    turn = 0

    display_board(board)
    while not game_over:
        # Player 1 turn
        if turn == 0:
            col = int(input("Player 1 make your selection (1-7): ")) - 1
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)
                if winning_move(board, 1):
                    print("Player 1 wins!")
                    game_over = True
            else:
                print("Invalid selection, please try again.")
                continue

        # Player 2 turn
        else:
            col, minimax_score = minimax(board, 5, -np.Inf, np.Inf, True)
            if is_valid_location(board, col):
                print("Computer selects column:", int(col or 0) + 1)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)
                if winning_move(board, 2):
                    print("Computer wins!")
                    game_over = True
            else:
                print("Invalid selection, please try again.")
                continue
        display_board(board)
        turn += 1
        turn %= 2

if __name__ == "__main__":
    main()
