"""A (very small) collection of tools for working with A* algorithm."""

import math

import networkx as nx

def data(G, algorithm_steps, mercator_positions):
	"""Prepares data for visualization from A* algorithm steps."""

	data_sources = []
	for step in algorithm_steps:
		# Prepare node colors based on algorithm state
		node_colors = []
		for node in G.nodes():
			if node == step['current']:
				node_colors.append("red")  # Current node
			elif node in step['open_set']:
				node_colors.append("green")  # Open set
			else:
				node_colors.append("lightgrey")  # Unvisited node

		# Create a ColumnDataSource for nodes
		node_data = dict(
			x=[mercator_positions[node][0] for node in G.nodes()],
			y=[mercator_positions[node][1] for node in G.nodes()],
			label=[node for node in G.nodes()],
			color=node_colors  # Set node colors based on the algorithm step
		)
		data_sources.append(node_data)

	return data_sources

def steps(G, start_stop_id, end_stop_id):
	"""Performs A* search algorithm and records the state at each step."""

	pos = nx.get_node_attributes(G, 'pos')

	def heuristic(node):
		x1, y1 = pos[node]
		x2, y2 = pos[end_stop_id]

		return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

	open_set = {start_stop_id}
	came_from = {}
	g_score = {node: float('inf') for node in G.nodes()}
	g_score[start_stop_id] = 0
	f_score = {node: float('inf') for node in G.nodes()}
	f_score[start_stop_id] = heuristic(start_stop_id)

	algorithm_steps = []

	while open_set:
		current = min(open_set, key=lambda node: f_score[node])

		if current == end_stop_id:
			break

		open_set.remove(current)

		algorithm_steps.append({
			'current': current,
			'open_set': open_set.copy(),
			'f_score': f_score.copy()
		})

		for neighbor in G.neighbors(current):
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + heuristic(neighbor)
				if neighbor not in open_set:
					open_set.add(neighbor)

	return algorithm_steps, came_from
