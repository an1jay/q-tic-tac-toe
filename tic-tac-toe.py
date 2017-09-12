# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 17:38:16 2017

@author: Anirudh Jayakumar
"""
import random
import os.path
import pickle
import sys
#tic tac toe game

class TicTacToe:
    def __init__(self, player1, player2, verbose=False):
        self.board=[' ']*9
        self.verbose=verbose
        self.player1 = player1
        self.player2 = player2
        self.player1turn = random.choice([True, False])

    def play(self):
        self.player1.startGame()
        self.player2.startGame()
        while True:
            if self.player1turn:
                player = self.player1
                otherplayer = self.player2
            else:
                player = self.player2
                otherplayer = self.player1
            self.chars = (player.char, otherplayer.char)

            #player moves
            if (player.type=="Human"):
                self._print()
                #print("Player 1's turn: ", self.player1turn, end=" ")
            move = player.move(self.board)

            #if illegal move, reward and exit game
            if (self.board[move-1]!=' '):
                player.reward(-99, self.board[:])
                print("Illegal move")
                break
            self.board[move-1] = player.char

            #check winner
            res = self.isEnded()
            if(res[0]):
                if (res[1]==1):
                    if self.verbose:
                        self._print()
                        print("\n %s won!" % player.type)
                    player.reward(1, self.board[:])
                    otherplayer.reward(-1, self.board[:])
                    break
                elif (res[1]==2):
                    if self.verbose:
                        self._print()
                        print("\n % won!" % otherplayer.type)
                    player.reward(-1, self.board[:])
                    otherplayer.reward(1, self.boar[:])
                    break
                else:
                    if self.verbose:
                        self._print()
                        print("\n", "Tie!")
                    player.reward(0.5, self.board[:])
                    otherplayer.reward(0.5, self.board[:])
                    break
            else:
                otherplayer.reward(0, self.board[:])
            self.player1turn = not self.player1turn

    def _print(self):
        print("|".join(self.board[0:3]))
        print("|".join(self.board[3:6]))
        print("|".join(self.board[6:9]), end=" ")

    def isEnded(self):
        #returns (BOOL: whether game is over, who won - 0=noone, 1=player1, 2 = player2)
        top = self.board[0:3]
        mid = self.board[3:6]
        bot = self.board[6:9]
        for pl in range(2):
            player = self.chars[pl]
            #horizontals
            for j in range(3):
                won = top[j]==player and mid[j] == player and bot[j]==player
                if won:
                    return (won, pl+1)

            #verticals
            for row in [top, mid, bot]:
                won = row[0]==player and row[1]==player and row[2]==player
                if won:
                    return (won, pl+1)

            #diagonals
            won = top[0]==player and mid[1]==player and bot[2]==player
            if won:
                return (won, pl+1)
            won = top[2]==player and mid[1]==player and bot[0]==player
            if won:
                return (won, pl+1)
        if (self.board.count(" ")==0):
            return (True, 0)
        else:
            return (False, 0)

class HumanPlayer:
    def __init__(self, char = 1):
        self.type = "Human"
        self.char = char

    def startGame(self):
        print("\n____________________________\nNew Game")
    
    def move(self, board):
        while True:
            try:
                move = input("Where do you want to move? (Enter number 1-9 or '-' to exit) ")
                print("____________________________")
                if (move == '-'):
                    sys.exit(0)
                move=int(move)
                if not (move in range(10)[1:]):
                    raise ValueError
            except ValueError:
                print("Invalid move entered. Try Again.")
            else:
                break
        return move

    def reward(self, value, board):
        pass

class QLearningPlayer:
    def __init__(self, char=2, speak=False, epsilon=0.4, alpha=0.3, gamma=0.9):
        self.type = "QLearning"
        self.char = char
        self.epsilon = epsilon #chance of random exploration
        self.gamma = gamma #discount factor for future reward
        self.alpha = alpha #learning rate
        self.speak=speak
        self.q={} #q function -> (state, action) -> (key: QValue)
        
    def visualise(self):
        print(list(self.q.items())[0:100])
        
    def availableMoves(self, board):
        return [i+1 for i in range(9) if board[i]==" "]
    
    def startGame(self):
        self.prevBoard = (" ",)*9
        self.lastMove = None

    def getQ(self, state, action):
        if self.q.get((state, action)) is None:
            self.q[(state, action)] = 1.0
        return self.q.get((state, action))
    
    def move(self, board):
        self.prevBoard = tuple(board)
        actions = self.availableMoves(board)

        #disobey Q values determined action with epsilon chance
        if random.random() < self.epsilon:
            self.lastMove = random.choice(actions)
            return self.lastMove

        #choose action with hghest Q value
        qValues = [self.getQ(self.prevBoard, a) for a in actions]
        if self.speak:
           print("Actions", actions)
           print("Q vals:", qValues)
        maxQValue = max(qValues)

        #if more than one largest Q value, choose randomly among them
        if qValues.count(maxQValue) > 1:
            best_options = [i for i in range(len(actions)) if qValues[i] == maxQValue]
            i = random.choice(best_options)
        #if only one largest Q value, choose it
        else:
            i = qValues.index(maxQValue)

        self.last_move = actions[i]
        return actions[i]

    def reward(self, value, board):
        if self.lastMove:
            self.learn(state=self.prevBoard, action=self.lastMove, reward=value, result_state=tuple(board))

    def learn(self, state, action, reward, result_state):
        prev = self.getQ(state, action)
        maxqnew = max([self.getQ(result_state, a) for a in self.availableMoves(state)])
        self.q[(state, action)] = prev + self.alpha * ((reward + self.gamma*maxqnew) - prev)

#training = False
training = True
#playHuman = False
playHuman = True
trainCycles = 200000
trainEpsilon=0.9

if (os.path.exists("Qlearners.data")):
    p1, p2 = pickle.load(open("Qlearners.data", "rb"))
else:
    p1 = QLearningPlayer('X')
    p2 = QLearningPlayer('O')
if training:
    print("Training")
    p1.epsilon=trainEpsilon
    p2.epsilon=trainEpsilon
    for i in range(trainCycles):
        if (i % int(trainCycles/100))==0:
            print(int((i/trainCycles)*100),"%", end=" | ")
            #epsilon decay
            p1.epsilon=trainEpsilon*(1-i/trainCycles)
        t=TicTacToe(p1,p2)
        t.play()
    pickle.dump((p1,p2), open("Qlearners.data", "wb" ))
    print("\nTraining Done")

if playHuman:
    p1.epsilon=0
    p2 = HumanPlayer("O")
    while True:
        j=TicTacToe(p1,p2, verbose=True)
        j.play()