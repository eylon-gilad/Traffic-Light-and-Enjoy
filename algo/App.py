from typing import Any, Dict, List, Optional

from flask import Flask, request, jsonify, Response

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight

app = Flask(__name__)

# Store the Junction object here after parsing the JSON
junction: Optional[Junction] = None


@app.route("/junction-info", methods=["POST"])
def post_junction_info() -> Response:
    """
    Receives JSON containing information about a junction, including
    roads, lanes, cars, and traffic lights, then constructs the
    corresponding objects.
    """
    global junction

    data: Optional[Dict[str, Any]] = request.get_json()
    if not data or "junction" not in data:
        return jsonify({"error": "Invalid request. 'junction' key not found."}, 400)

    # Extract the junction portion of the data
    junction_data: Dict[str, Any] = data["junction"]

    # Parse traffic lights data
    traffic_light_data: List[Dict[str, Any]] = junction_data.get("traffic_lights", [])
    traffic_lights: List[TrafficLight] = []
    for tl in traffic_light_data:
        tl_id: int = tl.get("traffic_light_index", 0)
        origins: List[int] = tl.get("input_index", [])
        destinations: List[int] = tl.get("output_index", [])
        state: bool = tl.get("state", False)
        traffic_lights.append(
            TrafficLight(
                id=tl_id, origins=origins, destinations=destinations, state=state
            )
        )

    # Parse roads data
    roads_data: List[Dict[str, Any]] = junction_data.get("roads", [])
    roads: List[Road] = []
    for rd in roads_data:
        road_id: int = rd.get("road_index", 0)
        congection_level: int = rd.get("congection_level", 0)

        # Parse lanes data for this road
        lanes_data: List[Dict[str, Any]] = rd.get("lanes", [])
        lanes: List[Lane] = []
        for ln in lanes_data:
            lane_id: int = ln.get("lane_index", 0)

            # Parse cars data for this lane
            cars_data: List[Dict[str, Any]] = ln.get("cars", [])
            cars: List[Car] = []
            for car in cars_data:
                car_id: int = car.get("car_index", 0)
                dist: List[float] = car.get("dist", [])
                velocity: float = car.get("velocity", 0.0)
                dest: str = car.get("dest", "")
                car_type: str = car.get("car_type", "CAR")

                cars.append(
                    Car(
                        id=car_id,
                        dist=dist,
                        velocity=velocity,
                        dest=dest,
                        car_type=car_type,
                    )
                )

            lanes.append(Lane(id=lane_id, cars=cars))

        roads.append(Road(id=road_id, lanes=lanes, congection_level=congection_level))

    # Construct the Junction object
    junction_id: int = junction_data.get("id", 0)
    junction = Junction(id=junction_id, traffic_lights=traffic_lights, roads=roads)

    return jsonify({"message": "Junction information updated successfully."}, 200)


@app.route("/traffic-light-state", methods=["GET"])
def get_traffic_light_state() -> Response:
    """
    Returns the current state of all traffic lights in the junction.
    If the junction is not yet set, returns an error.
    """
    global junction

    if junction is None:
        return jsonify({"error": "Junction not set yet."}, 400)

    traffic_light_states: List[Dict[str, Any]] = []
    for tl in junction.get_traffic_lights():
        traffic_light_states.append(
            {
                "traffic_light_index": tl.get_id(),
                "origins": tl.get_origins(),
                "destinations": tl.get_destinations(),
                "state": tl.get_state(),
            }
        )

    return jsonify({"traffic_lights": traffic_light_states}, 200)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8080)
