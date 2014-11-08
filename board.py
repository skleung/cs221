'''
Represents a point of intersection on the game board. Holds all information about that particular intersection
'''
class Node:

  # adjacentNodes: a list of nodes that are adjacent to this particular node
  # player: whoever controls this particular node
  # isSettlement: whether this node is a settlement or not
  # isCity: whether this node is a city or not

  # diceValues: a set of dice values that this node is 
  def __init__(self, diceValues, resources, adjacentNodes):
    self.diceValues = diceValues
    self.resources = resources
    self.adjacentNodes = adjacentNodes
    self.player = None
    self.isSettlement = False
    self.isCity = False

  def settle(self):
    self.isSettlement = True

  def upgrade(self):
    if (self.isSettlement):
      self.isCity = True
    else:
      raise Exception, "Can't upgrade to a city without a settlement!"

class Edge:

  # player: whoever controls this edge
  # inRoad: not sure if we need this, but perhaps we could have a road of edges...
  
class Board:
  def __init__(self, layout):
    nodes = {} # maps dice numbers to nodes
    for tile in layout.tiles:
      if tile.edge:;

