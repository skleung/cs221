from gameUtil import *
import random
from board import *
from enum import Enum

VICTORY_POINTS_TO_WIN = 10
STARTING_NUM_OF_CARDS = 7
SETTLEMENT_POINTS = 3

Actions = Enum(["DRAW", "SETTLE", "CITY", "ROAD", "TRADE"])
"""
This class defines a player agent and allows a user to retrieve possible actions from the agent
hand = a list of Cards that the agent holds
victoryPoints = the number of victory points the agent has
"""
class Agent:
  def __init__(self, name, agentIndex):
    self.name = name
    self.agentIndex = agentIndex
    self.victoryPoints = 0
    # TODO(sierrakn): Make this a dict
    self.resources = ([ResourceTypes.WOOL, ResourceTypes.BRICK, 
      ResourceTypes.ORE, ResourceTypes.GRAIN, ResourceTypes.LUMBER])
    # List of edges
    self.roads = []
    # List of vertices
    self.settlements = []
  # to string method will print the agent's name
  def __str__(self):
    return self.name
  
  """
  The Agent will receive a GameState and returns a tuple containing string and its metadata
  (e.g. ('settle', metadata telling where the agent decided to settle))
  """
  def getAction(self, state):
    #TODO: get the "best" action according to minimax?
    legalActions = state.getLegalActions(self.agentIndex)
    if len(legalActions) < 1:
      raise Exception("Game has ended")
    return legalActions[0]

  def applyAction(self, action):
    if action[0] == Actions.SETTLE:
      self.settlements.append(action[1])
      self.victoryPoints = self.victoryPoints + SETTLEMENT_POINTS
      for i in range(4): self.resources.pop()
    if action[0] == Actions.ROAD:
      self.roads.append(action[1])
      for i in range(3): self.resources.pop()

  # TODO(sierrakn): Actually roll dice and distribute resources accordingly
  def updateResources(self, state):
    totalHexes = Set()
    for vertex in self.settlements:
      hexes = state.data.board.getHexes(vertex)
      for hex in hexes: totalHexes.add(hex) # avoid duplicates
    for hex in totalHexes:
      self.resources.append(ResourceTypes.WOOL)

  def drawCard(self, state):
    card = state.data.deck.drawCard()
    if card.value == "Victory":
      self.victoryPoints += 1
    self.hand.append(card)

  """
  Kicks off the game, decides where to settle and build a road in the very first move of the game
  """
  def initialize(self, state):
    return
    # for i in range(STARTING_NUM_OF_CARDS):
    #   self.drawCard(state)

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
    self.deck = Deck()
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
    board = Board(BeginnerLayout)
    # initializes the game state's data with the number of agents and the player agents
    self.data.initialize(agents, board)
    for agent in self.data.agents:
      agent.initialize(self)

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
    if len(agent.resources) > 3:
      for edge in agent.roads:
        # TODO(sierrakn): smarter way to check if two away from settlement?
        vertices = board.getVertexEnds(edge)
        for vertex in vertices:
          canSettle = True
          if vertex.isSettlement: canSettle = False; continue
          for neighborVertex in board.getNeighborVertices(vertex):
            if neighborVertex.isSettlement: canSettle = False; break
            for secondNeighbor in board.getNeighborVertices(neighborVertex):
              if secondNeighbor.isSettlement: canSettle = False; break
          if canSettle: 
            legalActions.append((Actions.SETTLE, vertex))
    # build road connecting to either settlement or road
    if len(agent.resources) > 2:
      for vertex in agent.settlements:
        vertexEdges = board.getEdgesOfVertex(vertex)
        for roadEdge in vertexEdges:
          if roadEdge.player == None: legalActions.append((Actions.ROAD, roadEdge))
      for edge in agent.roads:
        vertices = board.getVertexEnds(edge)
        for vertex in vertices:
          if vertex.isSettlement: continue
          roadEdges = board.getEdgesOfVertex(vertex)
          for roadEdge in roadEdges: 
            if roadEdge.player == None: legalActions.append((Actions.ROAD, roadEdge))

    return legalActions

  def generateSuccessor(self, playerIndex, action):
    # Check that successors exist
    if self.gameOver(): raise Exception('Can\'t generate a successor of a terminal state.')
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
    agentIndex = 0
    agents = state.data.agents
    board = state.data.board
    numAgents = len(agents)
    # every player chooses where to put first settlement
    # for agentIndex in range(numAgents):
    initialSettlements = [board.vertices[3][1], board.vertices[1][7], board.vertices[4][7]]
    for i in range(numAgents):
      agents[i].settlements.append(initialSettlements[i])
      initialSettlements[i].settle(i)
    while (state.gameOver() < 0):
      agent = agents[agentIndex]
      # roll dice
      # TODO(sierrakn): Actually roll dice and distribute resources accordingly
      for ag in state.data.agents:
        ag.updateResources(state)
      # get an action from the state
      action = agent.getAction(state)
      print agentIndex
      print action
      agent.applyAction(action)
      board.applyAction(agent.agentIndex, action)
      # store move history
      self.moveHistory.append((agent.name, action))
      agentIndex = (agentIndex+1) % numAgents

    print state.data.agents[state.gameOver()], " won the game"

gState = GameState() 
#initializes the game state
gState.initialize()
game = Game()
game.run(gState)
