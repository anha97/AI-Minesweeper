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
        self.coveredTiles = self.rowDimension * self.colDimension
        self.x = startX
        self.y = startY

        # Update our board at the first tile
        self.board[self.y][self.x].visited = True
        self.board[self.y][self.x].covered = False
        self.board[self.y][self.x].label = 0


    def isValidCoordinates(self, y: int, x: int) -> bool:
        """Returns True if (y,x) are valid coordinates, False otherwise."""
        return (y < self.rowDimension and y >= 0 and x < self.colDimension and x >= 0)
    

    def generateNeighbors(self, y: int, x: int) -> [(int,int)]:
        """Generates all valid neighbor coordinates of a tile given coordinates (y,x)."""
        validNeighbors = []

        if self.isValidCoordinates(y - 1, x - 1): # Top-left neighbor
            validNeighbors.append((y - 1, x - 1))
        if self.isValidCoordinates(y, x - 1): # Top neighbor
            validNeighbors.append((y, x - 1))
        if self.isValidCoordinates(y + 1, x - 1): # Top-right neighbor
            validNeighbors.append((y + 1, x - 1))
        if self.isValidCoordinates(y - 1, x): # Left neighbor
            validNeighbors.append((y - 1, x))
        if self.isValidCoordinates(y + 1, x): # Right neighbor
            validNeighbors.append((y + 1, x))
        if self.isValidCoordinates(y - 1, x + 1): # Bottom-left neighbor
            validNeighbors.append((y - 1, x + 1))
        if self.isValidCoordinates(y, x + 1): # Bottom neighbor
            validNeighbors.append((y, x + 1))
        if self.isValidCoordinates(y + 1, x + 1): # Bottom-right neighbor
            validNeighbors.append((y + 1, x + 1))

        return validNeighbors
        
    def getMarked(self, y: int, x: int) -> None:
        """Calculate's the number of marked neighbors given a tile at (y, x)."""
        numOfMarked = 0
        for y2, x2 in self.generateNeighbors(y, x):
            if self.board[y2][x2].marked == True:
                numOfMarked += 1
        return numOfMarked

    def getAction(self, number: int) -> "Action Object":
        """
        Based on the label provided for the last tile we visited, the agent
        computes the next action to perform. The argument number is the label.
        """

        # ------- PRE-WORK ------------

        # Update the board with the tile we just uncovered
        self.board[self.y][self.x].visited = True if number != -1 else False
        self.board[self.y][self.x].covered = False if number != -1 else True
        self.board[self.y][self.x].label = number

        # Calculate the amount of covered tiles	
        self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])

        # LEAVE if we meet the game condition	
        if self.coveredTiles == self.totalTiles:
            return Action(AI.Action.LEAVE)

        # Remove the last uncovered tile from the covered frontier if it was in there
        if (self.y, self.x) in self.coveredFrontier:
            self.coveredFrontier.remove((self.y, self.x))

        # Remove tiles from the uncovered frontier if they are not neighboring any covered nodes
        uncovered_to_remove = []
        for y, x in self.uncoveredFrontier:
            neighbor_count = [(y2, x2) for y2, x2 in self.generateNeighbors(y, x) if self.board[y2][x2].covered]
            if len(neighbor_count) == 0 or all([True if self.board[y3][x3].marked else False for y3, x3 in neighbor_count]):
                uncovered_to_remove.append((y, x))
            
        for tile in uncovered_to_remove:
            self.uncoveredFrontier.remove(tile)

        # If we last uncovered a tile with label 0, all of its neighbors are safe
        if number == 0:

            # Process each neighbor
            for y, x in self.generateNeighbors(self.y, self.x):
                if not self.board[y][x].visited:
                    if (y, x) not in self.coveredFrontier:
                        self.coveredFrontier.add((y, x))
                    self.safeToUncover.add((y, x))

            # Don't forget to add the last tile we uncovered to our uncovered frontier (might need to change this)
            self.uncoveredFrontier.add((self.y, self.x))

        elif number == -1:

            # Not sure if we should add the flagged bomb to the uncoveredFrontier... probably not but we could need to

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(y, x) for y, x in self.generateNeighbors(self.y, self.x) if not self.board[y][x].visited and not self.board[y][x].marked and (y, x) not in self.uncoveredFrontier and (y, x) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)
        
        # If we last uncovered a tile with label > 0, ..... blah blah blah
        else:

            # Add the node to the uncovered frontier set
            self.uncoveredFrontier.add((self.y, self.x))

            # Neighboring nodes that aren't safe or uncovered frontier nodes are covered frontier nodes
            newCoveredFrontierTiles = {(y, x) for y, x in self.generateNeighbors(self.y, self.x) if not self.board[y][x].visited and not self.board[y][x].marked and (y, x) not in self.uncoveredFrontier and (y, x) not in self.safeToUncover}
            self.coveredFrontier = self.coveredFrontier.union(newCoveredFrontierTiles)

         # ------- PRE-WORK ------------


        # --------- DEBUG --------------

        # print("\nnumber = {}".format(number))
        # print("coveredTiles = {}\nmineTotal = {}".format(self.coveredTiles, self.mineTotal))
        # print("safe ({}): {}".format(len(self.safeToUncover), self.safeToUncover))
        # print("uncovered frontier ({}): {}".format(len(self.uncoveredFrontier), self.uncoveredFrontier))
        # print("covered frontier ({}): {}\n".format(len(self.coveredFrontier), self.coveredFrontier))

        # --------- DEBUG --------------


        # FIRST RULE OF THUMB: Uncover a safe tile, if any
        if self.safeToUncover:
            y, x = self.safeToUncover.pop()
            self.x = x
            self.y = y
            return Action(AI.Action.UNCOVER, x, y)


        # SECOND RULE OF THUMB: Check if any uncovered frontier tiles have just one unvisited neighbor
        for y, x in self.uncoveredFrontier:

            # Keep track of the unvisited neighbors for each uncovered frontier tile
            unvisited_neighbor_count = 0
            unvisited_neighbor = None

            # Now, count all of the unvisited neighbors
            for y2, x2 in self.generateNeighbors(y, x):
                if not self.board[y2][x2].visited:
                    unvisited_neighbor_count += 1
                    unvisited_neighbor = (y2, x2)
            
            # If the count is 1, then we know that that one unvisited neighbor is a bomb
            if unvisited_neighbor_count == 1:

                # Get the coordinates of this tile
                y3, x3 = unvisited_neighbor

                # Don't do anything if it is already flagged
                if self.board[y3][x3].marked:
                    continue

                # Flag if it isn't already
                self.board[y3][x3].marked = True
                self.x = x3
                self.y = y3

                # Remove the tile from the covered frontier if it is in there
                if (y3, x3) in self.coveredFrontier:
                    self.coveredFrontier.remove((y3, x3))

                # Finally, return the flag action
                return Action(AI.Action.FLAG, x3, y3)


        # THIRD RULE OF THUMB: Calculate effective label
        for y, x in self.uncoveredFrontier:
            
            # Calculate the marked neighbor count and effective label of an uncovered frontier tile
            self.board[y][x].markedNeighbors = self.getMarked(y, x)
            self.board[y][x].effectiveLabel = self.board[y][x].label - self.board[y][x].markedNeighbors

            # Calculate the unmarked neighbor count of the uncovered frontier tile
            self.board[y][x].unmarkedNeighbors = sum([1 for y3, x3 in self.generateNeighbors(y, x) if not self.board[y3][x3].visited]) - self.board[y][x].markedNeighbors

            # If effective label is 0, all remaining unvisited neighbors are safe to uncover
            if self.board[y][x].effectiveLabel == 0:

                # Check all of the tile's neighbors
                for y2, x2 in self.generateNeighbors(y, x):

                    # Select one of the unvisited tiles
                    if not self.board[y2][x2].visited and not self.board[y2][x2].marked:
                        
                        self.x = x2
                        self.y = y2
                        return Action(AI.Action.UNCOVER, x2, y2)



            # If effective label is the same as the unmarked neighbor count, then all remaining unmarked neighbors are mines
            elif self.board[y][x].effectiveLabel == self.board[y][x].unmarkedNeighbors:
                
                # Check all of the tile's neighbors
                for y2, x2 in self.generateNeighbors(y, x):

                    # Select one of the unmarked, unvisited tiles
                    if not self.board[y2][x2].visited and not self.board[y2][x2].marked:

                        self.board[y2][x2].marked = True
                        self.x = x2
                        self.y = y2

                        # Remove the tile from the covered frontier if it is in there
                        if (y2, x2) in self.coveredFrontier:
                            self.coveredFrontier.remove((y2, x2))

                        # Finally, return the flag action
                        return Action(AI.Action.FLAG, x2, y2)

        
        # FOURTH RULE OF THUMB: Guess (as of now)
        for y, x in self.coveredFrontier:
            self.x = x
            self.y = y
            return Action(AI.Action.UNCOVER, x, y)


        # Place-holder <----------------- make sure to remove this!
        return Action(AI.Action.LEAVE)