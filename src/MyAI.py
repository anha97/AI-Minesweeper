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

class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
                self.board = [[0] * (colDimension + 1) for i in range(rowDimension + 1)]
                totalTiles = rowDimension * colDimension
                mineTotal = totalMines
                for i in range(rowDimension, 0, -1):
                        for j in range(colDimension, 0 , -1):
                                if i == 1:
                                        if j == 1:
                                                self.board[i][j] = {"12" : 0, "22" : 0, "21" : 0}
                                        elif j == colDimension:
                                                self.board[i][j] = {"71" : 0, "72" : 0, "82" : 0}
                                        else:
                                                self.board[i][j] = {str(i)+str(j - 1): 0, str(i + 1)+str(j - 1): 0, str(i + 1)+str(j): 0, str(i + 1)+str(j + 1): 0, str(i)+str(j + 1): 0}
                                elif i == colDimension:
                                        if j == 1:
                                                self.board[i][j] = {"17" : 0, "27" : 0, "28" : 0}
                                        elif j == colDimension:
                                                self.board[i][j] = {"78" : 0, "77" : 0, "87" : 0}
                                        else:
                                                self.board[i][j] = {str(i) + str(j - 1): 0, str(i - 1) + str(j - 1): 0, str(i - 1) + str(j): 0, str(i - 1) + str(j + 1): 0, str(i) + str(j + 1): 0}
                                else:
                                        if j == 1:
                                                self.board[i][j] = {str(i - 1) + str(j): 0, str(i - 1) + str(j + 1): 0, str(i) + str(j + 1): 0, str(i + 1) + str(j + 1): 0, str(i + 1) + str(j): 0}
                                        elif j == colDimension:
                                                self.board[i][j] = {str(i - 1) + str(j): 0, str(i - 1) + str(j - 1): 0, str(i) + str(j - 1): 0, str(i + 1) + str(j - 1): 0, str(i + 1) + str(j): 0}
                                        else:
                                                self.board[i][j] = {str(i) + str(j - 1): 0, str(i + 1) + str(j - 1): 0, str(i + 1) + str(j): 0, str(i + 1) + str(j + 1): 0, str(i) + str(j + 1):0, str(i - 1) + str(j + 1): 0, str(i - 1) + str(j): 0, str(i - 1) + str(j - 1): 0}



		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		# col = x & row = y
		# for dictionary value: 0 ==> covered, 1 ==> uncovered, -1 ==> mine/flag

                
                      
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		
	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		if numOfUncovered == totalTiles:
                        return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
