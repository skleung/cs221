
from sets import Set

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

class Enum(set):
  def __getattr__(self, name):
    if name in self:
      return name
    raise AttributeError

ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER", "NOTHING"])
Resources = ([ResourceTypes.BRICK, ResourceTypes.BRICK, ResourceTypes.BRICK,
  ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL,
  ResourceTypes.ORE, ResourceTypes.ORE, ResourceTypes.ORE,
  ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN,
  ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER,
  ResourceTypes.NOTHING])
NumberChits = [-1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

# Keeps track of resource + numberchit
class Tile:
  def __init__(self, resource, number):
    self.resource = resource
    self.number = number

BeginnerLayout = [([None, None, Tile(ResourceTypes.GRAIN, 9), None, None],
  [Tile(ResourceTypes.LUMBER, 11), Tile(ResourceTypes.WOOL, 12), Tile(ResourceTypes.BRICK, 5), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.GRAIN, 8)],
  [Tile(ResourceTypes.BRICK, 4), Tile(ResourceTypes.ORE, 6), Tile(ResourceTypes.GRAIN, 11), Tile(ResourceTypes.LUMBER, 4), Tile(ResourceTypes.ORE, 3)],
  [Tile(ResourceTypes.NOTHING, -1), Tile(ResourceTypes.LUMBER, 3), Tile(ResourceTypes.WOOL, 10), Tile(ResourceTypes.WOOL, 9), Tile(ResourceTypes.LUMBER, 6)],
  [None, Tile(ResourceTypes.BRICK, 8), Tile(ResourceTypes.ORE, 5), Tile(ResourceTypes.GRAIN, 2), None]]

"""
Board keeps track of hexagons, edges, and vertexes and how they relate
Data structure idea from http://stackoverflow.com/a/5040856
The rules are: "an hexagon at (x,y) is a neighbor of hexagons at (x, y±1), (x±1,y), 
and (x±1,y+1) for even xs or (x±1,y-1) for odd xs.
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
        self.hexagons[i][j] = Hexagon(i, j, tile.resource, tile.number)
    for i in range(numRows*2+2):
      for j in range(numCols*2+2):
        self.vertices[i][j] = Vertex(i, j)
        self.edges[i][j] = Edge(i, j)

  def getNeighborHexes(hex):
    neighbors = []
    x = hex.X
    y = hex.Y
    offset = 1
    if x % 2 != 0:
      offset = -1
    neighbors.append(self.hexagons[x][y+1])
    neighbors.append(self.hexagons[x][y-1])
    neighbors.append(self.hexagons[x+1][y])
    neighbors.append(self.hexagons[x-1][y])
    neighbors.append(self.hexagons[x+1][y+offset])
    neighbors.append(self.hexagons[x-1][y+offset])
    return neighbors

  def getNeighborVertices(vertex):
    neighbors = []
    x = vertex.X
    y = vertex.Y
    # Logic from thinking that this is saying getEdgesOfVertex
    # and then for each edge getVertexEnds, taking out the three that are ==vertex
    neighbors.append(self.vertices[x][y+1])
    neighbors.append(self.vertices[x+1][y])
    neighbors.append(self.vertices[x-1][y])

  def getVertices(hex):
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

  def getEdges(hex):
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

  def getVertexEnds(edge):
    edgeVertices = []
    x = edge.X
    y = edge.Y
    if x%2 == 0:
      edgeVertices.append(self.vertices[x/2][y])
      edgeVertices.append(self.vertices[x/2][y+1])
    else:
      edgeVertices.append(self.vertices[(x-1)/2][y])
      edgeVertices.append(self.vertices[(x+1)/2][y])
    return edgeVertices

  def getEdgesOfVertex(vertex):
    vertexEdges = []
    x = edge.X
    y = edge.Y
    vertexEdges.append(self.edges[x*2][y])
    vertexEdges.append(self.edges[x*2+1][y])
    vertexEdges.append(self.edges[x*2-1][y])
    return vertexEdges

  def getHexes(vertex):
    vertexHexes = []
    x = edge.X
    y = edge.Y
    xOffset = x % 2
    yOffset = y % 2
    vertexHexes.append(self.hexagons[x-1][(y+xOffset)/2-1])
    vertexHexes.append(self.hexagons[x-(1-yOffset)*xOffset][(y-1)/2])
    vertexHexes.append(self.hexagons[x][(y-xOffset)/2])
    return vertexHexes
   

