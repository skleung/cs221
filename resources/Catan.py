# Angela Zhang, afzhang
# Catan.py
###########################################
# Settlers of Catan
# MAIN FILE: Initializes the game
###########################################
import tile
import player
import developmentCards
import vertices
import draw
import random
import pickle
from Tkinter import *
import tkMessageBox

class Catan(object):
    def mousePressed(self, event):
        key = vertices.findRange(event.x, event.y, self.vertices)
        if ((key != None) and (vertices.isLegal(key, self.vertices)) and
            ((self.startFlag < 3) or (vertices.isLegal2(key, self.roads)))
            #settlements don't have to be by a road at the start of the game
            and (self.curPlayer.boughtSettlement == True)):
            self.vertices[key][0] = 1 #1 means settlement, 2 means city 
            self.vertices[key][1] = self.curPlayer
            self.curPlayer.boughtSettlement = False #placed a settlement
            self.lastV = 0
            if (self.startFlag == 1): self.placedS += 1
        elif ((key != None) and (self.curPlayer.boughtRoad > 0)):
            for road in self.roads:
                if ((self.lastV in road) and (key in road) and
                    (self.lastV != key) and (vertices.legalRoad(self, key))
                    and (road[2] == None)):
                    road[2] = self.curPlayer.num #place road
                    self.curPlayer.boughtRoad -= 1 #placed the road
                    if (self.startFlag == 1): self.placedR += 1
            self.lastV = key
        elif ((key != None) and (self.curPlayer.boughtUpgrade == True) and
              (self.vertices[key][1] == self.curPlayer)):
            self.vertices[key][0] = 2 #1 means settlement, 2 means city
            self.curPlayer.boughtUpgrade = False #placed the upgrade
        if (self.startFlag == 1): #last player goes twice in a row
            self.curPlayer.boughtSettlement = True
            self.curPlayer.boughtRoad = 1
            if (self.placedS == 2): #already put down 2 settlements
                self.curPlayer.boughtSettlement = False
            if (self.placedR == 4): #already put down 2 roads
                self.curPlayer.boughtRoad = 0
            
    def keyPressed(self, event):
        if (event.char == "1"):
            self.menu = 1 #draw launch screen
            self.hideButtons()
        if (event.char == "2"):
            self.menu = 2 #draw game
            self.showButtons() #make buttons appear
        if (event.char == "3"):
            self.menu = 3 #draw instructions
            self.hideButtons()
            
    def timerFired(self): pass

    def initPlayers(self): #always at least a 2 person game
        self.player1 = player.Player()
        self.player1.setPlayer(1)
        self.player2 = player.Player()
        self.player2.setPlayer(2)
    
    def init(self):
        self.tiles = tile.tiles()
        self.deck = developmentCards.generateDeck()
        self.vertices = vertices.init()
        self.roads = vertices.initRoads(self.vertices)
        draw.drawInit(self)
        self.diceRolled = False
        self.resourcesCollected = False
        self.gameOver = False
        self.initPlayers()
        self.curPlayer = self.player1
        self.dice = self.rollDice()
        self.lastV = 0
        self.startFlag = 0
        self.placedS = 0
        self.placedR = 0
        self.menu = 1
        self.curLargestArmy = 2 #need at least 3 Soldiers to get bonus VP
            
    def drawGame(self):
        if (self.gameOver == False):
            draw.drawBG(self)
            draw.drawTitle(self)
            draw.drawBoard(self)
            draw.drawDiceRoll(self)
            draw.drawPlayer(self, self.curPlayer)
            #draw.drawKey(self)
            draw.drawRoads(self, self.roads, self.vertices)
            draw.drawSettlements(self, self.vertices)
        else: #gameOver is true
            draw.drawWinner(self) #draw winning screen
            self.hideButtons()          #hide all buttons 
            self.f.place(x=20, y=565)   #except for New Game button
        
    def redrawAll(self):
        if (self.menu == 1):
            self.a.pack_forget()
            draw.drawMenuScreen(self)
        elif (self.menu == 2):
            self.drawGame()
        elif (self.menu == 3):
            draw.drawInstructions(self)

    def rollDice(self):
        rolls = range(1,7)
        if (self.diceRolled == False): #only roll dice once per turn
            self.die1 = random.choice(rolls)
            self.die2 = random.choice(rolls)
            self.dice = self.die1 + self.die2
            self.diceRolled = True
        if (self.resourcesCollected == False): #only collect resources once
            vertices.addResources(self.dice, self.vertices, self.tiles)
            self.resourcesCollected = True

    def buyRoad(self):
        self.curPlayer.subtractRoad()

    def buySettlement(self):
        self.curPlayer.subtractSettlement()

    def upgradeSettlement(self):
        self.curPlayer.subtractUpgrade()
        
    def buyCard(self):
        bought = self.curPlayer.subtractCard()
        if (bought == True): #player had the resources to buy a card
            if (len(self.deck) > 0): #deck still has cards in it
                card = self.deck[0]
                self.deck = self.deck[1:] #remove that card from deck
                developmentCards.cardPopup(self, card)
        else: #player didn't have the resources to buy a card
            warning = "You don't have the resources to buy a development "
            warning += "card!\nYou need 1 each of ore, wheat, and wool."
            tkMessageBox.showwarning(title="Not Enough Resources!",
                                     message=warning)
    
    def nextPlayer(self):
        if (self.curPlayer.boughtUpgrade == True):
            warning = "You need to use the upgrade you have before "
            warning += "you end your turn."
            tkMessageBox.showwarning(title=None, message=warning)
        elif (self.curPlayer.boughtSettlement == True):
            warning = "You need to place the settlement you have before "
            warning += "you end your turn."
            tkMessageBox.showwarning(title=None, message=warning)
        elif (self.curPlayer.boughtRoad > 0):
            warning = "You need to place the road you have before "
            warning += "you end your turn."
            tkMessageBox.showwarning(title=None, message=warning)
        elif (self.diceRolled == False and self.startFlag >= 3):
            warning = "You forgot to roll the dice!"
            tkMessageBox.showwarning(title=None, message=warning)
        else:
            self.diceRolled = False
            self.resourcesCollected = False
            if (self.curPlayer == self.player1):
                self.curPlayer = self.player2
            else:
                self.curPlayer = self.player1
            self.lastV = 0
            self.startFlag += 1
            if (self.startFlag == 2):
                self.curPlayer.boughtSettlement = True
                self.curPlayer.boughtRoad = 1
            if (self.startFlag == 3):
                #each player gets 1 of each resource they're adjacent to
                vertices.getStartResources(self)
                self.a.configure(state='normal')
                #can start getting resources from dice rolls now

    def newGame(self):
        self.init()
        self.hideButtons()

    def tryToWin(self):
        VP = self.curPlayer.getVP(self.vertices)
        if (VP >= 10): #need 10 victory points to win the game
            message = "Player " + str(self.curPlayer.num) +" has won the game!"
            message += "\n\nCongratulations!"
            tkMessageBox.showinfo(title="You won the game! (:",
                                  message=message)
            self.gameOver = True
        else:
            message = "You didn't win! You only have " + str(VP)
            message += " victory points; you need 10 to win!"
            tkMessageBox.showinfo(title="Not enough victory points. :(",
                                  message=message)

    def showButtons(self):
        self.a.place(x=578, y=210)
        self.b.place(x=260, y=30)
        self.c.place(x=343, y=30)
        self.d.place(x=260, y=70)
        self.e.place(x=585, y=370)
        self.f.place(x=20, y=565)
        self.g.place(x=570, y=325)
        self.h.place(x=540, y=560)
        self.i.place(x=620, y=560)
        self.j.place(x=350, y=70)
        
    def hideButtons(self):
        self.a.place_forget()
        self.b.place_forget()
        self.c.place_forget()
        self.d.place_forget()
        self.e.place_forget()
        self.f.place_forget()
        self.g.place_forget()
        self.h.place_forget()
        self.i.place_forget()
        self.j.place_forget()

    def loadHelper(self):
        self.top = Toplevel()
        Label(self.top, text="Load Existing Game").pack()
        self.entry = Entry(self.top)
        self.entry.pack(padx=5)
        self.entryButton = Button(self.top, text="Load", command=self.load)
        self.entryButton.pack(pady=5)
        
    def load(self): #based off of what Jordan sent to recitation G
        self.fileName = self.entry.get() + '.txt'
        self.top.destroy()
        fileName = self.fileName
        try:
            with open(fileName, 'rb') as file:
                data = pickle.load(file)
                self.tiles = data["tiles"]          #load old board
                self.deck = data["deck"]
                self.vertices = data["vertices"]
                self.roads = data["roads"]
                self.player1.resources=data["p1R"]  #load player info
                self.player2.resources=data["p2R"]
                self.player1.army=data["p1A"]
                self.player2.army=data["p2A"]
                self.player1.largestArmy=data["p1La"]
                self.player2.largestArmy=data["p2La"]
                self.player1.longestRoad=data["p1Lo"]
                self.player2.longestRoad=data["p2Lo"]
                self.player1.VPcards=data["p1VP"]
                self.player2.VPcards=data["p2VP"]                
                self.startFlag = 3  #make sure start game sequence doesn't
                                    #happen when load existing game
        except:
            text=""

    def save(self):
        if (self.startFlag < 3): #players haven't done start sequence
            no = "You haven't even finished the game set up!"
            no += "\nYou can't save this game yet."
            tkMessageBox.showwarning(title="Can't Save!", message=no)
        else:
            self.top = Toplevel()
            Label(self.top, text="Name Your Save").pack()
            self.entry = Entry(self.top)
            self.entry.pack(padx=5)
            self.entryButton = Button(self.top, text="Save",
                                      command=self.saved)
            self.entryButton.pack(pady=5)
    
    def saved(self):
        self.fileName = self.entry.get() + '.txt'
        self.top.destroy()
        fileName = self.fileName
        p1 = self.player1
        p2 = self.player2
        with open(fileName, 'wb') as file:   
            pickle.dump(dict(tiles=self.tiles, deck=self.deck,
                           vertices=self.vertices, roads=self.roads,
                             p1R=p1.resources, p2R=p2.resources,
                             p1A=p1.army, p2A=p2.army,
                             p1La=p1.largestArmy, p2La=p2.largestArmy,
                             p1Lo=p1.longestRoad, p2Lo=p2.longestRoad,
                             p1VP=p1.VPcards, p2VP=p2.VPcards), file) 
        
    def run(self, width=700, height=600):
        # create the root and the canvas
        root = Tk()
        self.width = width
        self.height = height
        self.canvas = Canvas(root, width=width, height=height)
        root.resizable(0,0)
        self.root = root
        self.a = Button(root, text="Roll the Dice", command=self.rollDice,
                        state=DISABLED)
                        #can't get resources from dice at the start of game
        self.b = Button(root, text="Buy Road", command=self.buyRoad) 
        self.c = Button(root, text="Buy Settlement",
                        command=self.buySettlement)
        self.d = Button(root, text="Buy Upgrade",
                        command=self.upgradeSettlement)
        self.e = Button(root, text="End Turn", command=self.nextPlayer)
        self.f = Button(root, text="New Game", command=self.newGame)
        self.g = Button(root, text="Declare Victory!", command=self.tryToWin)
        self.h = Button(root, text="Save Game", command=self.save)
        self.i = Button(root, text="Load Game", command=self.loadHelper)
        self.j = Button(root, text="Buy DVP Card", command=self.buyCard)
        self.canvas.pack()
        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redrawAll()
        def mousePressedWrapper(event):
            self.mousePressed(event)
            redrawAllWrapper()
        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()
        #draws a circle around a vertex if mouse hovers over it (for UI)
        def hover(event):
            if (self.menu == 2): #only draw when viewing board
                key = vertices.findRange(event.x, event.y, self.vertices)
                if (key != None):
                    #find the center of vertex to draw circle around
                    vx, vy = self.vertices[key][len(self.vertices[key])-1]
                    color = draw.findColor(self.curPlayer.num)
                    self.canvas.create_oval(vx-20, vy-20, vx+20, vy+20,
                                            outline = color, width=2)
        root.bind("<Button-1>", mousePressedWrapper)
        root.bind("<Key>", keyPressedWrapper)
        root.bind("<Motion>", hover)
        # set up timerFired events
        self.timerFiredDelay = 250 # milliseconds
        def timerFiredWrapper():
            self.timerFired()
            redrawAllWrapper()
            # pause, then call timerFired again
            self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        root.mainloop()

app = Catan()
app.run()
