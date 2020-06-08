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
        
        self.sol = dict()
        self.invalid = dict()

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

    def getAdjacentCoveredFrontierSet(self, tile_y: int, tile_x: int, tiles: set) -> set:
        """
            Recursively generates a subset of the covered frontier for us to model check.
            All tiles must be adjacent to each other, and the set must not exceed a size of 10,
            as so to limit the computational complexity of model checking.
        """
        if len(tiles) == 10:
            return tiles

        tiles.add((tile_y, tile_x))
        
        for y, x in self.generateNeighbors(tile_y, tile_x):
            if (y, x) not in tiles and (y, x) in self.coveredFrontier:
                self.getAdjacentCoveredFrontierSet(y, x, tiles)

        return tiles

    def getCorrespondingUncoveredFrontierSet(self, covered_adjacent_tiles: set) -> set:
        """Generates all tiles adjacent to the covered frontier subset computed by self.getAdjacentCoveredFrontierSet()."""
        tiles = set()
        for y, x in self.uncoveredFrontier:
            for y2, x2 in covered_adjacent_tiles:
                if (y2, x2) in self.generateNeighbors(y, x):
                    tiles.add((y, x))
        return tiles

    def isModelConsistent(self, model: dict, uncoveredFrontierSet: set) -> bool:
        """Given a model, returns True if a model is consistent with the uncovered frontier set provided, otherwise it returns False."""

        # Calculate the effective labels of the uncoveredFrontierSet
        for y, x in uncoveredFrontierSet:
            self.board[y][x].effectiveLabel = self.board[y][x].label - self.getMarked(y, x)

        actual = {(y,x) : self.board[y][x].effectiveLabel for y, x in uncoveredFrontierSet}
        given = {(y,x) : 0 for y, x in uncoveredFrontierSet}

        for tile, value in model.items():
            # If there is a bomb, increment the count for each neighboring tile in the uncovered frontier set
            if value == 1:
                neighbors = self.generateNeighbors(tile[0], tile[1])
                for uncovered_tile in uncoveredFrontierSet:
                    if uncovered_tile in neighbors:
                        given[uncovered_tile] += 1

        # print("actual: ", actual, "\ngiven: ", given)
        return actual == given

    def generateConsistentModels(self, currentModel: dict, uncoveredFrontierSet: set) -> list:
        """Recursively generates all consistent models given a subset of adjacent covered frontier nodes and its uncovered frontier neighbors."""
        consistentModels = []

        # Base case: all tiles are assigned a value of either 0(no bomb) or 1(has bomb)
        if all([True if value != None else False for value in currentModel.values()]):

            # Determine if the model is consistent (need to do this)
            if self.isModelConsistent(currentModel, uncoveredFrontierSet):
                consistentModels.append(currentModel)

            return consistentModels
            
        # Create a copy of the currentModel (to edit)
        currentModelCopy = dict(currentModel)

        # Assign a value for a tile that hasn't been assigned yet
        for tile, value in currentModelCopy.items():

            if value == None:

                # Recurse for the 0 case
                currentModelCopy[tile] = 0
                consistentModels += self.generateConsistentModels(currentModelCopy, uncoveredFrontierSet)

                # Recurse for the 1 case
                currentModelCopy[tile] = 1
                consistentModels += self.generateConsistentModels(currentModelCopy, uncoveredFrontierSet)
                
                # Break the loop
                break

        return consistentModels

    def calculateProbabilitiesOfConsistentModels(self, coveredTiles: set, consistentModels: list) -> dict:
        """Returns a dictionary of each tile with a value of the probability that it appears in each consistent model."""
        totalModels = len(consistentModels)

        # Create a dictionary with the key as the tile and the value as the count of how many times it is a bomb
        counts = {tile : 0 for tile in coveredTiles}

        # Count all the tiles a tile is a bomb
        for model in consistentModels:
            for tile, value in model.items():
                if value == 1:
                    counts[tile] += 1

        # Calculate the probabilities using the total model count
        return {tile : count/totalModels for tile, count in counts.items()}

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
        
        if self.flagTotal == self.mineTotal:
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

                        # Finally, return the flag action
                        return Action(AI.Action.FLAG, x2, y2)

        
        # FOURTH RULE OF THUMB: Model Checking
        # print("doing model checking...");
        for y, x in self.coveredFrontier:

            # Generate a subset of adjacent covered frontier tiles (10 or less)
            coveredSet = set()
            coveredSet = self.getAdjacentCoveredFrontierSet(y, x, coveredSet)

            # Generate all of the uncovered frontier neighbors of the adjacent covered frontier subset
            uncoveredSet = self.getCorrespondingUncoveredFrontierSet(coveredSet)

            # Compute all of the consistent models
            consistentModels = self.generateConsistentModels({tile : None for tile in coveredSet}, uncoveredSet)

            # Act if there are any consistent models from this subset
            if consistentModels:
        
                # Calculate the probabilities that each tile in the covered subset is a tile in those models
                probabilities = self.calculateProbabilitiesOfConsistentModels(coveredSet, consistentModels)
                sortedProbabilities = sorted(probabilities.items(), key=(lambda x: x[1]))
                sortedProbabilitiesReverse = sorted(probabilities.items(), key=(lambda x: x[1]), reverse=True)
                # print(sortedProbabilities)

                # # Iterate through the list, sorting by descending probabilities (thus the first element should be of the highest probability)
                # for tile, probability in sortedProbabilitiesReverse:

                #     # If the probability is equal to 1, we should be certain that there is a bomb there
                #     if probability == 1.0:

                #         # Get all the 1.0 probability tiles, and choose randomly out of them
                #         highestProbabilityTiles = [tile2 for tile2, probability2 in sortedProbabilitiesReverse if probability2 == probability]
                #         chosen_y, chosen_x = choice(highestProbabilityTiles)

                #         # Set x and y and marked
                #         self.x = chosen_x
                #         self.y = chosen_y
                #         self.board[chosen_y][chosen_x].marked = True

                #         # Finally, choose to uncover the chosen tile
                #         return Action(AI.Action.FLAG, chosen_x, chosen_y)


                # Iterate through the list, sorting by ascending probabilities (thus the first element should be of the lowest probability)
                for tile, probability in sortedProbabilities:

                    # If the probability is less than or equal to 25%, choose the tile
                    if probability <= .35:

                        # Get all the lowest probability tiles, and choose randomly out of them
                        lowestProbabilityTiles = [tile2 for tile2, probability2 in sortedProbabilities if probability2 == probability]
                        chosen_y, chosen_x = choice(lowestProbabilityTiles)

                        # Set x and y
                        self.x = chosen_x
                        self.y = chosen_y

                        # Finally, choose to uncover the chosen tile
                        return Action(AI.Action.UNCOVER, chosen_x, chosen_y)


        # FIFTH RULE OF THUMB: Guess!
        # print("failed :(\nGuessing...");
        for y, x in self.coveredFrontier:

            # Set x and y
            self.x = x
            self.y = y

            return Action(AI.Action.UNCOVER, x, y)


        # SIXTH RULE OF THUMB: Just leave!
        return Action(AI.Action.LEAVE)