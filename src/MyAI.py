# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action
from random import choice
# from time import ?

queueOfZero = []	# Keep track of tiles that have a label of 0 only

# A helper class to help keep track of individual
# tiles in the Minesweeper board. Each object keeps
# track of various metrics, such as the label, effective
# label, and if the tile has been visited, covered, or
# marked. Position on the board is denoted by the tile's
# index into the 2D board array that our agent maintains.
#
# Example: self.board[5][7] <==> Tile at (5,7)
class Tile:
    
    def __init__(self):
        self.visited = False
        self.covered = True
        self.marked = False
        self.label = 0
        self.effectiveLabel = 0
        self.markedNeighbors = 0
        self.unmarkedNeighbors = 0


class MyAI( AI ):

    def __init__(self, rowDimension: int, colDimension: int, totalMines: int, startX: int, startY: int):

        # Set up board, have to set it up this way
        # because using a list comprehension was messing
        # things up alot...
        self.board = []
        for i in range(rowDimension):
            self.board.append([])
            for j in range(colDimension):
                self.board[i].append(Tile())

        # Keep track of safe tiles to uncover
        # with a set of (x,y) coordinates
        self.safeToUncover = set()

        # Keep track of our frontier, aka the nodes
        # that separate the known from the unknown
        self.uncoveredFrontier = set()
        self.coveredFrontier = set()

        # Declare vars
        self.mineTotal = totalMines
        self.rowDimension = rowDimension
        self.colDimension = colDimension
        self.totalTiles = self.rowDimension * self.colDimension
        self.x = startX
        self.y = startY

        # Update our board at the first tile
        self.board[self.x][self.y].visited = True
        self.board[self.x][self.y].covered = False
        self.board[self.x][self.y].label = 0


    def isValidCoordinates(self, x: int, y: int) -> bool:
        """Returns True if (x,y) are valid coordinates, False otherwise."""
        return (x < self.rowDimension and x >= 0 and y < self.colDimension and y >= 0)
    

    def generateNeighbors(self, x: int, y: int) -> [(int,int)]:
        """Generates all valid neighbor coordinates of a tile given coordinates (x,y)."""

        validNeighbors = []

        if self.isValidCoordinates(x - 1, y - 1): # Top-left neighbor
            validNeighbors.append((x - 1, y - 1))
        if self.isValidCoordinates(x, y - 1): # Top neighbor
            validNeighbors.append((x, y - 1))
        if self.isValidCoordinates(x + 1, y - 1): # Top-right neighbor
            validNeighbors.append((x + 1, y - 1))
        if self.isValidCoordinates(x - 1, y): # Left neighbor
            validNeighbors.append((x - 1, y))
        if self.isValidCoordinates(x + 1, y): # Right neighbor
            validNeighbors.append((x+1, y))
        if self.isValidCoordinates(x - 1, y + 1): # Bottom-left neighbor
            validNeighbors.append((x - 1, y + 1))
        if self.isValidCoordinates(x, y + 1): # Bottom neighbor
            validNeighbors.append((x, y + 1))
        if self.isValidCoordinates(x + 1, y + 1): # Bottom-right neighbor
            validNeighbors.append((x + 1, y + 1))

        return validNeighbors				
        
    def getMarked(self, x, y):
        numOfMarked = 0
        for _x, _y in self.generateNeighbors(x, y):
            if self.board[_x][_y].marked == True:
                numOfMarked += 1
        return numOfMarked

    def getAction(self, number: int) -> "Action Object":
        """
        Based on the label provided for the last tile we visited, the agent
        computes the next action to perform. The argument number is the label.
        """
        
        # Action for the AI
        action = ""

        # Reference to last tile uncovered
        lastTile = self.board[self.x][self.y]

        # Calculate the amount of covered tiles	
        self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])
        # LEAVE if we meet the game condition	
        if self.coveredTiles == self.totalTiles:
            return Action(AI.Action.LEAVE)

        # Update the board with the tile we just uncovered
        lastTile.visited = True
        lastTile.covered = False
        lastTile.label = number

        # Add new safe tiles if we uncovered a tile with label 0
        if number == 0:
            for x, y in self.generateNeighbors(self.x, self.y):
                if not self.board[x][y].visited:
                    if (x, y) in self.coveredFrontier:
                        self.coveredFrontier.remove((x,y))
                    self.safeToUncover.add((x,y))

        # Add nodes to frontier if we uncovered a tile with a non-zero label
        else:
            # Add the node to the uncovered frontier set
            self.uncoveredFrontier.add((self.x, self.y))

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(x, y) for x, y in self.generateNeighbors(self.x, self.y) if not self.board[x][y].visited and (x, y) not in self.uncoveredFrontier and (x, y) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)



        # print("safe ({}): {}".format(len(self.safeToUncover), self.safeToUncover))
        # print("uncovered frontier ({}): {}".format(len(self.uncoveredFrontier), self.uncoveredFrontier))
        # print("covered frontier ({}): {}".format(len(self.coveredFrontier), self.coveredFrontier))

        
        # FIRST RULE OF THUMB: Uncover a safe tile
        if self.safeToUncover:
            x, y = self.safeToUncover.pop()
            self.x = x
            self.y = y
            return Action(AI.Action.UNCOVER, x, y)

        # SECOND RULE OF THUMB: Check if any uncovered frontier nodes
        # have just one unvisited neighbor
        # You need to consider to update frontier after flagging <-------------------------------------------------
        for x, y in self.uncoveredFrontier:
            unvisited_neighbor_count = 0
            unvisited_neighbor = None
            for x2, y2 in self.generateNeighbors(x, y):
                if not self.board[x2][y2].visited:
                    unvisited_neighbor_count += 1
                    unvisited_neighbor = (x2, y2)
            if unvisited_neighbor_count == 1:
                x3, y3 = unvisited_neighbor
                if self.board[x3][y3].marked:
                    continue
                self.board[x3][y3].marked = True
                if (x3, y3) in self.coveredFrontier:
                    self.coveredFrontier.remove((x3, y3))
                self.uncoveredFrontier.remove((x, y))
                return Action(AI.Action.FLAG, x3, y3)

        # THIRD RULE OF THUMB: Calculate effective label
        for x, y in self.uncoveredFrontier:
            self.board[x][y].markedNeighbors = self.getMarked(x, y)
            self.board[x][y].effectiveLabel = self.board[x][y].label - self.board[x][y].markedNeighbors
            if self.board[x][y].effectiveLabel == 0:
                # Update self.safeToUncover
                for _x, _y in self.generateNeighbors(x, y):
                    if self.board[_x][_y].covered == True and self.board[_x][_y].marked == False:
                        self.board[_x][_y].covered = False
                        self.board[_x][_y].visited = True
                        if (_x, _y) in self.coveredFrontier:
                            self.coveredFrontier.remove((_x, _y))
                            self.uncoveredFrontier.add((_x, _y))
                        self.x = _x
                        self.y = _y
                        return Action(AI.Action.UNCOVER, _x, _y)


        # Have yet to implement better logic
        return Action(AI.Action.LEAVE)