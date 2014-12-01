from board import *


class HexagonTests:
	"""
	Class: HexagonTests
	--------------------------
	A class containing all tests for the Hexagon class.
	--------------------------
	"""

	def __init__(self):
		pass

	def testHexagonInit(self):
		"""
		Method: testHexagonInit
		--------------------------
		Tests to make sure all instance variables are properly
		initialized.
		--------------------------
		"""
		print "Running testHexagonInit....."

		h1 = Hexagon(1, 2, ResourceTypes.WOOL, 5)
		assert(h1.X is 1)
		assert(h1.Y is 2)
		assert(h1.resource is ResourceTypes.WOOL)
		assert(h1.diceValue is 5)

		h1 = Hexagon(3, 4, ResourceTypes.LUMBER, 3)
		assert(h1.X is 3)
		assert(h1.Y is 4)
		assert(h1.resource is ResourceTypes.LUMBER)
		assert(h1.diceValue is 3)

	def testHexagonCopy(self):
		"""
		Method: testHexagonCopy
		--------------------------
		Tests to make sure the deepCopy method on Hexagon
		properly deep copies a given hexagon.
		--------------------------
		"""
		print "Running testHexagonCopy....."

		h1 = Hexagon(1, 2, ResourceTypes.WOOL, 5)
		h2 = h1.deepCopy()

		# Make sure they're not the same object
		assert(h1 != h2)

		# Make sure X is not changed
		h1.X = 0
		assert(h2.X != 0)

		# Make sure Y is not changed
		h1.Y = 3
		assert(h2.Y != 3)

		# Make sure resource type is not changed
		h1.resource = ResourceTypes.LUMBER
		assert(h2.resource != ResourceTypes.LUMBER)

		# Make sure dice roll number is not changed
		h1.diceValue = 6
		assert(h2.diceValue != 6)

	def testHexagonPrint(self):
		"""
		Method: testHexagonPrint
		--------------------------
		Tests to make sure the __repr__ method on Hexagon
		properly stringifies a given hexagon.
		--------------------------
		"""
		print "Running testHexagonPrint....."

		# Make suret the print works for every resource type
		for resourceType in ResourceTypes:

			# Create a new tile with that resource type
			h1 = Hexagon(1, 2, resourceType, 5)
			stringRep = h1.__repr__()

			# Make sure the string representation contains the
			# correct roll value and resource string
			correctStringRep = "/" + ResourceDict[resourceType] + "5\\"
			assert(stringRep == correctStringRep)

	def runAllTests(self):
		"""
		Method: runTests
		--------------------------
		Run all tests for this test class.
		--------------------------
		"""
		print "Running Hexagon tests....."
		print "--------------------------"
		
		self.testHexagonPrint()
		print "Success!"
		self.testHexagonCopy()
		print "Success!"

