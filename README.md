# Routation
Routation is a puzzle about moving pieces around a board by turning gears.

The goal of Routation is to move the green piece to the green hole. However, no red pieces can fall in any holes, and the green piece can only fall into the green hole. You'll find that most gears are unable to rotate most of the time, so you'll have to "unlock" them by rotating a series of other gears.

This repo contains sample puzzles and solutions generated using my routation_puzzle_generator script. Each puzzle is labeled with the minimum number of moves required to complete the puzzle, and usually the higher that number, the more difficult the puzzle is. If you're looking for an extra challenge, try solving the puzzle in the optimal number of moves. Note that the holes in the sample puzzles are denoted by circles, while the pieces are denoted by filled color in the gear gaps. 

It also has a solver for any given board/hole configuration. The solution is generated as text telling you which gear to rotate in which direction at each step.

If you are interested in making a puzzle for your own use, 3d models of the Routation board and pieces can be found in the 3d printing folder, soon to be uploaded to a dedicated STL sharing website.

