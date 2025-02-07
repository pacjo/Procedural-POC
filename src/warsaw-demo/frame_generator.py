import os

from bokeh.io import export_png

from ztm_data.api import get_api_key, get_stop_data, get_routes_data
from visualization import create_graph, prepare_visualization_data, create_bokeh_plot, create_tile_map, draw_edges, draw_nodes, draw_path
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

	path_renderers = []

	if algorithm_data_sources:
		for step_idx, new_node_data in enumerate(algorithm_data_sources):
			# Update node data
			node_data.data = new_node_data

			# Frame skipping block. In case of a bug, uncomment and change the if statement to the number of the last successful frame (minus about 10 to work around fading)
			# if (step_idx < 1390):
			# 	print(f"Skipping frame {step_idx}")
			# 	continue

			for path_renderer in path_renderers:
				try:
					path_renderers.remove(path_renderer)
					map.renderers.remove(path_renderer)
				except:
					pass

			# fade out the paths
			for path_data in algorithm_steps[step_idx]['all_paths']:
				path = path_data['path']
				frame_number = path_data['frame_number']
				age = step_idx - frame_number
				fade_speed = 0.2
				alpha = max(0, 1 - age * fade_speed)

				path_renderers.append(draw_path(map, G, path, mercator_positions, color=f"rgba(255, 0, 0, {alpha})"))

			# Save the current frame as an image
			filename = os.path.join(frames_dir, f"frame_{step_idx:04d}.png")
			try:
				export_png(
					obj = map,
					filename=filename,
					width=2000,
					height=2000,
					timeout=10
				)
			except Exception as e:
				print(f"Error saving frame {step_idx} (caused by {e}), skipping")

			print(f"Saved frame: {filename}")
	else:
		print("Could not compute A* algorihtm.")

	print("A* done!")

if __name__ == '__main__':
	api_key = get_api_key()

	stops_data = get_stop_data(api_key)
	routes_data = get_routes_data(api_key)

	# Create the graph
	G = create_graph(stops_data, routes_data)

	# Visualize the graph
	# visualize_graph(G)
	# visualize_graph(G, "('1238', '01')", "('7006', '01')")		# MR-PW
	visualize_graph(G, "('1238', '01')", "('1542', '01')")		# MR-Bandurskiego
