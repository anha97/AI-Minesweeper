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

totalFlag = 0
mineTotal = 0
numOfUncovered = 0
totalTiles = 0

class Tile:
	
	def __init__(self):
		self.visited = False
		self.covered = True
		self.marked = False
		self.label = 0
		self.effectiveLabel = 0
		self.markedNeighbor = 0

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		# Set up board
		self.board = [[Tile()] * (colDimension) for _ in range(rowDimension)]

		# Set up vars
		self.totalTiles = rowDimension * colDimension
		self.mineTotal = totalMines
		self.rowDimension = rowDimension
		self.colDimension = colDimension

		self.x = startX
		self.y = startY
		self.board[startX][startY].visited = True
		self.board[startX][startY].covered = False

	def position(self, x, y):
		return (x < 10 and x > 0 and y < 10 and y > 0)
	
	def neighbor(self, x, y):
		result = list()
		if self.position(x, y - 1):	# Check for left neighbor
			result.append((x, y - 1))
		if self.position(x - 1, y):	# Check for bottom neighbor
			result.append((x - 1, y))
		if self.position(x, y + 1):	# Check for right neighbor
			result.append((x, y + 1))
		if self.position(x + 1, y):	# Check for top neighbor
			result.append((x + 1, y))
		return result
		
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





