
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

  def __init__(self, X, Y, diceValues, resources):
    self.X = X
    self.Y = Y
    self.diceValues = diceValues
    self.resources = resources
    self.adjacentNodes = adjacentNodes
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

class Board:
  def __init__(self, layout):
    self.hexagons = [[0 for x in xrange(10)] for x in xrange(10)] 
    self.edges = [[0 for x in xrange(22)] for x in xrange(22)] 
    self.vertices = [[0 for x in xrange(22)] for x in xrange(22)] 
    for i in range(10):
      for j in range(10):
        self.hexagons[i][j] = Hexagon(i, j, None, None)
    for i in range(22):
      for j in range(22):
        self.vertices[i][j] = Vertex(i, j, None, None)
        self.edges[i][j] = Edge(i, j)
     # for tile in layout.tiles:

  def getNeighbors(hex):
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
   

