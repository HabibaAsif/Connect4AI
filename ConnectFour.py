import numpy as np
import random
import pygame
import sys
import math

class Game:
    def __init__(self,row=6,col=7,player=0,AI=1,empt=0,player_piece=1,AI_piece=2,wind_leng=4):
        self.ROW_COUNT=row
        self.COLUMN_COUNT=col
        self.PLAYER=player
        self.AI=AI
        self.EMPTY=empt
        self.PLAYER_PIECE=player_piece
        self.AI_PIECE=AI_piece
        self.WINDOW_LENGTH= wind_leng

    def create_board(self):
        board = np.zeros((self.ROW_COUNT,self.COLUMN_COUNT))
        return board

    def drop_piece(self,board,row, col, piece):
        board[row][col] = piece

    def is_valid_location(self,board, col):
        return board[self.ROW_COUNT-1][col] == 0

    def get_next_open_row(self,board, col):
        for r in range(self.ROW_COUNT):
            if board[r][col] == 0:
                return r
            
    def print_board(self,board):
        print(np.flip(board, 0))
    
    def winning_move(self,board, piece):
        	# Check horizontal locations for win
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
                
                # Check vertical locations for win
        for c in range(self.COLUMN_COUNT):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
                
                # Check positively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(self.ROW_COUNT-3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True

            	# Check negatively sloped diaganols
        for c in range(self.COLUMN_COUNT-3):
            for r in range(3, self.ROW_COUNT):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True
                    
    def evaluate_window(self,window, piece):
        score=0
        opp_piece = self.PLAYER_PIECE
        if piece == self.PLAYER_PIECE:
            opp_piece = self.AI_PIECE
            
        if window.count(piece) == 4:
            score += 100
        
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2
            
        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4
        
        return score
        
    def score_position(self,board, piece):
        score = 0
        
        ## Score center column
        center_array = [int(i) for i in list(board[:, self.COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 3
        ## Score Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(self.COLUMN_COUNT-3):
                window = row_array[c:c+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)
        ## Score Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(self.ROW_COUNT-3):
                window = col_array[r:r+self.WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)
        ## Score posiive sloped diagonal
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)
        for r in range(self.ROW_COUNT-3):
            for c in range(self.COLUMN_COUNT-3):
                window = [board[r+3-i][c+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)
        return score
        
    def is_terminal_node(self,board):
        return self.winning_move(board, self.PLAYER_PIECE) or self.winning_move(board, self.AI_PIECE) or len(self.get_valid_locations(board)) == 0
        
    def minimax(self,board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(board, self.AI_PIECE):
                    return (None, 100000000000000)
                elif self.winning_move(board, self.PLAYER_PIECE):
                    return (None, -10000000000000)
                else: # Game is over, no more valid moves
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(board, self.AI_PIECE))
        
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.AI_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
            
        else: # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                self.drop_piece(b_copy, row, col, self.PLAYER_PIECE)
                new_score = self.minimax(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value
            
    def get_valid_locations(self,board):
        valid_locations = []
        for col in range(self.COLUMN_COUNT):
            if self.is_valid_location(board, col):
                valid_locations.append(col)
        return valid_locations
        
    def pick_best_move(self,board, piece):
        valid_locations = self.get_valid_locations(board)
        best_score = -10000
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = self.get_next_open_row(board, col)
            temp_board = board.copy()
            self.drop_piece(temp_board, row, col, piece)
            score = self.score_position(temp_board, piece)
            if score > best_score:
                best_score = score
                best_col = col
        return best_col

#class' and variables' assignment
game=Game()
board=game.create_board()
game.print_board(board)
PLAYER,PLAYER_PIECE=0,1
AI,AI_PIECE=1,2
game_over=False
turn = random.randint(PLAYER,AI)
mode=int(input('Select your difficulty :\n1. Easy\n2. Medium\n3. Hard : '))
#game loop
while not game_over:
    #player 1 input
    if turn == PLAYER:
        col = int(input('Player 1 make your selection (0-6):'))
        if game.is_valid_location(board,col):
            row = game.get_next_open_row(board,col)
            game.drop_piece(board,row,col,PLAYER_PIECE)
            if game.winning_move(board,PLAYER_PIECE):
                print("Player 1 Wins!!")
                game_over=True
    #player 2 input
    elif turn == AI and mode == 1:
        #change the integer value of the below to change the difficulty
        col, minimax_score = game.minimax(board, 3, -math.inf, math.inf, True)
        # below 3 = easy (too dumb to play)
        # 3 = easy (not dumb & playable)
        # 4 = medium (perfect)
        # 5 = hard (not much difference than 4 but still working great)
        # above 5 = hard (taking too long to make a move due to computing)
        if game.is_valid_location(board,col):
            row = game.get_next_open_row(board,col)
            game.drop_piece(board,row,col,AI_PIECE)
            if game.winning_move(board,AI_PIECE):
                print("AI Wins!!\nIn Easy Mode")
                game_over=True
                game.print_board(board)
                break
    elif turn == AI and mode == 2:
        col, minimax_score = game.minimax(board, 4, -math.inf, math.inf, True)
        if game.is_valid_location(board,col):
            row = game.get_next_open_row(board,col)
            game.drop_piece(board,row,col,AI_PIECE)
            if game.winning_move(board,AI_PIECE):
                print("AI Wins!!\nIn Medium Mode")
                game_over=True
                game.print_board(board)
                break
    elif turn == AI and mode == 3:
        col, minimax_score = game.minimax(board, 5, -math.inf, math.inf, True)
        if game.is_valid_location(board,col):
            row = game.get_next_open_row(board,col)
            game.drop_piece(board,row,col,AI_PIECE)
            if game.winning_move(board,AI_PIECE):
                print("AI Wins!!\nIn Hard Mode")
                game_over=True
                game.print_board(board)
                break
            
    game.print_board(board)
    #increment the turn var
    turn +=1
    # make it even/odd and the remainder(0/1) decides the turn
    turn = turn % 2 
