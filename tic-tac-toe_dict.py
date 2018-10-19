# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 16:41:40 2018

@author: Anirudh
"""
import os
import pickle
import random
import sys

BLANK = ' '
EXIT = '-'

#random.seed(42)


def smartPrint(statement, verbose, last='\n'):
    # =========================================================================
    # Utility method to print statement if verbose = True
    # =========================================================================
    if verbose:
        print(statement, end=last)
    else:
        pass


class Player:
    def __init__(self):
        pass

    def startGame(self):
        # =====================================================================
        # Do set up in this method
        # =====================================================================
        pass

    def move(self, board):
        # =====================================================================
        # Make move given the state of the board
        # =====================================================================
        pass

    def reward(self, *args):
        # =====================================================================
        # Only for Q Learning Player - reward the player so the Q Learning
        # Player can update the Q value
        # =====================================================================
        pass

    def printBoard(self, board):
        # =====================================================================
        # Utility Method to print the board to console
        # =====================================================================
        print('|'.join(board[0:3]))
        print('|'.join(board[3:6]))
        print('|'.join(board[6:9]))


class HumanPlayer(Player):
    def __init__(self, verbose=True):
        self.VERBOSE = verbose

    def startGame(self):
        # =====================================================================
        # Tell player it is the start of a new game
        # =====================================================================
        smartPrint('============', verbose=self.VERBOSE)
        smartPrint('New Game', verbose=self.VERBOSE)
        smartPrint('============', verbose=self.VERBOSE)

    def move(self, board):
        # =====================================================================
        # Get move from player by showing board
        # =====================================================================
        while True:
            try:
                self.printBoard(board)
                move = input('Your move? (1-9 or - to exit)\n')
                print('============')
                if (move == EXIT):
                    sys.exit(0)
                move = int(move)
                if not (move-1 in range(9)):
                    raise ValueError
            except ValueError:
                print('Invalid move; try again:\n')
            else:
                return move-1



class QLearnerPlayer(Player):
    def __init__(self, verbose=False, epsilon=0.4, alpha=0.3, gamma=0.9, defaultQ = 1):
        self.VERBOSE = verbose
        self.EPSILON = epsilon  # chance of random exploration
        self.ALPHA = alpha  # dicount factor for future reward
        self.GAMMA = gamma  # learning rate
        self.DEFAULTQ = defaultQ  # default q-value for new state, action pairs

        self.q = {}  # Q function -> {(state, action) : q_val}
        self.prevMove = None  # Previous move
        self.prevBoard = (' ',) * 9

    def availableMoves(self, board):
        # =====================================================================
        # Get all legal moves in the board
        # =====================================================================
        return [i for i in range(9) if board[i] == ' ']

    def startGame(self):
        pass

    def getQ(self, state, action):
        # =====================================================================
        # Get Q-Value for (State, Action) pair. If no Q-Value exists for a
        # (State, Action) pair, create Q-Value of DEFAULTQ for that pair
        # =====================================================================
        if self.q.get((state, action)) is None:
            self.q[(state, action)] = self.DEFAULTQ
        return self.q[(state, action)]

    def move(self, board):
        # =====================================================================
        # Get move by picking randomly (with probability epsilon) and otherwise
        # picking the (one of the) action(s) with the highest Q-Value, given
        # the current state (i.e. board), or if
        # =====================================================================
        self.prevBoard = tuple(board)
        actions = self.availableMoves(board)

        # Choose random action with epsilon chance
        if random.random() < self.EPSILON:
            self.prevMove = random.choice(actions)
            return self.prevMove

        # Otherwise choose action(s) with highest Q value
        QValues = [self.getQ(self.prevBoard, a) for a in actions]
        maxQValue = max(QValues)
        # If multiple best actions, choose one at random
        if QValues.count(maxQValue) > 1:
            bestActions = [i for i in range(len(actions)) if QValues[i] == maxQValue]
            bestMove = actions[random.choice(bestActions)]
        # If only one best action, choose that
        else:
            bestMove = actions[QValues.index(maxQValue)]

        self.prevMove = bestMove
        return self.prevMove

    def reward(self, value, board):
        # =====================================================================
        # Update Q value for the (State, Action) pair just played in the 'move'
        # method
        # =====================================================================
        if self.prevMove:
            prevQ = self.getQ(self.prevBoard, self.prevMove)

            maxQnew = max([self.getQ(tuple(board), a) for a in self.availableMoves(self.prevBoard)])
            self.q[(self.prevBoard, self.prevMove)] = prevQ + self.ALPHA *((value + self.GAMMA * maxQnew)-prevQ)

class TicTacToe:
    def __init__(self, player1, player2, verbose=False):
        self.VERBOSE = verbose
        self.P1CHAR = 'X'
        self.P2CHAR = 'O'

        self.player1 = player1
        self.player2 = player2

        self.player1turn = random.choice([True, False])
        self.board = [' '] * 9

    def play(self):
        # =====================================================================
        # Main method of the class - actually plays the game
        # =====================================================================

        # Initialise players
        self.player1.startGame()
        self.player2.startGame()

        # Main game loop
        while True:
            if self.player1turn:
                player = self.player1
                otherplayer = self.player2
                chars = (self.P1CHAR, self.P2CHAR)
            else:
                player = self.player2
                otherplayer = self.player1
                chars = (self.P2CHAR, self.P1CHAR)
            # Check winner
            gameOver, whoWon = self.isGameOver(chars)
            # If game over, reward winner 1 and loser, -1; if tie, reward both 0.5 and break from loop
            # If not game over reward player 0
            if gameOver:
                if whoWon == chars[0]:
                    if self.VERBOSE:
                        player.printBoard(self.board[:])
                    smartPrint('\n %s won!' % player.__class__.__name__, verbose=self.VERBOSE)
                    player.reward(1, self.board[:])
                    otherplayer.reward(-1, self.board[:])
                if whoWon == chars[1]:
                    if self.VERBOSE:
                        player.printBoard(self.board[:])
                    smartPrint('\n %s won!' % otherplayer.__class__.__name__, verbose=self.VERBOSE)
                    otherplayer.reward(1, self.board[:])
                    player.reward(-1, self.board[:])
                else:
                    if self.VERBOSE:
                        player.printBoard(self.board[:])
                    smartPrint('Tie!', verbose=self.VERBOSE)
                    player.reward(0.5, self.board[:])
                    otherplayer.reward(0.5, self.board[:])
                break
            else:
                player.reward(0, self.board[:])
            self.player1turn = not self.player1turn

            # Player moves
            move = player.move(self.board)

            # If illegal move is made, reward player -99 and exit game
            if self.board[move] != ' ':
                player.reward(-99, self.board[:])
                print('Illegal move!!')
                break
            self.board[move] = chars[0]

    def isGameOver(self, chars):
        # =====================================================================
        # Returns (gameOver, char), where gameOver is a Boolean indicating
        # whether the game is over and char is the character of the winning
        # player. If char is None, no winner.
        # =====================================================================
        top = self.board[0:3]
        mid = self.board[3:6]
        bot = self.board[6:9]
        for char in chars:
            # check horizontal victories
            for j in range(3):
                gameOver = top[j] == char and mid[j] == char and bot[j] == char
                if gameOver:
                    return (gameOver, char)
            # check vertical victories
            for row in [top, mid, bot]:
                gameOver = row[0] == char and row[1] == char and row[2] == char
                if gameOver:
                    return (gameOver, char)

            # check diagonal victories
            gameOver = top[0] == char and mid[1] == char and bot[2] == char
            if gameOver:
                return (gameOver, char)
            gameOver = top[2] == char and mid[1] == char and bot[0] == char
            if gameOver:
                return (gameOver, char)

        # check for draw - 0 spaces left
        if (self.board.count(' ') == 0):
            return (True, None)
        else:
            return (False, None)

if __name__ == '__main__':
    trainCycles = 20000
    trainEpsilon = 0.4
    if os.path.exists('AI.pkl'):
        p1, p2 = pickle.load(open('AI.pkl', 'rb'))
    else:
        p1 = QLearnerPlayer()
        p2 = QLearnerPlayer()

    print('Training')
    p1.EPSILON = trainEpsilon
    p2.EPSILON = trainEpsilon

    for i in range(trainCycles):
        t = TicTacToe(p1, p2)
        t.play()

    pickle.dump((p1, p2), open('AI.pkl', 'wb'))
    print('\nTraining Done')

    p1.EPSILON = 0
    p2 = HumanPlayer()
    j = TicTacToe(p1, p2, verbose=True)
    j.play()