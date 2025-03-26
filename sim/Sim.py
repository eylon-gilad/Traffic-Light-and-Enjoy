"""
Sim.py

This module provides the Sim class which manages the traffic simulation.
It handles updating traffic lights, moving cars, generating new cars, and
managing the simulation loop on a separate background thread.
"""

import math
import random
import threading
import time
from typing import List, Optional
import numpy as np
from random import uniform
from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from sim.Client import Client
import threading


class Sim:
    """
    Manages the main simulation logic on a background thread.

    Attributes:
        __junctions (List[Junction]): List of junctions in the simulation.
        __stop_event (threading.Event): Event to signal simulation stop.
        __lock (threading.Lock): Lock to synchronize simulation updates.
        ui_enabled (bool): Flag indicating whether UI mode is enabled.
        __time_step (float): Time step per simulation loop (faster if UI is disabled).
        __thread (Optional[threa`ding.Thread]): Thread running the simulation loop.
    """

    __DEFAULT_TIME_STEP: float = 1 / 30  # Default ~30 FPS for UI mode
    LANE_WIDTH: int = 50
    CAR_ID: int = 0

    def __init__(
        self, junctions: Optional[List[Junction]] = None, if_ui: bool = True
    ) -> None:
        """
        Initializes the simulation.

        Args:
            junctions (Optional[List[Junction]]): List of junctions. Defaults to empty list.
            if_ui (bool): If True, simulation runs at ~30 FPS; if False, runs faster.
        """
        self.__junctions: List[Junction] = junctions if junctions else []
        self.__stop_event = threading.Event()
        self.__lock = threading.Lock()
        self.ui_enabled: bool = if_ui
        # Use a slower time step if UI is enabled; otherwise, use a faster step.
        self.__time_step: float = (1 / 30) if self.ui_enabled else (1 / 1000)
        self.__thread: Optional[threading.Thread] = None
        self.__client_failed: bool = False
        self.has_yellow: bool = False

    def start(self) -> None:
        """
        Starts the simulation in a new background thread.
        """
        self.__stop_event.clear()
        if self.__thread and self.__thread.is_alive():
            # Simulation is already running.
            return

        # Build each Junction on the server
        for junction in self.__junctions:
            try:
                Client.send_build_junction(junction)
            except Exception as exc:
                self.__set_all_lights_red()
                self.__client_failed = True

            # Start the traffic-light algorithm on the server
            try:
                Client.start_algorithm()
            except Exception as exc:
                self.__set_all_lights_red()
                self.__client_failed = True

            # Start the main simulation loop on a background thread
            self.__thread = threading.Thread(target=self.__run, daemon=True)
            self.__thread.start()

    def __run(self) -> None:
        """
        Main simulation loop. Updates traffic lights, moves cars, and generates new cars,
        then sleeps for the remainder of the time step.
        """
        # Send initial junction info
        for junction in self.__junctions:
            try:
                Client.send_junction_info(junction)
            except Exception as exc:
                self.__set_all_lights_red()
                self.__client_failed = True

        while not self.__stop_event.is_set():
            start_time: float = time.perf_counter()

            # 1) Send updated junction info if still functional
            if not self.__client_failed:
                for junction in self.__junctions:
                    try:
                        Client.send_junction_info(junction)
                    except Exception as exc:
                        self.__set_all_lights_red()
                        self.__client_failed = True

            # 2) Update traffic lights from server if client is functional
            if not self.__client_failed:
                thread = threading.Thread(target=self.__update_traffic_lights, daemon=True)
                thread.start()
            else:
                # Keep them forced red
                self.__set_all_lights_red()

            # 3) Advance the simulation
            self.__next()

            # 4) Generate new cars in all lanes
            self.__gen_cars()

            Client.send_junction_info_to_statistics(self.__junctions[0])
            Client.send_collision_info_to_statistics(self.__check_cars_collision())

            # 4) Sleep the remainder of the time step
            elapsed: float = time.perf_counter() - start_time
            sleep_time: float = max(0.0, self.__time_step - elapsed)
            time.sleep(sleep_time)

    def __next(self) -> None:
        """
        Advances the simulation by moving all cars in every lane of every road.
        """
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        # Copy the list to avoid issues when removing items during iteration.
                        for car in list(lane.get_cars()):
                            self.__move_car(car, lane, junction)

    def __move_car(self, car: Car, lane: Lane, junction: Junction) -> None:
        """
        Updates the position and velocity of a car using a simplified physics model.

        The method considers acceleration, deceleration, traffic lights, and the distance
        to the car ahead. It also handles lane transitions and removing cars that exit the simulation.

        Args:
            car (Car): The car object to update.
            lane (Lane): The current lane in which the car is driving.
            junction (Junction): The junction associated with the lane.
        """
        velocity: float = car.get_velocity()
        dist: float = car.get_dist()

        # Lane-level configuration: deceleration, acceleration limits, and desired velocity.
        deceleration: float = getattr(
            lane, "max_decel", 3.0
        )  # Fallback deceleration value.
        acceleration_limit: float = getattr(lane, "max_accel", 2.0)
        desired_velocity: float = lane.max_vel

        # Calculate the minimum safe stopping distance.
        safe_distance: float = max(
            60, (velocity**2) / (2 * deceleration) if deceleration > 0 else 60
        )

        # Check if the traffic light for this lane is green.
        light_green: bool = self.__check_if_green(lane, junction)

        # Determine distance to the car ahead.
        distance_to_car_ahead: float = self.__distance_to_car_ahead(lane, car)

        # If the light is red and the car is near the junction, set desired velocity to 0.
        if not light_green and 5 <= dist < 40:
            desired_velocity = 0
        # If a car ahead is too close, reduce desired velocity.
        elif distance_to_car_ahead < safe_distance:
            fraction: float = distance_to_car_ahead / safe_distance
            desired_velocity = min(desired_velocity, velocity * fraction)

        # Calculate the acceleration needed to reach the desired velocity.
        raw_acc: float = (desired_velocity - velocity) / self.__time_step
        # Clamp acceleration within deceleration and acceleration limits.
        acc: float = max(-deceleration, min(raw_acc, acceleration_limit))

        # Update the velocity and compute displacement.
        new_velocity: float = velocity + acc * self.__time_step
        displacement: float = (velocity * self.__time_step) + (
            0.5 * acc * (self.__time_step**2)
        )
        new_dist: float = dist - displacement

        # Update the car's state.
        car.set_velocity(new_velocity)
        car.set_dist(new_dist)

        # If the car reaches the junction, try to transfer it to its destination lane.
        if new_dist <= 0:
            dest_lane: Lane = random.choice(junction.get_lanes_by_ids([car.get_dest()]))

            if dest_lane and dest_lane.get_id() != lane.get_id():
                cur_road: Road = junction.get_road_by_id(lane.get_id() // 10)
                dest_road: Road = junction.get_road_by_id(dest_lane.get_id() // 10)
                for road in junction.get_roads():
                    if (road.get_from_side().value - cur_road.get_from_side().value) % 4 == 2:
                        cur_parr_road: Road = road
                    elif (road.get_from_side().value - dest_road.get_from_side().value) % 4 == 2:
                        dest_parr_road: Road = road

                turn_type = (dest_road.get_from_side().value - cur_road.get_from_side().value) % 4
                if turn_type == 1:  # Right Turn
                    shift = (len(cur_road.get_lanes()) + len(cur_parr_road.get_lanes())) * self.LANE_WIDTH + 20
                    car.set_dist(-shift)
                    lane.remove_car(car)
                    dest_lane.add_car(car)
                elif turn_type == 3:  # Left Turn
                    dist_to_shift = (len(dest_parr_road.get_lanes())) * self.LANE_WIDTH + 20
                    dist_to_end_road = (len(dest_road.get_lanes()) + len(dest_parr_road.get_lanes())) * self.LANE_WIDTH + 20
                    shift = (len(cur_road.get_lanes())) * self.LANE_WIDTH
                    if new_dist <= -dist_to_shift:
                        car.set_dist(-shift)
                        lane.remove_car(car)
                        dest_lane.add_car(car)

        # Remove the car if it has moved beyond the exit threshold.
        exit_threshold: float = (
            -2 * lane.LENGTH
        )  # Example threshold for leaving the simulation.
        if new_dist < exit_threshold:
            lane.remove_car(car)

    def __does_collide(self, car1: Car, car2: Car) -> bool:
        road_dest_1_id: int = (car1.dest // 10) % 10
        road_dest_2_id: int = (car2.dest // 10) % 10

        road_origin_1_id: int = (car1.origin // 10) % 10
        road_origin_2_id: int = (car2.origin // 10) % 10

        road_dest_1: Road = self.__junctions[0].get_road_by_id(int(str(self.__junctions[0].id) + str(road_dest_1_id)))
        road_dest_2: Road = self.__junctions[0].get_road_by_id(int(str(self.__junctions[0].id) + str(road_dest_2_id)))

        if road_origin_1_id != road_origin_2_id:
            # Check if roads perpendicular
            if (road_dest_1.get_to_side().value + road_dest_2.get_to_side().value) % 2 == 1:
                return True

            # Check if going to the same road but not from the same origin
            if road_dest_1_id == road_dest_2_id :
                return True

        return False

    def __is_car_in_junction(self, car: Car) -> bool:
        junction_width: float = len(self.__junctions[0].get_road_by_id(
            int(str(self.__junctions[0].id) + str(1))).get_lanes()) + \
            + len(self.__junctions[0].get_road_by_id(int(str(self.__junctions[0].id) + str(2))).get_lanes()) + 20

        junction_height: float = len(self.__junctions[0].get_road_by_id(
            int(str(self.__junctions[0].id) + str(3))).get_lanes()) + \
            + len(self.__junctions[0].get_road_by_id(int(str(self.__junctions[0].id) + str(4))).get_lanes()) + 20

        junction_size = min(junction_width, junction_height)

        return -junction_size < car.dist < 0

    def __check_cars_collision(self) -> int:
        """
        Returns how many collisions happen
        """
        cars: List[Car] = self.get_junctions()[0].get_all_cars()
        collision_count: int = 0

        for car1 in cars:
            for car2 in cars:
                if self.__is_car_in_junction(car1) and self.__is_car_in_junction(car2):
                    if self.__does_collide(car1, car2):
                        collision_count += 1

        return collision_count // 2

    @staticmethod
    def __distance_to_car_ahead(lane: Lane, this_car: Car) -> float:
        """
        Computes the gap (in distance) to the nearest car ahead in the same lane.

        Args:
            lane (Lane): The lane to check.
            this_car (Car): The car for which the gap is computed.

        Returns:
            float: The distance gap to the nearest car ahead, or math.inf if no car is ahead.
        """
        this_dist: float = this_car.get_dist()
        # Identify cars that are physically ahead (with a smaller distance value).
        cars_ahead = [
            c for c in lane.get_cars() if c.get_dist() < this_dist and c != this_car
        ]
        if not cars_ahead:
            return math.inf
        # Return the smallest gap.
        return min(this_dist - c.get_dist() for c in cars_ahead)

    @staticmethod
    def __check_if_green(lane: Lane, junction: Junction) -> bool:
        """
        Checks if any traffic light controlling the given lane is green.

        Args:
            lane (Lane): The lane to check.
            junction (Junction): The junction that contains the traffic lights.

        Returns:
            bool: True if any traffic light for the lane is green, False otherwise.
        """
        for tl in junction.get_traffic_lights():
            if lane.get_id() in tl.get_origins() and tl.get_state() is True and not tl.get_is_yellow():
                return True
        return False

    def __update_traffic_lights(self) -> None:
        """
        Updates the traffic lights in all junctions.

        NOTE: This is a naive time-based toggler for demonstration purposes.
        The actual toggling mechanism is either time-based or random, as commented out.
        """
        with self.__lock:
            if self.has_yellow:
                return
            prev_tls = self.__junctions[0].get_traffic_lights()
            self.__junctions[0].set_traffic_lights(Client.get_traffic_lights_states())
            cur_tls = self.__junctions[0].get_traffic_lights()
            for prev_tl in prev_tls:
                for cur_tl in cur_tls:
                    if cur_tl.get_id() == prev_tl.get_id() and cur_tl.get_state() != prev_tl.get_state():
                        cur_tl.set_is_yellow(True)
                        if not self.has_yellow:
                            self.has_yellow = True
                            wait_time = self.__time_step * 30 * 2.5

                            def change_all_yellow():
                                self.has_yellow = False
                                for tl in self.__junctions[0].get_traffic_lights():
                                    if tl.get_is_yellow():
                                        tl.set_is_yellow(False)

                            timer = threading.Timer(wait_time, change_all_yellow)
                            timer.start()

    def __gen_cars(self) -> None:
        """
        Generates cars for each lane based on the lane's car creation rate.
        Approximately one car is generated every (1/rate) seconds on average.
        """
        with self.__lock:
            for junction in self.__junctions:
                for road in junction.get_roads():
                    for lane in road.get_lanes():
                        rate: float = lane.get_car_creation()  # Cars per second.
                        if rate > 0:
                            num_cars: int = np.random.poisson(rate)
                            for _ in range(num_cars):
                                # Generate a random speed within a range based on lane's maximum velocity.
                                speed: float = uniform(
                                    lane.max_vel * 0.5, lane.max_vel * 1.2
                                )
                                car_id: int = self.CAR_ID
                                self.CAR_ID += 1
                                new_car: Car = Car(
                                    car_id=car_id,
                                    dist=lane.LENGTH,
                                    velocity=speed,
                                    dest=random.choice(junction.get_traffic_light_by_lane_id(lane_id=lane.get_id()).get_destinations()),
                                    car_type="CAR",
                                    origin=lane.get_id()
                                )
                                lane.add_car(new_car)

    def stop(self) -> None:
        """
        Stops the simulation thread.
        """
        self.__stop_event.set()
        if self.__thread:
            self.__thread.join()
            self.__thread = None

    def pause(self) -> None:
        """
        Pauses the simulation by stopping the simulation thread.
        """
        self.stop()

    def resume(self) -> None:
        """
        Resumes the simulation if it is not already running.
        """
        self.start()

    def get_junctions(self) -> List[Junction]:
        """
        Returns the list of junctions in the simulation.

        Returns:
            List[Junction]: The junctions managed by the simulation.
        """
        return self.__junctions

    def get_random_directions(self, lane_index: int, lane_amount: int = 3) -> int:
        """
        Determines a random driving direction for a car based on its lane index.

        The function computes possible directions, filters them based on traffic light paths,
        and then returns one random valid direction.

        Args:
            lane_index (int): The identifier for the lane (includes road info).
            lane_amount (int): The total number of lanes on the road (default is 3).

        Returns:
            int: The selected driving direction.
        """
        road_id: int = lane_index // 10 % 10
        options: List[int] = self.all_car_directions(lane_index, lane_amount)
        options = self.remove_no_lights_paths(road_id, options)
        if len(options) == 0:
            return road_id
        return options[random.randint(0, len(options) - 1)]

    def remove_no_lights_paths(
        self, road_id: int, options: List[int], junction_id: int = 1
    ) -> List[int]:
        """
        Filters out driving direction options that do not have corresponding traffic light paths.

        Args:
            road_id (int): The current road identifier.
            options (List[int]): List of potential direction options.
            junction_id (int): The index of the junction in the list to use (default is 1).

        Returns:
            List[int]: A filtered list of valid driving directions.
        """
        lights = self.__junctions[junction_id].traffic_lights
        valid_options: List[int] = []
        for light in lights:
            if road_id in light.get_origins():
                outputs = light.get_destinations()
                for option in options:
                    if option in outputs:
                        valid_options.append(option)
        return valid_options

    @staticmethod
    def all_car_directions(lane_index: int, lane_amount: int = 3) -> List[int]:
        """
        Creates all possible driving directions for a car based on its lane index.

        Args:
            lane_index (int): The full identifier of the lane (including road id).
            lane_amount (int): The number of lanes on the road (default is 3).

        Returns:
            List[int]: A list of possible driving directions.
        """
        # Transformation maps for left and right turns.
        l_transform: List[int] = [3, 2, 0, 1]
        r_transform: List[int] = [2, 3, 1, 0]
        road_id: int = lane_index // 10 % 10
        lane_id: int = lane_index % 10
        division_lane: int = lane_amount // 3
        options: List[int] = []
        # Middle lanes: go straight.
        if division_lane - 1 <= lane_id < 1 + 2 * division_lane:
            options.append(road_id)
        # Left lanes: can turn left (and potentially U-turn).
        if lane_id < division_lane:
            options.append(l_transform[road_id])
            # TODO: Review ambiguous behavior for U-turn addition.
            if road_id % 2 == 0:
                options.append(road_id + 1)
            else:
                options.append(road_id - 1)
        # Right lanes: can turn right.
        if lane_id >= 2 * division_lane:
            options.append(r_transform[road_id])
        return options

    def __set_all_lights_red(self) -> None:
        """
        Set all traffic lights in the simulation to red (local state).
        """
        with self.__lock:
            for junction in self.__junctions:
                for tl in junction.get_traffic_lights():
                    tl.red()
