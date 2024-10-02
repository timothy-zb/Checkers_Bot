# group1.py
import random
from copy import deepcopy
import time

from components.GuiHandler import GREY, PURPLE  # Ensure PURPLE is imported as well

def group2(self, board):
    """
    Implements the AI's move selection using the minimax algorithm with the advanced evaluation function
    and quiescence search for tactical positions.
    """
    start_time = time.time()
    depth = 3  # Adjust based on performance requirements
    best_score = float('-inf')
    best_move = None
    best_choice = None
    possible_moves = self.getPossibleMoves(board)
    
    if not possible_moves:
        self.game.end_turn()
        return
    
    # Order moves to prioritize captures and promotions
    ordered_moves = order_moves(possible_moves, board, self.color)
    
    for move in ordered_moves:
        for choice in move[2]:
            new_board = deepcopy(board)
            # Simulate the move
            self.moveOnBoard(new_board, (move[0], move[1]), choice)
            # Call minimax with alpha-beta pruning and quiescence search
            score = minimax(self, new_board, depth - 1, False, float('-inf'), float('inf'), self.opponent_color, start_time)
            if score > best_score:
                best_score = score
                best_move = move
                best_choice = choice
            # Time check to ensure responsiveness
            if time.time() - start_time > 19:
                break
    return best_move, best_choice

def minimax(self, board, depth, maximizingPlayer, alpha, beta, current_color, start_time):
    """
    Minimax algorithm with alpha-beta pruning and quiescence search.
    """
    # Time constraint check
    if time.time() - start_time > 19:
        return advanced_evaluate(self, board)
    
    if depth == 0:
        return quiescence_search(self, board, alpha, beta, maximizingPlayer, start_time)

    if isGameOver(self, board, current_color):
        return advanced_evaluate(self, board)
    
    if maximizingPlayer:
        maxEval = float('-inf')
        possible_moves = getPossibleMovesForColor(self, board, current_color)
        # Order moves within minimax as well
        ordered_moves = order_moves(possible_moves, board, current_color)
        for move in ordered_moves:
            for choice in move[2]:
                new_board = deepcopy(board)
                self.moveOnBoard(new_board, (move[0], move[1]), choice)
                eval = minimax(self, new_board, depth - 1, False, alpha, beta, self.opponent_color, start_time)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            # Time check within loop
            if time.time() - start_time > 19:
                break
        return maxEval
    else:
        minEval = float('inf')
        possible_moves = getPossibleMovesForColor(self, board, current_color)
        # Order moves within minimax as well
        ordered_moves = order_moves(possible_moves, board, current_color)
        for move in ordered_moves:
            for choice in move[2]:
                new_board = deepcopy(board)
                self.moveOnBoard(new_board, (move[0], move[1]), choice)
                eval = minimax(self, new_board, depth - 1, True, alpha, beta, self.color, start_time)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            # Time check within loop
            if time.time() - start_time > 19:
                break
        return minEval

def quiescence_search(self, board, alpha, beta, maximizingPlayer, start_time):
    """
    Quiescence search to extend the search in "noisy" positions where captures are available.
    This prevents horizon effects by continuing to search tactical sequences.
    """
    stand_pat = advanced_evaluate(self, board)
    
    # If we can't beat alpha, return immediately (pruning).
    if maximizingPlayer:
        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return alpha
        beta = min(beta, stand_pat)

    # Get possible capture moves only (or moves that significantly change material balance).
    capture_moves = get_capture_moves(self, board, self.color if maximizingPlayer else self.opponent_color)

    for move in capture_moves:
        for choice in move[2]:
            new_board = deepcopy(board)
            self.moveOnBoard(new_board, (move[0], move[1]), choice)
            score = quiescence_search(self, new_board, alpha, beta, not maximizingPlayer, start_time)
            if maximizingPlayer:
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta  # Beta cut-off
            else:
                beta = min(beta, score)
                if beta <= alpha:
                    return alpha  # Alpha cut-off

    return alpha if maximizingPlayer else beta

def advanced_evaluate(self, board):
    """
    Advanced evaluation function considering multiple factors:
    - Piece Count
    - King Pieces
    - Piece Positioning
    - Mobility
    """
    score = 0
    player_pieces, opponent_pieces = self.allPiecesLocation(board)
    
    # Piece Count
    score += len(player_pieces) - len(opponent_pieces)
    
    # King Pieces
    player_kings = sum(1 for piece in player_pieces if board.getSquare(piece[0], piece[1]).squarePiece.king)
    opponent_kings = sum(1 for piece in opponent_pieces if board.getSquare(piece[0], piece[1]).squarePiece.king)
    score += (player_kings - opponent_kings) * 1.5  # Kings are 1.5 times more valuable
    
    # Piece Positioning
    for piece in player_pieces:
        x, y = piece
        # Encourage advancing pieces (for GREY, y increases; for PURPLE, y decreases)
        if self.color == GREY:
            score += y * 0.1
        else:
            score += (7 - y) * 0.1
        # Central control
        if 2 <= x <= 5:
            score += 0.5
    for piece in opponent_pieces:
        x, y = piece
        if self.opponent_color == GREY:
            score -= y * 0.1
        else:
            score -= (7 - y) * 0.1
        if 2 <= x <= 5:
            score -= 0.5
    
    # Mobility
    player_mobility = len(self.getPossibleMoves(board))
    opponent_mobility = 0
    for move in getPossibleMovesForColor(self, board, self.opponent_color):
        opponent_mobility += len(move[2])
    score += (player_mobility - opponent_mobility) * 0.05
    
    return score

def getPossibleMovesForColor(self, board, color):
    """
    Retrieves all possible moves for a given color.
    """
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
    """
    Returns only the capture moves for the given color. 
    These are moves where a piece can capture an opponent's piece.
    """
    capture_moves = []
    possible_moves = getPossibleMovesForColor(self, board, color)
    for move in possible_moves:
        from_x, from_y, to_positions = move
        for to_x, to_y in to_positions:
            if abs(to_x - from_x) > 1 or abs(to_y - from_y) > 1:  # Capture condition
                capture_moves.append((from_x, from_y, [(to_x, to_y)]))
    return capture_moves

def isGameOver(self, board, color):
    """
    Checks if the game is over for a given color.
    """
    for x in range(8):
        for y in range (8):
            square = board.getSquare(x, y)
            if square.squarePiece and square.squarePiece.color == color:
                if board.get_valid_legal_moves(x, y, False):
                    return False
    return True

def order_moves(moves, board, color):
    """
    Orders moves to prioritize captures and king promotions.
    """
    def move_priority(move):
        from_x, from_y, to_positions = move
        priority = 0
        for to_pos in to_positions:
            to_x, to_y = to_pos
            # Check if the move is a capture
            if abs(to_x - from_x) > 1 or abs(to_y - from_y) > 1:
                priority += 10
            # Check for king promotion
            piece = board.getSquare(from_x, from_y).squarePiece
            if piece.color == GREY and to_y == 0:
                priority += 5
            elif piece.color == PURPLE and to_y == 7:
                priority += 5
            # Encourage central control
            if 2 <= to_x <= 5:
                priority += 1
        return priority
    
    # Sort moves based on priority in descending order
    sorted_moves = sorted(moves, key=lambda move: move_priority(move), reverse=True)
    return sorted_moves
