from gameUtil import *
import random
from basicBoard import *
from enum import Enum
import pdb

VICTORY_POINTS_TO_WIN = 10
STARTING_NUM_OF_CARDS = 7
SETTLEMENT_POINTS = 3
ROAD_POINTS = 1
SETTLEMENT_COST = 4
ROAD_COST = 3

DEBUG = False

# Currently we only use SETTLE and ROAD (no draw, because you actually always draw if you have < 7 cards)
Actions = Enum(["SETTLE", "CITY", "ROAD", "TRADE"])

def evalFn(currentGameState, currentPlayerIndex):
  currentPlayer = currentGameState.data.agents[currentPlayerIndex]
  return 3 * len(currentPlayer.settlements) + len(currentPlayer.roads)

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
    self.depth = 2
    
    # List of Tiles
    self.roads = []
    
    # List of Tiles
    self.settlements = []

    # TODO(sierrakn): Make this a Counter of resource type -> number of that resource in hand
    self.resources = ([ResourceTypes.WOOL, ResourceTypes.BRICK, 
      ResourceTypes.ORE, ResourceTypes.GRAIN, ResourceTypes.LUMBER])
    

  # to string method will print the agent's name
  def __str__(self):
    return self.name

  def copy(self):
    newCopy = Agent(self.name, self.agentIndex)
    newCopy.victoryPoints = self.victoryPoints
    newCopy.depth = self.depth
    newCopy.roads = self.roads
    newCopy.settlements = self.settlements
    newCopy.resources = self.resources
    return newCopy
  
  """
  The Agent will receive a GameState and returns a tuple containing string and its metadata
  (e.g. ('settle', metadata telling where the agent decided to settle - Vertex or Edge))
  """
  def getAction(self, state):
    legalActions = state.getLegalActions(self.agentIndex)
    if len(legalActions) == 0: return None
    return legalActions[0]

    # # A function that recursively calculates and returns a tuple
    # # containing the best action/value (in the format (value, action))
    # # for the current player at the current state with the current depth.
    # def recurse(state, currDepth, playerIndex):
    #   # TERMINAL CASES
    #   # ---------------------
    #   # won, lost
    #   if state.gameOver() == playerIndex:
    #     return (float('inf'), None)
    #   elif state.gameOver() > -1:
    #     return (float('-inf'), None)

    #   # max depth reached
    #   if currDepth is 0:
    #     return (self.evaluationFunction(state, playerIndex), None)

    #   # no possible actions (must pass)
    #   possibleActions = state.getLegalActions(playerIndex)
    #   if len(possibleActions) == 0:
    #     return (0, None)

    #   # RECURSIVE CASE
    #   # ---------------------

    #   # Parallel lists of values and their corresponding actions
    #   vals = []
    #   actions = []

    #   # New depth (depth - 1 for last ghost, otherwise depth)
    #   # New player goes through 0, 1,...numAgents - 1 (looping around)
    #   newDepth = currDepth - 1 if playerIndex == state.getNumAgents() - 1 else currDepth
    #   newPlayerIndex = playerIndex + 1 if playerIndex != state.getNumAgents() - 1 else 0

    #   # Iterate over each possible action, recording action and value
    #   for currAction in possibleActions:
    #     value, action = recurse(state.generateSuccessor(playerIndex, currAction), newDepth, newPlayerIndex)
    #     vals.append(value)
    #     actions.append(currAction)

    #   # Should all players maximize, or just our player (player 0)?
    #   if playerIndex == 0:
    #     return (max(vals), actions[vals.index(max(vals))])

    #   return (min(vals), actions[vals.index(min(vals))])

    # value, action = recurse(state, self.depth, self.agentIndex)
    # return action


  def applyAction(self, action):
    if action == None: return

    if action[0] == Actions.SETTLE:
      self.settlements.append(action[1])
      self.victoryPoints = self.victoryPoints + SETTLEMENT_POINTS
      for i in range(4): self.resources.pop()
    if action[0] == Actions.ROAD:
      self.roads.append(action[1])
      self.victoryPoints = self.victoryPoints + ROAD_POINTS
      for i in range(3): self.resources.pop()
    #TODO: need to refresh the amount of resources ....

  # TODO(sierrakn): Actually roll dice and distribute resources accordingly
  def updateResources(self, state):
    for i in xrange(len(self.settlements)):
      self.resources.append(ResourceTypes.WOOL)

  # def drawCard(self, state):
  #   card = state.data.deck.drawCard()
  #   if card.value == "Victory":
  #     self.victoryPoints += 1
  #   self.hand.append(card)

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
  def __init__( self, prevData = None ):
      """
      Generates a new data packet by copying information from its predecessor.
      """
      if prevData != None:
        self.board = prevData.board
        self.agents = self.copyagents( prevData.agents)
      else:
        self.agents = [] 
        self.deck = None
        self.board = None

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
  def initialize(self, agents, board):
    #creates a new deck by calling the deck's constructor
    #self.deck = Deck()
    self.agents = agents
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
  def initialize(self, layout = None):
    # print "Enter the number of player agents:"
    # numAgents = int(raw_input())
    numAgents = 3
    # creates an array of player agents
    agents = [Agent("Player"+str(i), i) for i in range(numAgents)]
    # initialize board
    board = BasicBoard(6)
    # initializes the game state's data with the number of agents and the player agents
    self.data.initialize(agents, board)
    for agent in self.data.agents:
      agent.initialize(self) # This currently does nothing

  # Get possible actions from the current state
  # An action is a tuple with action and metadata
  # For SETTLE this is the Vertex
  # For ROAD this is the Edge
  def getLegalActions(self, agentIndex):
    if self.gameOver() >= 0: return []
    legalActions = []
    agent = self.data.agents[agentIndex]
    board = self.data.board

    # TODO(sierrakn): change to actual resources
    # If they can build a settlement...
    if len(agent.resources) >= SETTLEMENT_COST:
      # for edge in agent.roads:
      #   # TODO(sierrakn): smarter way to check if two away from settlement?
      #   vertices = board.getVertexEnds(edge)
      #   for vertex in vertices:
      #     print "Starting looking from settlement " + str((vertex.X, vertex.Y))
      #     canSettle = True
      #     if vertex.isSettlement: canSettle = False; continue
      #     for neighborVertex in board.getNeighborVertices(vertex):
      #       if neighborVertex.isSettlement: canSettle = False; break
      #       print "Jumped to neighbor at " + str((neighborVertex.X, neighborVertex.Y))
      #       for secondNeighbor in board.getNeighborVertices(neighborVertex):
      #         if secondNeighbor.isSettlement: canSettle = False; break
      #         print "Looking at neighbor " + str((secondNeighbor.X, secondNeighbor.Y))
      #     if canSettle: 
      #       print "Can settle!"
      #       legalActions.append((Actions.SETTLE, vertex))

      # Check each road for possible settlement locations (at ends of roads)
      for road in agent.roads:
        roadEnds = board.getUnoccupiedRoadEndpoints(road)

        # Look at the unoccupied endpoints (up to 3) of this road to see
        # if we can put a settlement here
        for roadEnd in roadEnds:
            if board.isValidSettlementLocation(roadEnd):
              if (Actions.SETTLE, roadEnd) not in legalActions:
                legalActions.append((Actions.SETTLE, roadEnd))


    # If they can build a road...
    if len(agent.resources) >= ROAD_COST:
      # for vertex in agent.settlements:
      #   vertexEdges = board.getEdgesOfVertex(vertex)
      #   for roadEdge in vertexEdges:
      #     if roadEdge.player == None: legalActions.append((Actions.ROAD, roadEdge))
      # for edge in agent.roads:
      #   vertices = board.getVertexEnds(edge)
      #   for vertex in vertices:
      #     if vertex.isSettlement: continue
      #     roadEdges = board.getEdgesOfVertex(vertex)
      #     for roadEdge in roadEdges: 
      #       if roadEdge.player == None: legalActions.append((Actions.ROAD, roadEdge))

      # Look at every space adjacent to all settlements
      for settlement in agent.settlements:
        unoccupiedNeighbors = board.getUnoccupiedNeighbors(settlement, diagonals=False)
        for neighbor in unoccupiedNeighbors:
          if (Actions.ROAD, neighbor) not in legalActions:
            legalActions.append((Actions.ROAD, neighbor))

      # Look at every unoccupied road endpoint of every road
      for road in agent.roads:
        unoccupiedEndpoints = board.getUnoccupiedRoadEndpoints(road)
        for unoccupiedEndpoint in unoccupiedEndpoints:
          if (Actions.ROAD, unoccupiedEndpoint) not in legalActions:
            legalActions.append((Actions.ROAD, unoccupiedEndpoint))

    return legalActions

  def generateSuccessor(self, playerIndex, action):
    # Check that successors exist
    #if self.gameOver(): raise Exception('Can\'t generate a successor of a terminal state.')
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
    initialSettlements = [board.getTile(2,2), board.getTile(4,4), board.getTile(4,0)]
    for i in range(numAgents):
      agents[i].settlements.append(initialSettlements[i])
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
      for ag in state.data.agents:
        oldResourceNum = len(ag.resources)
        ag.updateResources(state)
        if DEBUG: print "Agent " + str(ag.agentIndex) + " gained " + str(len(ag.resources) - oldResourceNum) + " resources.  Total: " + str(len(ag.resources))
      if DEBUG: print "\n"

      # get an action from the state
      action = agent.getAction(state)
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
  print "Resources: " + str(len(agent.resources))
  print "----------------------------"

  print "Took action " + str(action[0])
  print "The board now looks like this:"
  board.printBoard()
  print "\n\n\n"

gState = GameState() 
#initializes the game state
gState.initialize()
game = Game()
game.run(gState)
