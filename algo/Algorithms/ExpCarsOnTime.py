import logging
import time
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Road import Road


class ExpCarsOnTimeController(BaseAlgorithm):
    """
    An experimental controller that calculates a cost function based on
    how long cars have been waiting on each possible traffic-light combination.
    """

    def __init__(self, junction: Junction) -> None:
        """
        Initialize the experimental algorithm with a given junction.

        :param junction: The Junction object to manage.
        """
        super().__init__(junction)
        self.epsilon: float = 0.01
        # Tracks how long each car has been on each combination of traffic lights:
        # self.cars_time_tracker[ (light_id_tuple) ][car_id ] = [time_waiting, start_time]
        self.cars_time_tracker: Dict[Tuple[int, ...], Dict[int, List[float]]] = defaultdict(dict)
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(junction).get_combinations()
        for comb in self.combinations:
            self.cars_time_tracker[comb] = defaultdict()

        # Will hold the final cost for each combination
        self.costs: Dict[Tuple[int, ...], List[float]] = {}

    def start(self) -> None:
        """
        Continuously run the cost-based traffic control logic.
        Chooses the combination of lights that yields the highest cost
        (i.e., presumably the largest waiting times) and sets those lights to green.
        """
        while True:
            print(self.combinations)

            try:
                self.remove_unrelevant_cars()
                self.set_cars_time()
                self.calc_costs()
                logging.info(self.cars_time_tracker)
                if self.costs:
                    # Determine which combination has the highest cost
                    # Then set those traffic lights to green, and others to red
                    traffic_lights_max_cost_ids = max(self.costs, key=self.costs.get)
                    for traffic_light in self.junction.get_traffic_lights():
                        if traffic_light.get_id() in traffic_lights_max_cost_ids:
                            print(traffic_light.get_id())
                            traffic_light.green()
                        else:
                            traffic_light.red()
            except Exception as e:
                # This is critical logic, so we log the error but keep running
                logging.error(f"Error in ExpCarsOnTimeController loop: {e}")

    def remove_unrelevant_cars(self) -> None:
        """
        Remove cars from the tracking dictionary if they no longer exist in the junction.
        """
        # Accumulate IDs of cars that no longer exist.
        to_delete = []
        try:
            roads: List[Road] = self.junction.get_roads()
            lanes = np.concatenate([road.get_lanes() for road in roads])
            cars = np.concatenate([lane.get_cars() for lane in lanes])
            existing_car_ids = [car.get_id() for car in cars]
        except Exception as e:
            logging.error(f"Failed gathering existing cars: {e}")
            return

        for combination in self.cars_time_tracker:
            for car_id in self.cars_time_tracker[combination]:
                if car_id not in existing_car_ids:
                    to_delete.append(car_id)

        # Delete outdated references
        for combination in self.cars_time_tracker:
            for outdated_id in to_delete:
                if outdated_id in self.cars_time_tracker[combination]:
                    del self.cars_time_tracker[combination][outdated_id]

        logging.debug(f"Removed car IDs: {to_delete}")

    def calc_costs(self) -> None:
        """
        Calculate a cost function for each traffic-light combination.
        The cost function is based on the average waiting time of cars in that combination.
        """
        self.costs.clear()
        for combination, car_dict in self.cars_time_tracker.items():
            time_sum: float = 0.0
            count_cars: int = 0
            for car_id, time_info in car_dict.items():
                time_waiting = time_info[0]
                time_sum += time_waiting
                count_cars += 1
            if count_cars != 0:
                # Original formula: cost = (count_cars+1)^(avg_time)
                avg_time = time_sum / count_cars
                self.costs[combination] = [(count_cars + 1) ** (avg_time+1)]

    def set_cars_time(self) -> None:
        """
        Update how long each car has been present on each traffic-light combination.
        """
        for comb in self.combinations:
            for traffic_light_id in comb:
                origins: List[int] = self.junction.get_traffic_light_by_id(traffic_light_id).get_origins()
                road_id: int = origins[0] // 10
                road: Road = self.junction.get_road_by_id(road_id)
                # For each lane that leads to this traffic light, track waiting times
                for lane in road.get_lanes_by_ids(origins):
                    for car in lane.cars:
                        if car.get_id() not in self.cars_time_tracker[comb]:
                            # Store [delta_time, start_time]
                            self.cars_time_tracker[comb][car.get_id()] = [0.0, time.time()]
                        else:
                            _, start_time = self.cars_time_tracker[comb][car.get_id()]
                            self.cars_time_tracker[comb][car.get_id()] = [
                                time.time() - start_time,
                                start_time,
                            ]
