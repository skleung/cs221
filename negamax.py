import sys
sys.path.insert(0, '/easyAI/easyAI')

from easyAI import TwoPlayersGame
from easyAI import AI_Player, Negamax
from board import BeginnerLayout, Board, Edge, Hexagon, Vertex
from game import *
from agents import * 
class Settlers(TwoPlayersGame):
  def __init__(self, players):
    self.game = Game()
    self.players = players
    self.game.initializePlayers()
    self.game.initializeSettlementsAndResourcesLumberBrick()
    self.nplayer = 1

  def possible_moves(self):
    return self.game.gameState.getLegalActions(self.nplayer-1)

  def make_move(self, action):
    self.game.gameState.makeMove(self.nplayer-1, action)

  def is_over(self):
    """
    Method: is_over()

    Returns True if the game is over
    """
    return self.game.gameState.gameOver() >= 0

  def show(self):
    return

  def scoring(self):
    return defaultEvalFn(self.game.gameState, self.nplayer-1)


ai_algo = Negamax(1)
Settlers([AI_Player(ai_algo),AI_Player(ai_algo)]).play()
