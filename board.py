
from sets import Set
from enum import Enum

Actions = Enum(["DRAW", "SETTLE", "CITY", "ROAD", "TRADE"])
ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER", "NOTHING"])
Resources = ([ResourceTypes.BRICK, ResourceTypes.BRICK, ResourceTypes.BRICK,
  ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL,
  ResourceTypes.ORE, ResourceTypes.ORE, ResourceTypes.ORE,
  ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN,
  ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER,
  ResourceTypes.NOTHING])
NumberChits = [-1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

# A hexagon is a tile on the board and has a resource and a dice number
class Hexagon:

  def __init__(self, X, Y, resource, diceValue):
    self.X = X
    self.Y = Y
    self.resource = resource
    self.diceValue = diceValue

# Previously "Node"
# A vertex is an intersection between hexagons, a valid settlement location
class Vertex:

  def __init__(self, X, Y):
    self.X = X
    self.Y = Y
    self.player = None
    self.isSettlement = False
    self.isCity = False

  def settle(self, player):
    self.isSettlement = True
    self.player = player

  def upgrade(self):
    if (self.isSettlement):
      self.isCity = True
      self.isSettlement = False
    else:
      raise Exception, "Can't upgrade to a city without a settlement!"

# An edge is a path betwen Vertices, a valid road location
class Edge:
  def __init__(self, X, Y, player = None):
    self.X = X
    self.Y = Y
    self.player = player

# Keeps track of resource + numberchit
class Tile:
  def __init__(self, resource, number):
    self.resource = resource
    self.number = number

BeginnerLayout = ([[None, None, Tile(ResourceTypes.GRAIN, 9), None, None],
  [Tile(ResourceTypes.LUMBER, 11), Tile(ResourceTypes.WOOL, 12), Tile(ResourceTypes.BRICK, 5), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.GRAIN, 8)],
  [Tile(ResourceTypes.BRICK, 4), Tile(ResourceTypes.ORE, 6), Tile(ResourceTypes.GRAIN, 11), Tile(ResourceTypes.LUMBER, 4), Tile(ResourceTypes.ORE, 3)],
  [Tile(ResourceTypes.NOTHING, -1), Tile(ResourceTypes.LUMBER, 3), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.WOOL, 9), Tile(ResourceTypes.LUMBER, 6)],
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
  def __init__(self, layout):
    numRows = len(layout)
    numCols = len(layout[0])
    self.hexagons = [[0 for x in xrange(numCols)] for x in xrange(numRows)] 
    self.edges = [[0 for x in xrange(numCols*2+2)] for x in xrange(numRows*2+2)] 
    self.vertices = [[0 for x in xrange(numCols*2+2)] for x in xrange(numRows*2+2)] 
    for i in range(numRows):
      for j in range(numCols):
        tile = layout[i][j]
        if tile == None:
          self.hexagons[i][j] = None
        else:
          self.hexagons[i][j] = Hexagon(i, j, tile.resource, tile.number)
    for i in range(numRows*2+2):
      for j in range(numCols*2+2):
        self.vertices[i][j] = Vertex(i, j)
        self.edges[i][j] = Edge(i, j)

  def applyAction(self, playerIndex, action):
    if action[0] == Actions.SETTLE:
      vertex = action[1]
      vertex.settle(playerIndex)
    if action[0] == Actions.ROAD:
      edge = action[1]
      edge.player = playerIndex

  def getNeighborHexes(self, hex):
    neighbors = []
    x = hex.X
    y = hex.Y
    offset = 1
    if x % 2 != 0:
      offset = -1
    hexOne = self.hexagons[x][y+1]
    hexTwo = self.hexagons[x][y-1]
    hexThree = self.hexagons[x+1][y]
    hexFour = self.hexagons[x-1][y]
    hexFive = self.hexagons[x+1][y+offset]
    hexSix = self.hexagons[x-1][y+offset]
    if hexOne != None: neighbors.append(hexOne)
    if hexTwo != None: neighbors.append(hexTwo)
    if hexThree != None: neighbors.append(hexThree)
    if hexFour != None: neighbors.append(hexFour)
    if hexFive != None: neighbors.append(hexFive)
    if hexSix != None: neighbors.append(hexSix)
    return neighbors

  def getNeighborVertices(self, vertex):
    neighbors = []
    x = vertex.X
    y = vertex.Y
    # Logic from thinking that this is saying getEdgesOfVertex
    # and then for each edge getVertexEnds, taking out the three that are ==vertex
    if y < len(self.vertices[0])-1:
      vertexOne = self.vertices[x][y+1]
      if vertexOne != None: neighbors.append(vertexOne)
    if x < len(self.vertices)-1:
      vertexTwo = self.vertices[x+1][y]
      if vertexTwo != None: neighbors.append(vertexTwo)
    if x > 0:
      vertexThree = self.vertices[x-1][y]
      if vertexThree != None: neighbors.append(vertexThree)
    return neighbors

  def getVertices(self, hex):
    hexVertices = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    hexVertices.append(self.vertices[x][2*y+offset])
    hexVertices.append(self.vertices[x][2*y+1+offset])
    hexVertices.append(self.vertices[x][2*y+2+offset])
    hexVertices.append(self.vertices[x+1][2*y+offset])
    hexVertices.append(self.vertices[x+1][2*y+1+offset])
    hexVertices.append(self.vertices[x+1][2*y+2+offset])
    return hexVertices

  def getEdges(self, hex):
    hexEdges = []
    x = hex.X
    y = hex.Y
    offset = x % 2
    hexEdges.append(self.edges[2*x][2*y+offset])
    hexEdges.append(self.edges[2*x][2*y+1+offset])
    hexEdges.append(self.edges[2*x+1][2*y+offset])
    hexEdges.append(self.edges[2*x+1][2*y+2+offset])
    hexEdges.append(self.edges[2*x+2][2*y+offset])
    hexEdges.append(self.edges[2*x+2][2*y+1+offset])
    return hexEdges

  def getVertexEnds(self, edge):
    edgeVertices = []
    x = edge.X
    y = edge.Y
    vertexOne = self.vertices[(x-1)/2][y]
    vertexTwo = self.vertices[(x+1)/2][y]
    if x%2 == 0:
      vertexOne = self.vertices[x/2][y]
      vertexTwo = self.vertices[x/2][y+1]
    if vertexOne != None: edgeVertices.append(vertexOne)
    if vertexTwo != None: edgeVertices.append(vertexTwo)
    return edgeVertices

  def getEdgesOfVertex(self, vertex):
    vertexEdges = []
    x = vertex.X
    y = vertex.Y
    edgeOne = self.edges[x*2][y]
    edgeTwo = self.edges[x*2+1][y]
    edgeThree = self.edges[x*2-1][y]
    if edgeOne != None: vertexEdges.append(edgeOne)
    if edgeTwo != None: vertexEdges.append(edgeTwo)
    if edgeThree != None: vertexEdges.append(edgeThree)
    return vertexEdges

  def getHexes(self, vertex):
    vertexHexes = []
    x = vertex.X
    y = vertex.Y
    xOffset = x % 2
    yOffset = y % 2
    if x > 0 and (y+xOffset) > 0:
      hexOne = self.hexagons[x-1][(y+xOffset)/2-1]
      if hexOne != None: vertexHexes.append(hexOne)
    if y > 0 and x-(1-yOffset) > 0:
      hexTwo = self.hexagons[x-(1-yOffset)*xOffset][(y-1)/2]
      if hexTwo != None: vertexHexes.append(hexTwo)
    if (y-xOffset) > 0 and (y-xOffset)/2 < len(self.hexagons[0]):
      hexThree = self.hexagons[x][(y-xOffset)/2]
      if hexThree != None: vertexHexes.append(hexThree)
    return vertexHexes
   

