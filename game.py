from gameUtil import Deck
from gameUtil import Card
from gameUtil import Dice
# TODO: Implement Board class with nodes to represent places to put settlements

class GameStateData:
  def __init__( self, prevState = None ):
      """
      Generates a new data packet by copying information from its predecessor.
      """
      if prevState != None:
        self.deck = prevState.deck.shallowCopy()
        #TODO: add nodes for building settlements

  """
  This method should be called to start or initialize the GameStateData
  """
  def initialize(self, layout = None):
    self.deck = Deck()
    self.board = Board(layout)

class GameState:
  def __init__( self, prevState = None ):
    """
    Generates a new state by copying information from its predecessor if it exists
    """
    if prevState != None: # Initial state
      self.data = GameStateData(prevState.data)
    else:
      self.data = GameStateData()

  def __eq__( self, other ):
    """
    Allows two states to be compared.
    """
    return self.data == other.data

  def __hash__( self ):
    """
    Allows states to be keys of dictionaries.
    """
    return hash( self.data )

  def __str__( self ):
    return str(self.data)

  """
  Creates a GameState based on a layout if it exists
  """
  def initialize(self, layout = None):
    self.data = GameStateData()
    # initialize other game state parameters, number of agents playing, etc...