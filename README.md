# AI-Minesweeper

We've implemented a code for AI to make the best viable move for Minesweeper. Moreover, we created four test cases, which AI will make its best judgement to uncover/flag a tile, based on given information from the board.

    Uncover a tile with the label "0"
    Uncover a tile if and only if the effective label (eff. label = label - marked/flagged adjacent tiles) is equal to 0
    Flag a tile if the effective label is equal to the covered ajacent tiles
    Generate 2^10 models from each uncovered frontier and calculate the probability to either uncover or flag a tile.

5x5, 8x8, and 16x16 (board size) are manageable for the AI since it can solve decently well out of 1000 games.

Author: Andrew Ha & Joshua Costa
