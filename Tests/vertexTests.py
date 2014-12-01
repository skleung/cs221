from board import *


class VertexTests:
	"""
	Class: VertexTests
	--------------------------
	A class containing all tests for the Vertex class.
	--------------------------
	"""

	def __init__(self):
		pass

	def testVertexInit(self):
		"""
		Method: testVertexInit
		--------------------------
		Tests to make sure all instance variables are properly
		initialized.
		--------------------------
		"""
		print "Running testVertexInit....."

		v1 = Vertex(1, 2)
		assert(v1.X is 1)
		assert(v1.Y is 2)
		assert(v1.player is None)
		assert(not v1.isSettlement)
		assert(not v1.isCity)
		assert(v1.canSettle)

		v1 = Vertex(3, 4)
		assert(v1.X is 3)
		assert(v1.Y is 4)
		assert(v1.player is None)
		assert(not v1.isSettlement)
		assert(not v1.isCity)
		assert(v1.canSettle)

	def testVertexPrint(self):
		"""
		Method: testVertexPrint
		--------------------------
		Tests the stringification of Vertex to make sure it's correct.
		Tests for Vertexes with settlements, cities, and nothing.
		--------------------------
		"""
		print "Running testVertexPrint...."

		# Test with vertex at (1,2) settled/upgraded by 4
		v1 = Vertex(1, 2)
		assert(v1.__repr__() == "Unoccupied (1, 2)")

		v1.settle(4)
		assert(v1.__repr__() == "S4 (1, 2)")

		v1.upgrade(4)
		assert(v1.__repr__() == "C4 (1, 2)")

		# Test with vertex at (3,5) settled/upgraded by 2
		v1 = Vertex(3, 5)
		assert(v1.__repr__() == "Unoccupied (3, 5)")

		v1.settle(2)
		assert(v1.__repr__() == "S2 (3, 5)")

		v1.upgrade(2)
		assert(v1.__repr__() == "C2 (3, 5)")

		# Test with unoccupied but unsettlable vertex
		v1 = Vertex(3, 5)
		v1.canSettle = False
		assert(v1.__repr__() == "Unsettlable (3, 5)")

	def testVertexIsOccupied(self):
		"""
		Method: testVertexIsOccupied
		--------------------------
		Tests to make sure a Vertex correctly reports whether or
		not it is occupied.
		--------------------------
		"""
		print "Running testVertexIsOccupied...."

		# Test with Vertex at (3,4) settled/upgraded by 2
		v1 = Vertex(3, 4)
		assert(not v1.isOccupied()) # Not occupied initially

		# Settle (now occupied)
		v1.settle(2)
		assert(v1.isOccupied())

		# Upgrade (still occupied)
		v1.upgrade(2);
		assert(v1.isOccupied())

		# Test with Vertex at (1,2) settled/upgraded by 5
		v1 = Vertex(1, 2)
		assert(not v1.isOccupied()) # Not occupied initially

		# Settle (now occupied)
		v1.settle(5)
		assert(v1.isOccupied())

		# Upgrade (still occupied)
		v1.upgrade(5);
		assert(v1.isOccupied())

	def testVertexCopy(self):
		"""
		Method: testVertexCopy
		--------------------------
		Tests to make sure the deepCopy method on Vertex
		properly deep copies a given vertex.
		--------------------------
		"""
		print "Running testVertexCopy....."

		v1 = Vertex(1, 2)
		v1.player = 5
		v2 = v1.deepCopy()

		# Make sure they're not the same object
		assert(v1 != v2)

		# Make sure X is not changed
		v1.X = 0
		assert(v2.X != 0)

		# Make sure Y is not changed
		v1.Y = 3
		assert(v2.Y != 3)

		# Make sure player is not changed
		v1.player = 6
		assert(v2.player != 6)

		# Make sure settlement/city booleans are not changed
		v1.isSettlement = True
		assert(not v2.isSettlement)

		v1.isCity = True
		assert(not v2.isCity)

	def testVertexSettle(self):
		"""
		Method: testVertexSettle
		--------------------------
		Tests to make sure a Vertex's instance variables
		are properly updated when settling, and that
		improperly settling correctly raises an exception.
		--------------------------
		"""
		print "Running testVertexSettle...."

		v1 = Vertex(1, 2)

		# Make sure settling properly updates state
		v1.settle(2)
		assert(v1.player is 2)
		assert(v1.isSettlement)
		assert(not v1.isCity)
		assert(not v1.canSettle)

		# Make sure you can't settle twice (this should
		# raise an exception but be caught)
		try:
			v1.settle(2)
			print "Error: allowed multiple settles"
		except:
			# Make sure nothing about the Vertex changed
			assert(v1.player is 2)
			assert(v1.isSettlement)
			assert(not v1.isCity)
			assert(not v1.canSettle)

	def testVertexUpgrade(self):
		"""
		Method: testVertexUpgrade
		--------------------------
		Tests to make sure a Vertex's instance variables
		are properly updated when upgrading from a settlement
		to a city, and that improperly settling correctly
		raises an exception.
		--------------------------
		"""
		print "Running testVertexUpgrade....."

		# ---- Minitest 1: Check valid upgrading ----
		v1 = Vertex(3, 4)

		# Make sure upgrading properly updates state
		v1.settle(3)
		v1.upgrade(3)
		assert(v1.player is 3)
		assert(not v1.isSettlement)
		assert(v1.isCity)
		assert(not v1.canSettle)
		# ---- End Minitest 1 ---- #


		# ---- Minitest 2: Make sure you can't upgrade twice (this should
		# raise an exception but be caught) ----
		try:
			v1.upgrade(3)
			print "Error: allowed multiple upgrades"
		except:
			# Make sure nothing about the Vertex changed
			assert(v1.player is 3)
			assert(not v1.isSettlement)
			assert(v1.isCity)
			assert(not v1.canSettle)
		# ---- End Minitest 2 ---- #


		# ---- Minitest 3: Make sure two different players can't build
		# a settlement here and upgrade it ----
		v1 = Vertex(3, 4)
		v1.settle(3)

		# Make sure two different players can't build (this
		# should raise an exception but be caught)
		try:
			v1.upgrade(4)
			print "Error: two different players allowed to settle/upgrade"
		except:
			# Make sure nothing about the Vertex changed
			assert(v1.player is 3)
			assert(v1.isSettlement)
			assert(not v1.isCity)
			assert(not v1.canSettle)
		# ---- End Minitest 3 ---- #


		# ---- Minitest 4: Make sure the Vertex has a settlement before
		# upgrading ----
		v1 = Vertex(3, 4)

		# Make sure a settlement is present before upgrading (this
		# should raise an exception but be caught)
		try:
			v1.upgrade(4)
			print "Error: upgraded without settlement!"
		except:
			# Make sure nothing about the Vertex changed
			assert(v1.player is None)
			assert(not v1.isSettlement)
			assert(not v1.isCity)
			assert(v1.canSettle)
		# ---- End Minitest 4 ---- #

	def runAllTests(self):
		"""
		Method: runTests
		--------------------------
		Run all tests for this test class.
		--------------------------
		"""
		print "Running Vertex tests....."
		print "-------------------------"
		
		self.testVertexCopy()
		print "Success!"
		self.testVertexSettle()
		print "Success!"
		self.testVertexUpgrade()
		print "Success!"
		self.testVertexPrint()
		print "Success!"
		self.testVertexInit()
		print "Success!"
		self.testVertexIsOccupied()
		print "Success!"

