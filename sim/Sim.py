import math
import time
from random import uniform, gauss
from typing import List, Any
from threading import Thread, Lock
from utils.TrafficLight import TrafficLight
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.Car import Car


class Sim:
    __junctions: List[Junction] = []
    __TIME_STEP: float = 1 / 30

    def __init__(self, junctions=None, time_step: float = __TIME_STEP):
        if junctions is None:
            junctions = []
        self.__thread: Thread | None = None
        self.__junctions: List[Junction] = junctions
        self.__time_step: float = time_step
        self.__stop: bool = False
        self.__lock = Lock()

    def start(self) -> None:
        """Starts the simulation in a new thread."""
        self.__stop = False
        self.__thread = Thread(target=self.__run)
        self.__thread.start()

    def __run(self) -> None:
        """Main simulation loop."""
        while not self.__stop:
            start_time = time.perf_counter()
            self.__next()
            self.__gen_cars()
            self.update_physics()
            self.gen_frame()
            elapsed = time.perf_counter() - start_time
            self.__time_step = max(1 / 60, elapsed)  # Adjust dynamic time step

    def __next(self) -> None:
        """Progresses the simulation to the next state."""
        for junction in self.__junctions:
            roads: List[Road] = junction.get_roads()
            for road in roads:
                lanes: List[Lane] = road.get_lanes()
                for lane in lanes:
                    cars: List[Car] = lane.get_cars()
                    for index, car in enumerate(cars):
                        self.__move_car(car, lane, junction)

    def __move_car(self, car: Car, lane: Lane, junction: Junction) -> None:
        """Move the car based on its current velocity, distance, and decision to stop or change lanes."""
        with self.__lock:
            vel: float = car.get_velocity()
            dist: float = car.get_dist()

            should_stop: bool = self.__check_stop_condition(car, lane, junction)
            if should_stop:
                vel = 0

            new_dist: float = dist - (vel * (self.__time_step / 3600))
            car.set_dist(new_dist)

            if junction and car.needs_lane_change():
                self.__switch_lane(car, lane)

            car.set_velocity(vel)

    def gen_frame(self) -> None:
        """Generate a frame for the frontend."""
        pass

    def __check_stop_condition(self, car: Car, lane: Lane, junction: Junction) -> bool:
        """Check if the car should stop based on traffic rules."""
        if car.get_dist() < 10 and not self.__check_if_green(lane, junction):
            return True

        if self.__check_car_ahead(lane, car) < 10:
            return True

        return False

    @staticmethod
    def __check_if_green(lane: Lane, junction: Junction) -> bool:
        """Check if the light is green for the lane."""
        for tl in junction.get_traffic_lights():
            for origin in tl.get_origins():
                if origin == lane.get_id():
                    return tl.get_state() == "green"
        return False

    @staticmethod
    def __check_car_ahead(lane: Lane, car: Car) -> float:
        """Check the distance from the car ahead in the same lane."""
        car_positions = {c.get_dist(): c for c in lane.get_cars()}
        distances = [
            dist - car.get_dist() for dist in car_positions if dist < car.get_dist()
        ]
        return min(distances, default=math.inf)

    def update_physics(self) -> None:
        """Update the physics of the simulation (placeholder)."""
        pass

    @staticmethod
    def __switch_lane(car: Car, lane: Lane) -> None:
        """Handle lane changes for cars."""
        next_lane = lane.get_adjacent_lane()
        if next_lane and next_lane.has_space():
            lane.remove_car(car)
            next_lane.add_car(car)

    @staticmethod
    def __create_random_dest(lane_index: int = -1) -> Any:
        """Assigns a random destination to the car."""
        if lane_index < 0:
            raise ValueError("Missing parameters for 'create_random_dest' function.")
        return f"Destination_{lane_index}"

    def __gen_cars(self) -> None:
        """Generate cars in the simulation based on car creation rate."""
        car_id_counter = 0
        try:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        car_creation_rate = lane.get_car_creation()
                        num_cars = max(
                            0, int(gauss(car_creation_rate, car_creation_rate / 3))
                        )
                        for _ in range(num_cars):
                            speed = max(
                                0.0, uniform(lane.max_vel - 10, lane.max_vel + 10)
                            )
                            new_car = Car(
                                car_id_counter,
                                lane.LENGTH,
                                speed,
                                self.__create_random_dest(lane.get_id()),
                                "CAR",
                            )
                            lane.add_car(new_car)
                            car_id_counter += 1
        except Exception as e:
            print(f"Error generating cars: {e}")

    def stop(self) -> None:
        """Stops the simulation."""
        self.__stop = True
        if self.__thread:
            self.__thread.join()
