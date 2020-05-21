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
        """Calculate's the number of marked neighbors given a tile at (x,y)."""
        numOfMarked = 0
        for x2, y2 in self.generateNeighbors(x, y):
            if self.board[x2][y2].marked == True:
                numOfMarked += 1
        return numOfMarked

    def getAction(self, number: int) -> "Action Object":
        """
        Based on the label provided for the last tile we visited, the agent
        computes the next action to perform. The argument number is the label.
        """

        # ------- PRE-WORK ------------

        # Update the board with the tile we just uncovered
        self.board[self.x][self.y].visited = True if number != -1 else False
        self.board[self.x][self.y].covered = False if number != -1 else True
        self.board[self.x][self.y].label = number

        # Calculate the amount of covered tiles	
        self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])

        # LEAVE if we meet the game condition	
        if self.coveredTiles == self.totalTiles:
            return Action(AI.Action.LEAVE)
        
        if self.flagTotal == self.mineTotal:
            return Action(AI.Action.LEAVE)

        # Remove the last uncovered tile from the covered frontier if it was in there
        if (self.x, self.y) in self.coveredFrontier:
            self.coveredFrontier.remove((self.x, self.y))

        # Remove tiles from the uncovered frontier if they are not neighboring any covered nodes
        uncovered_to_remove = []
        for x, y in self.uncoveredFrontier:
            neighbor_count = [(x2, y2) for x2, y2 in self.generateNeighbors(x, y) if self.board[x2][y2].covered]
            if len(neighbor_count) == 0 or all([True if self.board[x3][y3].marked else False for x3, y3 in neighbor_count]):
                uncovered_to_remove.append((x, y))
            
        for tile in uncovered_to_remove:
            self.uncoveredFrontier.remove(tile)

        # If we last uncovered a tile with label 0, all of its neighbors are safe
        if number == 0:

            # Process each neighbor
            for x, y in self.generateNeighbors(self.x, self.y):
                if not self.board[x][y].visited:
                    if (x, y) not in self.coveredFrontier:
                        self.coveredFrontier.add((x, y))
                    self.safeToUncover.add((x, y))

            # Don't forget to add the last tile we uncovered to our uncovered frontier (might need to change this)
            self.uncoveredFrontier.add((self.x, self.y))

        elif number == -1:

            # Not sure if we should add the flagged bomb to the uncoveredFrontier... probably not but we could need to

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(x, y) for x, y in self.generateNeighbors(self.x, self.y) if not self.board[x][y].visited and not self.board[x][y].marked and (x, y) not in self.uncoveredFrontier and (x, y) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)
        
        # If we last uncovered a tile with label > 0, ..... blah blah blah
        else:

            # Add the node to the uncovered frontier set
            self.uncoveredFrontier.add((self.x, self.y))

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(x, y) for x, y in self.generateNeighbors(self.x, self.y) if not self.board[x][y].visited and not self.board[x][y].marked and (x, y) not in self.uncoveredFrontier and (x, y) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)

         # ------- PRE-WORK ------------


        # --------- DEBUG --------------

        # print("\ncoveredTiles = {}\nmineTotal = {}".format(self.coveredTiles, self.mineTotal))
        # print("safe ({}): {}".format(len(self.safeToUncover), self.safeToUncover))
        # print("uncovered frontier ({}): {}".format(len(self.uncoveredFrontier), self.uncoveredFrontier))
        # print("covered frontier ({}): {}\n".format(len(self.coveredFrontier), self.coveredFrontier))

        # --------- DEBUG --------------


        # FIRST RULE OF THUMB: Uncover a safe tile, if any
        if self.safeToUncover:
            x, y = self.safeToUncover.pop()
            self.x = x
            self.y = y
            return Action(AI.Action.UNCOVER, x, y)


        # SECOND RULE OF THUMB: Check if any uncovered frontier tiles have just one unvisited neighbor
        for x, y in self.uncoveredFrontier:

            # Keep track of the unvisited neighbors for each uncovered frontier tile
            unvisited_neighbor_count = 0
            unvisited_neighbor = None

            # Now, count all of the unvisited neighbors
            for x2, y2 in self.generateNeighbors(x, y):
                if not self.board[x2][y2].visited:
                    unvisited_neighbor_count += 1
                    unvisited_neighbor = (x2, y2)
            
            # If the count is 1, then we know that that one unvisited neighbor is a bomb
            if unvisited_neighbor_count == 1:

                # Get the coordinates of this tile
                x3, y3 = unvisited_neighbor

                # Don't do anything if it is already flagged
                if self.board[x3][y3].marked:
                    continue

                # Flag if it isn't already
                self.board[x3][y3].marked = True
                self.x = x3
                self.y = y3

                # Remove the tile from the covered frontier if it is in there
                if (x3, y3) in self.coveredFrontier:
                    self.coveredFrontier.remove((x3, y3))

                # Finally, return the flag action
                return Action(AI.Action.FLAG, x3, y3)


        # THIRD RULE OF THUMB: Calculate effective label
        for x, y in self.uncoveredFrontier:
            
            # Calculate the marked neighbor count and effective label of an uncovered frontier tile
            self.board[x][y].markedNeighbors = self.getMarked(x, y)
            self.board[x][y].effectiveLabel = self.board[x][y].label - self.board[x][y].markedNeighbors

            # Calculate the unmarked neighbor count of the uncovered frontier tile
            self.board[x][y].unmarkedNeighbors = sum([1 for x3, y3 in self.generateNeighbors(x, y) if not self.board[x3][y3].visited]) - self.board[x][y].markedNeighbors
            # print("\ntile: {}, {}".format(x, y))
            # print("effective label: {}".format(self.board[x][y].effectiveLabel))
            # print("marked neighbors: {}".format(self.board[x][y].markedNeighbors))
            # print("unmarked neighbors: {}\n".format(self.board[x][y].unmarkedNeighbors))

            # If effective label is 0, all remaining unvisited neighbors are safe to uncover
            if self.board[x][y].effectiveLabel == 0:

                # Check all of the tile's neighbors
                for x2, y2 in self.generateNeighbors(x, y):

                    # Select one of the unvisited tiles
                    if not self.board[x2][y2].visited and not self.board[x2][y2].marked:
                        # print("Case 1")
                        # print("tile: {}, {}".format(x, y))
                        # print("effective label: {}".format(self.board[x][y].effectiveLabel))
                        # print("neighbor tile: {}, {}".format(x2, y2))
                        
                        self.x = x2
                        self.y = y2
                        return Action(AI.Action.UNCOVER, x2, y2)



            # If effective label is the same as the unmarked neighbor count, then all remaining unmarked neighbors are mines
            elif self.board[x][y].effectiveLabel == self.board[x][y].unmarkedNeighbors:
                
                # Check all of the tile's neighbors
                for x2, y2 in self.generateNeighbors(x, y):

                    # Select one of the unmarked, unvisited tiles
                    if not self.board[x2][y2].visited and not self.board[x2][y2].marked:
                        # print("Case 2")
                        # print("tile: {}, {}".format(x, y))
                        # print("effective label: {}".format(self.board[x][y].effectiveLabel))
                        # print("neighbor tile: {}, {}".format(x2, y2))

                        self.board[x2][y2].marked = True
                        self.x = x2
                        self.y = y2

                        # Remove the tile from the covered frontier if it is in there
                        if (x2, y2) in self.coveredFrontier:
                            self.coveredFrontier.remove((x2, y2))

                        # Finally, return the flag action
                        return Action(AI.Action.FLAG, x2, y2)

        # Place-holder <----------------- make sure to remove this!
        return Action(AI.Action.LEAVE)