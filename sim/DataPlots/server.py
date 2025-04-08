from flask import Flask, request, jsonify
from typing import Dict, List, Any

from utils.Junction import Junction
from utils.Car import Car
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight

server = Flask(__name__)

# Global data structures
car_time_in_sim: Dict[int, float] = {}
cars_per_road_history: Dict[int, List[int]] = {}
lane_avg_speeds_history: Dict[int, List[float]] = {}
traffic_light_state_history: Dict[int, List[int]] = {}

# For correlation:
total_cars_history: List[int] = []
avg_velocity_history: List[float] = []
collisions: List[int] = [0]


iteration_count = 0


def parse_json_to_junction(data: Dict[str, Any]) -> Junction:
    """
    Convert the JSON payload into a Junction object with roads, lanes, cars, traffic lights.
    """
    junction_data = data["junction"]

    # Traffic lights
    traffic_lights = []
    for tl_info in junction_data.get("traffic_lights", []):
        tl_id = tl_info.get("traffic_light_index", 0)
        origins = tl_info.get("input_index", [])
        destinations = tl_info.get("output_index", [])
        state = bool(tl_info.get("state", False))
        traffic_lights.append(TrafficLight(tl_id, origins, destinations, state))

    # Roads
    roads = []
    for road_data in junction_data.get("roads", []):
        road_id = road_data.get("road_index", 0)
        congestion_level = road_data.get("congection_level", 0)

        # Lanes
        lanes = []
        for lane_data in road_data.get("lanes", []):
            lane_id = lane_data.get("lane_index", 0)
            cars = []
            for car_info in lane_data.get("cars", []):
                c_id = car_info.get("car_index", 0)
                dist = car_info.get("dist", 0.0)
                velocity = float(car_info.get("velocity", 0.0))
                dest = car_info.get("dest", 0)
                car_type = car_info.get("car_type", "CAR")
                cars.append(Car(c_id, dist, velocity, dest, car_type))
            lanes.append(Lane(lane_id=lane_id, cars=cars))

        roads.append(
            Road(road_id=road_id, lanes=lanes, congection_level=congestion_level)
        )

    # Build final Junction
    junction_id = junction_data.get("id", 0)
    return Junction(junction_id, traffic_lights, roads)


@server.route("/update-data", methods=["POST"])
def update_data():
    """
    Receives JSON from the sim. Parses the junction, then updates:
      1) car_time_in_sim
      2) cars_per_road_history
      3) lane_avg_speeds_history
      4) traffic_light_state_history
      5) total_cars_history, avg_velocity_history
    """
    global iteration_count
    iteration_count += 1

    data = request.get_json()
    junction = parse_json_to_junction(data)

    # Assume each POST ~ 1 second
    delta_t = 1.0

    # Gather all cars
    all_cars = []
    for road in junction.get_roads():
        for lane in road.get_lanes():
            all_cars.extend(lane.get_cars())

    # (1) Car times
    for car in all_cars:
        if car.get_id() not in car_time_in_sim:
            car_time_in_sim[car.get_id()] = 0.0
        car_time_in_sim[car.get_id()] += delta_t

    # (2) Cars per road
    for road in junction.get_roads():
        road_id = road.get_id()
        num_cars_in_road = sum(len(l.get_cars()) for l in road.get_lanes())
        if road_id not in cars_per_road_history:
            cars_per_road_history[road_id] = []
        cars_per_road_history[road_id].append(num_cars_in_road)

    # (3) Lane avg speeds
    for road in junction.get_roads():
        for lane in road.get_lanes():
            lane_id = lane.get_id()
            cars_in_lane = lane.get_cars()
            if cars_in_lane:
                avg_speed = sum(c.get_velocity() for c in cars_in_lane) / len(
                    cars_in_lane
                )
            else:
                avg_speed = 0.0

            if lane_id not in lane_avg_speeds_history:
                lane_avg_speeds_history[lane_id] = []
            lane_avg_speeds_history[lane_id].append(avg_speed)

    # (4) Traffic lights
    for tl in junction.get_traffic_lights():
        tl_id = tl.get_id()
        state_val = 1 if tl.get_state() else 0
        if tl_id not in traffic_light_state_history:
            traffic_light_state_history[tl_id] = []
        traffic_light_state_history[tl_id].append(state_val)

    # (5) Correlation data
    total_cars_now = len(all_cars)
    total_cars_history.append(total_cars_now)
    if total_cars_now > 0:
        avg_vel_now = sum(c.get_velocity() for c in all_cars) / total_cars_now
    else:
        avg_vel_now = 0.0
    avg_velocity_history.append(avg_vel_now)

    return jsonify({"message": "Data updated"}), 200


@server.route("/send_collision", methods=["POST"])
def get_collisions():
    data = request.get_json()
    collisions.append(int(data["Collisions"]))

    return jsonify({"message": "Data updated"}), 200
