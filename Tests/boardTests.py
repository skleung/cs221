from board import * 

class BoardTests:
  def __init__(self):
    self.board = Board(BeginnerLayout)
    self.hexDict = {}
    for i, tile in enumerate(self.board.tiles):
      self.hexDict[tile] = i+1

  def testGetHexes(self):
    print "Testing GetHexes... "
    testVertices = ( # tuples of vertex with expected hexagons
      (Vertex(1,3), [1,2,5]), # testing odd, odd
      (Vertex(4,4), [11, 12, 16]), # testing even, even
      (Vertex(2,5), [5, 9, 10]), # testing even, odd
      (Vertex(3,6), [10, 14, 15]), # testing odd, even
      (Vertex(0,2), [1]), # testing only one hex
      (Vertex(4,2), [7, 12]), # testing two hexes
      (Vertex(3,1), [3, 7]) # testing two hexes
      )

    for vertex, hexes in testVertices:
      outputHexes = self.board.getHexes(vertex)
      outputHexList = [self.hexDict[x] for x in outputHexes]
      if set(hexes) != set(outputHexList):
        raise Exception("GetHexes was wrong for vertex at " + str(vertex.X) + "," + str(vertex.Y) + "\n"
          + "Should have returned hexes " + str(hexes) + " but instead returned hexes " + str(outputHexList))

  def runAllTests(self):
    self.testGetHexes()
    print "Success!"