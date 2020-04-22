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
	
	def __init__():
		self.visited = False
		self.covered = True
		self.marked = False
		self.label = 0
		self.effectiveLabel = 0

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		# Set up board array
                self.board = [[Tile()] * (colDimension) for _ in range(rowDimension)]

		# Set up board vars
                self.totalTiles = rowDimension * colDimension
                self.mineTotal = totalMines
		
		self.x = startX
		self.y = startY


                      

		
	def getAction(self, number: int) -> "Action Object":
	
		# Calculate the amount of covered tiles	
		self.coveredTiles = sum([sum([1 for tile in self.board[row] if tile.covered == True]) for row in range(self.rowDimension)])
	
		# LEAVE if we meet the game condition	
		if self.coveredTiles == self.totalTiles:
                        return Action(AI.Action.LEAVE)


