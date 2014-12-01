from board import *
from Tkinter import *

class Draw:
	# Takes a list of 19 tiles
  def __init__(self, tiles):
    print tiles
    self.root = Tk()
    self.root.resizable(0,0)
    self.tiles = tiles
    self.dimenInit()
    self.imageInit()
    self.canvas = Canvas(self.root, width=self.width, height=self.height)
    self.canvas.pack()

  def dimenInit(self):
		self.d = 70 # distance from center to edge of hex
		self.r = 11 # radius
		self.width = 700
		self.height = 600

  def imageInit(self):
    self.desert = PhotoImage(file = 'resources/desert.gif')
    self.field = PhotoImage(file = 'resources/field.gif')
    self.forest = PhotoImage(file = 'resources/forest.gif')
    self.hill = PhotoImage(file = 'resources/hill.gif')
    self.mountain = PhotoImage(file = 'resources/mountain.gif')
    self.pasture = PhotoImage(file = 'resources/pasture.gif')

  def drawBoard(self):
    yOffset = self.height/2 - self.d * 1.5
    index = 0
    tilesInRow = [3,4,5,4,3]
    for row in tilesInRow:
      xOffset = self.width/2 - self.d*2.5 - self.d*0.7*row
      self.drawRow(row, index, xOffset, yOffset)
      index += row
      yOffset += self.d * 1.2

  def drawRow(self, numTiles, index, xOffset, yOffset):
    for tile in range(numTiles):
      print index
      xOffset += self.d * 1.4
      hexagon = self.tiles[index]
      image = self.getImageForResource(hexagon.resource)
      self.canvas.create_image(xOffset, yOffset, image=image)
      self.drawNum(xOffset, yOffset, hexagon.diceValue)
      index += 1

  def getImageForResource(self, resource):
		return {
			ResourceTypes.GRAIN: self.field, 
			ResourceTypes.WOOL: self.pasture, 
			ResourceTypes.ORE: self.mountain, 
			ResourceTypes.LUMBER: self.forest, 
			ResourceTypes.BRICK: self.hill, 
			ResourceTypes.NOTHING: self.desert
		}.get(resource, None)

  def drawNum(self, xOffset, yOffset, num):
    if ((num == 8) or (num == 6)): color = "red"
    else: color = "black"
    self.canvas.create_oval(xOffset-self.r, yOffset-self.r, xOffset+self.r, yOffset+self.r, fill="white")
    self.canvas.create_text(xOffset, yOffset, text=str(num), fill=color)

  def drawBG(self):
    self.canvas.create_rectangle(0, 0, self.width, self.height, fill = "light sky blue") 


