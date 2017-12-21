# Racetrack

This is a python script that uses tensorflow to train a neural network in order to figure out a (kind of optimal) way to get to the finish line. The racetrack is randomly generated each time in order to ensure that the grid is not mapped out and stored somewhere.

The program generates a racetrack like so:

<img src="https://github.com/erbzz/racetrack/blob/master/imgs/ex2_full.gif" width="480">

The starting point is the blue dot (upper right) and the finish line is the red line (bottom left). All the black bolded lines are walls or hazards that the program must avoid. If the program intersects any of those lines, it is considered a crash and "You lose!" If the program is able to navigate to the finish line, land on the finish line and return a velocity of (0,0), then the program has successfully reached the goal and "You win!"


********************************************************************************
In order to run this on your machine, make sure you have python3.6 or higher. Simply copy all of the files onto your device, navigate to the racetrack repository and do:
    * python3 runtrack.py

This will open up a tdraw/turtle graphic that will display the racetrack, and the program.
