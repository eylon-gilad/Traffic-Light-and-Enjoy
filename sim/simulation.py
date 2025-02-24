# sim/simulation.py

import random
from utils.Car import Car
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight


class StaticIntersectionSimulation:
    def __init__(self):
        """
        Creates a static simulation state representing a realistic four‐arm intersection.
        Each of the four roads (north, south, east, west) has 4 lanes with many cars
        approaching the junction (incoming only). Also creates a traffic light for each approach.
        """
        self.roads = []
        self.lane_width = 40  # lane width in pixels
        num_cars_per_lane = 2

        # Define four roads with directions and unique IDs
        self.road_data = {
            'north': 1,
            'south': 2,
            'east': 3,
            'west': 4
        }

        # Create 4 lanes per road
        for road_direction, road_id in self.road_data.items():
            lanes = []
            for lane_index in range(4):
                cars = []
                for i in range(num_cars_per_lane):
                    # Random distance from the junction edge (between 20 and 300 pixels)
                    dist_val = random.uniform(20, 300)
                    img_index = random.randint(1, 7)
                    car = Car(
                        id=road_id * 100 + lane_index * 10 + i,
                        dist=[dist_val],
                        velocity=0.0,
                        dest=road_direction,
                        car_type="CAR"
                    )
                    car.img_index = img_index  # assign a random car image index
                    cars.append(car)
                lane = Lane(id=road_id * 10 + lane_index, cars=cars)
                lanes.append(lane)
            road = Road(id=road_id, lanes=lanes, congection_level=0)
            road.direction = road_direction  # store direction for drawing purposes
            self.roads.append(road)

        # Create one traffic light per approach.
        # For realism, let’s assume north and south have green while east and west have red.
        self.traffic_lights = []
        self.traffic_lights.append(self.create_traffic_light(1, 'north', True))
        self.traffic_lights.append(self.create_traffic_light(2, 'south', True))
        self.traffic_lights.append(self.create_traffic_light(3, 'east', False))
        self.traffic_lights.append(self.create_traffic_light(4, 'west', False))

    def create_traffic_light(self, id, direction, state):
        tl = TrafficLight(id=id, origins=[], destinations=[], state=state)
        tl.direction = direction
        return tl

    def get_roads(self):
        return self.roads

    def get_traffic_lights(self):
        return self.traffic_lights
