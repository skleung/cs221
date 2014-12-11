
# CHANGES - Vertex canSettle -> occupied(), Hexagon tostring
from sets import Set
from enum import Enum
from collections import Counter
from gameConstants import *
import math
import random

# Different resource types a tile could have
ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER" ,"NOTHING"])
# A dictionary from resource type (enum, above) to string representation
# so we can print out the resource type easily
ResourceDict = {ResourceTypes.GRAIN:"G", ResourceTypes.WOOL:"W", ResourceTypes.ORE:"O", ResourceTypes.LUMBER:"L", ResourceTypes.BRICK:"B", ResourceTypes.NOTHING:"N"}

# ---------- DELETE? ----------- #
# Resources = ([ResourceTypes.BRICK, ResourceTypes.BRICK, ResourceTypes.BRICK,
#   ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL,
#   ResourceTypes.ORE, ResourceTypes.ORE, ResourceTypes.ORE,
#   ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN,
#   ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER,
#   ResourceTypes.NOTHING])
# NumberChits = [-1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
# ---------- DELETE? ----------- #

class Hexagon:
  """
  Class: Hexagon
  ---------------------------
  A Hexagon represents a single resource tile on our gameboard.
  A Hexagon has a resource type (of type ResourceTypes.__),
  a roll number (indicating what number marker has been placed on it),
  and the x and y coordinate of the hexagon in the gameboard.
  ---------------------------
  """

  def __init__(self, X, Y, resource, diceValue):
    self.X = X
    self.Y = Y
    self.resource = resource
    self.diceValue = diceValue

  def deepCopy(self):
    """
    Method: deepCopy
    --------------------------
    Parameters: NA
    Returns: a deep copy of self (with all instance variables
      properly copied)
    --------------------------
    """
    return Hexagon(self.X, self.Y, self.resource, self.diceValue)

  def __repr__(self):
    """
    Method: __repr__
    --------------------------
    Parameters: NA
    Returns: a string representation of self including
      the resource type (as a string) and the assigned
      roll value.  E.g. /L4\\ for a lumber hexagon
      with dice roll number 4.
    --------------------------
    """
    coordinateString = " (" + str(self.X) + ", " + str(self.Y) + ")"
    return "/" + ResourceDict[self.resource] + str(self.diceValue) + coordinateString + "\\"


class Vertex:
  """
  Class: Vertex
  ---------------------------
  (Previously the Node class).  A Vertex is an intersection
  between multiple Hexagons (up to 3, but as few as 1).  A
  Vertex represents a possible settlement location on the board.
  It has its x and y coordinate in the game board, And information
  about what is built on this Vertex including whether or not it
  it is a settlement or city, and what player (if any) has occupied
  this Vertex.  A Vertex can later be settled on (only once)
  by a player, or upgraded (by that player only) from a settlement
  to a city.
  ---------------------------
  """

  def __init__(self, X, Y):
    self.X = X
    self.Y = Y

    # Initially this Vertex is unsettled
    self.player = None
    self.isSettlement = False
    self.isCity = False
    self.canSettle = True

  def equivLocation(self, other):
    if other.X == self.X and other.Y == self.Y: return True
    return False

  def isOccupied(self):
    """
    Method: isOccupied
    --------------------------
    Parameters: NA
    Returns: Whether or not this Vertex has already been
      built on (settlement or city) by a player
    --------------------------
    """
    return self.isSettlement or self.isCity

  def deepCopy(self):
    """
    Method: deepCopy
    --------------------------
    Parameters: NA
    Returns: a deep copy of self (with all instance variables
      properly copied)
    --------------------------
    """
    copy = Vertex(self.X, self.Y)
    copy.player = self.player
    copy.isSettlement = self.isSettlement
    copy.isCity = self.isCity
    copy.canSettle = self.canSettle
    return copy

  def settle(self, playerIndex):
    """
    Method: settle
    --------------------------
    Parameters:
      playerIndex: the index of the player that is building a settlement
    Returns: NA

    Marks this Vertex as settled by the given player index.
    This "builds" a settlemement on this Vertex owned
    by the given player index.  Raises an exception if there
    is already a settlement built on this Vertex.
    --------------------------
    """
    if self.isSettlement:
      raise Exception("Can't settle here - already settled by player " + str(self.player) + "! At " + str(self))
    elif self.isCity:
      raise Exception("Can't settle here - already a city owned by player " + str(self.player) + "! At " + str(self))

    self.isSettlement = True
    self.player = playerIndex
    self.canSettle = False

  def upgrade(self, playerIndex):
    """
    Method: settle
    --------------------------
    Parameters:
      player: the player that is upgrading to a city
    Returns: NA

    Upgrades this Vertex from a settlement to a city.
    Raises an exception if this Vertex has not yet been
    settled, if a city already exists here, or if a different
    player is upgrading to a city than the one that built
    the original settlement.
    --------------------------
    """
    # Throws exception if this vertex has not been settled, or is being
    # upgraded by a different player than the one who settled
    if self.isCity:
      raise Exception("Player " + str(self.player) + " already built a city here!")
    elif not self.isSettlement:
      raise Exception("Player " + str(playerIndex) + " can't upgrade to a city without building a settlement first!")
    elif self.player != playerIndex:
      raise Exception("Player " + str(playerIndex) + " is trying to upgrade Player " + str(self.player) + "'s settlement!")
      
    # Mark as a city and not a settlement
    self.isCity = True
    self.isSettlement = False

  def __repr__(self):
    """
    Method: __repr__
    --------------------------
    Parameters: NA
    Returns: a string representation of self including
      whether or not there is a settlement or city here
      and if so, which player controls the settlement/city.
      E.g. 'S3' means a settlement owned by player 3.  'C5' means
      a city owned by player 5. '--' means this vertex is unoccupied.
    --------------------------
    """
    coordinateString = " (" + str(self.X) + ", " + str(self.Y) + ")"

    s = ""
    if self.isOccupied():
      if self.isSettlement:
        s = "S"
      elif self.isCity:
        s = "C"

      return s + str(self.player) + coordinateString

    elif not self.canSettle:
      return "Unsettlable" + coordinateString
    else:
      return "Unoccupied" + coordinateString

class Edge:
  """
    Class: Edge
    --------------------------
    An Edge represents the edge of a Hexagon, and also connects
    two Vertexes together (like a graph).  On the board,
    an Edge represents a possible location to build a road.
    It stores its X and Y coordinate in the game board, along
    with (optionally) the index of the player that built
    a road on this Edge.
    --------------------------
    """

  def __init__(self, X, Y, playerIndex = None):
    self.X = X
    self.Y = Y
    self.player = playerIndex

  def equivLocation(self, other):
    if other.X == self.X and other.Y == self.Y: return True
    return False

  def isOccupied(self):
    """
    Method: isOccupied
    --------------------------
    Parameters: NA
    Returns: whether or not a road has been built
      on this Edge.
    --------------------------
    """
    return self.player != None

  def deepCopy(self):
    """
    Method: deepCopy
    --------------------------
    Parameters: NA
    Returns: a deep copy of self (with all instance variables
      properly copied)
    --------------------------
    """
    return Edge(self.X, self.Y, self.player)
    
  def build(self, playerIndex):
    """
    Method: build
    --------------------------
    Parameters:
      playerIndex: the index of the player that is building on this Edge
    Returns: NA

    Builds a new road on behalf of the given player, and updates
    this Edge accordingly.  Raises an exception if a road has
    already been built on this Edge.
    --------------------------
    """
    if self.player != None:
      raise Exception("Player " + str(self.player) + " already has a road here! At " + str(self))
    self.player = playerIndex

  def __repr__(self):
    """
    Method: __repr__
    --------------------------
    Parameters: NA
    Returns: a string representation of self including
      whether or not a road was built on this edge, and if so,
      what player owns it.  E.g. 'R5' means a road owned by player 5,
      '--' means nothing is built on this edge.
    --------------------------
    """
    coordinateString = " (" + str(self.X) + ", " + str(self.Y) + ")"
    if self.isOccupied():
      return "R" + str(self.player) + coordinateString
    else:
      return "Unoccupied" + coordinateString


class Tile:
  def __init__(self, resource, number):
    self.resource = resource
    self.number = number

BeginnerLayout = ([[None, None, Tile(ResourceTypes.GRAIN, 9), None, None],
  [Tile(ResourceTypes.LUMBER, 11), Tile(ResourceTypes.WOOL, 12), Tile(ResourceTypes.BRICK, 5), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.GRAIN, 8)],
  [Tile(ResourceTypes.BRICK, 4), Tile(ResourceTypes.ORE, 6), Tile(ResourceTypes.GRAIN, 11), Tile(ResourceTypes.LUMBER, 4), Tile(ResourceTypes.ORE, 3)],
  [Tile(ResourceTypes.NOTHING, 7), Tile(ResourceTypes.LUMBER, 3), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.WOOL, 9), Tile(ResourceTypes.LUMBER, 6)],
  [None, Tile(ResourceTypes.BRICK, 8), Tile(ResourceTypes.ORE, 5), Tile(ResourceTypes.GRAIN, 2), None]])


"""
Board keeps track of hexagons, edges, and vertexes and how they relate
Data structure idea from http://stackoverflow.com/a/5040856
The rules are: "an hexagon at (x,y) is a neighbor of hexagons at (x, y(+/-)1), (x(+/-)1,y), 
and (x(+/-)1,y+1) for even xs or (x(+/-)1,y-1) for odd xs.
You consider an hexagon at (x,y) delimited by the vertices at positions 
(x,2y), (x,2y+1), (x,2y+2), (x+1,2y), (x+1,2y+1), and (x+1,2y+2), for even xs. 
For odd xs, add 1 to the y coordinate. 
The edges surrounding it are those at (2x,2y), (2x,2y+1), (2x+1, 2y), (2x+1,2y+2), (2x+2,2y), 
and (2x+2,2y+1), with an additional adjustment to y by adding one if x is odd."
A board with 19 tiles that looks like this:
    1   2   3
  4   5   6   7
8   9   10  11 12
 13  14   15  16
   17  18   19
will create a grid like this:
[N, N, 3,  N,   N]
[1, 2, 6,  7,  12]
[4, 5, 10, 11, 16]
[8, 9, 14, 15, 19]
[N, 13, 17, 18, N]
Which is necessary to know when creating layouts
"""
class Board:
  # Layout is just a double list of Tiles, some will be None
  def __init__(self, layout=None):
    if layout == None: raise Exception("Must pass layout to Board.")
    self.layout = layout
    random.seed()
    
    self.numRows = len(layout)
    self.numCols = len(layout[0])
    self.hexagons = [[None for x in xrange(self.numCols)] for x in xrange(self.numRows)] 
    self.edges = [[None for x in xrange(self.numCols*2+2)] for x in xrange(self.numRows*2+2)] 
    self.vertices = [[None for x in xrange(self.numCols*2+2)] for x in xrange(self.numRows*2+2)] 
    self.allSettlements = []
    self.allCities = []
    self.allRoads = []
    # This dictionary will map a tile's dice number to a list of tiles that that dice roll corresponds to
    self.dieRollDict = {}
    self.resourceDict = {}
    for i in range(self.numRows):
      for j in range(self.numCols):
        tile = layout[j][i] # Layout reverse, see above
        if tile == None:
          self.hexagons[i][j] = None
        else:
          self.hexagons[i][j] = Hexagon(i, j, tile.resource, tile.number)
          if tile.number in self.dieRollDict:
            self.dieRollDict[tile.number].append(self.hexagons[i][j])
          else:
            self.dieRollDict[tile.number] = [self.hexagons[i][j]]

          if tile.resource in self.resourceDict:
            self.resourceDict[tile.resource].append(self.hexagons[i][j])
          else:
            self.resourceDict[tile.resource] = [self.hexagons[i][j]]

    for row in self.hexagons:
      for hexagon in row:
        if hexagon == None: continue
        edgeLocations = self.getEdgeLocations(hexagon)
        vertexLocations = self.getVertexLocations(hexagon)
        for xLoc,yLoc in edgeLocations:
          if self.edges[xLoc][yLoc] == None:
            self.edges[xLoc][yLoc] = Edge(xLoc,yLoc)
        for xLoc,yLoc in vertexLocations:
          if self.vertices[xLoc][yLoc] == None:
            self.vertices[xLoc][yLoc] = Vertex(xLoc,yLoc)
    # brute forcing this because I don't want to debug
    if self.numRows == 5 and self.numCols == 5:
      self.visualBoard = [[None for x in xrange(self.numCols)] for x in xrange(self.numRows)] 
      rowZero = [None, None, self.hexagons[0][1], self.hexagons[1][1], self.hexagons[2][0]]
      self.visualBoard[0] = rowZero
      rowOne = [None, self.hexagons[0][2], self.hexagons[1][2], self.hexagons[2][1], self.hexagons[3][1]]
      self.visualBoard[1] = rowOne
      rowTwo = [self.hexagons[0][3], self.hexagons[1][3], self.hexagons[2][2], self.hexagons[3][2], self.hexagons[4][1]]
      self.visualBoard[2] = rowTwo
      rowThree = [None, self.hexagons[1][4], self.hexagons[2][3], self.hexagons[3][3], self.hexagons[4][2]]
      self.visualBoard[3] = rowThree
      rowFour = [None, None, self.hexagons[2][4], self.hexagons[3][4], self.hexagons[4][3]]
      self.visualBoard[4] = rowFour
    else: self.visualBoard = None
    self.tiles = []
    for row in self.visualBoard:
      for tile in row:
        if tile != None: self.tiles.append(tile)

  def printData(self):
    print self.hexagons
    print self.edges
    print self.vertices

  def deepCopy(self):
    copy = Board(self.layout)
    copy.hexagons = []
    for row in self.hexagons:
      copyHexRow = []
      for hexagon in row:
        if hexagon != None: copyHexRow.append(hexagon.deepCopy())
        else: copyHexRow.append(None)
      copy.hexagons.append(copyHexRow)
    copy.edges = []
    for row in self.edges:
      copyEdgeRow = []
      for edge in row:
        if edge != None: copyEdgeRow.append(edge.deepCopy())
        else: copyEdgeRow.append(None)
      copy.edges.append(copyEdgeRow)
    copy.vertices = []
    for row in self.vertices:
      copyVertexRow = []
      for vertex in row:
        if vertex != None: copyVertexRow.append(vertex.deepCopy())
        else: copyVertexRow.append(None)
      copy.vertices.append(copyVertexRow)
    copy.allSettlements = []
    for settlement in self.allSettlements:
      copy.allSettlements.append(settlement.deepCopy())
    copy.allRoads = []
    for road in self.allRoads:
      copy.allRoads.append(road.deepCopy())
    return copy

  def applyAction(self, playerIndex, action):
    if action is None:
      return
      
    if action[0] == ACTIONS.TRADE:
      return
      
    if action[0] == ACTIONS.SETTLE:
      actionVertex = action[1]
      vertex = self.getVertex(actionVertex.X, actionVertex.Y)
      vertex.settle(playerIndex)
      # All vertices one away are now unsettleable
      for neighborVertex in self.getNeighborVertices(vertex):
        neighborVertex.canSettle = False
      self.allSettlements.append(vertex)

    if action[0] == ACTIONS.ROAD:
      actionEdge = action[1]
      edge = self.getEdge(actionEdge.X, actionEdge.Y)
      edge.build(playerIndex)
      self.allRoads.append(edge)

    if action[0] == ACTIONS.CITY:
      actionVertex = action[1]
      vertex = self.getVertex(actionVertex.X, actionVertex.Y)
      vertex.upgrade(playerIndex)
      self.allCities.append(vertex)
      for settlement in self.allSettlements:
        if settlement.X == vertex.X and settlement.Y == vertex.Y:
          self.allSettlements.remove(settlement)
          break

  def getResourcesFromDieRollForPlayer(self, playerIndex, dieRoll):
    hexagons = self.dieRollDict[dieRoll] #retrieve the hexagons that correspond to that dice roll
    resources = []
    for hexagon in hexagons:
      for vertex in self.getVertices(hexagon):
        if vertex.player == playerIndex:
          if hexagon.resource != ResourceTypes.NOTHING:
            resources.append(hexagon.resource)
            if vertex.isCity: resources.append(hexagon.resource)

    return resources

  # Gives back a random hex corresponding to that resource
  def getRandomResourceHex(self, resource):
    return random.choice(self.resourceDict[resource])

  def getRandomVerticesForAllResources(self):
    resourcesForSettlement = [ResourceTypes.LUMBER, ResourceTypes.BRICK, ResourceTypes.WOOL, ResourceTypes.GRAIN]
    randomVerticesForBothPlayers = []
    for playerAgent in range(2):
      verticesForPlayer = []
      for resource in resourcesForSettlement:
        randomHex = self.getRandomResourceHex(resource)
        randomVertex = self.getRandomVertexOnHex(randomHex)
        self.applyAction(playerAgent, (ACTIONS.SETTLE, randomVertex))
        verticesForPlayer.append(randomVertex)
      randomVerticesForBothPlayers.append(verticesForPlayer)
    return randomVerticesForBothPlayers

  # return lumber hex num=index
  def getLumberHex(self, index):
    return ({
      1: self.hexagons[0][1],
      2: self.hexagons[3][2],
      3: self.hexagons[1][3],
      4: self.hexagons[4][3]
    }.get(index, None))

  def getBrickHex(self, index):
    return ({
      1: self.hexagons[2][1],
      2: self.hexagons[0][2],
      3: self.hexagons[1][4]
    }.get(index, None))

  def getRandomVertexOnHex(self, hex):
    vertices = self.getVertices(hex)
    vertex = None
    while vertex == None:
      index = random.randint(0, len(vertices)-1)
      vertex = vertices[index]
      if not vertex.canSettle: vertex = None
    return vertex

  # returns 4 locations for settlements
  def getRandomVerticesForSettlement(self):
    # get random lumber hexes
    lumberIndexOne = random.randint(1, 4)
    lumberIndexTwo = random.randint(1, 4)
    while lumberIndexTwo == lumberIndexOne:
      lumberIndexTwo = random.randint(1, 4)
    lumberHexOne = self.getLumberHex(lumberIndexOne)
    lumberHexTwo = self.getLumberHex(lumberIndexTwo)

    # get random brick hexes
    brickIndexOne = random.randint(1, 3)
    brickIndexTwo = random.randint(1, 3)
    while brickIndexTwo == brickIndexOne:
      brickIndexTwo = random.randint(1, 3)
    brickHexOne = self.getBrickHex(brickIndexOne)
    brickHexTwo = self.getBrickHex(brickIndexTwo)

    if (lumberHexOne.resource != ResourceTypes.LUMBER
      or lumberHexTwo.resource != ResourceTypes.LUMBER
      or brickHexOne.resource != ResourceTypes.BRICK
      or brickHexTwo.resource != ResourceTypes.BRICK): raise Exception("Should be a lumber or brick hex")

    vertexOne = self.getRandomVertexOnHex(lumberHexOne)
    self.applyAction(0, (ACTIONS.SETTLE, vertexOne))
    vertexTwo = self.getRandomVertexOnHex(brickHexOne)
    self.applyAction(0, (ACTIONS.SETTLE, vertexTwo))
    vertexThree = self.getRandomVertexOnHex(lumberHexTwo)
    self.applyAction(1, (ACTIONS.SETTLE, vertexThree))
    vertexFour = self.getRandomVertexOnHex(brickHexTwo)
    self.applyAction(1, (ACTIONS.SETTLE, vertexFour))
    return [(vertexOne, vertexTwo), (vertexThree, vertexFour)]

  def getRandomVertexForSettlement(self):
    vertex = None
    while vertex == None:
      vX = random.randint(0, len(self.vertices)-1)
      vY = random.randint(0, len(self.vertices[vX])-1)
      vertex = self.vertices[vX][vY]
      if vertex != None and not vertex.canSettle: vertex = None
    return vertex

  def getRandomRoad(self, vertex):
    edges = self.getEdgesOfVertex(vertex)
    randomEdge = None
    while randomEdge == None:
      randomEdge = edges[random.randint(0, len(edges)-1)]
      if randomEdge.isOccupied(): randomEdge = None
    return randomEdge

  def getEdge(self, x, y):
    return self.edges[x][y]

  def getVertex(self, x, y):
    return self.vertices[x][y]

  def getHex(self, x, y):
    return self.hexagons[x][y]

  def getNeighborHexes(self, hex):
    neighbors = []
    x = hex.X
    y = hex.Y
    offset = 1
    if x % 2 != 0:
      offset = -1

    if (y+1) < len(self.hexagons[x]):
      hexOne = self.hexagons[x][y+1]
      if hexOne != None: neighbors.append(hexOne)
    if y > 0:
      hexTwo = self.hexagons[x][y-1]
      if hexTwo != None: neighbors.append(hexTwo)
    if (x+1) < len(self.hexagons):
      hexThree = self.hexagons[x+1][y]
      if hexThree != None: neighbors.append(hexThree)
    if x > 0:
      hexFour = self.hexagons[x-1][y]
      if hexFour != None: neighbors.append(hexFour)
    if (y+offset) >= 0 and (y+offset) < len(self.hexagons[x]):
      if (x+1) < len(self.hexagons):
        hexFive = self.hexagons[x+1][y+offset]
        if hexFive != None: neighbors.append(hexFive)
      if x > 0:
        hexSix = self.hexagons[x-1][y+offset]
        if hexSix != None: neighbors.append(hexSix)
    return neighbors

  # Vertices connected to vertex via roads
  def getNeighborVerticesViaRoad(self, vertex, player):
    neighbors = []
    edgesOfVertex = getEdgesOfVertex(vertex)
    for edge in edgesOfVertex:
      if edge.player == player:
        vertexEnds = getVertexEnds(edge)
        for vertexEnd in vertexEnds:
          if vertexEnd != vertex: neighbors.append(vertexEnd)
    return neighbors

  def getNeighborVertices(self, vertex):
    neighbors = []
    x = vertex.X
    y = vertex.Y
    offset = -1
    if x % 2 == y % 2: offset = 1
    # Logic from thinking that this is saying getEdgesOfVertex
    # and then for each edge getVertexEnds, taking out the three that are ==vertex
    if (y+1) < len(self.vertices[0]):
      vertexOne = self.vertices[x][y+1]
      if vertexOne != None: neighbors.append(vertexOne)
    if y > 0:
      vertexTwo = self.vertices[x][y-1]
      if vertexTwo != None: neighbors.append(vertexTwo)
    if (x+offset) >= 0 and (x+offset) < len(self.vertices):
      vertexThree = self.vertices[x+offset][y]
      if vertexThree != None: neighbors.append(vertexThree)
    return neighbors

  # used to initially create vertices
  def getVertexLocations(self, hex):
    vertexLocations = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    offset = 0-offset
    vertexLocations.append((x, 2*y+offset))
    vertexLocations.append((x, 2*y+1+offset))
    vertexLocations.append((x, 2*y+2+offset))
    vertexLocations.append((x+1, 2*y+offset))
    vertexLocations.append((x+1, 2*y+1+offset))
    vertexLocations.append((x+1, 2*y+2+offset))
    return vertexLocations

  # used to initially create edges
  def getEdgeLocations(self, hex):
    edgeLocations = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    offset = 0-offset
    edgeLocations.append((2*x,2*y+offset))
    edgeLocations.append((2*x,2*y+1+offset))
    edgeLocations.append((2*x+1,2*y+offset))
    edgeLocations.append((2*x+1,2*y+2+offset))
    edgeLocations.append((2*x+2,2*y+offset))
    edgeLocations.append((2*x+2,2*y+1+offset))
    return edgeLocations

  # tested
  def getVertices(self, hex):
    hexVertices = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    offset = 0-offset
    hexVertices.append(self.vertices[x][2*y+offset]) # top vertex
    hexVertices.append(self.vertices[x][2*y+1+offset]) # left top vertex
    hexVertices.append(self.vertices[x][2*y+2+offset]) # left bottom vertex
    hexVertices.append(self.vertices[x+1][2*y+offset]) # right top vertex
    hexVertices.append(self.vertices[x+1][2*y+1+offset]) # right bottom vertex
    hexVertices.append(self.vertices[x+1][2*y+2+offset]) # bottom vertex
    return hexVertices

  def getEdges(self, hex):
    hexEdges = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    offset = 0-offset
    hexEdges.append(self.edges[2*x][2*y+offset])
    hexEdges.append(self.edges[2*x][2*y+1+offset])
    hexEdges.append(self.edges[2*x+1][2*y+offset])
    hexEdges.append(self.edges[2*x+1][2*y+2+offset])
    hexEdges.append(self.edges[2*x+2][2*y+offset])
    hexEdges.append(self.edges[2*x+2][2*y+1+offset])
    return hexEdges

  # returns (start, end) tuple
  def getVertexEnds(self, edge):
    x = edge.X
    y = edge.Y
    vertexOne = self.vertices[(x-1)/2][y]
    vertexTwo = self.vertices[(x+1)/2][y]
    if x%2 == 0:
      vertexOne = self.vertices[x/2][y]
      vertexTwo = self.vertices[x/2][y+1]
    return (vertexOne, vertexTwo)

  def getEdgesOfVertex(self, vertex):
    vertexEdges = []
    x = vertex.X
    y = vertex.Y
    offset = -1
    if x % 2 == y % 2: offset = 1
    edgeOne = self.edges[x*2][y-1]
    edgeTwo = self.edges[x*2][y]
    edgeThree = self.edges[x*2+offset][y]
    if edgeOne != None: vertexEdges.append(edgeOne)
    if edgeTwo != None: vertexEdges.append(edgeTwo)
    if edgeThree != None: vertexEdges.append(edgeThree)
    return vertexEdges

  # tested
  def getHexes(self, vertex):
    vertexHexes = []
    x = vertex.X
    y = vertex.Y
    xOffset = x % 2
    yOffset = y % 2

    if x < len(self.hexagons) and y/2 < len(self.hexagons[x]):
      hexOne = self.hexagons[x][y/2]
      if hexOne != None: vertexHexes.append(hexOne)

    weirdX = x
    if (xOffset+yOffset) == 1: weirdX = x-1
    weirdY = y/2 
    if yOffset == 1: weirdY += 1
    else: weirdY -= 1
    if weirdX >= 0 and weirdX < len(self.hexagons) and weirdY >= 0 and weirdY < len(self.hexagons):
      hexTwo = self.hexagons[weirdX][weirdY]
      if hexTwo != None: vertexHexes.append(hexTwo)

    if x > 0 and x < len(self.hexagons) and y/2 < len(self.hexagons[x]):
      hexThree = self.hexagons[x-1][y/2]
      if hexThree != None: vertexHexes.append(hexThree)
      
    return vertexHexes
   

