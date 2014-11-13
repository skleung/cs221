
from sets import Set
from enum import Enum

Actions = Enum(["DRAW", "SETTLE", "CITY", "ROAD", "TRADE"])
ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER", "NOTHING"])
Structure = Enum(["ROAD", "SETTLEMENT", "NONE"])
Resources = ([ResourceTypes.BRICK, ResourceTypes.BRICK, ResourceTypes.BRICK,
  ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL, ResourceTypes.WOOL,
  ResourceTypes.ORE, ResourceTypes.ORE, ResourceTypes.ORE,
  ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN, ResourceTypes.GRAIN,
  ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER, ResourceTypes.LUMBER,
  ResourceTypes.NOTHING])
NumberChits = [-1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]


class Tile:
  """
  Class: Tile
  ---------------------------
  A Tile represents a single square on our square gameboard.  A tile
  has a resource type, a roll number, and, optionally, can have a road
  or settlement be built on it by a single player.
  ---------------------------
  """


  def __init__(self, resource, number, x, y):
    self.resource = resource
    self.x = x
    self.y = y
    self.number = number
    self.player = None
    self.structure = Structure.NONE # Settlement, vertical road, or horizontal road


  """
  Method: settle
  ---------------------------
  Parameters:
    playerIndex: the index of the player that is settling on this tile
  Returns: NA

  Marks this tile as settled by the given player.  Throws an exception if
  this tile has already been used.
  ---------------------------
  """
  def settle(self, playerIndex):
    if self.player != None: raise Exception("This tile is already used!")
    self.player = playerIndex
    self.structure = Structure.SETTLEMENT


  """
  Method: buildRoad
  ---------------------------
  Parameters:
    playerIndex: the index of the player that is building a road on this tile
    start: an (x,y) tuple representing the start square this road is connecting from
    end: an (x,y) tuple representing the end square this road is connecting to
  Returns: NA

  Builds a road owned by the given player on this tile.
  ---------------------------
  """
  def buildRoad(self, playerIndex):
    if self.player != None: raise Exception("This tile is already used!")

    self.player = playerIndex
    self.structure = Structure.ROAD


  """
  Method: toString
  ---------------------------
  Parameters: NA
  Returns: NA

  Prints out a description of this tile
  ---------------------------
  """
  def toString(self):
    print "--------------TILE INFO AT (" + str(self.x) + ", " + str(self.y) + ")---------------"
    print "Owned by player: " + str(self.player)
    print "Structure: " + str(self.structure)
    print "Resource Type: " + str(self.resource)
    print "Tile number: " + str(self.number)


  """
  Method: strRepresentation
  ---------------------------
  Parameters: NA
  Returns: a "stringified" version of this tile

  Returns a string representing this tile.  If this tile is unused, this method
  returns "-".  If it is a settlement, it returns "S#", where # = the player who owns
  the settlement.  IF it is a road, it returns "R#", where # = the player who owns
  the road.  (Note: This method assumes the player index will never be more than 1 digit,
  since all tile string representations are length 2).
  ---------------------------
  """
  def strRepresentation(self):
    if self.structure == Structure.NONE: return "--"
    elif self.structure == Structure.ROAD: return "R" + str(self.player)
    elif self.structure == Structure.SETTLEMENT: return "S" + str(self.player)



class BasicBoard:
  """
  Class: BasicBoard
  ---------------------------
  A BasicBoard is an n x n grid of Tiles representing a simplified
  version of the Settlers of Catan gameboard.  Every Tile can be built
  on, and every tile has a resource type and roll number, along with an x and y.
  A BasicBoard contains an n x n grid of Tiles, as well as a list of all
  built settlements and a list of all built roads.
  ---------------------------
  """

  def __init__(self, size):
    self.board = [[Tile(ResourceTypes.BRICK, 5, j, i) for i in xrange(size)] for j in xrange(size)]
    self.settlements = []
    self.roads = []
    self.size = size


  """
  Method: getTile
  ---------------------------
  Parameters:
    x: the x coordinate of the tile to get
    y: the y coordinate of the tile to get
  Returns: the Tile object at that (x,y), or None if the coordinates are out of bounds

  Returns the tile on the board at the given coordinates, or None if the
  coordinates are out of bounds.
  ---------------------------
  """
  def getTile(self, x, y):
    if 0 <= x < self.size and 0 <= y < self.size:
      return self.board[x][y]
    return None


  """
  Method: printBoard
  ---------------------------
  Parameters: NA
  Returns: NA

  Prints out an ASCII representation of the current board state.
  It does this by printing out each row inside square brackets.
  Each tile is either '--' if it's unused, 'RX' if it's a road,
  or 'SX' if it's a settlement.  The 'X' in the road or settlement
  representation is the player who owns that road/settlement.
  ---------------------------
  """
  def printBoard(self):
    for row in self.board:
      s = "["
      for tile in row:
        s += " " + tile.strRepresentation() + " "
      print s + "]"


  """
  Method: applyAction
  ---------------------------
  Parameters:
    playerIndex: the index of the player that is taking an action
    action: a tuple (ACTION_TYPE, Tile) representing the action to be
    taken and where that action should be taken.
  Returns: NA

  Updates the board to take the given action for the given player.  The action
  can either be building a settlement or building a road.
  ---------------------------
  """
  def applyAction(self, playerIndex, action):

    # Mark the tile as a settlement
    if action[0] == Actions.SETTLE:
      tile = action[1]
      tile.settle(playerIndex)
      self.settlements.append(tile)

    # Or mark the tile as a road
    elif action[0] == Actions.ROAD:
      tile = action[1]
      tile.buildRoad(playerIndex)
      self.roads.append(tile)


  """
  Method: getNeighborTiles
  ---------------------------
  Parameters:
    tile: the Tile object to find the neighbors of
  Returns: a list of all the non-diagonal adjacent tiles to this tile

  Returns a list of all of the tiles immediately surrounding
  the passed-in tile (NOT DIAGONAL)
  ---------------------------
  """
  def getNeighborTiles(self, tile):
    neighbors = []

    for dx in range(-1, 2):
      for dy in range(-1, 2):

        # Ignore diagonal tiles and the original tile
        if (dx != 0 and dy != 0) or (dx == 0 and dy == 0): continue

        # If this location is in bounds, add the tile to our list
        currTile = self.getTile(tile.x + dx, tile.y + dy)
        if currTile != None:
          neighbors.append(currTile)

    return neighbors


  """
  Method: getRoadEnds
  ---------------------------
  Parameters:
    road: the road to return the endpoints for
  Returns: a list of all the endpoints for this road

  Returns a list of all of the endpoints that this road connects.
  Note that this road can connect up to 4 endpoints (because the
  road is just a square on the board).
  ---------------------------
  """
  def getRoadEnds(self, road):
    return self.getNeighborTiles(road)

   
