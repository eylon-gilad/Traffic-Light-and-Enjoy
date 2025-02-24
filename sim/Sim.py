import math
from typing import List, Dict, Any, Tuple
from threading import Thread
from utils.TrafficLight import TrafficLight
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.Car import Car


class Sim:
    junctions: List[Junction] = []
    TIME_STEP: float = 1 / 30

    def __init__(self, junctions: List[Junction] = [], time_step: float = TIME_STEP):
        self.thread: Thread = None
        self.junctions: List[Junction] = junctions
        self.time_step: float = time_step
        self.stop: bool = False

    def start(self) -> None:
        self.stop = False
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self) -> None:
        while not self.stop:
            self.next()
            self.gen_cars()
            self.update_physics()
            self.gen_frame()

    def next(self) -> str:
        for junction in self.junctions:
            roads: List[Road] = junction.get_roads()
            for road in roads:
                lanes: List[Lane] = road.get_lanes()
                for lane in lanes:
                    cars: List[Car] = lane.get_cars()
                    for index, car in enumerate(cars):
                        self.move_car(car, lane, road, junction, index)

        return "Hello, World!"

    def move_car(self, car: Car, lane: Lane, road: Road, junction: Junction, index: int) -> None:
        """
        Move the car based on its current velocity, distance, and decision to stop or change lanes.

        Steps:
        1. Calculate all distances for the current car.
        2. Decide whether it should stop based on traffic rules, other cars, or obstacles.
        3. Continue moving based on car speed or stopping condition.
        4. Move the car based on its speed (in kph) and time timestamp.
        5. If needed, switch lanes (only for turns in the junction).
        """
        # Calculate current velocity and distance
        vel: float = car.get_velocity()  # Car velocity in kph
        dist: float = car.get_dist()  # Current distance traveled

        # Check if car should stop at a junction or based on traffic rules
        should_stop: bool = self.__check_stop_condition(car, lane, road, junction)
        if should_stop:
            vel = 0  # Set velocity to 0 if stopping is necessary

        # Update car position based on velocity
        new_dist: float = dist - (vel * (self.time_step / 3600))  # Convert speed to distance

        # Move the car to its new position
        car.set_dist(new_dist)

        # Handle lane change at junctions
        if junction and car.needs_lane_change():
            self.switch_lane(car, lane, junction)

        # Update the car's velocity
        car.set_velocity(vel)

    def gen_frame(self) -> None:
        """
        Generate a frame for the frontend.
        """
        pass

    def __check_stop_condition(self, car: Car, lane: Lane, road: Road, junction: Junction) -> bool:
        """
        Check if the car should stop based on traffic rules.
        """
        if car.get_dist() < 10 and not self.__check_if_green(lane, junction):
            return True

        if self.__check_car_ahead(lane, car) < 10:
            return True

        return False

    def __check_if_green(self, lane: Lane, junction: Junction) -> bool:
        """
        Check if the light is green for the lane.
        """
        for tl in junction.get_traffic_lights():
            for origin in tl.get_origins():
                if origin == lane.get_id():
                    return tl.get_state() == 'green'
        return False

    def __check_car_ahead(self, car: Car, lane: Lane) -> float:
        """
        Check the distance from the car ahead in the same lane.

        Returns:
            float: The minimum distance to the car ahead or math.inf if there are no cars ahead.
        """
        cars_ahead = [other_car for other_car in lane.get_cars() if other_car.get_dist() < car.get_dist()]

        if not cars_ahead:
            return math.inf

        min_dist = min(other_car.get_dist() - car.get_dist() for other_car in cars_ahead)

        return min_dist

    def update_physics(self) -> None:
        """
        Placeholder function to update the physics of the simulation.
        """
        pass

    def switch_lane(self, car: Car, lane: Lane, junction: Junction) -> None:
        """
        Placeholder function for handling lane changes.
        """
        pass

    def gen_cars(self):
        """
        Placeholder function to generate cars in the simulation. per lane.
        """
        for junction in self.junctions:
            roads = junction.get_roads()
            for road in roads:
                lanes = road.get_lanes()
                for lane in lanes:
                    lane.

