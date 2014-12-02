from agents import PlayerAgent, DiceAgent, PlayerAgentExpectiminimax, PlayerAgentRandom
from board import BeginnerLayout, Board, Edge, Hexagon, Vertex
from collections import Counter
from draw import *


class GameState:
  """
  Class: GameState
  -------------------------------
  A class representing all information about the current state of the game.
  Includes a Board object representing the current state of the game board,
  as well as a list of all agents (players + random agents + other agents) in the game.
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
      self.playerAgents = [playerAgent.deepCopy(self.board) for playerAgent in prevState.playerAgents]

    else:
      self.board = Board(layout)
      self.playerAgents = [None] * NUM_PLAYERS

    # Make the dice agent
    self.diceAgent = DiceAgent()

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
    agent = self.playerAgents[agentIndex]

    # If they can build a road...
    if agent.canBuildRoad():

      # Look at all unoccupied edges coming from the player's existing settlements and cities
      agentSettlements = []; agentSettlements.extend(agent.settlements); agentSettlements.extend(agent.cities)
      for settlement in agentSettlements:
        currEdges = self.board.getEdgesOfVertex(settlement)
        for currEdge in currEdges:
          if not currEdge.isOccupied():
            if (ACTIONS.ROAD, currEdge) not in legalActions:
              legalActions.append((ACTIONS.ROAD, currEdge))

      # Look at all unoccupied edges coming from the player's existing roads
      for road in agent.roads:
        currVertices = self.board.getVertexEnds(road)
        for vertex in currVertices:
          if vertex.player != None and vertex.player != agentIndex: continue
          currEdges = self.board.getEdgesOfVertex(vertex)
          for currEdge in currEdges:
            if not currEdge.isOccupied(): 
              if (ACTIONS.ROAD, currEdge) not in legalActions:
                legalActions.append((ACTIONS.ROAD, currEdge)) 

    # If they can settle...
    if agent.canSettle():

      # Look at all unoccupied endpoints of the player's existing roads
      for road in agent.roads:
        possibleSettlements = self.board.getVertexEnds(road)
        for possibleSettlement in possibleSettlements:
          if possibleSettlement.canSettle:
            if (ACTIONS.SETTLE, possibleSettlement) not in legalActions:
              legalActions.append((ACTIONS.SETTLE, possibleSettlement))

    # If they can build a city...
    if agent.canBuildCity():

      # All current settlements are valid city locations
      for settlement in agent.settlements:
        if (ACTIONS.CITY, settlement) not in legalActions:
          legalActions.append((ACTIONS.CITY, settlement))
            
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
    state.playerAgents[playerIndex].applyAction(action)
    state.board.applyAction(playerIndex, action)
    return state

  def getNumPlayerAgents(self):
    """
    Method: getNumPlayerAgents
    ----------------------------
    Parameters: NA
    Returns: the number of PLAYER agents (players) in the game
    ----------------------------
    """
    return len(self.playerAgents)

  def gameOver(self):
    """
    Method: gameOver
    ----------------------------
    Parameters: NA
    Returns: the index of the player that has won, or -1 if the game has not ended
    ----------------------------
    """
    # See if any of the agents have won
    for agent in self.playerAgents:
      if agent.hasWon():
        return agent.agentIndex
    return -1

  def updatePlayerResourcesForDiceRoll(self, diceRoll, verbose = False):
    """
    Method: updatePlayerResourcesForDiceRoll
    -----------------------------------------
    Parameters:
      diceRoll - the dice total of the 2 rolled 6-sided dice
        to use to distribute more resources
    Returns: NA

    Updates the resource counts of all agents based on the
    given dice roll.
    -----------------------------------------
    """
    for agent in self.playerAgents:
      gainedResources = agent.updateResources(diceRoll, self.board)
      if verbose:
        print str(agent.name) + " received: " + str(gainedResources)
        print str(agent.name) + " now has: " + str(agent.resources)


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
    self.draw = Draw(self.gameState.board.tiles)

  def drawGame(self):
    """
    Method: drawGame
    ----------------------
    Parameters: NA
    Returns: NA

    Draws the graphics for displaying the board
    tiles.
    ----------------------
    """
    self.draw.drawBG()
    self.draw.drawTitle()
    self.draw.drawBoard()
    # draw.drawDiceRoll()
    # draw.drawPlayer(self.curPlayer)
    #draw.drawKey(self)
    self.draw.drawRoads(self.gameState.board.allRoads, self.gameState.board)
    self.draw.drawSettlements(self.gameState.board.allSettlements)
    self.draw.drawCities(self.gameState.board.allCities)
    # else: #gameOver is true
    #     draw.drawWinner(self) #draw winning screen
    #     self.hideButtons()          #hide all buttons 
    #     self.f.place(x=20, y=565)   #except for New Game button

  def createPlayer(self, playerCode, index):
    color = getColorForPlayer(index)

    if playerCode == 0:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color)
    elif playerCode == 1:
      return PlayerAgentRandom("Player "+str(index), index, color)
    elif playerCode == 2:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, evalFn=builderEvalFn)
    elif playerCode == 3:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, evalFn=resourceEvalFn)

  def initializePlayers(self):
    print "Player Agent Specifications:"
    print "-----------------------------"
    print "0: ExpectiMiniMax Agent - with default heuristic"
    print "1: Random Agent"
    print "2: ExpectiMiniMax Agent - with builder Heuristic"
    print "3: ExpectiMiniMax Agent - with resource Heuristic"

    playerAgentStr = raw_input("Enter your specifications (Press ENTER for '0 1'):").strip()
    playerAgentStr = '0 1' if playerAgentStr is "" else playerAgentStr

    playerAgents = [int(num) for num in playerAgentStr.split(" ")]    

    for i in xrange(NUM_PLAYERS):
      self.gameState.playerAgents[i] = self.createPlayer(playerAgents[i], i)

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
    # Welcome message
    print "WELCOME TO SETTLERS OF CATAN!"
    print "-----------------------------"
    DEBUG = True if raw_input("DEBUG mode? (y/n) ") == "y" else False
    self.initializePlayers()

    # --- START RESOURCE/SETTLEMENT INITIALIZATION --- #

    # Each player starts with 2 settlements
    # Use beginner board suggested settlements
    initialSettlements = ([
      (self.gameState.board.getVertex(2, 4), self.gameState.board.getVertex(3, 5)),
      (self.gameState.board.getVertex(1, 4), self.gameState.board.getVertex(4, 6))])

    initialRoads = ([
      (self.gameState.board.getEdge(4, 3), self.gameState.board.getEdge(6, 4)),
       (self.gameState.board.getEdge(2, 3), self.gameState.board.getEdge(8, 6)),])
    # Use % to essentially loop through and assign a settlement to each agent until
    # there are no more settlements to assign
    # ASSUMPTION: len(initialSettlements) is a clean multiple of # agents
    for i in range(len(self.gameState.playerAgents)):
      agent = self.gameState.playerAgents[i % self.gameState.getNumPlayerAgents()]
      settleOne, settleTwo = initialSettlements[i]
      roadOne, roadTwo = initialRoads[i]
      agent.settlements.append(settleOne); agent.settlements.append(settleTwo)
      agent.roads.append(roadOne); agent.roads.append(roadTwo)
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, settleOne))
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, settleTwo))
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, roadOne))
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, roadTwo))

    # Each player starts with resources for each of their settlements
    for agent in self.gameState.playerAgents:
      agent.collectInitialResources(self.gameState.board)

    # --- END RESOURCE/SETTLEMENT INITIALIZATION --- #

    # Turn tracking
    turnNumber = 1
    currentAgentIndex = 0

    # Main game loop
    while (self.gameState.gameOver() < 0):

      # Draw the gameboard
      self.drawGame()

      # Initial information
      currentAgent = self.gameState.playerAgents[currentAgentIndex]
      print "---------- TURN " + str(turnNumber) + " --------------"
      print "It's " + str(currentAgent.name) + "'s turn!"

      # Print player info
      if DEBUG:
        print "PLAYER INFO:"
        for a in self.gameState.playerAgents:
          print a

      raw_input("Press ENTER to proceed:")
      
      # Dice roll + resource distribution
      diceRoll = self.gameState.diceAgent.rollDice()
      print "Rolled a " + str(diceRoll)
      self.gameState.updatePlayerResourcesForDiceRoll(diceRoll, verbose = DEBUG)

      # The current player performs 1 action
      value, action = currentAgent.getAction(self.gameState)
      if DEBUG: 
        print "Best Action: " + str(action)
        print "Best Value: " + str(value)
      
      currentAgent.applyAction(action)
      self.gameState.board.applyAction(currentAgent.agentIndex, action)

      # Print out the updated game state
      if (action != None):
        print str(currentAgent.name) + " took action " + str(action[0]) + " at " + str(action[1]) + "\n"
      else:
        print str(currentAgent.name) + " had no actions to take"
      
      print currentAgent

      # Track the game's move history
      self.moveHistory.append((currentAgent.name, action))
      
      # Go to the next player/turn
      currentAgentIndex = (currentAgentIndex+1) % self.gameState.getNumPlayerAgents()
      turnNumber += 1

    print self.gameState.playerAgents[self.gameState.gameOver()].name + " won the game"
    return self.gameState.gameOver()


game = Game()
# for i in range(100): # for multiple iterations
game.run()
