from gameUtil import *
from board import *
import random
from enum import Enum
import random
import collections
import itertools
import pdb
import copy

VICTORY_POINTS_TO_WIN = 10
STARTING_NUM_OF_CARDS = 7
SETTLEMENT_POINTS = 3
ROAD_POINTS = 1
SETTLEMENT_COST = 4
ROAD_COST = 3

ORE_COST_OF_CITY = 3
GRAIN_COST_OF_CITY = 2

DEBUG = False

def printActions(actions):
  print "----- Possible Actions ------"
  s = ""
  for action in actions:
    if action[0] == Actions.ROAD:
      s += "Road at "
    else:
      s += "Settlement at "
    s += str(action[1]) + ", "
  print s


# Currently we only use SETTLE and ROAD (no draw, because you actually always draw if you have < 7 cards)
Actions = Enum(["SETTLE", "CITY", "ROAD", "TRADE"])

"""
This evaluation function describes the current score of a particular state given a player index.
"""
def evalFn(currentGameState, currentPlayerIndex):
  currentPlayer = currentGameState.data.agents[currentPlayerIndex]
  return 5 * len(currentPlayer.settlements) + len(currentPlayer.roads)

"""
This class defines a player agent and allows a user to retrieve possible actions from the agent
hand = a list of Cards that the agent holds
victoryPoints = the number of victory points the agent has
"""
class Agent:
  def __init__(self, name, agentIndex):
    self.evaluationFunction = evalFn
    self.name = name
    self.agentIndex = agentIndex
    self.victoryPoints = 0
    self.depth = 1
    # List of Edges
    self.roads = []

    # List of Vertices
    self.settlements = []

    # List of Cities owned
    self.cities = []

    # Counter of resources
    self.resources = collections.Counter()
    for resource in [ResourceTypes.WOOL, ResourceTypes.BRICK, ResourceTypes.ORE, ResourceTypes.GRAIN, ResourceTypes.LUMBER]:
      self.resources[resource] = 0
    

  # to string method will print the agent's name
  def __repr__(self):
    return self.name

  """
  This method determines whether the Agent has the resources to settle. It will return
  the number of possible settlements given the agent's resources.
  """
  def canSettle(self):
    wool = self.resources[ResourceTypes.WOOL] 
    brick = self.resources[ResourceTypes.BRICK] 
    grain = self.resources[ResourceTypes.GRAIN] 
    lumber = self.resources[ResourceTypes.LUMBER] 
    numSettlements = 0
    while (wool > 0 and brick > 0 and grain > 0 and lumber > 0):
      wool-=1
      brick-=1
      grain-=1
      lumber-=1
      numSettlements+=1  
    return numSettlements

  """
  This method determines whether the Agent has the resources to build a city. It will return
  the number of possible settlements given the agent's resources.
  """
  def canBuildCity(self):
    ore = self.resources[ResourceTypes.ORE] 
    grain = self.resources[ResourceTypes.GRAIN] 
    numCity = 0
    while (ore > 2 and grain > 1):
      ore-=3
      grain-=2
      numCity+=1
    return numCity

  """
  This method determines whether the Agent has the resources to build a city. It will return
  the number of possible roads given the agent's resources.
  """
  def canBuildRoad(self):
    brick = self.resources[ResourceTypes.BRICK] 
    lumber = self.resources[ResourceTypes.LUMBER] 
    numCity = 0
    while (brick > 0 and lumber > 0):
      brick-=1
      lumber-=1
      numCity+=1
    return numCity

  def deepCopy(self, board):
    newCopy = Agent(self.name, self.agentIndex)
    newCopy.victoryPoints = self.victoryPoints
    newCopy.depth = self.depth
    newCopy.roads = []
    for road in self.roads:
      newCopy.roads.append(board.getEdge(road.X, road.Y))
    newCopy.settlements = []
    for settlement in self.settlements:
      newCopy.settlements.append(board.getVertex(settlement.X, settlement.Y))
    newCopy.resources = self.resources
    return newCopy
  
  """
  The Agent will receive a GameState anyd returns a tuple containing string and its metadata
  (e.g. ('settle', metadata telling where the agent decided to settle - Vertex or Edge))
  """
  def getAction(self, state):
    # legalActions = state.getLegalActions(self.agentIndex)
    # if len(legalActions) == 0: return None
    # return legalActions[0]

    # A function that recursively calculates and returns a tuple
    # containing the best action/value (in the format (value, action))
    # for the current player at the current state with the current depth.
    def recurse(state, currDepth, playerIndex):
      # TERMINAL CASES
      # ---------------------
      # won, lost
      if state.gameOver() == playerIndex:
        return (float('inf'), None)
      elif state.gameOver() > -1:
        return (float('-inf'), None)

      # max depth reached
      if currDepth is 0:
        return (self.evaluationFunction(state, playerIndex), None)

      # no possible actions (must pass)
      possibleActions = state.getLegalActions(playerIndex)
      if len(possibleActions) == 0:
        return (float('-inf'), None)

      # RECURSIVE CASE
      # ---------------------

      # Parallel lists of values and their corresponding actions
      vals = []
      actions = []

      # New depth (depth - 1 for last ghost, otherwise depth)
      # New player goes through 0, 1,...numAgents - 1 (looping around)
      newDepth = currDepth - 1 if playerIndex == state.getNumAgents() - 1 else currDepth
      newPlayerIndex = (playerIndex + 1) % state.getNumAgents()

      # Iterate over each possible action, recording action and value
      for currAction in possibleActions:
        value, action = recurse(state.generateSuccessor(playerIndex, currAction), newDepth, newPlayerIndex)
        vals.append(value)
        actions.append(currAction)

      # Should all players maximize, or just our player (player 0)?
      if playerIndex == 0:
        return (max(vals), actions[vals.index(max(vals))])
      return (min(vals), actions[vals.index(min(vals))])

    value, action = recurse(state, self.depth, self.agentIndex)
    if DEBUG: 
      print "Best Action: " + str(action)
      print "Best Value: " + str(value)
    return action


  def applyAction(self, action):
    if action == None: return

    if action[0] == Actions.SETTLE:
      numSettlements = len(action[1])
      self.settlements += action[1]
      if self.canSettle() >= numSettlements:
        self.resources[ResourceTypes.LUMBER] -= numSettlements
        self.resources[ResourceTypes.BRICK] -= numSettlements
        self.resources[ResourceTypes.WOOL] -= numSettlements
        self.resources[ResourceTypes.GRAIN] -= numSettlements
      else:
        raise Exception("not enough resources to settle!")
    if action[0] == Actions.ROAD:
      self.roads += action[1]
      numRoads = len(action[1])
      if self.canBuildRoad() >= numRoads:
        self.resources[ResourceTypes.LUMBER] -= numRoads
        self.resources[ResourceTypes.BRICK] -= numRoads
      else:
        raise Exception("not enough resources to build a road!")
    if action[0] == Actions.CITY:
      self.cities += action[1]
      numCities = len(action[1])
      if self.canBuildCity() >= numCities:
        self.resources[ResourceTypes.ORE] -= numCities*ORE_COST_OF_CITY
        self.resources[ResourceTypes.GRAIN] -= numCities*GRAIN_COST_OF_CITY
      else:
        raise Exception("not enough resources to build a city!")

    #refresh the cards in the hand!
    # self.reloadHand()

  def updateResources(self, state):
    # TODO: Don't hardcode the resources that are rolled
    resourcesRolled = [ResourceTypes.WOOL, ResourceTypes.BRICK, ResourceTypes.LUMBER, ResourceTypes.GRAIN]
    print "BEFORE: "+self.name + " has "+ str(self.resources)
    self.resources += collections.Counter(resourcesRolled)
    print "UPDATED: "+self.name + " has " + str(self.resources)

  """
  Kicks off the game, decides where to settle and build a road in the very first move of the game
  """
  def initialize(self, state):
    return
    # for i in range(STARTING_NUM_OF_CARDS):
    #   self.drawCard(state)

  #An agent wins if they get more than 10 victory points
  def won(self):
    return self.victoryPoints >= VICTORY_POINTS_TO_WIN

# class AgentRules:
#   #edits the state to be updated with the action taken
#   def applyAction(state, agentIndex, action):
#     agentState = state.data.agents[agentIndex]
#     if action[0] = "Draw":
#       agentState.

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
      # for settlement in agent.settlements:
      #   unoccupiedNeighbors = board.getUnoccupiedNeighbors(settlement, diagonals=False)
      #   for neighbor in unoccupiedNeighbors:
      #     if (Actions.ROAD, neighbor) not in legalActions:
      #       validRoads.add(neighbor)

      # # Look at every unoccupied road endpoint of every road
      # for road in agent.roads:
      #   unoccupiedEndpoints = board.getUnoccupiedRoadEndpoints(road)
      #   for unoccupiedEndpoint in unoccupiedEndpoints:
      #     if (Actions.ROAD, unoccupiedEndpoint) not in legalActions:
      #       validRoads.add(unoccupiedEndpoint)

      for settlement in agent.settlements:
        validRoads+=board.getEdgesOfVertex(settlement)
            
      # Get all possible combinations with 1 more roads
      for numPossibleRoads in range(1, agent.canBuildRoad()+1):
        # run through combinations using itertools
        for combination in list(itertools.combinations(validRoads, numPossibleRoads)):
          legalActions.append((Actions.ROAD, list(combination)))

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
      if agent.won():
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
    
    # Each player starts with 1 settlement (but no victory points for it)
    initialSettlements = [[board.getVertex(2,2)], [board.getVertex(4,4)], [board.getVertex(4,0)]]
    for i in range(numAgents):
      agents[i].settlements += initialSettlements[i]
      board.applyAction(i, (Actions.SETTLE, initialSettlements[i]))

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
      raw_input("Type ENTER to proceed:")
      
      agent = agents[agentIndex]

      # distribute resources
      # TODO(sierrakn): Actually roll dice and distribute resources accordingly
      for currAgent in state.data.agents:
        currAgent.updateResources(state)
        if DEBUG: print "Agent " + str(currAgent.agentIndex) + " has " + str(agent.resources)
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
