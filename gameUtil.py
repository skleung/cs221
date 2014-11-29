# from enum import Enum

# ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER"])

# RESOURCE_DISTRIBUTION = [
#   # 12 case 
#   [ResourceType.WOOL],
#   # 11 case
#   [ResourceType.LUMBER, ResourceType.GRAIN],
#   [ResourceType.LUMBER, ResourceType.GRAIN],
#   # 10 case
#   [ResourceType.WOOL, ResourceType.WOOL],
#   [ResourceType.WOOL, ResourceType.WOOL],
#   [ResourceType.WOOL, ResourceType.WOOL],
#   # 9 case
#   [ResourceType.WOOL, ResourceType.GRAIN],
#   [ResourceType.WOOL, ResourceType.GRAIN],
#   [ResourceType.WOOL, ResourceType.GRAIN],
#   [ResourceType.WOOL, ResourceType.GRAIN],
#   # 8 case
#   [ResourceType.GRAIN, ResourceType.BRICK],
#   [ResourceType.GRAIN, ResourceType.BRICK],
#   [ResourceType.GRAIN, ResourceType.BRICK],
#   [ResourceType.GRAIN, ResourceType.BRICK],

# ]
import random

class Card:
  def __init__(self, value):
    self.value = value
    if (value in RESOURCE_NAMES):
      self.isResource = True
    elif (value == "Victory"):
      self.isVictory = True
    else:
      self.isDevelopment = True

class Deck:
  def __init__(self):
    self.cards = []
    for resource in RESOURCE_NAMES:
      self.cards+= [Card(resource)]*12 
      #TODO: How many resource cards of each type do we have in a deck?
    self.cards += [Card("Victory")]*5 + [Card("Soldier")]*14 + [Card("Monopoly")]*2 + [Card("Plenty")]*2 + [Card("Road")]*2 
    # shuffles cards
    random.shuffle(self.cards)

  def drawCard(self):
    return self.cards.pop(0)
