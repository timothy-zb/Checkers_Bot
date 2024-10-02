import random
from copy import deepcopy
import time

# Constants for time management
TIME_LIMIT = 19  # Maximum time for the AI to think
GREY = (128, 128, 128)
PURPLE = (178, 102, 255)

def group1(self, board):
    start_time = time.time()
    best_move, best_choice = None
    depth = 1

    while True:
        best_score = float('-inf')
        possible_moves = self.getPossibleMoves(board)

        if not possible_moves:
            self.game.end_turn()
            return
        
        ordered_moves = order_moves(possible_moves, board, self.color)

        for move in ordered_moves:
            for choice in move[2]:
                new_board = deepcopy(board)
                self.moveOnBoard(new_board, (move[0], move[1]), choice)
                score = minimax(self, new_board, depth, False, float('-inf'), float('inf'), self.opponent_color, start_time)

                if score > best_score:
                    best_score = score
                    best_move = move
                    best_choice = choice

                if time.time() - start_time > TIME_LIMIT:
                    break

        if time.time() - start_time > TIME_LIMIT:
            break

        depth += 1  # Increase the depth for the next iteration

    return best_move, best_choice

def minimax(self, board, depth, maximizingPlayer, alpha, beta, current_color, start_time):
    if time.time() - start_time > TIME_LIMIT:
        return advanced_evaluate(self, board)

    if depth == 0:
        return quiescence_search(self, board, alpha, beta, maximizingPlayer, start_time)

    if isGameOver(self, board, current_color):
        return advanced_evaluate(self, board)

    possible_moves = getPossibleMovesForColor(self, board, current_color)
    ordered_moves = order_moves(possible_moves, board, current_color)

    if maximizingPlayer:
        maxEval = float('-inf')
        for move in ordered_moves:
            for choice in move[2]:
                new_board = deepcopy(board)
                self.moveOnBoard(new_board, (move[0], move[1]), choice)
                eval = minimax(self, new_board, depth - 1, alpha, beta, self.opponent_color, start_time)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return maxEval
    else:
        minEval = float('inf')
        for move in ordered_moves:
            for choice in move[2]:
                new_board = deepcopy(board)
                self.moveOnBoard(new_board, (move[0], move[1]), choice)
                eval = minimax(self, new_board, depth - 1, alpha, beta, self.color, start_time)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return minEval

def quiescence_search(self, board, alpha, beta, maximizingPlayer, start_time):
    stand_pat = advanced_evaluate(self, board)

    if maximizingPlayer:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    capture_moves = get_capture_moves(self, board, self.color if maximizingPlayer else self.opponent_color)

    for move in capture_moves:
        for choice in move[2]:
            new_board = deepcopy(board)
            self.moveOnBoard(new_board, (move[0], move[1]), choice)
            score = quiescence_search(self, new_board, alpha, beta, not maximizingPlayer, start_time)
            if maximizingPlayer:
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta
            else:
                beta = min(beta, score)
                if beta <= alpha:
                    return alpha

    return alpha if maximizingPlayer else beta

def advanced_evaluate(self, board):
    score = 0
    player_pieces, opponent_pieces = self.allPiecesLocation(board)
    
    # Piece Count
    score += len(player_pieces) - len(opponent_pieces)

    # King Pieces
    player_kings = sum(1 for piece in player_pieces if board.getSquare(piece[0], piece[1]).squarePiece.king)
    opponent_kings = sum(1 for piece in opponent_pieces if board.getSquare(piece[0], piece[1]).squarePiece.king)
    score += (player_kings - opponent_kings) * 1.5

    # Piece Safety and Positioning
    for piece in player_pieces:
        x, y = piece
        score += evaluate_piece_safety(board, piece)  # Evaluate safety
        if self.color == GREY:
            score += y * 0.1  # Encourage advancing pieces
        else:
            score += (7 - y) * 0.1
        if 2 <= x <= 5:
            score += 0.5  # Central control

    # Mobility
    player_mobility = len(self.getPossibleMoves(board))
    opponent_mobility = sum(len(move[2]) for move in getPossibleMovesForColor(self, board, self.opponent_color))
    score += (player_mobility - opponent_mobility) * 0.05

    return score

def evaluate_piece_safety(board, piece):
    x, y = piece
    threats = 0

    # Check all opponent pieces for threats to the current piece
    for i in range(8):
        for j in range(8):
            opponent_square = board.getSquare(i, j)
            if opponent_square.squarePiece and opponent_square.squarePiece.color != board.getSquare(x, y).squarePiece.color:
                # Check if the opponent can move to (x, y)
                legal_moves = board.get_valid_legal_moves(i, j, False)
                if (x, y) in legal_moves:
                    threats += 1

    # The safety score decreases with the number of threats
    return -threats * 0.5  # Each threat reduces the score

def getPossibleMovesForColor(self, board, color):
    possible_moves = []
    for i in range(8):
        for j in range(8):
            square = board.getSquare(i, j)
            if square.squarePiece and square.squarePiece.color == color:
                legal_moves = board.get_valid_legal_moves(i, j, self.game.continue_playing)
                if legal_moves:
                    possible_moves.append((i, j, legal_moves))
    return possible_moves

def get_capture_moves(self, board, color):
    capture_moves = []
    possible_moves = getPossibleMovesForColor(self, board, color)
    for move in possible_moves:
        from_x, from_y, to_positions = move
        for to_x, to_y in to_positions:
            if abs(to_x - from_x) > 1 or abs(to_y - from_y) > 1:  # Capture condition
                capture_moves.append((from_x, from_y, [(to_x, to_y)]))
    return capture_moves

def isGameOver(self, board, color):
    for x in range(8):
        for y in range(8):
            square = board.getSquare(x, y)
            if square.squarePiece and square.squarePiece.color == color:
                if board.get_valid_legal_moves(x, y, False):
                    return False
    return True

def order_moves(moves, board, color):
    def move_priority(move):
        from_x, from_y, to_positions = move
        priority = 0
        for to_pos in to_positions:
            to_x, to_y = to_pos
            if abs(to_x - from_x) > 1 or abs(to_y - from_y) > 1:
                priority += 10  # Capture
            piece = board.getSquare(from_x, from_y).squarePiece
            if (piece.color == GREY and to_y == 0) or (piece.color == PURPLE and to_y == 7):
                priority += 5  # Promotion
            if 2 <= to_x <= 5:
                priority += 1  # Central control
        return priority
    
    return sorted(moves, key=lambda move: move_priority(move), reverse=True)
