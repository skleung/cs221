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
NUM_PLAYERS = 3
""" ------------------ """




"""
EVALUATION FUNCTIONS
---------------------
"""
# EVAL FUNCTION: THE BUILDER
# --------------------------
# 5 utility points per settlement, 1 per road
def builderEvalFn(currentGameState, currentPlayerIndex):
  currentPlayer = currentGameState.agents[currentPlayerIndex]
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

  def collectInitialResources(self, board):
    """
    Method: collectInitialResources
    --------------------------------
    Parameters:
      board - a Board object representing the current board state

    Returns: NA

    Takes the current board setup and awards the current player
    resources for each of his/her current settlements.  For example,
    if the player had a settlement bordering BRICK and ORE and another
    one bordering BRICK, this player would receive 2 BRICK and 1 ORE.
    --------------------------------
    """
    # Get resources for each settlement
    for settlement in self.settlements:

      # Find all tiles bordering this settlement and
      # take 1 resource of each of the surrounding tile types
      borderingTiles = board.getHexes(settlement)
      for borderingTile in borderingTiles:
        self.resources[borderingTile.resource] += 1

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


class GameState:
  """
  Class: GameState
  -------------------------------
  A class representing all information about the current state of the game.
  Includes a Board object representing the current state of the game board,
  as well as a list of all agents (players + random agents) in the game.
  -------------------------------
  """

  def __init__(self, prevState = None, layout = BeginnerLayout):
    """
    Method: __init__
    -----------------------------
    Parameters:
      prevState - an optional GameState object to pass in.  If this is passed
        in, this new GameState object will instead be cloned from prevState
      layout - an optional board layout to pass in to define the layout
        of the game board

    Returns: NA

    Initializes the GameState object, either by creating a new one from
    scratch or by cloning an optionally passed-in other GameState object.
    Can also optionally define the board layout if you are creating a new
    GameState object from scratch.
    ------------------------------
    """
    if prevState is not None:
      self.board = prevState.board.deepCopy()
      self.agents = [agent.deepCopy(self.board) for agent in prevState.agents]
    else:
      self.board = Board(layout)
      self.agents = [Agent("Player " + str(i), i) for i in xrange(NUM_PLAYERS)]

  def getLegalActions(self, agentIndex):
    """
    Method: getLegalActions
    ------------------------------
    Parameters:
      agentIndex - the index of the agent to return legal actions for

    Returns: a list of action tuples (ACTION, LOCATION) (e.g. (ACTIONS.SETTLE, *some Vertex object*))
      representing all the valid actions that the given agent/player can take
    ------------------------------
    """
    legalActions = []

    if self.gameOver() >= 0: return legalActions

    agent = self.agents[agentIndex]

    # If they can build a road...
    if agent.canBuildRoad():

      # Look at all unoccupied roads coming from the player's existing settlements
      for settlement in agent.settlements:
        currEdges = self.board.getEdgesOfVertex(settlement)
        for currEdge in currEdges:
          if not currEdge.isOccupied():
            legalActions.append((ACTIONS.ROAD, currEdge))        

    # If they can settle...
    if agent.canSettle():

      # Look at all unoccupied endpoints of the player's existing roads
      for road in agent.roads:
        possibleSettlements = self.board.getVertexEnds(road)
        for possibleSettlement in possibleSettlements:
          if possibleSettlement.canSettle:
            legalActions.append((ACTIONS.SETTLE, settlement))
            
    return legalActions

  def generateSuccessor(self, playerIndex, action):
    """
    Method: generateSuccessor
    ----------------------------
    Parameters:
      playerIndex - the number of the player that is about to take an action
      action - the action that the player is about to take

    Returns: a new GameState object with playerIndex having taken 'action'

    Creates a clone of the current game state, and then performs the
    given action on behalf of the given player.  Returns the resulting
    GameState object.
    ----------------------------
    """
    if self.gameOver() >= 0:
      raise Exception("Can\'t generate a successor of a terminal state!")

    # Create a copy of the current state, and perform the given action
    # for the given player
    state = GameState(self)
    state.agents[playerIndex].applyAction(action)
    state.board.applyAction(playerIndex, action)
    return state

  def getNumAgents(self):
    """
    Method: getNumAgents
    ----------------------------
    Parameters: NA

    Returns: the number of agents in the current game
    ----------------------------
    """
    return len(self.agents)

  def gameOver(self):
    """
    Method: gameOver
    ----------------------------
    Parameters: NA
    Returns: the index of the player that has won, or -1 if the game has not ended
    ----------------------------
    """
    # See if any of the agents have won
    for agent in self.agents:
      if agent.hasWon():
        return agent.agentIndex
    return -1


class Game:
  """
  Class: Game
  ------------------------
  Represents all information about a game, and controls game flow.
  In addition to containing a GameState object to keep track of all game
  state, a Game object also contains the game's move history as a list
  of (AGENTNAME, ACTION) tuples.
  ------------------------
  """

  def __init__(self, gameState = GameState()):
    """
    Method: __init__
    ----------------------
    Parameters:
      gameState - an optional pre-defined GameState object to use for the game.
        If one isn't passed in, the Game begins with a newly-created GameState object.

    Returns: NA

    Initializes the Game object by initializing the move history list
    and the internal GameState object.
    ----------------------
    """
    self.moveHistory = []
    self.gameState = gameState

  def run(self):    
    """
    Method: run
    ----------------------
    Parameters: NA
    Returns: NA

    Runs the main game loop.  Initializes all the players' resources
    and settlements, prints out the game state, and then begins the main loop.
    Each turn, the dice are rolled, and all players get resources.  Then, the
    player whose turn it is can take 1 action, and the game state is updated
    accordingly.  The game continues until 1 player wins by reaching
    VICTORY_POINTS_TO_WIN victory points.
    ----------------------
    """
    # --- PLAYER INITIALIZATION --- #

    # Each player starts with 2 settlements
    initialSettlements = [self.gameState.board.getVertex(2,2), 
      self.gameState.board.getVertex(4,4), 
      self.gameState.board.getVertex(4,0)]

    # Use % to essentially loop through and assign a settlement to each agent until
    # there are no more settlements to assign
    # ASSUMPTION: len(initialSettlements) is a clean multiple of # agents
    for i, settlement in enumerate(self.gameState.agents):
      agent = self.gameState.agents[i % self.gameState.getNumAgents()]
      agent.settlements.append(initialSettlements[i])
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, initialSettlements[i]))

    # Each player starts with resources for each of their settlements
    for agent in self.gameState.agents:
      agent.collectInitialResources(self.gameState.board)

    # --- END PLAYER INITIALIZATION --- #

    # --- GAME START --- #

    # Welcome message
    print "WELCOME TO SETTLERS OF CATAN!"
    print "-----------------------------"
    DEBUG = True if raw_input("DEBUG mode? (y/n) ") == "y" else False
    print "Here's the gameboard.  Drumroll please....."
    self.gameState.board.printBoard()

    # Turn tracking
    turnNumber = 1
    currentAgentIndex = 0

    # Main game loop
    while (self.gameState.gameOver() < 0):

      # Initial information
      currentAgent = self.gameState.agents[currentAgentIndex]
      print "---------- TURN " + str(turnNumber) + " --------------"
      print "It's " + str(currentAgent) + "'s turn!"
      raw_input("Type ENTER to proceed:")
      
      # Dice roll + resource distribution
      dieRoll = randint(1,6) + randint(1,6)
      if DEBUG:
        print "Rolled a " + str(dieRoll)

      for agent in self.gameState.agents:
        agent.updateResources(dieRoll, self.gameState.board)
        if DEBUG:
          print str(agent) + ": " + str(agent.resources)

      # The current player performs 1 action
      action = currentAgent.getAction(self.gameState)
      currentAgent.applyAction(action)
      self.gameState.board.applyAction(currentAgent.agentIndex, action)

      # Print out the updated game state
      if DEBUG:
        printGameActionForAgent(action, currentAgent, self.gameState.board)
      elif action is None:
        print "Unable to take any actions"

      print "The board now looks like this:"
      self.gameState.printBoard()

      # Track the game's move history
      self.moveHistory.append((currentAgent.name, action))
      
      # Go to the next player/turn
      currentAgentIndex = (currentAgentIndex+1) % numAgents
      turnNumber += 1

    print self.gameState.agents[self.gameState.gameOver()], " won the game"


# Debugging method to print out info about the agent's action
def printGameActionForAgent(action, agent, board):
  print "\n---------- PLAYER " + str(agent) + "----------"
  print "Victory points: " + str(agent.victoryPoints)
  print "Resources: " + str(agent.resources)
  print "----------------------------"

  print "Took action " + str(action[0])
  print "\n\n\n"


game = Game()
game.run()
