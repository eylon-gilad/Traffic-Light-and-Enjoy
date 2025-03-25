import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from flask import Flask, request, jsonify
from typing import Dict, List, Any

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight

# Flask server
server = Flask(__name__)

# Global storage for received data
car_to_time_in_sim: Dict[int, float] = {}
cars_per_road_history: Dict[int, List[int]] = {}


def parse_json_to_junction(data) -> Junction:
    junction_data: Dict[str, Any] = data["junction"]

    # Parse traffic lights
    traffic_light_info: List[Dict[str, Any]] = junction_data.get("traffic_lights", [])
    traffic_lights: List[TrafficLight] = []
    for tl_info in traffic_light_info:
        tl_id: int = tl_info.get("traffic_light_index", 0)
        origins: List[int] = tl_info.get("input_index", [])
        destinations: List[int] = tl_info.get("output_index", [])
        state: bool = bool(tl_info.get("state", False))
        traffic_lights.append(
            TrafficLight(
                light_id=tl_id, origins=origins, destinations=destinations, state=state
            )
        )

    # Parse roads
    roads_data: List[Dict[str, Any]] = junction_data.get("roads", [])
    roads: List[Road] = []
    for road_data in roads_data:
        road_id: int = road_data.get("road_index", 0)
        congection_level: int = road_data.get("congection_level", 0)

        # Parse lanes for this road
        lanes_data: List[Dict[str, Any]] = road_data.get("lanes", [])
        lanes: List[Lane] = []
        for lane_data in lanes_data:
            lane_id: int = lane_data.get("lane_index", 0)

            # Parse cars for this lane
            cars_data: List[Dict[str, Any]] = lane_data.get("cars", [])
            cars: List[Car] = []
            for car_info in cars_data:
                car_id: int = car_info.get("car_index", 0)
                dist: float = car_info.get("dist", 0.0)
                velocity: float = float(car_info.get("velocity", 0.0))
                dest: int = car_info.get("dest", 0)
                car_type: str = car_info.get("car_type", "CAR")

                cars.append(
                    Car(
                        car_id=car_id,
                        dist=dist,
                        velocity=velocity,
                        dest=dest,
                        car_type=car_type,
                    )
                )

            lanes.append(Lane(lane_id=lane_id, cars=cars))

        roads.append(Road(road_id=road_id, lanes=lanes, congection_level=congection_level))

    # Construct the Junction object
    junction_id: int = junction_data.get("id", 0)
    junction = Junction(junction_id=junction_id, traffic_lights=traffic_lights, roads=roads)

    return junction


# Define POST request route to update data
@server.route("/update-data", methods=["POST"])
def update_data():
    global car_to_time_in_sim, cars_per_road_history
    data = request.get_json()  # Get JSON data from client
    junction = parse_json_to_junction(data)

    """
    Update how long each car has been in the simulation.
    In this example, we assume 1 iteration = 1 second.
    Adjust 'delta_t' if you use a different time-step.
    """
    delta_t = 1.0

    # Gather all cars in all lanes of all roads for this junction
    all_cars = []
    for road in junction.get_roads():
        for lane in road.get_lanes():
            all_cars.extend(lane.get_cars())

    # Update or initialize times
    for car in all_cars:
        if car.get_id() not in car_to_time_in_sim:
            car_to_time_in_sim[car.get_id()] = 0.0
        car_to_time_in_sim[car.get_id()] += delta_t
        """
        Record how many cars are currently in each road at this iteration.
        """
        for road in junction.get_roads():
            road_id = road.get_id()
            num_cars_in_road = sum(len(lane.get_cars()) for lane in road.get_lanes())

            if road_id not in cars_per_road_history:
                cars_per_road_history[road_id] = []
            cars_per_road_history[road_id].append(num_cars_in_road)

    return jsonify({"message": "Data updated successfully"}), 200


# Dash app
app = dash.Dash(__name__, server=server)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content"),
    dcc.Interval(id="interval-component", interval=2000, n_intervals=0)  # Refresh every 2 sec
])


# Layouts
def home_layout():
    return html.Div([
        html.H1("Page 1: Live Plot"),
        dcc.Graph(id="live-plot"),
        dcc.Link("Go to Page 2", href="/page-2")
    ])


def page_2_layout():
    return html.Div([
        html.H1("Page 2: Live Plot"),
        dcc.Graph(id="live-plot-2"),
        dcc.Link("Go back to Page 1", href="/")
    ])


# Page Routing
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/page-2":
        return page_2_layout()
    return home_layout()


# Update Plot on Page 1
@app.callback(Output("live-plot", "figure"), Input("interval-component", "n_intervals"))
def update_plot(n):
    # df = pd.DataFrame(car_to_time_in_sim)
    # fig = px.scatter(df, x="x", y="y", title="Live Data - Page 1")
    """
    Creates and shows a Plotly histogram of car times in the sim.
    """
    times = list(car_to_time_in_sim.values())
    if not times:
        return  # no data

    df = pd.DataFrame({'time_in_sim': times})
    fig = px.histogram(
        df,
        x='time_in_sim',
        nbins=20,
        title="Distribution of Car Times in Simulation"
    )
    fig.update_layout(
        xaxis_title="Time in Simulation (s)",
        yaxis_title="Number of Cars"
    )
    return fig


# Update Plot on Page 2
@app.callback(Output("live-plot-2", "figure"), Input("interval-component", "n_intervals"))
def update_plot_2(n):
    if not cars_per_road_history:
        return  # no data

    # Gather data: each row is (iteration, road_id, count)
    rows = []
    for road_id, counts in cars_per_road_history.items():
        for i, count in enumerate(counts):
            rows.append((i, road_id, count))

    df = pd.DataFrame(rows, columns=["iteration", "road_id", "car_count"])
    # Convert numeric road_ids to string to label them distinctly
    df["road_id"] = df["road_id"].astype(str)

    fig = px.line(
        df,
        x="iteration",
        y="car_count",
        color="road_id",
        title="Number of Cars in Each Road Over Time"
    )
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Number of Cars"
    )

    return fig


# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=80)
