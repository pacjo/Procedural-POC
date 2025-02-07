"""A (very small) collection of tools for working with A* algorithm."""

import math

import networkx as nx

def data(G, algorithm_steps, mercator_positions):
	"""Prepares data for visualization from A* algorithm steps."""

	data_sources = []
	for step in algorithm_steps:
		# Prepare node colors based on algorithm state
		node_colors = {}  # Use a dictionary for colors by node

		# Base color: Unvisited
		for node in G.nodes():
			node_colors[node] = "lightgrey"  # Default color

		# Color Visited Nodes with Fade
		for node, frame_number in step['visited'].items():
			age = step['step_idx'] - frame_number  # Calculate age of visit
			# Adjust the fade speed as needed. Higher fade_speed is faster
			fade_speed = 0.1
			# Calculate interpolation factor (0 to 1)
			interpolation_factor = min(1, age * fade_speed)

			# Interpolate between red (#ff0000) and lightgray (#d3d3d3)
			# colors from: https://docs.bokeh.org/en/latest/docs/reference/colors.html
			red_r = int(0xff * (1 - interpolation_factor) + 0xd3 * interpolation_factor)
			red_g = int(0x00 * (1 - interpolation_factor) + 0xd3 * interpolation_factor)
			red_b = int(0x00 * (1 - interpolation_factor) + 0xd3 * interpolation_factor)

			# Convert to hex color
			node_colors[node] = f'#{red_r:02x}{red_g:02x}{red_b:02x}'

		# Color Current Node (override fade if necessary)
		if step['current']: # step['current'] can be None in rare cases, when the destination is unreachable
			node_colors[step['current']] = "red"  # Current node

		# Color Open Set (override fade if necessary)
		for node in step['open_set']:
			node_colors[node] = "green"  # Open set

		# Convert to list for Bokeh ColumnDataSource
		node_colors_list = [node_colors[node] for node in G.nodes()]

		# Create a ColumnDataSource for nodes
		node_data = dict(
			x=[mercator_positions[node][0] for node in G.nodes()],
			y=[mercator_positions[node][1] for node in G.nodes()],
			label=[node for node in G.nodes()],
			color=node_colors_list  # Set node colors based on the algorithm step
		)
		data_sources.append(node_data)

	return data_sources

def reconstruct_path_to_current(came_from, start_stop_id, current_node):
	"""Reconstructs the path from the start to the current node."""
	path = [current_node]
	while current_node != start_stop_id:
		if current_node not in came_from:
			# No path found to current node
			return []
		current_node = came_from[current_node]
		path.append(current_node)
	path.reverse()
	return path

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
	visited = {}  # Keep track of visited nodes and their frame numbers
	step_idx = 0 # Step index for assigning frame number
	all_paths = [] # keep track of all paths

	while open_set:
		current = min(open_set, key=lambda node: f_score[node])

		if current == end_stop_id:
			break

		open_set.remove(current)

		# Store visited node with the current step index
		visited[current] = step_idx
		path_to_current = reconstruct_path_to_current(came_from, start_stop_id, current)

		all_paths.append({
			'path': path_to_current,
			'frame_number': step_idx
		})

		algorithm_steps.append({
			'step_idx': step_idx,
			'current': current,
			'open_set': open_set.copy(),
			'f_score': f_score.copy(),
			'visited': visited.copy(), # Important: copy the dictionary
            'all_paths': all_paths.copy()
		})

		for neighbor in G.neighbors(current):
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + heuristic(neighbor)
				if neighbor not in open_set:
					open_set.add(neighbor)

		step_idx += 1

	return algorithm_steps, came_from
