import math
import threading
import time
from random import uniform, expovariate
from typing import List

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane


# FIXME: do not use id as a variable name as it is a built-in function in python and may cause issues
class Sim:
    __DEFAULT_TIME_STEP: float = 1 / 30  # Default UI mode time step

    def __init__(self, junctions: List[Junction] = None, if_ui: bool = True):
        """
        Initialize the simulation.
        :param junctions: List of Junctions in the simulation.
        :param if_ui: If True, run simulation at ~30 FPS; otherwise ~1000 FPS.
        """
        self.__junctions: List[Junction] = junctions if junctions else []
        self.__thread: threading.Thread | None = None
        self.__stop_event = threading.Event()
        self.__lock = threading.Lock()
        self.if_ui: bool = if_ui
        self.__time_step: float = 1 / 30 if self.if_ui else 1 / 1000

    def start(self) -> None:
        """Starts the simulation in a new thread."""
        self.__stop_event.clear()
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__thread.start()

    def __run(self) -> None:
        """Main simulation loop."""
        while not self.__stop_event.is_set():
            start_time = time.perf_counter()
            self.__update_traffic_lights()
            self.__next()
            self.__gen_cars()
            elapsed = time.perf_counter() - start_time

            sleep_time = max(0.0, self.__time_step - elapsed)
            time.sleep(sleep_time)

    def __next(self) -> None:
        """Progresses the simulation state for each car."""
        for junction in self.__junctions:
            for road in junction.get_roads():
                for lane in road.get_lanes():
                    for car in list(lane.get_cars()):  # Avoid modifying while iterating
                        self.__move_car(car, lane, junction)

    def __move_car(self, car: Car, lane: Lane, junction: Junction) -> None:
        """Moves the car using physics-based acceleration and deceleration."""
        with self.__lock:
            velocity = car.get_velocity()
            dist = car.get_dist()
            deceleration = getattr(lane, "max_decel", 3.0)
            safe_distance = (velocity ** 2) / (2 * deceleration) if deceleration > 0 else 10

            light_green = self.__check_if_green(lane, junction)
            distance_to_car_ahead = self.__check_car_ahead(lane, car)
            desired_velocity = lane.max_vel

            if not light_green and dist < 30:
                desired_velocity = 0
            elif distance_to_car_ahead < safe_distance:
                desired_velocity = min(desired_velocity, velocity * (distance_to_car_ahead / safe_distance))

            acceleration = min(max((desired_velocity - velocity) / self.__time_step, -deceleration),
                               getattr(lane, "max_accel", 2.0))
            new_velocity = velocity + acceleration * self.__time_step
            displacement = velocity * self.__time_step + 0.5 * acceleration * (self.__time_step ** 2)
            new_dist = dist - displacement

            car.set_velocity(new_velocity)
            car.set_dist(new_dist)

            dest_lane = next(iter(junction.get_lanes_by_ids([car.get_dest()])), None)
            if new_dist <= 0 and dest_lane:
                if dest_lane:
                    if dest_lane.get_id() != lane.get_id():
                        lane.remove_car(car)
                        dest_lane.add_car(car)
                        car.set_dist(dest_lane.LENGTH)

            if new_dist <= getattr(lane, "after_length", -lane.LENGTH // 2):
                lane.remove_car(car)
                # TODO: move to the new junction

    @staticmethod
    def __check_if_green(lane: Lane, junction: Junction) -> bool:
        """Check if the traffic light for the lane is green."""
        return any(
            tl.get_state() is True for tl in junction.get_traffic_lights() if lane.get_id() in tl.get_origins()
        )

    @staticmethod
    def __check_car_ahead(lane: Lane, car: Car) -> float:
        """Returns the gap to the car ahead in the same lane."""
        cars_ahead = [other for other in lane.get_cars() if other.get_dist() < car.get_dist()]
        return min((car.get_dist() - other.get_dist() for other in cars_ahead), default=math.inf)

    def __update_traffic_lights(self) -> None:
        """Update traffic light cycles."""

        with self.__lock:
            for junction in self.__junctions:
                # TODO: make an http request to the backend to get the traffic light states
                count = 0
                for tl in junction.get_traffic_lights():
                    # TODO: update the traffic light states based on the response and not randomly(time based)
                    if count > 30 * 5:
                        tl.red() if tl.get_state() else tl.green()
                    count += 1

    def __gen_cars(self) -> None:
        """Generates new cars based on car creation probability."""
        try:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        num_cars = int(expovariate(lane.get_car_creation())) if lane.get_car_creation() > 0 else 0
                        for i in range(num_cars):
                            speed = max(0.0, uniform(lane.max_vel - 10, lane.max_vel + 10))
                            new_car = Car(i, lane.LENGTH, speed, self.__create_random_dest(lane), "CAR")
                            lane.add_car(new_car)
        except Exception as e:
            print(f"Error generating cars: {e}")

    def stop(self) -> None:
        """Stops the simulation."""
        self.__stop_event.set()
        if self.__thread:
            self.__thread.join()
            self.__thread = None

    def pause(self) -> None:
        """Pauses the simulation."""
        self.stop()

    def resume(self) -> None:
        """Resumes the simulation."""
        self.start()

    def get_junctions(self) -> List[Junction]:
        """Returns the list of junctions in the simulation."""
        return self.__junctions
