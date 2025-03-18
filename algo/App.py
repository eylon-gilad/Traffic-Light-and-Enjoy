import logging
from typing import Any, Dict, List, Optional

from flask import Flask, request, jsonify, Response

from algo.AlgoRunner import AlgoRunner
from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.TrafficLight import TrafficLight

app = Flask(__name__)

# Global references to the current Junction and the algorithm runner.
junction: Optional[Junction] = None
alg: Optional[AlgoRunner] = None

# Configure a basic logger (for demonstration).
logging.basicConfig(level=logging.INFO)


@app.route("/junction-info", methods=["POST"])
def post_junction_info() -> Response:
    """
    Receives JSON containing information about a junction, including
    roads, lanes, cars, and traffic lights, then constructs the
    corresponding objects and updates the global junction reference.

    Expected JSON format:
    {
        "junction": {
            "traffic_lights": [...],
            "roads": [...],
            ...
        }
    }

    :return: A JSON response indicating success or failure.
    """
    global junction, alg

    try:
        data: Optional[Dict[str, Any]] = request.get_json()
    except Exception as e:
        logging.error(f"Error parsing JSON: {e}")
        return jsonify({"error": "Invalid JSON data."}, 400)

    if not data or "junction" not in data:
        return jsonify({"error": "Invalid request. 'junction' key not found."}, 400)

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

    # Update junction info in the existing algorithm runner
    if alg is not None:
        alg.set_junction_info(junction)

    return jsonify({"message": "Junction information updated successfully."}, 200)


@app.route("/start-algorithm", methods=["GET"])
def start_algorithm() -> Response:
    """
    Instantiates the AlgoRunner with the global junction and starts
    the chosen traffic algorithm in a background thread.
    """
    global junction, alg

    if junction is None:
        return jsonify({"error": "No junction data available to start the algorithm."}, 400)

    try:
        alg = AlgoRunner(junction)
        alg.run()
        return jsonify({"message": "Algorithm runner started successfully."}, 200)
    except Exception as e:
        logging.error(f"Failed to start algorithm: {e}")
        return jsonify({"error": "Could not start the algorithm."}, 500)


@app.route("/build-junction", methods=["POST"])
def build_junction() -> Response:
    """
    Receives JSON to build a new Junction object, without cars,
    typically used for initial setup or placeholder.
    """
    global junction

    print("build-junction cos ameck")

    try:
        data: Optional[Dict[str, Any]] = request.get_json()
    except Exception as e:
        logging.error(f"Error parsing JSON in build-junction: {e}")
        return jsonify({"error": "Invalid JSON data."}, 400)

    if not data or "junction" not in data:
        return jsonify(({"error": "Invalid request. 'junction' key not found."}), 400)

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
        from_side: RoadEnum = RoadEnum.from_string(road_data.get("from", 0))
        to_side: RoadEnum = RoadEnum.from_string(road_data.get("to", 0))
        congection_level: int = road_data.get("congection_level", 0)

        lanes_data: List[Dict[str, Any]] = road_data.get("lanes", [])
        lane_objects: List[Lane] = []
        for ln_data in lanes_data:
            lane_id: int = ln_data.get("lane_index", 0)
            lane_objects.append(Lane(lane_id=lane_id))

        roads.append(
            Road(
                road_id=road_id,
                lanes=lane_objects,
                congection_level=congection_level,
                from_side=from_side,
                to_side=to_side,
            )
        )

    # Construct the Junction object
    junction_id: int = junction_data.get("id", 0)
    junction = Junction(junction_id=junction_id, traffic_lights=traffic_lights, roads=roads)

    print(junction.__str__())

    return jsonify({"message": "Junction was built successfully."}, 200)


@app.route("/traffic-light-state", methods=["GET"])
def get_traffic_light_state() -> Response:
    """
    Returns the current state of all traffic lights in the junction.
    If the junction or algorithm runner has not been set, an error is returned.
    """
    global junction, alg

    if junction is None or alg is None:
        return jsonify({"error": "Junction or algorithm runner not set yet."}, 400)

    try:
        current_lights = alg.get_current_state()
        traffic_light_states: List[Dict[str, Any]] = []
        for tl in current_lights:
            traffic_light_states.append(
                {
                    "traffic_light_index": tl.get_id(),
                    "origins": tl.get_origins(),
                    "destinations": tl.get_destinations(),
                    "state": tl.get_state(),
                }
            )
        return jsonify(({"traffic_lights": traffic_light_states}), 200)
    except Exception as e:
        logging.error(f"Failed to retrieve traffic light state: {e}")
        return jsonify(({"error": "Could not get traffic light state."}), 500)


if __name__ == "__main__":
    # Note: In production, debug and host/port might be set differently.
    app.run(debug=True, host="127.0.0.1", port=8080)
