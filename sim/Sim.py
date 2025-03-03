import math
import threading
import time
from random import uniform, expovariate
from typing import List, Optional

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane


class Sim:
    __DEFAULT_TIME_STEP: float = 1 / 30  # Default UI mode time step

    def __init__(self, junctions: List[Junction] = None, if_ui: bool = True):
        """
        Initialize the simulation.
        :param junctions: List of Junctions in the simulation.
        :param if_ui: If True, run simulation at ~30 FPS; otherwise ~1000 FPS.
        """
        self.__junctions: List[Junction] = junctions if junctions else []
        self.__thread: Optional[threading.Thread] = None
        self.__stop_event = threading.Event()
        self.__lock = threading.Lock()
        self.if_ui: bool = if_ui
        self.__time_step: float = 1 / 30 if self.if_ui else 1 / 1000

    def start(self) -> None:
        """Starts the simulation in a new thread."""
        self.__stop_event.clear()
        if self.__thread and self.__thread.is_alive():
            # Already running
            return
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
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        # Make a copy of cars so that removal doesn't break the iteration
                        for car in list(lane.get_cars()):
                            self.__move_car(car, lane, junction)

    def __move_car(self, car: Car, lane: Lane, junction: Junction) -> None:
        """
        Moves the car using (simple) physics-based acceleration/deceleration
        and checks if the car should switch lanes or be removed.
        """
        velocity = car.get_velocity()
        dist = car.get_dist()

        # Fallback deceleration if lane doesn't have max_decel
        deceleration = getattr(lane, "max_decel", 3.0)
        safe_distance = (velocity ** 2) / (2 * deceleration) if deceleration > 0 else 10

        # Check traffic light
        light_green = self.__check_if_green(lane, junction)

        # Get gap to car in front
        distance_to_car_ahead = self.__check_car_ahead(lane, car)

        # Desired velocity is the lane speed limit unless we need to slow down
        desired_velocity = lane.max_vel

        # If light is red, and we are within 30 units of the light, target velocity is 0
        if not light_green and dist < 30:
            desired_velocity = 0
        # If we're too close to the car ahead, slow down
        elif distance_to_car_ahead < safe_distance:
            # A simple slow-down factor based on the ratio
            desired_velocity = min(desired_velocity, velocity * (distance_to_car_ahead / safe_distance))

        # Calculate acceleration needed to get from velocity to desired_velocity within this timestep
        max_accel = getattr(lane, "max_accel", 2.0)
        raw_acc = (desired_velocity - velocity) / self.__time_step
        # Clamp acceleration between -deceleration and +max_accel
        acceleration = max(-deceleration, min(raw_acc, max_accel))

        # Update velocity
        new_velocity = velocity + acceleration * self.__time_step

        # Distance traveled in this time step (simple kinematics)
        displacement = velocity * self.__time_step + 0.5 * acceleration * (self.__time_step ** 2)
        new_dist = dist - displacement

        # Update car state
        car.set_velocity(new_velocity)
        car.set_dist(new_dist)

        # Check if we reached the next lane or left this lane
        dest_lane = next(iter(junction.get_lanes_by_ids([car.get_dest()])), None)
        if new_dist <= 0 and dest_lane:
            # Move car to the next lane if it’s a different one
            if dest_lane.get_id() != lane.get_id():
                lane.remove_car(car)
                dest_lane.add_car(car)
                car.set_dist(dest_lane.LENGTH)

        # If we are too far past the lane's endpoint, remove the car
        after_length = getattr(lane, "after_length", -(lane.LENGTH // 2))  # fallback
        if new_dist <= after_length:
            lane.remove_car(car)
            # Could do something more complex here, e.g., move to a next junction, etc.

    @staticmethod
    def __check_if_green(lane: Lane, junction: Junction) -> bool:
        """
        Check if the traffic light for this lane is green.
        This function assumes that if ANY traffic light that has this lane's ID as an origin is green,
        then the lane's signal is effectively green.
        """
        for tl in junction.get_traffic_lights():
            if lane.get_id() in tl.get_origins() and tl.get_state() is True:
                return True
        return False

    @staticmethod
    def __check_car_ahead(lane: Lane, car: Car) -> float:
        """Returns the gap to the car ahead in the same lane, or math.inf if no car ahead."""
        dist_of_this = car.get_dist()
        # Cars with distance < dist_of_this are "ahead" (since we measure dist from lane end)
        cars_ahead = [other for other in lane.get_cars() if other.get_dist() < dist_of_this and other is not car]
        if not cars_ahead:
            return math.inf
        # Minimum gap
        return min(dist_of_this - other.get_dist() for other in cars_ahead)

    def __update_traffic_lights(self) -> None:
        """
        Update traffic light cycles.
        (Currently just toggles some lights after a certain count for demonstration.)
        TODO: In a real scenario, fetch states from a backend or a more complex scheduling logic.
        """
        with self.__lock:
            # A silly time-based toggling demonstration
            for junction in self.__junctions:
                count = 0
                for tl in junction.get_traffic_lights():
                    # Flip state after 5 seconds (assuming 30 fps => ~150 updates)
                    if count > 30 * 5:
                        if tl.get_state():
                            tl.red()
                        else:
                            tl.green()
                    count += 1

    def __gen_cars(self) -> None:
        """
        Generates new cars based on an exponential distribution with parameter 'lane.get_car_creation()'.
        If lane.get_car_creation() is 0, it means no cars for that lane.
        """
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        car_creation_rate = lane.get_car_creation()
                        # Sometimes lane might have 0 creation rate => no new cars
                        if car_creation_rate > 0:
                            # On average, expovariate() will produce 1 event per 1/lambda
                            # We do int() to handle the possibility that we might get > 1 sometimes
                            num_cars = int(expovariate(car_creation_rate))
                            for i in range(num_cars):
                                speed = max(0.0, uniform(lane.max_vel - 10, lane.max_vel + 10))
                                new_car = Car(id=i,
                                              dist=lane.LENGTH,
                                              velocity=speed,
                                              dest=self.__create_random_dest(lane),
                                              car_type="CAR")
                                lane.add_car(new_car)

    @staticmethod
    def __create_random_dest(lane: Lane) -> Lane:
        # For now, we just return the same lane as the "destination".
        # In a bigger simulation, this would be replaced by an actual next-lane or route selection.
        return lane

    def stop(self) -> None:
        """Stops the simulation."""
        self.__stop_event.set()
        if self.__thread:
            self.__thread.join()
            self.__thread = None

    def pause(self) -> None:
        """Pauses the simulation (same as stop)."""
        self.stop()

    def resume(self) -> None:
        """Resumes the simulation."""
        self.start()

    def get_junctions(self) -> List[Junction]:
        """Returns the list of junctions in the simulation."""
        return self.__junctions
