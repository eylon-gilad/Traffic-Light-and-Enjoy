# app.py
import FastAPI
from typing import List
from utils.Junction import Junction
from utils.Road import Road
from utils.TrafficLight import TrafficLight
from utils.Car import Car


app = FastAPI()

# Sample data
junction = Junction()
traffic_light = TrafficLight()


@app.get("/simulation/full-state")
def get_full_simulation_state():
    """Returns the complete state of the traffic system including junctions, roads, lanes, cars, and traffic light."""
    state = {
        "traffic_light": "Green" if traffic_light.state else "Red",
        "junction": {
            "total_roads": len(junction.roads),
            "roads": [
                {
                    "road_index": idx,
                    "num_lanes": len(road.lanes),
                    "congestion_level": get_road_congestion(road),
                    "lanes": [
                        {
                            "lane_index": lane_idx,
                            "total_cars": len(lane.cars),
                            "cars": [
                                {
                                    "dist": car.dist,
                                    "velocity": car.velocity,
                                    "dest": car.dest,
                                    "car_type": car.car_type
                                } for car in lane.cars
                            ]
                        } for lane_idx, lane in enumerate(road.lanes)
                    ]
                } for idx, road in enumerate(junction.roads)
            ]
        }
    }
    return state


@app.post("/junctions/roads")
def add_road(num_lanes: int):
    """Adds a road with a specified number of lanes to the junction."""
    road = Road(num_lanes)
    junction.add_road(road)
    return {"message": "Road added", "total_roads": len(junction.roads)}


@app.post("/traffic-light/toggle")
def toggle_traffic_light():
    """Toggles the traffic light state."""
    traffic_light.toggle()
    return {"message": "Traffic light toggled", "new_state": "Green" if traffic_light.state else "Red"}


@app.post("/lanes/cars")
def add_car(road_index: int, lane_index: int, dist: List[float], velocity: float, dest: str, car_type: str):
    """Adds a car to a specified lane."""
    if road_index >= len(junction.roads):
        return {"error": "Invalid road index."}

    road = junction.roads[road_index]
    if lane_index >= len(road.lanes):
        return {"error": "Invalid lane index."}

    lane = road.lanes[lane_index]
    car = Car(dist, velocity, dest, car_type)
    lane.add_car(car)
    return {"message": "Car added", "total_cars": len(lane.cars)}


def get_road_congestion(road: Road):
    """Returns congestion level per road based on the number of cars."""
    total_cars = sum(len(lane.cars) for lane in road.lanes)
    if total_cars > 10:
        return "High"
    elif total_cars > 5:
        return "Moderate"
    else:
        return "Low"
