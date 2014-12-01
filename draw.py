from board import *
from Tkinter import *

def getColorForPlayer(player):
    return {
      0: "red",
      1: "blue",
      2: "black",
      3: "brown"
    }.get(player, None)

class Draw:
	# Takes a list of 19 tiles
  def __init__(self, tiles):
    self.root = Tk()
    self.root.resizable(0,0)
    self.title = PhotoImage(file = "resources/catan.gif")
    self.tiles = tiles
    self.vertexOffsets = self.verticesInit()
    self.dimenInit()
    self.imageInit()
    self.pieceInit()
    self.canvas = Canvas(self.root, width=self.width, height=self.height)
    self.canvas.pack()

  def dimenInit(self):
    self.d = 70 # distance from center to edge of hex
    self.hexWidth = self.d * 1.4 # equal to sqrt(3)/2 * height
    self.hexHeight = self.d * 1.6
    self.rowHeight = self.hexHeight * 0.75
    self.numR = 11 # radius of number oval
    self.width = 700
    self.height = 600
    self.yOffset = self.height/4
    self.xOffset = self.width/2

  def imageInit(self):
    self.desert = PhotoImage(file = 'resources/desert.gif')
    self.field = PhotoImage(file = 'resources/field.gif')
    self.forest = PhotoImage(file = 'resources/forest.gif')
    self.hill = PhotoImage(file = 'resources/hill.gif')
    self.mountain = PhotoImage(file = 'resources/mountain.gif')
    self.pasture = PhotoImage(file = 'resources/pasture.gif')

  def pieceInit(self):
    self.redS = PhotoImage(file = 'resources/redS.gif')
    self.blueS = PhotoImage(file = 'resources/blueS.gif')
    self.blackS = PhotoImage(file = 'resources/blackS.gif')
    self.brownS = PhotoImage(file = 'resources/brownS.gif')
    self.redC = PhotoImage(file = 'resources/redC.gif')
    self.blueC = PhotoImage(file = 'resources/blueC.gif')
    self.blackC = PhotoImage(file = 'resources/blackC.gif')
    self.brownC = PhotoImage(file = 'resources/brownC.gif')

  # initializes offsets for vertices based on hexagons. Makes things way simpler
  # because alternative is looking for intersecting hexagons and determining which vertex it is.
  def verticesInit(self):
    return (
      [[None, None, (3, 0), (2, 0.25), (2, 0.75), (1, 1), (1, 1.5), (0, 1.75), (0, 2.25), None, None], # diagonal 1
      [None, (5, 0), (4, 0.25), (4, 0.75), (3, 1), (3, 1.5), (2, 1.75), (2, 2.25), (1, 2.5), (1, 3), None], # diagonal 2
      [(7, 0), (6, 0.25), (6, 0.75), (5, 1), (5, 1.5), (4, 1.75), (4, 2.25), (3, 2.5), (3, 3), (2, 3.25), (2, 3.75)], # diagonal 3
      [(8, 0.25), (8, 0.75), (7, 1), (7, 1.5), (6, 1.75), (6, 2.25), (5, 2.5), (5, 3), (4, 3.25), (4, 3.75), (3, 4)], # diagonal 4
      [None, (9, 1), (9, 1.5), (8, 1.75), (8, 2.25), (7, 2.5), (7, 3), (6, 3.25), (6, 3.75), (5, 4), None], # diagonal 5
      [None, None, (10, 1.75), (10, 2.25), (9, 2.5), (9, 3), (8, 3.25), (8, 3.75), (7, 4),None, None]]) # diagonal 6

  def drawBoard(self):
    # yOffset = self.height/2 - self.d * 1.5
    cY = self.yOffset
    index = 0
    tilesInRow = [3,4,5,4,3]
    for row in tilesInRow:
      cX = self.xOffset - self.hexWidth/2*row
      self.drawRow(row, index, cX, cY)
      index += row
      cY += self.rowHeight

  def drawRow(self, numTiles, index, cX, cY):
    for tile in range(numTiles):
      cX += self.hexWidth
      hexagon = self.tiles[index]
      image = self.getImageForResource(hexagon.resource)
      self.canvas.create_image(cX, cY, image=image)
      self.drawNum(cX, cY, hexagon.diceValue)
      index += 1

  def drawNum(self, xOffset, yOffset, num):
    if ((num == 8) or (num == 6)): color = "red"
    else: color = "black"
    self.canvas.create_oval(xOffset-self.numR, yOffset-self.numR, xOffset+self.numR, yOffset+self.numR, fill="white")
    self.canvas.create_text(xOffset, yOffset, text=str(num), fill=color)

  def drawSettlements(self, vertices):
    for vertex in vertices:
      color = getColorForPlayer(vertex.player)
      image = self.findSImage(color, vertex.isSettlement, vertex.isCity)
      xPos, yPos = self.calculateVertexPosition(vertex)
      self.canvas.create_image(xPos, yPos, image = image)

  def drawCities(self, vertices):
    self.drawSettlements(vertices)

  def calculateVertexPosition(self, vertex):
    xOffset, yOffset = self.vertexOffsets[vertex.X][vertex.Y]
    # think of diagonal
    xPos = (self.xOffset 
      - self.hexWidth/2*4 # account for first 3 rows
      + self.hexWidth/2 * xOffset)
    yPos = (self.yOffset - self.hexHeight*0.5
      + self.hexHeight * yOffset)
    return (xPos, yPos)

  def drawRoads(self, roads, board):
    for road in roads:
      start, end = board.getVertexEnds(road)
      ox, oy = self.calculateVertexPosition(start)   #origin x, y
      ex, ey = self.calculateVertexPosition(end)  #end x, y
      color = getColorForPlayer(road.player)
      self.canvas.create_line(ox, oy, ex, ey, width=5, fill=color)

  def drawTitle(self):
    self.canvas.create_image(120, 70, image=self.title)

  def getImageForResource(self, resource):
		return {
			ResourceTypes.GRAIN: self.field, 
			ResourceTypes.WOOL: self.pasture, 
			ResourceTypes.ORE: self.mountain, 
			ResourceTypes.LUMBER: self.forest, 
			ResourceTypes.BRICK: self.hill, 
			ResourceTypes.NOTHING: self.desert
		}.get(resource, None)

  # get image associated with city and player
  def findSImage(self, color, settlement, city):
    if (settlement): #at this vertex there is a settlement
      return {
        "red": self.redS,
        "blue": self.blueS,
        "black": self.blackS,
        "brown": self.brownS
      }.get(color, None)
    elif (city): #at this vertex there is a city
      return {
        "red": self.redC,
        "blue": self.blueC,
        "black": self.blackC,
        "brown": self.brownC
      }.get(color, None)

  def drawBG(self):
    self.canvas.create_rectangle(0, 0, self.width, self.height, fill = "light sky blue") 


