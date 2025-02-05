from bokeh.plotting import show
from bokeh.models import CustomJS, Slider, Legend, LegendItem, Div
from bokeh.layouts import column, row
from bokeh.io import output_file

from ztm_data.api import get_api_key, get_stop_data, get_routes_data
from visualization import create_graph, prepare_visualization_data, create_bokeh_plot, create_tile_map, draw_edges, draw_nodes, create_zoom_callback, enable_wheel_zoom, draw_shortest_path
import a_star

def visualize_graph(G, start_stop_id=None, end_stop_id=None):
	"""Visualizes the graph with bokeh."""

	# Output to an HTML file
	output_file(filename = "graph.html", title="Warsaw demo")

	node_data, edge_data, mercator_positions, min_x, max_x, min_y, max_y, initial_ratio = prepare_visualization_data(G)
	map = create_bokeh_plot(min_x, max_x, min_y, max_y)

	# background
	create_tile_map(map)

	# content
	draw_edges(map, edge_data)
	draw_nodes(map, node_data)

	# Create legend
	legend_items = [
		LegendItem(label="Current", renderers=[map.scatter(x=0, y=0, size=10, color="red")]),
		LegendItem(label="Open Set", renderers=[map.scatter(x=0, y=0, size=10, color="green")]),
		LegendItem(label="Unvisited", renderers=[map.scatter(x=0, y=0, size=10, color="lightgrey")])
	]

	legend = Legend(items=legend_items, location="top_right", orientation='horizontal')

	# path
	# A* algorithm
	algorithm_steps = a_star.steps(G, start_stop_id, end_stop_id)
	algorithm_data_sources = a_star.data(G, algorithm_steps, mercator_positions)

	if algorithm_data_sources:
		# Slider to step through the algorithm
		slider = Slider(
			start=0,
			end=len(algorithm_data_sources) - 1,
			value=0,
			step=1,
			title="Algorithm Step"
		)

		callback = CustomJS(
			args=dict(
				node_source=node_data,
				edge_source=edge_data,
				algorithm_data_sources=algorithm_data_sources,
				slider=slider
			),
			code="""
				const step = slider.value;

				// Directly assign the new data to the data sources
				// TODO: handle edges too
				node_source.data = algorithm_data_sources[step];
				node_source.change.emit();
			"""
		)
		slider.js_on_change('value', callback)

		# utils
		create_zoom_callback(map, initial_ratio)
		enable_wheel_zoom(map)

		# tweak layout
		map.add_layout(legend, 'below')
		map.sizing_mode = "scale_height"

		div = Div(text="<h1>A* demo on data provided by ZTM/WTP</h1>")
		controls = column(div, slider)

		layout = row(map, controls)
		layout.sizing_mode = "stretch_both"

		# show results
		show(layout)
	else:
		print("Could not compute A* algorihtm.")

	# Draw shortest path on the final graph
	# TOOD: I don't think this works
	draw_shortest_path(map, G, start_stop_id, end_stop_id, mercator_positions)

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
