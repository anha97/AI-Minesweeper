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
		self.markedNeighbor = 0


class MyAI( AI ):

	def __init__(self, rowDimension: int, colDimension: int, totalMines: int, startX: int, startY: int):

		# Set up board
		self.board = [[Tile()] * (colDimension) for _ in range(rowDimension)]

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
		return (x < self.rowDimension and x > 0 and y < self.colDimension and y > 0)
	
	def generateNeighbors(self, x: int, y: int) -> [(int,int)]:
		"""Generates all valid neighbor coordinates of a tile given coordinates (x,y)."""

		validNeighbors = list()

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
		
	def getAction(self, number: int) -> "Action Object":

		# number = number of mines in the neighborhood

		# Action for the AI
		action = ""
		# Calculate the amount of covered tiles	
		self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])

		result = self.neighbor(self.x, self.y)
		if number == 0:	# No mines around the neighborhood
			# Need to check the neighbor before making a move
			
			action = AI.Action.UNCOVER
			coordX = 0
			coordY = 0
			return Action(action, coordX, coordY)

		# LEAVE if we meet the game condition	
		if self.coveredTiles == self.totalTiles:
                        return Action(AI.Action.LEAVE)

