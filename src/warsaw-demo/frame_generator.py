import os

from bokeh.io import export_png

from ztm_data.api import get_api_key, get_stop_data, get_routes_data
from visualization import create_graph, prepare_visualization_data, create_bokeh_plot, create_tile_map, draw_edges, draw_nodes, reconstruct_path, draw_path
import a_star

def visualize_graph(G, start_stop_id=None, end_stop_id=None):
	"""Visualizes the graph with bokeh."""

	node_data, edge_data, mercator_positions, min_x, max_x, min_y, max_y, initial_ratio = prepare_visualization_data(G)
	map = create_bokeh_plot(min_x, max_x, min_y, max_y)

	# background
	create_tile_map(map)

	# content
	draw_edges(map, edge_data)
	draw_nodes(map, node_data)

	# path
	# A* algorithm
	algorithm_steps, came_from = a_star.steps(G, start_stop_id, end_stop_id)
	algorithm_data_sources = a_star.data(G, algorithm_steps, mercator_positions)

	# Create directory for frames
	frames_dir = "frames"		# TODO: get from command line
	if not os.path.exists(frames_dir):
		os.makedirs(frames_dir)

	if algorithm_data_sources:
		for step_idx, new_node_data in enumerate(algorithm_data_sources):
			# Update node data
			node_data.data = new_node_data

			# Draw path
			draw_path(map, G, reconstruct_path(came_from, start_stop_id, end_stop_id), mercator_positions)

			# Save the current frame as an image
			filename = os.path.join(frames_dir, f"frame_{step_idx:04d}.png")
			export_png(
				obj = map,
				filename=filename,
				width=1000,
				height=1000,
				timeout=30
			)

			print(f"Saved frame: {filename}")
	else:
		print("Could not compute A* algorihtm.")

	# Draw shortest path on the final graph
	draw_path(map, G, reconstruct_path(came_from, start_stop_id, end_stop_id), mercator_positions)
	print("A* done!")

if __name__ == '__main__':
	api_key = get_api_key()

	stops_data = get_stop_data(api_key)
	routes_data = get_routes_data(api_key)

	# Create the graph
	G = create_graph(stops_data, routes_data)

	# Visualize the graph
	# visualize_graph(G)
	visualize_graph(G, "('1238', '01')", "('7006', '01')")		# MR-PW
	# visualize_graph(G, "('1238', '01')", "('1542', '01')")		# MR-Bandurskiego
