"""
File: h2.py

h2 function provides heuristic values needed for computing best
velocity.
"""


from __future__ import print_function	# Use the Python 3 print function
import runtrack as racetrack
import math
import sys				# to get readline

# in Python 3 we can just use math.inf, but that doesn't work in Python 2
infinity = float('inf')

g_metric = False	# if a grid has been computed, it will be 'edist' or 'xymax'
g_fline = False
g_walls = False
grid = []


def printm():
	for y in range(ymax+1):
		for x in range(xmax+1):
			if grid[x][y] == infinity: print('*',end=' ')
			else: print(grid[x][y],end=' ')
		print('')

def edist_grid(fline,walls):
	global grid, g_metric, g_fline, g_walls, xmax, ymax
	xmax = max([max(x,x1) for ((x,y),(x1,y1)) in walls])
	ymax = max([max(y,y1) for ((x,y),(x1,y1)) in walls])
	grid = [[edistw_to_line((x,y), fline, walls) for y in range(ymax+1)] for x in range(xmax+1)]
	flag = True
	print('computing edist grid', end=' '); sys.stdout.flush()
	while flag:
		print('.', end=''); sys.stdout.flush()
		flag = False
		for x in range(xmax+1):
			for y in range(ymax+1):
				for y1 in range(max(0,y-1),min(ymax+1,y+2)):
					for x1 in range(max(0,x-1),min(xmax+1,x+2)):
						if grid[x1][y1] != infinity and not racetrack.crash(((x,y),(x1,y1)),walls):
							if x == x1 or y == y1:
								d = grid[x1][y1] + 1
							else:
								d = grid[x1][y1] + 1.4142135623730951
							if d < grid[x][y]:
								grid[x][y] = d
								flag = True
	print(' done')
	g_metric = 'edist'
	g_fline = fline
	g_walls = walls
	return grid


def xymax_grid(fline,walls):
	global grid, g_metric, g_fline, g_walls, xmax, ymax
	xmax = max([max(x,x1) for ((x,y),(x1,y1)) in walls])
	ymax = max([max(y,y1) for ((x,y),(x1,y1)) in walls])
	grid = [[xymaxw_to_line((x,y), fline, walls) for y in range(ymax+1)] for x in range(xmax+1)]
	flag = True
	print('computing xymax grid', end=' '); sys.stdout.flush()
	while flag:
		print('.', end=''); sys.stdout.flush()
		flag = False
		for x in range(xmax+1):
			for y in range(ymax+1):
				for y1 in range(max(0,y-1),min(ymax+1,y+2)):
					for x1 in range(max(0,x-1),min(xmax+1,x+2)):
						if grid[x1][y1] != infinity and not racetrack.crash(((x,y),(x1,y1)),walls):
							d = grid[x1][y1] + max(abs(x-x1),abs(y-y1))
							if d < grid[x][y]:
								grid[x][y] = d
								flag = True
	print(' done')
	g_metric = 'xymax'
	g_fline = fline
	g_walls = walls
	return grid

def edistw_to_line(point, edge, walls):
	"""
	straight-line distance from (x,y) to the line ((x1,y1),(x2,y2)).
	Return infinity if there's no way to do it without intersecting a wall
	"""
#	if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#		return 0
	(x,y) = point
	((x1,y1),(x2,y2)) = edge
	if x1 == x2:
		ds = [math.sqrt((x1-x)**2 + (y3-y)**2) \
			for y3 in range(min(y1,y2),max(y1,y2)+1) \
			if not racetrack.crash(((x,y),(x1,y3)), walls)]
	else:
		ds = [math.sqrt((x3-x)**2 + (y1-y)**2) \
			for x3 in range(min(x1,x2),max(x1,x2)+1) \
			if not racetrack.crash(((x,y),(x3,y1)), walls)]
	ds.append(infinity)
	return min(ds)

def xymaxw_to_line(point, edge, walls):
	"""
	max of x-distance and y-distance from (x,y) to the line ((x1,y1),(x2,y2)).
	Return infinity if there's no way to do it without intersecting a wall
	"""
#	if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#		return 0
	(x,y) = point
	((x1,y1),(x2,y2)) = edge
	if x1 == x2:
		ds = [max(abs(x1-x), abs(y3-y)) \
			for y3 in range(min(y1,y2),max(y1,y2)+1) \
			if not racetrack.crash(((x,y),(x1,y3)), walls)]
	else:
		ds = [max(abs(x3-x), abs(y1-y)) \
			for x3 in range(min(x1,x2),max(x1,x2)+1) \
			if not racetrack.crash(((x,y),(x3,y1)), walls)]
	ds.append(infinity)
	return min(ds)

def distance(p1, p2, metric):
	(x1,y1) = p1
	(x2,y2) = p2
	if metric == 'edist':
		return math.sqrt((x1-x2)**2 + (y1-y2)**2)
	else:
		return max(abs(x1-x2), abs(y1-y2))

def h_h2(state, fline, walls, metric='edist', crash_aware=True, fline_aware=True):
	global g_metric, g_fline, g_walls
	if fline != g_fline or walls != g_walls or metric != g_metric:
#		if fline != g_fline: print('fline = ', fline, '; g_fline =', g_fline)
#		if walls != g_walls: print('walls different')
#		if metric != g_metric: print('metric = ', metric, '; g_metric =', g_metric)
		if metric == 'edist':
			edist_grid(fline, walls)
		elif metric == 'xymax':
			xymax_grid(fline, walls)
		else:
			raise RuntimeError("'" + metric + "' is not a known metric")
	((x,y),(u,v)) = state
	hval = float(grid[x][y])
	
	if crash_aware or fline_aware:
		penalty = 0
		# compute stopping distance
		au = abs(u); av = abs(v); 
		sdu = au*(au-1)/2.0
		sdv = av*(av-1)/2.0
		sd = max(sdu,sdv)
		# compute location after fastest stop
		if u < 0: sdu = -sdu
		if v < 0: sdv = -sdv
		sx = x + sdu
		sy = y + sdv
		if crash_aware:
			if racetrack.crash([(x,y),(sx,sy)],walls):
				if metric == 'edist': penalty += math.sqrt(au**2 + av**2)
				elif metric == 'xymax': penalty += max(au, av)
		if fline_aware:
				penalty += sd/10.0
		hval = max(hval+penalty,sd)
	return hval
	