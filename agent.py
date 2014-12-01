from collections import Counter
from copy import deepcopy
from gameConstants import *


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
    s = "---------- " + self.name + " ----------\n"
    s += "Victory points: " + str(self.victoryPoints) + "\n"
    s += "Resources: " + str(self.resources) + "\n"
    s += "Settlements: " + str(self.settlements) + "\n"
    s += "Roads: " + str(self.roads) + "\n"
    s += "Cities: " + str(self.cities) + "\n"
    s += "--------------------------------------------\n"
    return s


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
    newCopy.resources = deepcopy(self.resources)
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
    Returns: a Counter containing the number of each resource gained

    Takes the current die roll and board setup, and awards
    the current player resources depending on built settlements on the board.
    Returns the count of each resource that the player gained.
    -----------------------------
    """
    newResources = Counter(board.getResourcesFromDieRollForPlayer(self.agentIndex, dieRoll))
    self.resources += newResources
    return newResources

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
        if borderingTile.resource is not ResourceTypes.NOTHING:
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

