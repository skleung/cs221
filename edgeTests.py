from board import *


class EdgeTests:
	"""
	Class: Edge
	--------------------------
	A class containing all tests for the Edge class.
	--------------------------
	"""

	def __init__(self):
		pass

	def testEdgeInit(self):
		"""
		Method: testEdgeInit
		--------------------------
		Tests to make sure all instance variables are properly
		initialized.
		--------------------------
		"""
		print "Running testEdgeInit....."

		e1 = Edge(1, 2)
		assert(e1.X is 1)
		assert(e1.Y is 2)
		assert(e1.player is None)

		e1 = Edge(1, 2, 5)
		assert(e1.X is 1)
		assert(e1.Y is 2)
		assert(e1.player is 5)

		e1 = Edge(3, 4, 6)
		assert(e1.X is 3)
		assert(e1.Y is 4)
		assert(e1.player is 6)

	def testEdgeCopy(self):
		"""
		Method: testEdgeCopy
		--------------------------
		Tests to make sure the deepCopy method on Edge
		properly deep copies a given edge.
		--------------------------
		"""
		print "Running testEdgeCopy....."

		e1 = Edge(1, 2, 4)
		e2 = e1.deepCopy()

		# Make sure they're not the same object
		assert(e1 != e2)

		# Make sure X is not changed
		e1.X = 0
		assert(e2.X != 0)

		# Make sure Y is not changed
		e1.Y = 3
		assert(e2.Y != 3)

		# Make sure the player is not changed
		e1.player = 5
		assert(e2.player != 5)

	def testEdgeBuild(self):
		"""
		Method: testEdgeBuild
		--------------------------
		Tests to make sure building a road on an edge
		updates state properly.  Also makes sure improperly
		building a road raises an exception.
		--------------------------
		"""
		print "Running testEdgeBuild...."

		# Test valid building
		e1 = Edge(1, 2)
		e1.build(3)
		assert(e1.X is 1)
		assert(e1.Y is 2)
		assert(e1.player is 3)

		# Test having the same player build twice on this
		# Edge (should raise an exception but be caught)
		try:
			e1.build(3)
			print "Error: allowed multiple builds by the same player"
		except:
			# Make sure nothing about the Vertex changed
			assert(e1.player is 3)
			assert(e1.X is 1)
			assert(e1.Y is 2)

		# Test having different players both build on this
		# Edge (should raise an exception but be caught)
		try:
			e1.build(4)
			print "Error: allowed multiple builds by different players"
		except:
			# Make sure nothing about the Vertex changed
			assert(e1.player is 3)
			assert(e1.X is 1)
			assert(e1.Y is 2)


	def runAllTests(self):
		"""
		Method: runTests
		--------------------------
		Run all tests for this test class.
		--------------------------
		"""
		print "Running Edge tests...."
		print "----------------------"
		
		self.testEdgeInit()
		print "Success!"
		self.testEdgeCopy()
		print "Success!"
		self.testEdgeBuild()
		print "Success!"

