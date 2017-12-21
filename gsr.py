"""
File: gsr.py

This code should work in both Python 2.7 and Python 3.6.  The main program is a
domain-independent graph-search-for-A* algorithm, with hooks for drawing images:

search(s0, next_states, goal_test, strategy, h = lambda s: 0, verbose=0, draw_edges=None)

 - s0 is the initial state.
 - next_states(s) is the function to use for generating a list of successors of s.

 - strategy is the name of the search strategy. It should be one of these: 
   'bf' (best first), 'df' (depth first),
   'uc' (uniform cost), 'gbf' (greedy best first), or 'a*'.

 - h(s) is the heuristic function.

 - verbose specifies how/when to interact with the user. The default value is 2:
	0 - silent, just return the answer.
	1 - print some statistics at the end of the search.
	2 - print brief info at each iteration, and statistics at the end of the search.
	3 - print additional info at each iteration, and stats at the end of the search.
	4 - print the above, and pause at each iteration.

 - draw_edges(edges,status) is the function to use for drawing edges in the search graph.
   It should take the following arguments:
	- edges, a list of edges.
	- status, a string that indicates what kind of edges they are:
	  'expand', 'add', 'discard', 'frontier_prune', 'explored_prune', and 'solution'.
"""

from __future__ import print_function	# Use the Python 3 print function
import sys								# We need flush() and readline()

class Node():
	"""
    Args are current state, parent node, and cost of transition from
    parent state to current state. Each node includes an id number, 
    state, parent node, g-value, h-value, and list of children.
    """
	def __init__(self,state,parent,cost,h_value):
		global node_count
		self.state = state
		self.parent = parent
		node_count += 1                      # total number of nodes
		self.id = node_count                 # this node's ID number
		if parent: 
			parent.children.append(self)
			self.depth = parent.depth + 1    # depth in the search tree
			self.g = parent.g + cost         # total accumulated cost 
		else:
			self.depth = 0
			self.g = cost
		self.children = []
		self.h = h_value

def getpath(y):
	"""Return the path from the root to y"""
	path = [y]
	while y.parent:
		y = y.parent
		path.append(y)
	path.reverse()
	return path


# For each search strategy, there's a key function for sorting lists of nodes,
# and a formatting string for printing out information about them
sort_options = {
	'bf':	('id',	lambda x: x.id,    '#{0}: d {1}, g {3:.2f}, state {5}'),
	'df':	('-id',	lambda x: -x.id,   '#{0}: d {1}, g {3:.2f}, state {5}'),
	'uc':	('g',	lambda x: x.g,     '#{0}: g {3:.2f}, d {1}, state {5}'),
	'gbf':	('h',	lambda x: x.h,     '#{0}: h {4:.2f}, d {1}, g {3:.2f}, state {5}'),
	'a*':	('f',	lambda x: x.g+x.h, '#{0}: f {2:.2f}, g {3:.2f}, h {4:.2f}, d {1}, state {5}')}

def printnodes(message, nodes, strategy, verbose):
	"""For each node in nodes, print its state and its 'key_func' value"""
	(key_name, key_func, template) = sort_options[strategy]
	nodes.sort(key=key_func)	# no need to do this unless we're going to print them
	
	if verbose == 2:
		nodenames = ['#{} {:.2f}'.format(y.id,key_func(y)) for y in nodes[:5]]
		if len(nodes)>5: end = ', ...\n'
		else:	end = '\n'
		print('{:>11}{:>4}:'.format(message, len(nodes)), ', '.join(nodenames), end=end)
	else:
		if len(nodes) == 0:    print('    {:>10} {} nodes.'.format(message, len(nodes)))
		elif len(nodes) == 1:  print('    {:>10} {} node:'.format(message, len(nodes)))
		else:                  print('    {:>10} {} nodes:'.format(message, len(nodes)))
		for y in nodes[:10]:
			print('{:11}{}'.format('', nodeinfo(y,template)))
		if len(nodes) > 10: 
			print('{:11}{}'.format('', ' and {} more ...'.format(len(nodes)-10)))

def nodeinfo(y,template):
	"""return a one-line description of a node"""
	return template.format(y.id, y.depth, y.g+y.h, y.g, y.h, y.state)

def print_nodetypes(new, n_prune, e_prune, f_prune, frontier, strategy, verbose):
	printnodes('add', new, strategy, verbose)
	if n_prune: printnodes('discard', n_prune, strategy, verbose)
	if e_prune: printnodes('expl. rm', e_prune, strategy, verbose)
	if f_prune: printnodes('fron. rm', f_prune, strategy, verbose)
	printnodes('frontier', frontier, strategy, verbose)

def finish(x, node_count, prunes, frontier, explored, verbose, draw_edges):
	"""called after a successful search, to print info and/or draw the solution"""
	path = getpath(x)
	if verbose >= 1:
		# Path length = number of actions = number of nodes - 1
		print('==> Path length {}, cost {}.'.format(len(path)-1,x.g), \
			'Generated {}, pruned {}, explored {}, frontier {}.'.format( \
			node_count, prunes, len(explored), len(frontier)))
	if draw_edges:  draw_nodes(path, 'solution', draw_edges)
	return [p.state for p in path]

def draw_nodes(nodes, status,draw_edges):
	draw_edges([(x.parent.state[0],x.state[0]) for x in nodes if x.parent], status)

def draw_expand(x, n_prune, new, f_prune, e_prune, draw_edges):
	draw_nodes([x], 'expand', draw_edges)
	draw_nodes(n_prune, 'discard', draw_edges)
	draw_nodes(new, 'add', draw_edges)
	draw_nodes(f_prune, 'frontier_prune', draw_edges)
	draw_nodes(e_prune, 'explored_prune', draw_edges)


def expand(x, next_states, h, frontier, explored, strategy, verbose, draw_edges):
	"""
	Return six lists of nodes: new nodes, nodes pruned from new, frontier nodes,
	nodes pruned from frontier, explored node, and nodes pruned from explored
	"""
	(key_name, key_func, template) = sort_options[strategy]
	new = [Node(s, x, cost, h(s)) for (s,cost) in next_states(x.state)]

	# make a list of dominated new nodes, then prune them
	n_prune = [m for m in new if
		[n for n in explored if m.state == n.state and key_func(m) >= key_func(n)] or
		[n for n in frontier if m.state == n.state and key_func(m) >= key_func(n)] or
		[n for n in new if m.state == n.state and key_func(m) > key_func(n)] or
		[n for n in new if m.state == n.state and key_func(m) == key_func(n) and m.id > n.id]]
	new = [m for m in new if not m in n_prune]

	# make a list of dominated frontier nodes, then prune them
	f_prune = [m for m in frontier if
		[n for n in new if m.state == n.state and key_func(m) > key_func(n)]]
	frontier = [m for m in frontier if not m in f_prune]

	# make a list of dominated explored nodes, then prune them
	e_prune = [m for m in explored if
		[n for n in new if m.state == n.state and key_func(m) > key_func(n)]]
	explored = [m for m in explored if not m in e_prune]

	frontier.extend(new)
	frontier.sort(key=key_func)

	if verbose >= 2:
		print_nodetypes(new, n_prune, e_prune, f_prune, frontier, strategy, verbose)
	if draw_edges:
		draw_expand(x, n_prune, new, f_prune, e_prune, draw_edges)
	return (new, n_prune, frontier, f_prune, explored, e_prune)

def search(s0, next_states, goal_test, strategy, h=None, verbose=2, draw_edges=None):
	"""
	Graph search for a path from s0 (initial state) to a state that satisfies goal_test. 
	strategy is 'bf', 'df', 'uc', 'gbf', or 'a*'. If verbose >= 1, print some statistics
	at the end of the search. If verbose >= 2, also print some info at each iteration. If 
	verbose >= 3, print more info. If verbose >= 4, print info and pause at each iteration.
	"""
	global node_count
	node_count = 0		# total number of generated nodes
	prunes = 0			# total number of pruned nodes
	explored = []		# all nodes that have been expanded
	(key_name, key_func, template) = sort_options[strategy]
	if verbose >= 2:
		print('==> {} search, keep frontier ordered by {}:\n'.format(strategy, key_name))
	# Below, thes 2nd arg is None because the node has no parent.
	if h: frontier = [Node(s0,None,0,h(s0))]
	else: frontier = [Node(s0,None,0,None)]
	iteration = 0
	while frontier: 
		iteration += 1                  # keep track of how many iterations we've done
		x = frontier.pop(0)             # inefficient
		explored.append(x)
		if verbose >= 2: print('{0:>3} Expand'.format(iteration), nodeinfo(x,template))
		if goal_test(x.state):
			return finish(x, node_count, prunes, frontier, explored, verbose, draw_edges)
		(new, n_prune, frontier, f_prune, explored, e_prune) = expand( \
			x, next_states, h, frontier, explored, strategy, verbose, draw_edges)
		if verbose >= 4:
			print("continue > ", end='')
			sys.stdout.flush(); sys.stdin.readline()
		elif verbose >= 2: 	print('')
		prunes += len(n_prune) + len(f_prune) + len(e_prune)
	if verbose >= 3:	print("==> Couldn't find a solution.")
	return False
