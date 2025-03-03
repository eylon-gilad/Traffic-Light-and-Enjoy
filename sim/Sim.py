# Sim.py
import math
import threading
import time
from random import uniform, expovariate
from typing import List, Optional

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane


class Sim:
    """
    Manages the main simulation logic in a background thread.
    """
    __DEFAULT_TIME_STEP: float = 1 / 30  # default ~30 FPS for UI mode

    def __init__(self, junctions: List[Junction] = None, if_ui: bool = True):
        self.__junctions: List[Junction] = junctions if junctions else []
        self.__stop_event = threading.Event()
        self.__lock = threading.Lock()
        self.if_ui = if_ui
        # Faster step if there's no UI
        self.__time_step: float = (1 / 30) if self.if_ui else (1 / 1000)
        self.__thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Starts the simulation in a new thread."""
        self.__stop_event.clear()
        if self.__thread and self.__thread.is_alive():
            # Already running
            return
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__thread.start()

    def __run(self) -> None:
        """Main loop that continues until stop_event is triggered."""
        while not self.__stop_event.is_set():
            start_time = time.perf_counter()

            self.__update_traffic_lights()
            self.__next()
            self.__gen_cars()

            elapsed = time.perf_counter() - start_time
            sleep_time = max(0.0, self.__time_step - elapsed)
            time.sleep(sleep_time)

    def __next(self) -> None:
        """Progresses the simulation (all cars in all lanes)."""
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        # Copy list so removal doesn't break iteration
                        for car in list(lane.get_cars()):
                            self.__move_car(car, lane, junction)

    def __move_car(self, car: Car, lane: Lane, junction: Junction) -> None:
        """
        Moves the car using a simplified physics-based model:
          - Acceleration/deceleration
          - Checking traffic light
          - Checking distance to car ahead
        """
        velocity = car.get_velocity()
        dist = car.get_dist()

        # Lane-level config
        deceleration = getattr(lane, "max_decel", 3.0)  # fallback
        acceleration_limit = getattr(lane, "max_accel", 2.0)
        desired_velocity = lane.max_vel

        # Minimum distance needed to stop safely
        safe_distance = (velocity ** 2) / (2 * deceleration) if deceleration > 0 else 10

        # Check if the light is green for this lane
        light_green = self.__check_if_green(lane, junction)

        # Check distance to car in front
        distance_to_car_ahead = self.__distance_to_car_ahead(lane, car)

        # If light is red and car is close to junction, set desired_velocity=0
        if not light_green and dist < 30:
            desired_velocity = 0
        # If there's a car ahead too close, slow down
        elif distance_to_car_ahead < safe_distance:
            fraction = distance_to_car_ahead / safe_distance
            desired_velocity = min(desired_velocity, velocity * fraction)

        # Compute needed acceleration to go from velocity -> desired_velocity in this timestep
        raw_acc = (desired_velocity - velocity) / self.__time_step
        # Clamp
        acc = max(-deceleration, min(raw_acc, acceleration_limit))

        # s = v*t + 0.5*a*t^2
        new_velocity = velocity + acc * self.__time_step
        displacement = (velocity * self.__time_step) + (0.5 * acc * (self.__time_step ** 2))
        new_dist = dist - displacement

        # Update the car
        car.set_velocity(new_velocity)
        car.set_dist(new_dist)

        # If the car has reached the junction (dist <= 0), see if it needs to move to another lane
        if new_dist <= 0:
            # Attempt to move the car to its "dest" lane if that lane is different
            dest_lane = next(iter(junction.get_lanes_by_ids([car.get_dest()])), None)
            if dest_lane and dest_lane.get_id() != lane.get_id():
                lane.remove_car(car)
                dest_lane.add_car(car)
                # Reset the distance in the new lane
                car.set_dist(dest_lane.LENGTH)

        # If the car has gone beyond some threshold, remove it (it left the system)
        # You might choose a different approach for "exiting" the simulation
        exit_threshold = -20  # for example
        if new_dist < exit_threshold:
            lane.remove_car(car)

    @staticmethod
    def __distance_to_car_ahead(lane: Lane, this_car: Car) -> float:
        """
        Returns how far ahead the nearest car is in the same lane (distances measured from lane end).
        Larger 'dist' means the car is further from the junction, so "ahead" means 'dist' is smaller.
        """
        this_dist = this_car.get_dist()
        # Any car with a 'dist' less than this_dist is physically ahead.
        cars_ahead = [c for c in lane.get_cars() if c.get_dist() < this_dist and c != this_car]
        if not cars_ahead:
            return math.inf
        # The gap is (this_dist - that_dist)
        return min(this_dist - c.get_dist() for c in cars_ahead)

    @staticmethod
    def __check_if_green(lane: Lane, junction: Junction) -> bool:
        """
        Returns True if any traffic light that covers lane.id is green.
        """
        for tl in junction.get_traffic_lights():
            if lane.get_id() in tl.get_origins() and tl.get_state() is True:
                return True
        return False

    def __update_traffic_lights(self) -> None:
        """
        Very naive 'time-based' toggler for demonstration.
        Flip traffic lights every ~5 seconds (assuming 30 FPS => ~150 loops).
        """
        with self.__lock:
            for junction in self.__junctions:
                for tl in junction.get_traffic_lights():
                    # Toggle at random or after a certain count?
                    # Here we just flip it with small probability each step for demo
                    # or you could do a time-based approach.
                    pass
                    # Example (commented):
                    # if random.random() < 0.001:
                    #     if tl.get_state():
                    #         tl.red()
                    #     else:
                    #         tl.green()

    def __gen_cars(self) -> None:
        """
        Generate new cars for each lane based on an exponential distribution with
        parameter lane.get_car_creation(). If that is 0, no cars for that lane.
        """
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        rate = lane.get_car_creation()
                        if rate > 0:
                            # On average, expovariate(rate) yields 1 event per 1/rate
                            # We convert that to an integer number of new cars
                            num_cars = int(expovariate(rate))
                            for i in range(num_cars):
                                # Create a random velocity near the lane's max_vel
                                speed = uniform(lane.max_vel * 0.5, lane.max_vel * 1.2)
                                # Destination is the same lane ID for demonstration
                                car_id = int(time.time() * 1000)  # generate a pseudo-unique ID
                                new_car = Car(
                                    id=car_id,
                                    dist=lane.LENGTH,
                                    velocity=speed,
                                    dest=lane.get_id(),
                                    car_type="CAR",
                                )
                                lane.add_car(new_car)

    def stop(self) -> None:
        """Stop the simulation thread."""
        self.__stop_event.set()
        if self.__thread:
            self.__thread.join()
            self.__thread = None

    def pause(self) -> None:
        """Pauses the simulation (same as stop)."""
        self.stop()

    def resume(self) -> None:
        """Resumes the simulation if it’s not already running."""
        self.start()

    def get_junctions(self) -> List[Junction]:
        return self.__junctions
