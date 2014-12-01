from board import * 

class BoardTests:
	def __init__(self):
		self.board = Board(BeginnerLayout)
    self.hexDict = {}
    for i, tile in enumerate(self.board.tiles):
      self.hexDict[tile] = i

  def testGetHexes(self):
    print "Testing GetHexes... "
    testVertices = (
      (Vertex(1,3), [1,2,5]), # tuple of vertex with expected hexagons
      Vertex(4,4), []
      )

    for vertex, hexes in testVertices:
      outputHexes = self.board.getHexes(vertex)
      outputHexList = [self.hexDict[x] for x in outputHexes]
      if set(hexes) != set(outputHexList):
        raise Exception("GetHexes was wrong for vertex at " + vertex.X + "," + vertex.Y + "\n"
          + "Should have returned hexes " + str(hexes) + " but instead returned hexes " + str(outputHexList))



	def runAllTests(self):
    self.testGetHexes()
    print "Success!"