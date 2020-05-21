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
        self.flagTotal = 0
        self.rowDimension = rowDimension
        self.colDimension = colDimension
        self.totalTiles = self.rowDimension * self.colDimension
        self.x = startX
        self.y = startY
        
        self.sol = dict()
        self.invalid = dict()

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
        
    def removeUncovered(self) -> None:
        """Removes all tiles from the uncovered frontier if their effective label is 0 and they have no unmarked neighbors."""
        removeList = []

        # Iterate through the uncovered frontier
        for x, y in self.uncoveredFrontier:
            if self.board[x][y].effectiveLabel == 0 and self.board[x][y].unmarkedNeighbors == 0:
                removeList.append((x,y))

        # Remove tiles if there are any
        if removeList:
            for x, y in removeList:
                self.uncoveredFrontier.remove((x, y))

    def removeCovered(self) -> None:
        """Removes all tiles from the covered frontier if they have already been visited/flagged, as well as their neighbors."""
        removeList = []

        # Iterate through the covered frontier, as well as their neighbors
        for x, y in self.coveredFrontier:
            if self.board[x][y].marked or self.board[x][y].visited:
                removeList.append((x,y))
            for x2, y2 in self.generateNeighbors(x, y):
                if self.board[x2][y2].visited and self.board[x2][y2].label != 0 and self.board[x2][y2].unmarkedNeighbors == 0:
                    removeList.append((x2,y2))

        # Remove tiles if there are any
        if removeList:
            for x, y in removeList:
                if (x, y) in self.coveredFrontier:
                    self.coveredFrontier.remove((x,y))
        
    def getMarked(self, x: int, y: int) -> None:
        numOfMarked = 0
        for _x, _y in self.generateNeighbors(x, y):
            if self.board[_x][_y].marked == True:
                numOfMarked += 1
        return numOfMarked

    def getSolution(self, x: int, y: int, coveredList: list, uncoveredList: list) -> None:
        # Need to check for effectiveLabel when flagging tiles; you can't flag a tile if effectiveLabel == 0...
        if len(coveredList) == 0:
            return (x, y)

        else:
            change = False
            changeList = []
            x1, y1 = coveredList.pop()

            # Check to make sure not to "flag" the other tiles that are adjacent to the tile that you picked
            for newX, newY in self.generateNeighbors(x, y):
                if (newX, newY) in coveredList:
                    changeList.append((newX, newY))
                    change = True
                    break
            if change:
                for newX, newY in changeList:
                    coveredList.remove((newX, newY))
                if len(coveredList) != 0:
                    x1, y1 = coveredList.pop()
                else:
                    return self.sol[(x, y)]

            for newX, newY in self.generateNeighbors(x1, y1):
                if (newX, newY) in coveredList:
                    # This is where you will create two branches; flagging x1, y2 or other neighbor tiles
                    duplList = coveredList.copy()
                    duplList.remove((x1, y1))
                    self.sol[(x, y)].append(self.getSolution(x, y, duplList, uncoveredList))
                    coveredList.remove((newX, newY))
            
            return self.sol[(x,y)].append(self.getSolution(x, y, coveredList, uncoveredList))

    def getAction(self, number: int) -> "Action Object":
        """
        Based on the label provided for the last tile we visited, the agent
        computes the next action to perform. The argument number is the label.
        """

        # Reference to last tile uncovered
        lastTile = self.board[self.x][self.y]

        # Calculate the amount of covered tiles	
        self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])
        # LEAVE if we meet the game condition	
        if self.coveredTiles == self.totalTiles:
            return Action(AI.Action.LEAVE)
        
        if self.flagTotal == self.mineTotal:
            return Action(AI.Action.LEAVE)

        # Update the board with the tile we just uncovered
        lastTile.visited = True
        lastTile.covered = False
        lastTile.label = number

        # Remove unecessary tiles from the frontier (Tiles that have no possible moves left or tiles whose neighbors are all visited)
        self.removeUncovered()
        self.removeCovered()

        # Add new safe tiles if we uncovered a tile with label 0
        if number == 0:
            for x, y in self.generateNeighbors(self.x, self.y):
                if not self.board[x][y].visited:
                    if (x, y) in self.coveredFrontier:
                        self.coveredFrontier.remove((x,y))
                    self.safeToUncover.add((x,y))

        # Add nodes to frontier if we uncovered a tile with a non-zero label
        else:
            # Update variables for an uncovered tile
            for x2, y2 in self.generateNeighbors(self.x, self.y):
                if not self.board[x2][y2].visited:
                    self.board[self.x][self.y].unmarkedNeighbors += 1
                elif self.board[x2][y2].marked:
                    self.board[self.x][self.y].markedNeighbors += 1
            self.board[self.x][self.y].effectiveLabel = self.board[self.x][self.y].label - self.board[self.x][self.y].markedNeighbors

            # Add the node to the uncovered frontier set
            self.uncoveredFrontier.add((self.x, self.y))

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(x, y) for x, y in self.generateNeighbors(self.x, self.y) if not self.board[x][y].visited and (x, y) not in self.uncoveredFrontier and (x, y) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)


        # --------- DEBUG --------------
        # print("safe ({}): {}".format(len(self.safeToUncover), self.safeToUncover))
        # print("uncovered frontier ({}): {}".format(len(self.uncoveredFrontier), self.uncoveredFrontier))
        # print("covered frontier ({}): {}".format(len(self.coveredFrontier), self.coveredFrontier))
        # --------- DEBUG --------------


        # FIRST RULE OF THUMB: Uncover a safe tile
        if self.safeToUncover:
            x, y = self.safeToUncover.pop()
            self.x = x
            self.y = y

            # Update the uncovered tiles (whose label is not 0) that are adjacent to the current tile (tile w/ label 0)
            for x2, y2 in self.generateNeighbors(x, y):
                if self.board[x2][y2].label != 0:
                    if self.board[x2][y2].unmarkedNeighbors > 0:
                        self.board[x2][y2].unmarkedNeighbors -= 1

            return Action(AI.Action.UNCOVER, x, y)


        # SECOND RULE OF THUMB: Calculate effective label
        for x, y in self.uncoveredFrontier:

            # All the unmarked tiles are safe to uncover
            if self.board[x][y].effectiveLabel == 0:
                for _x, _y in self.generateNeighbors(x, y):
                    if self.board[_x][_y].covered == True and self.board[_x][_y].marked == False:

                        self.board[_x][_y].covered = False
                        self.board[_x][_y].visited = True

                        if (_x, _y) in self.coveredFrontier:
                            self.coveredFrontier.remove((_x, _y))

                        self.x = _x
                        self.y = _y

                        # Generate the neighbors from the tile with effectiveLabel == 0 and update variables
                        for x2, y2 in self.generateNeighbors(_x, _y):
                            if self.board[x2][y2].label != 0 and self.board[x2][y2].visited:
                                if self.board[x2][y2].unmarkedNeighbors > 0:
                                    self.board[x2][y2].unmarkedNeighbors -= 1

                        return Action(AI.Action.UNCOVER, _x, _y)

            # All adjacent tiles to the current tile are mines
            elif self.board[x][y].effectiveLabel == self.board[x][y].unmarkedNeighbors:

                # unvisitedNeighbors is a list that holds all of the unvisited neighbors of (x,y)
                unvisitedNeighbors = []
                # changeList is used to prevent the AI from not to update variables (same tile) again
                changeList = []
                # change is a boolean variable that notify the AI whether the (x, y) has changed or not (It should not uncover the previous move again; otherwise it would unnecessarily update the previous tile at the beginning (Line 178))
                change = False

                # Calculate all of the unvisited neighbors
                for x2, y2 in self.generateNeighbors(x, y):
                    if not self.board[x2][y2].visited:
                        unvisitedNeighbors.append((x2, y2))

                for x3, y3 in unvisitedNeighbors:
                    if self.board[x3][y3].marked:
                        continue

                    self.board[x3][y3].marked = True
                    self.board[x3][y3].visited = True

                    # Update uncovered tiles that are adjacent to the mine
                    for x4, y4 in self.generateNeighbors(x3, y3):
                        if self.board[x4][y4].label != 0 and self.board[x4][y4].visited:

                            self.board[x4][y4].unmarkedNeighbors -= 1
                            self.board[x4][y4].markedNeighbors += 1
                            self.board[x4][y4].effectiveLabel = self.board[x4][y4].label - self.board[x4][y4].markedNeighbors

                            changeList.append((x4, y4))

                            if self.board[x4][y4].effectiveLabel == 0 and self.board[x4][y4].unmarkedNeighbors != 0:
                                for newX, newY in self.generateNeighbors(x4, y4):
                                    if not self.board[newX][newY].visited and not self.board[newX][newY].marked:
                                        self.x = newX
                                        self.y = newY
                                        change = True

                    if (x3, y3) in self.coveredFrontier:
                        self.coveredFrontier.remove((x3, y3))

                    # self.flagTotal is for testing purpose (Ignore it; although I might use it depending on the situation)
                    self.flagTotal += 1
                
                # This if statement will prevent the AI from using the same previous move again
                if not change:
                    continue

                # Update the tiles that are not in changeList (Making sure not to update the same tiles as it did in line 248)
                for x2, y2 in self.generateNeighbors(self.x, self.y):
                    if (x2, y2) not in changeList and self.board[x2][y2].label != 0 and self.board[x2][y2].visited and not self.board[self.x][self.y].visited:
                        self.board[x2][y2].unmarkedNeighbors -= 1

                return Action(AI.Action.UNCOVER, self.x, self.y)
        

        # THIRD RULE OF THUMB: Model checking
        # Update coveredFrontier, removing unnecessary tiles
        self.removeCovered()
        
        #A storage for number of solutions (Not sure it should be a list)
        numOfSol = dict()
        # Find a way to determine a solution (Finding a possible move to flag a mine)
        
        # Find the uncovered tiles that are adjacent to covered tiles in coveredFrontier (Sometimes there are some uncovered tiles that didn't get removed from uncoveredFrontier (Not sure why))
        validUncovered = []
        for x, y in self.uncoveredFrontier:
            for x2, y2 in self.generateNeighbors(x, y):
                if (x2, y2) in self.coveredFrontier:
                    if (x, y) not in validUncovered:
                        validUncovered.append((x,y))

        # A solution...
        print("covered frontier ({}): {}".format(len(self.coveredFrontier), self.coveredFrontier))
        validUncovered.sort()
        print(validUncovered)

        small = 8
        for x, y in validUncovered:
            if small > self.board[x][y].unmarkedNeighbors:
                small = self.board[x][y].unmarkedNeighbors
        for x, y in validUncovered:
            if small == self.board[x][y].unmarkedNeighbors:
                validX = x
                validY = y
                break

        validUncovered.remove((validX, validY))
        print(validUncovered)
        print(validUncovered)
        numOfNeigh = []

        for x, y in self.generateNeighbors(validX, validY):
            if (x, y) in self.coveredFrontier:
                numOfNeigh.append((x, y))
        numOfNeigh.sort()
        print(numOfNeigh)
        #result = list(set(self.coveredFrontier) ^ set(numOfNeigh))
        for x, y in numOfNeigh:
            duplicateList = self.coveredFrontier.copy()
            self.sol[(x, y)] = list()
            duplicateList.remove((x,y))
            self.getSolution(x, y, duplicateList, validUncovered)

        for key, value in self.sol.items():
            if len(value) == 0:
                numOfSol[key] = 1
            else:
                numOfSol[key] = len(value)

        min_val =  min(numOfSol.values())

        result = [key for key, value in numOfSol.items() if value == min_val]
        # print(result)
            # for x2, y2 in result:
            #     break



        # Place-holder <----------------- make sure to remove this!

        return Action(AI.Action.LEAVE)