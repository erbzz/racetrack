"""
File: runtrack.py

A simple program for running the racetrack.
"""

import math, sys
import tdraw, turtle			# Code to use Python's "turtle drawing" package
import velo					# File containing the velocity program in velo.py
import maketrack

def main(problem=None, draw=1, single_step=0):
	"""
	Create a random racetrack problem, or take one as a parameter. Then,
	repeatedly retrieve next velocity from velo.main and move there, until
	either you crash or you reach the finish line and have velocity (0,0).
	If single_step = 1, then wait for carriage returns between steps.
	"""	
	if not problem:
		problem = maketrack.main()
	(p0, f_line, walls) = problem
	
	if draw:
		turtle.Screen()				# open the graphics window
		turtle.clearscreen()
		tdraw.draw_problem((p0, f_line, walls), title='foo')
	
	(x,y) = p0
	(u,v) = (0,0)

	i = 0
	while True:
		i += 1
	
		if goal_test((x,y), (u,v), f_line):
			print('\nYou win.')
			break

		state = ((x,y),(u,v))
		(u, v) = velo.main(state, f_line, walls)

		(xnew,ynew) = (x+u, y+v)
		print('Move {}: velo.main chose velocity {}'.format(i,(u,v)), end='')
		print(', new position is {}'.format((xnew,ynew)))
		edge = ((x,y), (xnew, ynew))
		if draw:
			draw_edge(edge, 'red') 
		
		if crash(edge, walls):
			print('\nYou have crashed, so you lose.')
			break		
		(x,y) = (xnew, ynew)

		if single_step:
			print("\n*** Finished move {}. Hit carriage return to continue.\n".format(i))
			sys.stdin.readline()


def draw_edge(edge,color):
	tdraw.draw_lines([edge], width=2, color=color,dots=6)


def goal_test(point,velocity,f_line):
	"""Test whether point is on the finish line and velocity is (0,0)"""
	return velocity == (0,0) and intersect((point,point), f_line)


def crash(move,walls):
	"""Test whether move intersects a wall in walls"""
	for wall in walls:
		if intersect(move,wall): return True
	return False


def intersect(e1,e2):
	"""Test whether edges e1 and e2 intersect"""	   
	
	# First, grab all the coordinates
	((x1a,y1a), (x1b,y1b)) = e1
	((x2a,y2a), (x2b,y2b)) = e2
	dx1 = x1a-x1b
	dy1 = y1a-y1b
	dx2 = x2a-x2b
	dy2 = y2a-y2b
	
	if (dx1 == 0) and (dx2 == 0):		# both lines vertical
		if x1a != x2a: return False
		else: 	# the lines are collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
	if (dx2 == 0):		# e2 is vertical (so m2 = infty), but e1 isn't vertical
		x = x2a
		# compute y = m1 * x + b1, but minimize roundoff error
		y = (x2a-x1a)*dy1/float(dx1) + y1a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	elif (dx1 == 0):		# e1 is vertical (so m1 = infty), but e2 isn't vertical
		x = x1a
		# compute y = m2 * x + b2, but minimize roundoff error
		y = (x1a-x2a)*dy2/float(dx2) + y2a
		return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
	else:		# neither line is vertical
		# check m1 = m2, without roundoff error:
		if dy1*dx2 == dx1*dy2:		# same slope, so either parallel or collinear
			# check b1 != b2, without roundoff error:
			if dx2*dx1*(y2a-y1a) != dy2*dx1*x2a - dy1*dx2*x1a:	# not collinear
				return False
			# collinear
			return collinear_point_in_edge((x1a,y1a),e2) \
				or collinear_point_in_edge((x1b,y1b),e2) \
				or collinear_point_in_edge((x2a,y2a),e1) \
				or collinear_point_in_edge((x2b,y2b),e1)
		# compute x = (b2-b1)/(m1-m2) but minimize roundoff error:
		x = (dx2*dx1*(y2a-y1a) - dy2*dx1*x2a + dy1*dx2*x1a)/float(dx2*dy1 - dy2*dx1)
		# compute y = m1*x + b1 but minimize roundoff error
		y = (dy2*dy1*(x2a-x1a) - dx2*dy1*y2a + dx1*dy2*y1a)/float(dy2*dx1 - dx2*dy1)
	return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 


def collinear_point_in_edge(point, edge):
	"""
	Helper function for intersect, to test whether a point is in an edge,
	assuming the point and edge are already known to be collinear.
	"""
	(x,y) = point
	((xa,ya),(xb,yb)) = edge
	# point is in edge if (i) x is between xa and xb, inclusive, and (ii) y is between
	# ya and yb, inclusive. The test of y is redundant unless the edge is vertical.
	if ((xa <= x <= xb) or (xb <= x <= xa)) and ((ya <= y <= yb) or (yb <= y <= ya)):
	   return True
	return False
		
main()
