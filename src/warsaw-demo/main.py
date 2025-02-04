import networkx as nx

from bokeh.plotting import figure, show, from_networkx
from bokeh.models import Circle, ColumnDataSource, CustomJS, WheelZoomTool
from bokeh.io import output_file

import pyproj
import xyzservices.providers as xyz

from ztm_data.api import get_api_key, get_stop_data, get_routes_data
from ztm_data.stop import ZTMStop

def create_stop_lookup(stops_data) -> dict[tuple[int, int], ZTMStop]:
	"""Creates a dictionary to look up ZTMStop objects by their combined 'zespol' and 'slupek' IDs."""

	stop_lookup = {}
	for stop_data in stops_data["result"]:
		stop = ZTMStop.create_from_json(stop_data["values"])

		# Filter out some "internal" stops
		if stop.slupek != "00" and int(stop.slupek) < 50:
			stop_id = (stop.zespol, stop.slupek)
			stop_lookup[stop_id] = stop

	return stop_lookup

def create_graph(stops_data, routes_data):
	"""Creates a graph from stops and routes data."""
	G = nx.Graph()
	stop_lookup = create_stop_lookup(stops_data)

	for line, directions in routes_data['result'].items():
		for direction, route in directions.items():
			ordered_stops = sorted(route.items(), key=lambda item: int(item[0]))
			previous_stop_id = None
			for _, stop_info in ordered_stops:
				stop_id = (stop_info['nr_zespolu'], stop_info['nr_przystanku'])

				if stop_id in stop_lookup:
					stop = stop_lookup[stop_id]

					G.add_node(
						str(stop_id),	  # Convert to string for bokeh
						pos=(stop.dlug_geo, stop.szer_geo),
						label=f"{stop.nazwa_zespolu} {stop.slupek}"
					)

					if previous_stop_id:
						G.add_edge(
							str(previous_stop_id),		  # Convert to string for bokeh
							str(stop_id),				  # Convert to string for bokeh
							line=line
						)
					previous_stop_id = stop_id
				else:
					print(f"Warning: Stop with id: {stop_id} not found in stop_lookup")

	return G

def prepare_visualization_data(G):
	"""Prepares data for visualization: transforms coords, creates ColumnDataSources."""

	pos = nx.get_node_attributes(G, 'pos')
	labels = nx.get_node_attributes(G, 'label')
	edge_labels = nx.get_edge_attributes(G, 'line')

	# Convert lat/lon to Web Mercator
	transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True)

	mercator_positions = {
		node: transformer.transform(pos[node][0], pos[node][1])
		for node in pos
	}

	# Calculate initial bounds in mercator coords
	min_x = min(coord[0] for coord in mercator_positions.values())
	max_x = max(coord[0] for coord in mercator_positions.values())
	min_y = min(coord[1] for coord in mercator_positions.values())
	max_y = max(coord[1] for coord in mercator_positions.values())

	initial_width = max_x - min_x
	initial_height = max_y - min_y
	initial_ratio = initial_width / initial_height

	# Prepare data for nodes
	node_xs = [mercator_positions[node][0] for node in G.nodes()]
	node_ys = [mercator_positions[node][1] for node in G.nodes()]
	node_labels = [labels[node] for node in G.nodes()]

	# Create a ColumnDataSource for nodes
	node_data = ColumnDataSource(dict(
		x=node_xs,
		y=node_ys,
		label=node_labels
	))

	# Prepare data for edges
	edge_xs = []
	edge_ys = []
	for start, end in G.edges():
		edge_xs.append([mercator_positions[start][0], mercator_positions[end][0]])
		edge_ys.append([mercator_positions[start][1], mercator_positions[end][1]])

	# Create a ColumnDataSource for edges
	edge_data = ColumnDataSource(dict(
		xs=edge_xs,
		ys=edge_ys,
		line=[edge_labels[edge] for edge in G.edges]
	))

	return node_data, edge_data, min_x, max_x, min_y, max_y, initial_ratio


def create_bokeh_plot(min_x, max_x, min_y, max_y):
	"""Creates a Bokeh plot with specified settings."""

	plot = figure(
		title="ZTM Warsaw Public Transport Network",
		x_axis_label="Longitude",
		y_axis_label="Latitude",
		tools="pan,wheel_zoom,box_zoom,reset,save",
		tooltips=[("Stop name", "@label")],
		sizing_mode="stretch_both",
		x_axis_type="mercator",
		y_axis_type="mercator",
		x_range=(min_x, max_x),
		y_range=(min_y, max_y),
	)

	return plot

def create_tile_map(plot):
	"""Adds a tile map to the Bokeh plot."""

	plot.add_tile(xyz.CartoDB.Positron)

def create_graph_renderer(G, mercator_positions, source_nodes):
	"""Creates a graph renderer for Bokeh plot."""

	graph_renderer = from_networkx(G, mercator_positions, scale=1)
	graph_renderer.node_renderer.data_source = source_nodes
	graph_renderer.node_renderer.glyph = Circle(radius=50)

	return graph_renderer

def draw_edges(plot, edge_data):
	"""Draws edges on the Bokeh plot using MultiLine glyphs."""

	plot.multi_line(
		xs='xs',
		ys='ys',
		source=edge_data,
		line_width=1,
		color='gray',
		alpha=0.7
	)

def draw_nodes(plot, node_data):
    """Draws nodes on the Bokeh plot using Circle glyphs."""

    plot.circle(
		x='x',
		y='y',
		source=node_data,
		size=10,
		color='skyblue',
		alpha=0.8
    )

def create_zoom_callback(plot, initial_ratio):
	"""Creates a zoom callback to maintain aspect ratio."""

	callback = CustomJS(args=dict(plot=plot, initial_ratio=initial_ratio), code=
		"""
		const x_range = plot.x_range
		const y_range = plot.y_range
		const current_width = x_range.end - x_range.start
		const current_height = y_range.end - y_range.start;

		const current_ratio = current_width / current_height
		if (Math.abs(current_ratio - initial_ratio) > 0.0001) {
			const new_width = current_height * initial_ratio;
			const mid_x = x_range.start + (current_width / 2);
			x_range.start = mid_x - (new_width / 2)
			x_range.end = mid_x + (new_width / 2)
			}
		"""
	)

	plot.x_range.js_on_change('start', callback)
	plot.x_range.js_on_change('end', callback)
	plot.y_range.js_on_change('start', callback)
	plot.y_range.js_on_change('end', callback)

def enable_wheel_zoom(plot):
	"""
	Enables wheel zoom by default.

	In reality it just switches the the tool, but the goal is met.
	"""

	plot.toolbar.active_scroll = plot.select_one(WheelZoomTool)

def visualize_graph(G):
	"""Visualizes the graph with bokeh."""

	# Output to an HTML file
	output_file("graph.html")

	node_data, edge_data, min_x, max_x, min_y, max_y, initial_ratio = prepare_visualization_data(G)
	plot = create_bokeh_plot(min_x, max_x, min_y, max_y)

	# background
	create_tile_map(plot)

	# content
	draw_edges(plot, edge_data)
	draw_nodes(plot, node_data)

	# utils
	create_zoom_callback(plot, initial_ratio)
	enable_wheel_zoom(plot)

	show(plot)

if __name__ == '__main__':
	api_key = get_api_key()

	stops_data = get_stop_data(api_key)
	routes_data = get_routes_data(api_key)

	# Create the graph
	G = create_graph(stops_data, routes_data)

	# Visualize the graph
	visualize_graph(G)
