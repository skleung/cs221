from gameUtil import *
from board import *
from random import randint
from enum import Enum
from collections import Counter
import copy

DEBUG = True


""" GAME CONSTANTS
---------------------- """
VICTORY_POINTS_TO_WIN = 10
STARTING_NUM_OF_CARDS = 7
SETTLEMENT_POINTS = 3
ROAD_COST = Counter({ResourceTypes.BRICK: 1, ResourceTypes.LUMBER: 1})
SETTLEMENT_COST = Counter({ResourceTypes.LUMBER: 1, ResourceTypes.BRICK: 1, ResourceTypes.WOOL: 1, ResourceTypes.GRAIN: 1})
CITY_COST = Counter({ResourceTypes.GRAIN: 2, ResourceTypes.ORE: 3})
ACTIONS = Enum(["SETTLE", "CITY", "ROAD"])
""" ------------------ """




"""
EVALUATION FUNCTIONS
---------------------
"""
# EVAL FUNCTION: THE BUILDER
# --------------------------
# 5 utility points per settlement, 1 per road
def builderEvalFn(currentGameState, currentPlayerIndex):
  currentPlayer = currentGameState.data.agents[currentPlayerIndex]
  return 5 * len(currentPlayer.settlements) + len(currentPlayer.roads)


"""
This class defines a player agent and allows a user to retrieve possible actions from the agent
hand = a list of Cards that the agent holds
victoryPoints = the number of victory points the agent has
"""
class Agent:
  """
  Class: Agent
  ---------------------
  Agent defines a player agent in Settlers consisting of a name, player index, max depth, and
  player stats/game-specific information like number of victory points, lists of
  all roads, settlements, and cities owned by the player, and a counter of resources
  that the player has.

  Instance Variables:
  ---
  evaluationFunction = the eval function to use in the minimax algorithm
  name = a string containing the name of the player
  agentIndex = the player index
  victoryPoints = the number of victory points the player has
  depth = the maximum depth to recurse in the minimax tree
  roads = a list of Edge objects representing the roads a player has
  settlements = a list of Vertex objects representing the settlements a player has
  cities = a list of Vertex objects representing the cities a player has
  resources = a Counter containing the count of each resource type (in ResourceTypes) the player has
  ---------------------
  """

  def __init__(self, name, agentIndex):
    self.evaluationFunction = builderEvalFn
    self.name = name
    self.agentIndex = agentIndex
    self.victoryPoints = 0
    self.depth = 3

    # List of Edges
    self.roads = []

    # List of Vertices
    self.settlements = []

    # List of Cities owned
    self.cities = []

    # Counter of resources initialized to zero
    self.resources = Counter({ResourceTypes.WOOL: 0, 
      ResourceTypes.BRICK: 0, 
      ResourceTypes.ORE: 0, 
      ResourceTypes.GRAIN: 0, 
      ResourceTypes.LUMBER: 0})

  def initialize(self, stateData):
    pass
    
  def __repr__(self):
    """
    Method: __repr__
    ---------------------
    Parameters: NA
    Returns:the player's name

    A string representation of the given Agent.
    ---------------------
    """
    return self.name

  def canSettle(self):
    """
    Method: canSettle
    ---------------------
    Parameters: NA
    Returns: True/False whether or not this Agent has enough
      resources to build a new settlement (based on the SETTLEMENT_COST constant)
    ---------------------
    """
    modifiedResources = self.resources - SETTLEMENT_COST

    # If any resource counts dip below 0, we don't have enough
    for resourceType in modifiedResources:
      if modifiedResources[resourceType] < 0:
        return False

    return True

  def canBuildCity(self):
    """
    Method: canBuildCity
    ----------------------
    Parameters: NA
    Returns: True/False whether or not this Agent has enough
      resources to build a new city (based on the CITY_COST constant)
    ----------------------
    """
    modifiedResources = self.resources - CITY_COST

    # If any resource counts dip below 0, we don't have enough
    for resourceType in modifiedResources:
      if modifiedResources[resourceType] < 0:
        return False

    return True

  def canBuildRoad(self):
    """
    Method: canBuildRoad
    ----------------------
    Parameters: NA
    Returns: True/False whether or not this Agent has enough
      resources to build a new road (based on the ROAD_COST constant)
    ----------------------
    """
    modifiedResources = self.resources - ROAD_COST

    # If any resource counts dip below 0, we don't have enough
    for resourceType in modifiedResources:
      if modifiedResources[resourceType] < 0:
        return False

    return True

  def deepCopy(self, board):
    """
    Method: deepCopy
    ----------------------
    Parameters:
      board - the current state of the board (an instance of Board)
    Returns: a deep copy of this instance of Agent, including full
      copies of all instance Variables
    ----------------------
    """
    newCopy = Agent(self.name, self.agentIndex)
    newCopy.victoryPoints = self.victoryPoints
    newCopy.depth = self.depth
    newCopy.roads = [board.getEdge(road.X, road.Y) for road in self.roads]
    newCopy.settlements = [board.getVertex(settlement.X, settlement.Y) for settlement in self.settlements]
    newCopy.resources = copy.deepcopy(self.resources)
    return newCopy
  

  def getAction(self, state):
    """
    Method: getAction
    ------------------------
    Parameters:
      state - a GameState object containing information about the current state of the game
    Returns: an action tuple (ACTION, LOCATION) of the action this player should take

    Returns the best possible action that the current player can take.  Implements
    The expectiminimax algorithm for determining the best possible move based
    on the policies of the other Agents in the game (including other players, the
    dice rolls, etc.).  Returns None if no action can be taken, or an action tuple
    otherwise - e.g. (ACTIONS.SETTLE, *corresponding Vertex object where settlement is*).
    ------------------------
    """

    # A function that recursively calculates and returns a tuple
    # containing the best action/value (in the format (value, action))
    # for the current player at the current state with the current depth.
    def recurse(state, currDepth, playerIndex):
      
      # TERMINAL CASES
      # ---------------------
      
      # If the player won
      if state.gameOver() == playerIndex:
        return (float('inf'), None)

      # or lost
      elif state.gameOver() > -1:
        return (float('-inf'), None)

      # If the max depth has been reached, call the eval function
      elif currDepth is 0:
        return (self.evaluationFunction(state, playerIndex), None)

      # If there are no possible actions (must pass)
      possibleActions = state.getLegalActions(playerIndex)
      if len(possibleActions) is 0:
        return (self.evaluationFunction(state, playerIndex), None)

      # RECURSIVE CASE
      # ---------------------

      # Parallel lists of values and their corresponding actions
      vals = []
      actions = []

      # New depth (depth - 1 for last player, otherwise depth)
      # newPlayerIndex goes through 0, 1,...numAgents - 1 (looping around)
      newDepth = currDepth - 1 if playerIndex == state.getNumAgents() - 1 else currDepth
      newPlayerIndex = (playerIndex + 1) % state.getNumAgents()

      # Iterate over each possible action, recording action and value
      for currAction in possibleActions:
        value, action = recurse(state.generateSuccessor(playerIndex, currAction), newDepth, newPlayerIndex)
        vals.append(value)
        actions.append(currAction)

      # Maximize/minimize
      if playerIndex == 0:
        return (max(vals), actions[vals.index(max(vals))])
      return (min(vals), actions[vals.index(min(vals))])

    # Call our recursive function
    value, action = recurse(state, self.depth, self.agentIndex)
    if DEBUG: 
      print "Best Action: " + str(action)
      print "Best Value: " + str(value)
    return action

  def applyAction(self, action):
    """
    Method: applyAction
    -----------------------
    Parameters:
      action - the action tuple (ACTION, LOCATION) to applyAction
    Returns: NA

    Applies the given action tuple to the current player.  Does this
    by deducting resources appropriately and adding to the player's
    lists of roads, settlements, and cities.
    -----------------------
    """
    if action is None:
      return

    # Settling
    if action[0] is ACTIONS.SETTLE:
      self.settlements.append(action[1])
      if not self.canSettle():
        raise Exception("Player " + str(self.agentIndex) + " doesn't have enough resources to build a settlement!")
      self.resources -= SETTLEMENT_COST

    # Building a road
    if action[0] is ACTIONS.ROAD:
      self.roads.append(action[1])
      if not self.canBuildRoad():
        raise Exception("Player " + str(self.agentIndex) + " doesn't have enough resources to build a road!")
      self.resources -= ROAD_COST

    # Building a city
    if action[0] is ACTIONS.CITY:
      self.cities.append(action[1])
      if not self.canBuildCity():
        raise Exception("Player " + str(self.agentIndex) + " doesn't have enough resources to build a city!")
      self.resources -= CITY_COST

  def updateResources(self, dieRoll, board):
    """
    Method: updateResources
    -----------------------------
    Parameters:
      dieRoll - the sum of the two dice Rolled
      board - a Board object representing the current board state
    Returns: NA

    Takes the current die roll and board setup, and awards
    the current player resources depending on built settlements on the board.
    -----------------------------
    """
    self.resources += Counter(board.getResourcesFromDieRollForPlayer(self.agentIndex, dieRoll))

  def hasWon(self):
    """
    Method: hasWon
    -----------------------------
    Parameters: NA
    Returns: True/False whether or not the curernt player
      has won the game (AKA met or exceeded VICTORY_POINTS_TO_WIN)
    -----------------------------
    """
    return self.victoryPoints >= VICTORY_POINTS_TO_WIN


class GameStateData:
  def __init__(self, prevData = None):
      """
      Generates a new data packet by copying information from its predecessor.
      """
      if prevData != None:
        self.board = self.copyBoard(prevData.board)
        self.agents = self.copyAgents(prevData.agents, self.board)
        self.deck = self.copyDeck(prevData.deck)
      else:
        self.board = None
        self.agents = [] 
        self.deck = None
        
  # Deep copy of the agents as used in the init() method above
  def copyAgents(self, agents, board):
    copiedAgents = []
    for agent in agents:
      copiedAgents.append(agent.deepCopy(board))
    return copiedAgents;

  # Deep copy of the agents as used in the init() method above
  def copyDeck(self, deck):
    # TODO(skleung): change this when using deck
    copiedDeck = None
    return copiedDeck;

  # Deep copy of the agents as used in the init() method above
  def copyBoard(self, board):
    copiedBoard = board.deepCopy()
    return copiedBoard;

  """
  This method should be called to start or initialize the GameStateData
  nPlayers: number of players in this game
  players: an array of player objects that contain information about each player
  layout: an optional parameter that specifies a particular board set up
  """
  def initialize(self, agents, board):
    #creates a new deck by calling the deck's constructor
    #self.deck = Deck()
    self.agents = agents
    for agent in self.agents:
      agent.initialize(self) # This currently does nothing
    self.board = board


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
  def initialize(self, layout):
    # print "Enter the number of player agents:"
    # numAgents = int(raw_input())
    numAgents = 3
    # creates an array of player agents
    agents = [Agent("Player"+str(i), i) for i in range(numAgents)]
    # initialize board
    board = Board(layout)
    # initializes the game state's data with the number of agents and the player agents
    self.data.initialize(agents, board)

  # Get possible actions from the current state
  # An action is a tuple with action and metadata
  # For SETTLE this is the Vertex
  # For ROAD this is the Edge
  def getLegalActions(self, agentIndex):
    if self.gameOver() >= 0: return []
    legalActions = []
    agent = self.data.agents[agentIndex]
    board = self.data.board

    # If they can build a road...
    if agent.canBuildRoad() > 0:
    # Look at every space adjacent to all settlements
      validRoads = []

      for settlement in agent.settlements:
        currEdges = board.getEdgesOfVertex(settlement)
        for currEdge in currEdges:
          if not currEdge.isOccupied():
            legalActions.append((ACTIONS.ROAD, currEdge))        

    # If they can settle
    if agent.canSettle > 0:
      validSettlements = []
      possibleSettlements = []

      for road in agent.roads:
        possibleSettlements += board.getVertexEnds(road)

      for settlement in possibleSettlements:
        # Ensure that the settlement and any neighboring settlements are unoccupied
        if settlement.canSettle:
          legalActions.append((ACTIONS.SETTLE, settlement))
            
    return legalActions

  """
  Returns the successor state after the specified agent takes the action.
  """
  def generateSuccessor(self, playerIndex, action):
    # Check that successors exist
    if self.gameOver() >= 0: raise Exception('Can\'t generate a successor of a terminal state.')
    # Copy current state
    state = GameState(self)
    state.data.agents[playerIndex].applyAction(action)
    state.data.board.applyAction(playerIndex, action)
    return state

  def getNumAgents(self):
    return len(self.data.agents)

  def gameOver(self):
    for i, agent in enumerate(self.data.agents):
      if agent.hasWon():
        return i
    return -1


"""
The Game class manages the control flow to solicit actions from agents
"""
class Game: 
  def __init__(self):
    self.gameOver = False
    self.moveHistory = []

  def run(self, state):
    agents = state.data.agents
    board = state.data.board
    numAgents = len(agents)
    
    # Each player starts with 1 settlement
    initialSettlements = [board.getVertex(2,2), board.getVertex(4,4), board.getVertex(4,0)]
    for i in range(numAgents):
      agents[i].settlements.append(initialSettlements[i])
      board.applyAction(i, (ACTIONS.SETTLE, initialSettlements[i]))

    # Each player starts with 2 settlements
    initialSettlements = [board.getVertex(1,1), board.getVertex(3,3), board.getVertex(0,0)]
    for i in range(numAgents):
      agents[i].settlements.append(initialSettlements[i])
      board.applyAction(i, (ACTIONS.SETTLE, initialSettlements[i]))

    # Welcome message
    print "WELCOME TO SETTLERS OF CATAN!"
    print "-----------------------------"
    DEBUG = True if raw_input("DEBUG mode? (y/n) ") == "y" else False
    print "Here's the gameboard.  Drumroll please....."
    board.printBoard()

    turnNum = 1
    agentIndex = 0
    while (state.gameOver() < 0):
      print "---------- TURN " + str(turnNum) + " --------------"
      print "It's Player " + str(agentIndex) + "'s turn!"
      raw_input("Type ENTER to proceed:")
      
      agent = agents[agentIndex]
      print "Currently: "+str(agent)+"'s turn."

      # distribute resources from the current agent's dice roll, and update everyone's resources
      dieRoll = randint(1,6) + randint(1,6)
      if DEBUG: print "Rolled a " + str(dieRoll)
      for a in agents:
        a.updateResources(dieRoll, board)
      if DEBUG: print "\n"

      # get an action from the state
      action = agent.getAction(state)
      if action != None:
        agent.applyAction(action)
        board.applyAction(agent.agentIndex, action)

      # Print out the action taken and the new board
      if DEBUG: print "\n"
      if DEBUG and action != None: printGameActionForAgent(action, agent, board)
      elif action: board.printBoard()
      else: print "Unable to take any actions"

      # store move history
      self.moveHistory.append((agent.name, action))
      
      # Go to the next player/turn
      agentIndex = (agentIndex+1) % numAgents
      turnNum += 1

    print state.data.agents[state.gameOver()], " won the game"


# Debugging method to print out info about the agent's action
def printGameActionForAgent(action, agent, board):
  print "---------- PLAYER " + str(agent.agentIndex) + "----------"
  print "Victory points: " + str(agent.victoryPoints)
  print "Resources: " + str(agent.resources)
  print "----------------------------"

  print "Took action " + str(action[0])
  print "The board now looks like this:"
  board.printBoard()
  print "\n\n\n"

gState = GameState() 
#initializes the game state
gState.initialize(BeginnerLayout)
game = Game()
game.run(gState)
