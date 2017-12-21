from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import racetrack
import gsr
import tensorflow as tf
import math
import sys


def main(state, f_line, walls):
    """
    Uses a trained neural network to return the best velocity
    value for the program to find a path to the finish line.
    This function uses the A* algorithm to do this.

    :param state:       The current state
    :param f_line:      The finish line of the arena
    :param walls:       The walls in the arena
    """

    # This is the placeholder variable for the feed-forward
    inp = tf.placeholder(shape=[1,16],dtype=tf.float32)
    L = tf.Variable(tf.random_uniform([16,4],0,0.01))
    
    # Helps the neural network choose actions
    out = tf.matmul(inp,L)
    predict = tf.argmax(out,1)

    # Get loss
    next = tf.placeholder(shape=[1,4],dtype=tf.float32)
    
    # Done by adding squares of next minus out
    loss = tf.reduce_sum(tf.square(next - out))
    neur = tf.train.GradientDescentOptimizer(learning_rate=0.2)

    # Minimizes the loss of the new updated model
    updateModel = neur.minimize(loss)

    # Time to use tensorflow for training below (by session)
    with tf.Session() as sess:
        # init velocity
        Z_dict = {}

        # init global variables for tf sessions
        sess.run(tf.global_variables_initializer())

        # Iterate through state vals
        i = 0
        while i < len(racetrack.next_states(state, walls)):
            elem = racetrack.next_states(state, walls)[i]
            i += 1
            (a,b) = elem

            # Set that val to 0
            Z_dict[b] = 0

        # Iterate through state vals again but for finding paths
        j = 0
        while j < len(racetrack.next_states(state, walls)):
            elem = racetrack.next_states(state, walls)[j]
            j += 1
            (a,b) = elem
            
            # A* algorithm to find route
            road = route(elem, f_line, walls)
            numcrashes = 0
            
            # To train network, punish crashes by decrementing pts
            if road:
                for point in road:
                    if (racetrack.crash(point,walls)):
                        numcrashes -= 1      
            
            # To train network, punish crashes and reward not crashes
            if (not racetrack.crash(elem,walls)): Z_dict[b] += 2
            else: Z_dict[b] -= 5
            
            # Adjust score based on crashes
            Z_dict[b] += numcrashes
        
        # Use constant for finding the best value
        const = -9999999
        (u,v) = (0,0)

        # Get the best possible velocity by iterating through the elements in Z_dict
        keys = Z_dict.keys()
        for elem in keys:
            
            # Get the respective velocity from the appropriate key
            velocity = Z_dict[elem]
            
            # If the curr const value is not the best
            if const < velocity:
                (u,v) = elem # this is the best value so far
                const = velocity # higher const
    
    # Return the best velocity value
    return (u,v)

def route(state,f_line, walls):
    """
    Gets the path using A* search.

    :param state:       The current state
    :param f_line:      The finish line of the arena
    :param walls:       The walls in the arena
    """

    # Get the goal, next state, and heuristic value
    goal = lambda state: racetrack.goal_test(state,f_line)  
    next = lambda state: [(n,1) for n in racetrack.next_states(state,walls)]
    h = lambda state: h_h2(state, f_line, walls)
    
    # gsr.py search using A* algorithm
    return gsr.search(state, next, goal, "a*", h, 0)

###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################
###################################################################################

"""
Dana's Code below from file h2.py. I put this here because the program was throwing
a silly error due to multiple main functions.
"""

infinity = float('inf')

g_metric = False    # if a grid has been computed, it will be 'edist' or 'xymax'
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
#   if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#       return 0
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
#   if min(x1,x2) <= x <= max(x1,x2) and  min(y1,y2) <= y <= max(y1,y2):
#       return 0
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
#       if fline != g_fline: print('fline = ', fline, '; g_fline =', g_fline)
#       if walls != g_walls: print('walls different')
#       if metric != g_metric: print('metric = ', metric, '; g_metric =', g_metric)
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