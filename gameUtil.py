RESOURCE_NAMES = ["Sheep", "Wheat", "Ore", "Brick", "Wood"]

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
      self.cards+= [Card(resource)]*12 #TODO: Research this number?
    self.cards += [Card("Victory")]*5 + [Card("Soldier")]*14 + [Card("Monopoly")]*2 + [Card("Plenty")]*2 + [Card("Road")]*2 
    # shuffles cards
    random.shuffle(self.cards)

  def drawCard(self):
    return self.cards.pop(0)
