import random
from utils.Car import Car
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight
from utils.Junction import Junction


def create_traffic_light(id, entry_angle, state):
    tl = TrafficLight(light_id=id, origins=[], destinations=[], state=state)
    tl.entry_angle = entry_angle  # store the numeric entry angle
    return tl


class StaticIntersectionSimulation:
    def __init__(self):
        """
        Creates a static simulation state representing a realistic four‐arm intersection.
        Each of the four roads has 4 lanes with many cars approaching the junction (incoming only).
        Road IDs will be numeric and of the form 11RR (e.g., 1101 for road 1).
        Lane IDs will be numeric and of the form 11RRLL (e.g., 110101 for lane 1 on road 1).

        Instead of storing a cardinal direction (e.g., "north"), each road gets an
        entry_angle property. In our example:
          - Road 1101 gets entry_angle = -90° (formerly north)
          - Road 1102 gets entry_angle = 90° (formerly south)
          - Road 1103 gets entry_angle = 0° (formerly east)
          - Road 1104 gets entry_angle = 180° (formerly west)
        """
        self.roads = []
        self.lane_width = 40  # lane width in pixels
        num_cars_per_lane = 2

        # Define entry angles in the order we want our four roads to appear.
        entry_angles = [-90, 90, 0, 180]
        for road_index in range(4):
            road_number = road_index + 1
            road_id = 1100 + road_number
            entry_angle = entry_angles[road_index]
            lanes = []
            for lane_index in range(4):
                cars = []
                for i in range(num_cars_per_lane):
                    # Random distance from the junction edge (between 20 and 300 pixels)
                    dist_val = random.uniform(20, 300)
                    img_index = random.randint(1, 7)
                    # Compute a car ID that incorporates the road and lane info.
                    car_id = road_id * 1000 + (lane_index + 1) * 100 + i
                    car = Car(
                        id=car_id,
                        dist=dist_val,
                        velocity=0.0,
                        dest=road_id,  # using road_id as a placeholder for destination
                        car_type="CAR",
                    )
                    car.img_index = img_index  # assign a random car image index
                    cars.append(car)
                # Create lane ID as 11RRLL (with lanes numbered 1–4)
                lane_id = road_id * 100 + (lane_index + 1)
                lane = Lane(lane_id=lane_id, cars=cars)
                lanes.append(lane)

            road = Road(road_id=road_id, lanes=lanes, congection_level=0)
            road.entry_angle = entry_angle  # store the numeric entry angle
            self.roads.append(road)

        # Create one traffic light per road.
        # For realism, let’s assume roads with entry_angle -90 and 90 (formerly north & south) are green.
        self.traffic_lights = []
        for road in self.roads:
            state = True if road.entry_angle in (-90, 90) else False
            tl = create_traffic_light(road.id, road.entry_angle, state)
            self.traffic_lights.append(tl)

    def get_roads(self):
        return self.roads

    def get_traffic_lights(self):
        return self.traffic_lights
