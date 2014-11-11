from gameUtil import *
import random

VICTORY_POINTS_TO_WIN = 2
"""
This class defines a player agent and allows a user to retrieve possible actions from the agent
"""
class Agent:
  def __init__(self, name):
    self.name = name
    self.victoryPoints = 0
  # to string method will print the agent's name
  def __str__(self):
    return self.name
  
  """
  The Agent will receive a GameState and returns a tuple containing string and its metadata
  (e.g. ('settle', metadata telling where the agent decided to settle))
  """
  # def getActions(self, state):
    #TODO: get possible actions from the current state

  #TODO: get the "best" action according to minimax?
  def getAction(self, state):
    return "draw"

  def updateAgent(self, state, action):
    if action == "draw":
      card = state.data.deck.drawCard()
      if card.value == "Victory":
        self.victoryPoints += 1

  #An agent wins if they get more than 10 victory points
  def won(self):
    return self.victoryPoints > VICTORY_POINTS_TO_WIN

# class AgentRules:
#   #edits the state to be updated with the action taken
#   def applyAction(state, agentIndex, action):
#     agentState = state.data.agents[agentIndex]
#     if action[0] = "Draw":
#       agentState.

class GameStateData:
  def __init__( self, prevState = None ):
      """
      Generates a new data packet by copying information from its predecessor.
      """
      if prevState != None:
        self.deck = prevState.deck.shallowCopy()
        self.agents = self.copyagents( prevState.agents )
      self.deck = None
      self.agents = []

  #allows for deep copy of the agent states as used in the init() method above
  def copyagents( self, agents ):
    copiedStates = []
    for agentState in agents:
      copiedStates.append( agentState.copy() )
    return copiedStates

        

  """
  This method should be called to start or initialize the GameStateData
  nPlayers: number of players in this game
  players: an array of player objects that contain information about each player
  layout: an optional parameter that specifies a particular board set up
  """
  def initialize(self, agents, layout=None):
    #creates a new deck by calling the deck's constructor
    self.deck = Deck()
    self.agents = agents


class GameState:
  def __init__(self, prevState = None):
    """
    Generates a new state by copying information from its predecessor if it exists
    """
    if prevState != None: # Initial state
      self.data = GameStateData(prevState.data)
    else:
      self.data = GameStateData()

  def __eq__( self, other ):
    """
    Allows two states to be compared.
    """
    return self.data == other.data

  def __hash__( self ):
    """
    Allows states to be keys of dictionaries.
    """
    return hash( self.data )

  def __str__( self ):
    return str(self.data)

  """
  Creates a GameState based on a layout if it exists
  """
  def initialize(self, layout = None):
    self.data = GameStateData()
    print "Enter the number of player agents:"
    numAgents = int(raw_input())
    #creates an array of player agents
    agents = [Agent("Player"+str(i)) for i in range(numAgents)]
    # TODO: initialize the board
    #initializes the game state's data with the number of agents and the player agents
    self.data.initialize(agents)

  def getNumAgents(self):
    return len(self.data.agents)

  def gameOver(self):
    for i, agent in enumerate(self.data.agents):
      if agent.won():
        return i
    return -1

  def generateSuccessor(self, playerIndex, action):
    #TODO: Update the game's state based on the action taken

    # Check that successors exist
    if self.gameOver(): raise Exception('Can\'t generate a successor of a terminal state.')

    # Copy current state
    state = GameState(self)


"""
The Game class manages the control flow to solicit actions from agents
"""
class Game: 

  def __init__(self):
    self.gameOver = False
    self.moveHistory = []

  def run(self, state):
    agentIndex = 0
    numAgents = len(state.data.agents)
    while (state.gameOver() < 0):
      agent = state.data.agents[agentIndex]
      #get an action from the state
      action = agent.getAction(state)
      agent.updateAgent(state, action)

      #store move history
      self.moveHistory.append((agent.name, action))
      agentIndex = (agentIndex+1) % numAgents

    print state.data.agents[state.gameOver()], " won the game"

gState = GameState() 
#initializes the game state
gState.initialize()
game = Game()
game.run(gState)
