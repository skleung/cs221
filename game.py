from agents import *
from board import BeginnerLayout, Board, Edge, Hexagon, Vertex
from gameConstants import *
from collections import Counter
from draw import *
import time

class GameState:
  """
  Class: GameState
  -------------------------------
  A class representing all information about the current state of the game.
  Includes a Board object representing the current state of the game board,
  as well as a list of all agents (players + random agents + other agents) in the game.
  -------------------------------
  """

  def __init__(self, layout = BeginnerLayout):
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
    
    self.board = Board(layout)
    self.playerAgents = [None] * NUM_PLAYERS

    # Make the dice agent
    self.diceAgent = DiceAgent()

  def deepCopy(self):
    copy = GameState()
    copy.board = self.board.deepCopy()
    copy.playerAgents = [playerAgent.deepCopy(copy.board) for playerAgent in self.playerAgents]
    return copy

  # def sortLegalActions(self, actions):


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
    legalActions = set( )
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
              legalActions.add((ACTIONS.ROAD, currEdge))

      # Look at all unoccupied edges coming from the player's existing roads
      for road in agent.roads:
        currVertices = self.board.getVertexEnds(road)
        for vertex in currVertices:
          if vertex.player != None and vertex.player != agentIndex: continue
          currEdges = self.board.getEdgesOfVertex(vertex)
          for currEdge in currEdges:
            if not currEdge.isOccupied(): 
              if (ACTIONS.ROAD, currEdge) not in legalActions:
                legalActions.add((ACTIONS.ROAD, currEdge)) 

    # If they can settle...
    if agent.canSettle():

      # Look at all unoccupied endpoints of the player's existing roads
      for road in agent.roads:
        possibleSettlements = self.board.getVertexEnds(road)
        for possibleSettlement in possibleSettlements:
          if possibleSettlement.canSettle:
            if (ACTIONS.SETTLE, possibleSettlement) not in legalActions:
              legalActions.add((ACTIONS.SETTLE, possibleSettlement))

    # If they can build a city...
    if agent.canBuildCity():
      # All current settlements are valid city locations
      for settlement in agent.settlements:
        legalActions.add((ACTIONS.CITY, settlement))
            
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
    copy = self.deepCopy()
    copy.playerAgents[playerIndex].applyAction(action, copy.board)
    copy.board.applyAction(playerIndex, action)
    return copy

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

  def updatePlayerResourcesForDiceRoll(self, diceRoll):
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
      if VERBOSE:
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

  def __init__(self, playerAgentNums = None):
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
    self.gameState = GameState()
    self.playerAgentNums = playerAgentNums 
    if GRAPHICS: self.draw = Draw(self.gameState.board.tiles)

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
      return PlayerAgentRandom("Player "+str(index), index, color)
    elif playerCode == 1:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, depth=DEPTH)
    elif playerCode == 2:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, depth=DEPTH,evalFn=builderEvalFn)
    elif playerCode == 3:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, depth=DEPTH,evalFn=resourceEvalFn)
    elif playerCode == 4:
      return PlayerAgentExpectimax("Player "+str(index), index, color, depth=DEPTH)
    elif playerCode == 5:
      return PlayerAgentExpectimax("Player "+str(index), index, color, depth=DEPTH,evalFn=builderEvalFn)
    elif playerCode == 6:
      return PlayerAgentExpectimax("Player "+str(index), index, color, depth=DEPTH,evalFn=resourceEvalFn)
    elif playerCode == 7:
      return PlayerAgentAlphaBeta("Player "+str(index), index, color, depth=DEPTH)
    elif playerCode == 8:
      return PlayerAgentAlphaBeta("Player "+str(index), index, color, depth=DEPTH,evalFn=builderEvalFn)
    elif playerCode == 9:
      return PlayerAgentAlphaBeta("Player "+str(index), index, color, depth=DEPTH,evalFn=resourceEvalFn)
    elif playerCode == 10:
      return PlayerAgentAlphaBeta("Player "+str(index), index, color, depth=DEPTH,evalFn=betterEvalFn)
    elif playerCode == 11:
      return PlayerAgentExpectimax("Player "+str(index), index, color, depth=DEPTH,evalFn=betterEvalFn)
    elif playerCode == 12:
      return PlayerAgentExpectiminimax("Player "+str(index), index, color, depth=DEPTH,evalFn=betterEvalFn)

  def initializePlayers(self):
    if (self.playerAgentNums == None):
      self.playerAgentNums = getPlayerAgentSpecifications()
    for i in xrange(NUM_PLAYERS):
      self.gameState.playerAgents[i] = self.createPlayer(self.playerAgentNums[i], i)

  def initializeSettlementsAndResourcesLumberBrick(self):
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #
    settlements = self.gameState.board.getRandomVerticesForSettlement()
    for i, playerSettlements in enumerate(settlements):
      agent = self.gameState.playerAgents[i]
      settleOne, settleTwo = playerSettlements
      agent.settlements.append(settleOne); 
      agent.settlements.append(settleTwo); 
      roadOne = self.gameState.board.getRandomRoad(settleOne)
      roadTwo = self.gameState.board.getRandomRoad(settleTwo)
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, roadOne))
      self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, roadTwo))
      agent.roads.append(roadOne);
      agent.roads.append(roadTwo);

    #add random settlement
    for i in range(len(self.gameState.playerAgents)):
      agent = self.gameState.playerAgents[i]
      for s in range(1):
        settlement = self.gameState.board.getRandomVertexForSettlement()
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, settlement))
        agent.settlements.append(settlement); 
        road = self.gameState.board.getRandomRoad(settlement)
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, road))
        agent.roads.append(road);

    # Each player starts with resources for each of their settlements
    for agent in self.gameState.playerAgents:
      agent.collectInitialResources(self.gameState.board)
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #

  def initializeSettlementsAndResourcesForSettlements(self):
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #
    settlements = self.gameState.board.getRandomVerticesForAllResources()
    for i, playerSettlements in enumerate(settlements):
      agent = self.gameState.playerAgents[i]
      for settlement in playerSettlements:
        randomRoad = self.gameState.board.getRandomRoad(settlement)
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, randomRoad))
        agent.settlements.append(settlement)
        agent.roads.append(randomRoad)
    # Each player starts with resources for each of their settlements
    for agent in self.gameState.playerAgents:
      agent.collectInitialResources(self.gameState.board)
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #

  def initializeSettlementsAndResourcesRandom(self):
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #
    for i in range(len(self.gameState.playerAgents)):
      agent = self.gameState.playerAgents[i]
      for s in range(NUM_INITIAL_SETTLEMENTS):
        settlement = self.gameState.board.getRandomVertexForSettlement()
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, settlement))
        agent.settlements.append(settlement); 
        road = self.gameState.board.getRandomRoad(settlement)
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, road))
        agent.roads.append(road);

    # Each player starts with resources for each of their settlements
    for agent in self.gameState.playerAgents:
      agent.collectInitialResources(self.gameState.board)
    # --- START RESOURCE/SETTLEMENT RANDOM INITIALIZATION --- #

  def initializeSettlementsAndResourcesPreset(self):
    # --- START RESOURCE/SETTLEMENT PRESET INITIALIZATION --- #
    # Each player starts with 2 settlements
    # # Use beginner board suggested settlements
    initialSettlements = ([
      (self.gameState.board.getVertex(2, 4), self.gameState.board.getVertex(4, 8)),
      (self.gameState.board.getVertex(2, 8), self.gameState.board.getVertex(3, 5)),
      (self.gameState.board.getVertex(3, 1), self.gameState.board.getVertex(4, 3)), # unused
      (self.gameState.board.getVertex(1, 4), self.gameState.board.getVertex(4, 6)) # unused
      ]) 
    initialRoads = ([
      (self.gameState.board.getEdge(4, 3), self.gameState.board.getEdge(8, 8)),
      (self.gameState.board.getEdge(4, 7), self.gameState.board.getEdge(6, 4)),
      (self.gameState.board.getEdge(6, 1), self.gameState.board.getEdge(8, 3)), # unused
      (self.gameState.board.getEdge(2, 3), self.gameState.board.getEdge(8, 6)) # unused
      ])

    # Pick two settlements at random and two roads that connect from them
    for i in range(len(self.gameState.playerAgents)):
      agent = self.gameState.playerAgents[i]
      for s in range(NUM_INITIAL_SETTLEMENTS):
        settlement = initialSettlements[i][s]
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.SETTLE, settlement))
        agent.settlements.append(settlement); 
        road = initialRoads[i][s]
        self.gameState.board.applyAction(agent.agentIndex, (ACTIONS.ROAD, road))
        agent.roads.append(road);

    # Each player starts with resources for each of their settlements
    for agent in self.gameState.playerAgents:
      agent.collectInitialResources(self.gameState.board)
    # --- START RESOURCE/SETTLEMENT PRESET INITIALIZATION --- #

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
    if VERBOSE:
      print "WELCOME TO SETTLERS OF CATAN!"
      print "-----------------------------"
    # DEBUG = True if raw_input("DEBUG mode? (y/n) ") == "y" else False
    self.initializePlayers()
    # self.initializeSettlementsAndResourcesPreset()
    # self.initializeSettlementsAndResourcesRandom()
    self.initializeSettlementsAndResourcesForSettlements()
    # Turn tracking
    turnNumber = 1
    currentAgentIndex = 0
    # Main game loop
    while (self.gameState.gameOver() < 0):
      # Draw the gameboard
      if GRAPHICS: self.drawGame()
      # Initial information
      currentAgent = self.gameState.playerAgents[currentAgentIndex]
      if VERBOSE:
        print "---------- TURN " + str(turnNumber) + " --------------"
        print "It's " + str(currentAgent.name) + "'s turn!"

      # Print player info
      if VERBOSE:
        print "PLAYER INFO:"
        for a in self.gameState.playerAgents:
          print a

      if GRAPHICS: raw_input("Press ENTER to proceed:")
      # Dice roll + resource distribution
      diceRoll = self.gameState.diceAgent.rollDice()
      if VERBOSE: print "Rolled a " + str(diceRoll)
      self.gameState.updatePlayerResourcesForDiceRoll(diceRoll)
      # The current player performs 1 action
      value, action = currentAgent.getAction(self.gameState)
      if VERBOSE: 
        print "Best Action: " + str(action)
        print "Best Value: " + str(value)
      currentAgent.applyAction(action, self.gameState.board)
      self.gameState.board.applyAction(currentAgent.agentIndex, action)
      
      if VERBOSE:# Print out the updated game state
        if (action != None):
          print str(currentAgent.name) + " took action " + str(action[0]) + " at " + str(action[1]) + "\n"
        else:
          print str(currentAgent.name) + " had no actions to take"
      # Track the game's move history
      self.moveHistory.append((currentAgent.name, action))
      # Go to the next player/turn
      currentAgentIndex = (currentAgentIndex+1) % self.gameState.getNumPlayerAgents()
      turnNumber += 1

      # Caps the total number of iterations for a game
      if turnNumber > CUTOFF_TURNS: break

    winner = self.gameState.gameOver()
    if winner < 0: return (winner, turnNumber, -1)
    agentWinner = self.gameState.playerAgents[winner]
    agentLoser = self.gameState.playerAgents[1-winner]
    if VERBOSE: print agentWinner.name + " won the game"
    return (winner, turnNumber, agentWinner.victoryPoints - agentLoser.victoryPoints)

def getStringForPlayer(playerCode):
  return ({
    0: "Random Agent",
    1: "ExpectiMiniMax Agent - with default heuristic",
    2: "ExpectiMiniMax Agent - with builder Heuristic",
    3: "ExpectiMiniMax Agent - with resource Heuristic",
    4: "Expectimax Agent - with default heuristic",
    5: "Expectimax Agent - with builder Heuristic",
    6: "Expectimax Agent - with resource Heuristic",
    7: "AlphaBeta Agent - with default Heuristic",
    8: "AlphaBeta Agent - with builder Heuristic",
    9: "AlphaBeta Agent - with resource Heuristic",
    10: "AlphaBeta Agent - with better Heuristic",
    11: "Expectimax Agent - with better Heuristic",
    12: "Expectiminimax Agent - with better Heuristic"
  }.get(playerCode, "Not a player."))

def getPlayerAgentSpecifications():
  if VERBOSE:
    print "Player Agent Specifications:"
    print "-----------------------------"
    print "0: Random Agent"
    print "1: ExpectiMiniMax Agent - with default heuristic"
    print "2: ExpectiMiniMax Agent - with builder Heuristic"
    print "3: ExpectiMiniMax Agent - with resource Heuristic"
    print "4: Expectimax Agent - with default heuristic"
    print "5: Expectimax Agent - with builder Heuristic"
    print "6: Expectimax Agent - with resource Heuristic"
    print "7: AlphaBeta Agent - with default Heuristic"
    print "8: AlphaBeta Agent - with builder Heuristic"
    print "9: AlphaBeta Agent - with resource Heuristic"
    print "10: AlphaBeta Agent - with better Heuristic"
    print "11: Expectimax Agent - with better Heuristic"
    print "12: Expectiminimax Agent - with better Heuristic"

    firstPlayerAgent = int(raw_input("Which player type should the first player be: ").strip())
    secondPlayerAgent = int(raw_input("Which player type should the second player be: ").strip())
    return [firstPlayerAgent, secondPlayerAgent]
  else:
    return DEFAULT_PLAYER_ARRAY

# We now have 7 agents including the alpha beta agents
NUM_ITERATIONS = int(raw_input("Enter number of iterations: "));
DEPTH = int(raw_input("Enter depth of recursion for non-random agents: "));
playerAgentNums = getPlayerAgentSpecifications()

numWins = {}
totalVictoryPointDiff = {}
totalTurns = {}
debugStatistics = []

for player in range(2):
  numWins[player] = 0
  totalVictoryPointDiff[player] = 0
  totalTurns[player] = 0

START_TIME = time.time()
for i in range(NUM_ITERATIONS): # for multiple iterations
  print "STARTING GAME " + str(i) + ": "
  game = Game(playerAgentNums = playerAgentNums)
  stats = game.run()
  debugStatistics.append(stats)
  winner, turns, diffPoints = stats
  if winner < 0: 
    print "**did not finish**"
    continue
  numWins[winner]+=1
  totalVictoryPointDiff[winner] += diffPoints
  totalTurns[winner] += turns

print "============="
print "\nGame statistics for " + str(NUM_ITERATIONS) + " iterations and depth " + str(DEPTH) + ": "
print "Player 0: "+ getStringForPlayer(playerAgentNums[0])
print "Player 1: "+ getStringForPlayer(playerAgentNums[1])
print "============="
# print debugStatistics
# player is the player num, not the type of player
totalWins = 0
for player, wins in numWins.iteritems():
  totalWins += wins
  playerType = playerAgentNums[player]
  if wins >= 0: print "PlayerAgent " + str(player) + " (" + getStringForPlayer(playerType) + ") won "+str(wins)+ " games."
  if wins > 0:
    print "With an average of " + str(totalVictoryPointDiff[player]/float(wins)) + " victory points difference per game."
    print "     an average of " + str(totalTurns[player]/float(wins)) + " turns to win game."
    print " and an average of " + str(float(time.time()-START_TIME)/NUM_ITERATIONS) + " seconds per game."
print "============="
for player in numWins:
  if totalWins == 0:
    totalWins = 1
  print "Player " + str(player) + " win percentage: "+str(float(numWins[player])/totalWins)
print "Total elapsed time: "+str(float(time.time()-START_TIME))
print "\n"

