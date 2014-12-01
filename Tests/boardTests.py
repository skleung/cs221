from board import * 

class BoardTests:
  def __init__(self):
    self.board = Board(BeginnerLayout)
    self.hexDict = {}
    self.reverseHexDict = {}
    for i, tile in enumerate(self.board.tiles):
      self.hexDict[tile] = i+1
      self.reverseHexDict[i+1] = tile
    for i in range (19):
      print str(i+1) + " : " + str(self.reverseHexDict[i+1])


  def testGetNeighborHexes(self):
    print "Testing getNeighborHexes... "
    testHexes = ([
      (5, [1,2,6,10,9,4]), # testing odd
      (14, [9,10,15,18,17,13]), # testing even
      (1, [2,5,4]), # testing edge with three
      (7, [3,6,11,12]), # testing edge with four
      (18, [17,14,15,19]) # testing edge with four
      ])

    for hexNum, hexNumbers in testHexes:
      hexagon = self.reverseHexDict[hexNum]
      outputHexes = self.board.getNeighborHexes(hexagon)
      outputHexNums = [self.hexDict[x] for x in outputHexes]
      if set(hexNumbers) != set(outputHexNums):
        raise Exception("getNeighborHexes was wrong for hex " + str(hexNum) + "\n"
          + "Should have returned hexes " + str(hexNumbers) + " but instead returned hexes " + str(outputHexNums))

  def testGetNeighborVertices(self):
    print "Testing getNeighborVertices... "
    testVertices = ([ # tuples of vertex with expected neighbor vertices
      (Vertex(1,3), [Vertex(1,2), Vertex(1,4), Vertex(2,3)]), # testing odd, odd
      (Vertex(4,4), [Vertex(4,3), Vertex(4,5), Vertex(5,4)]), # testing even, even
      (Vertex(2,5), [Vertex(2,4), Vertex(2,6), Vertex(1,5)]), # testing even, odd
      (Vertex(3,6), [Vertex(3,5), Vertex(3,7), Vertex(2,6)]), # testing odd, even
      (Vertex(0,2), [Vertex(0,3), Vertex(1,2)]), # testing only two vertices
      (Vertex(5,2), [Vertex(4,2), Vertex(5,3)]), # testing only two vertices
      (Vertex(3,0), [Vertex(2,0), Vertex(3,1)]) # testing only two vertices
      ])

    def equivalent(vertexList, otherVertexList):
      if len(vertexList) != len(otherVertexList):
        return False
      for vertex in vertexList:
        exists = False
        for i in range(len(otherVertexList)):
          if vertex.equivLocation(otherVertexList[i]): exists = True
        if not exists: return False
      return True

    for vertex, vertices in testVertices:
      outputVertices = self.board.getNeighborVertices(vertex)
      if not equivalent(vertices, outputVertices):
        raise Exception("getNeighborVertices was wrong for vertex at " + str(vertex.X) + "," + str(vertex.Y) + "\n"
          + "Should have returned vertices " + str(vertices) + " but instead returned vertices " + str(outputVertices))

  def testGetVertices(self):
    print "Testing getVertices... "
    testHexes = ([ # tuples of hex with expected vertices
      (1, [Vertex(0,2), Vertex(0,3), Vertex(0,4), Vertex(1,4), Vertex(1,3), Vertex(1,2)]), # testing odd
      (3, [Vertex(2,0), Vertex(2,1), Vertex(2,2), Vertex(3,2), Vertex(3,1), Vertex(3,0)]), # testing edge
      (10, [Vertex(2,4), Vertex(2,5), Vertex(2,6), Vertex(3,6), Vertex(3,5), Vertex(3,4)]), # testing even, middle
      (19, [Vertex(4,6), Vertex(4,7), Vertex(4,8), Vertex(5,8), Vertex(5,7), Vertex(5,6)]), # testing edge
      ])

    def equivalent(vertexList, otherVertexList):
      if len(vertexList) != len(otherVertexList):
        return False
      for vertex in vertexList:
        exists = False
        for i in range(len(otherVertexList)):
          if vertex.equivLocation(otherVertexList[i]): exists = True
        if not exists: return False
      return True

    for hexNum, vertices in testHexes:
      hexagon = self.reverseHexDict[hexNum]
      outputVertices = self.board.getVertices(hexagon)
      if not equivalent(vertices, outputVertices):
        raise Exception("getVertices was wrong for hex " + str(hexNum) + "\n"
          + "Should have returned vertices " + str(vertices) + " but instead returned vertices " + str(outputVertices))

  def testGetEdges(self):
    print "Testing getEdges... "
    testHexes = ([ # tuples of hex with expected vertices
      (1, [Edge(0,2), Edge(0,3), Edge(1,4), Edge(2,3), Edge(2,2), Edge(1,2)]), # testing odd
      (3, [Edge(4,0), Edge(4,1), Edge(5,2), Edge(6,1), Edge(6,0), Edge(5,0)]), # testing edge
      (10, [Edge(4,4), Edge(4,5), Edge(5,6), Edge(6,5), Edge(6,4), Edge(5,4)]), # testing even, middle
      (19, [Edge(8,6), Edge(8,7), Edge(9,8), Edge(10,7), Edge(10,6), Edge(9,6)]), # testing edge
      ])

    def equivalent(edgeList, otherEdgeList):
      if len(edgeList) != len(otherEdgeList):
        return False
      for edge in edgeList:
        exists = False
        for i in range(len(otherEdgeList)):
          if edge.equivLocation(otherEdgeList[i]): exists = True
        if not exists: return False
      return True

    for hexNum, edges in testHexes:
      hexagon = self.reverseHexDict[hexNum]
      outputEdges = self.board.getEdges(hexagon)
      if not equivalent(edges, outputEdges):
        raise Exception("getEdges was wrong for hex " + str(hexNum) + "\n"
          + "Should have returned edges " + str(edges) + " but instead returned edges " + str(outputEdges))

  def testGetVertexEnds(self):
    print "Testing getVertexEnds... "
    testEdges = ([ # tuples of edge with expected vertices
      (Edge(3,3), [Vertex(1,3), Vertex(2,3)]), # testing odd, odd
      (Edge(8,6), [Vertex(4,6), Vertex(4,7)]), # testing even, even
      (Edge(4,7), [Vertex(2,7), Vertex(2,8)]), # testing odd, even
      (Edge(6,5), [Vertex(3,5), Vertex(3,6)]), # testing even, odd
      (Edge(1,2), [Vertex(0,2), Vertex(1,2)]), # testing edge of board
      (Edge(5,0), [Vertex(2,0), Vertex(3,0)]), # testing edge of board
      ])

    def equivalent(vertexPair, otherVertexPair):
      if vertexPair[0].equivLocation(otherVertexPair[0]) and vertexPair[1].equivLocation(otherVertexPair[1]):
        return True
      if vertexPair[0].equivLocation(otherVertexPair[1]) and vertexPair[1].equivLocation(otherVertexPair[0]):
        return True
      return False

    for edge, vertices in testEdges:
      outputVertices = self.board.getVertexEnds(edge)
      if not equivalent(vertices, outputVertices):
        raise Exception("getVertexEnds was wrong for edge at " + str(edge.X) + "," + str(edge.Y) + "\n"
          + "Should have returned vertices " + str(vertices) + " but instead returned vertices " + str(outputVertices))

  def testGetEdgesOfVertex(self):
    print "Testing getEdgesOfVertex... "
    testVertices = ([ # tuples of vertex with expected edges
      (Vertex(1,3), [Edge(2,2), Edge(2,3), Edge(3,3)]), # testing odd, odd
      (Vertex(4,4), [Edge(8,3), Edge(8,4), Edge(9,4)]), # testing even, even
      (Vertex(2,5), [Edge(3,5), Edge(4,4), Edge(4,5)]), # testing even, odd
      (Vertex(3,6), [Edge(5,6), Edge(6,5), Edge(6,6)]), # testing odd, even
      (Vertex(0,2), [Edge(0,2), Edge(1,2)]), # testing only two edges
      (Vertex(5,2), [Edge(9,2), Edge(10,2)]), # testing only two edges
      (Vertex(3,0), [Edge(5,0), Edge(6,0)]) # testing only two edges
      ])

    def equivalent(edgeList, otherEdgeList):
      if len(edgeList) != len(otherEdgeList):
        return False
      for edge in edgeList:
        exists = False
        for i in range(len(otherEdgeList)):
          if edge.equivLocation(otherEdgeList[i]): exists = True
        if not exists: return False
      return True

    for vertex, edges in testVertices:
      outputEdges = self.board.getEdgesOfVertex(vertex)
      if not equivalent(edges, outputEdges):
        raise Exception("getEdgesOfVertex was wrong for vertex at " + str(vertex.X) + "," + str(vertex.Y) + "\n"
          + "Should have returned edges " + str(edges) + " but instead returned edges " + str(outputEdges))

  def testGetHexes(self):
    print "Testing getHexes... "
    testVertices = ([ # tuples of vertex with expected hexagons
      (Vertex(1,3), [1,2,5]), # testing odd, odd
      (Vertex(4,4), [11, 12, 16]), # testing even, even
      (Vertex(2,5), [5, 9, 10]), # testing even, odd
      (Vertex(3,6), [10, 14, 15]), # testing odd, even
      (Vertex(0,2), [1]), # testing only one hex
      (Vertex(4,2), [7, 12]), # testing two hexes
      (Vertex(3,1), [3, 7]) # testing two hexes
      ])

    for vertex, hexes in testVertices:
      outputHexes = self.board.getHexes(vertex)
      outputHexList = [self.hexDict[x] for x in outputHexes]
      if set(hexes) != set(outputHexList):
        raise Exception("getHexes was wrong for vertex at " + str(vertex.X) + "," + str(vertex.Y) + "\n"
          + "Should have returned hexes " + str(hexes) + " but instead returned hexes " + str(outputHexList))

  def runAllTests(self):
    self.testGetNeighborHexes()
    print "Success!"
    self.testGetNeighborVertices()
    print "Success!"
    self.testGetVertices()
    print "Success!"
    self.testGetEdges()
    print "Success!"
    self.testGetVertexEnds()
    print "Success!"
    self.testGetEdgesOfVertex()
    print "Success!"
    self.testGetHexes()
    print "Success!"