import logging
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Road import Road


class DynamicWeightedTrafficController(BaseAlgorithm):
    """
    A dynamic traffic light controller that selects the optimal combination
    of green lights based on a weighted score of total waiting time and the
    number of waiting cars. Incorporates hysteresis to prevent unnecessary
    rapid switching.
    """

    def __init__(
        self,
        junction: Junction,
        alpha: float = 1.0,
        beta: float = 5.0,
        hysteresis_threshold: float = 10.0,
    ) -> None:
        """
        Initialize the controller.

        :param junction: The Junction object to manage.
        :param alpha: Weight factor for total waiting time.
        :param beta: Weight factor for the number of cars waiting.
        :param hysteresis_threshold: Minimum score difference required to switch combinations.
        """
        super().__init__(junction)
        self.alpha = alpha
        self.beta = beta
        self.hysteresis_threshold = hysteresis_threshold

        # Tracks waiting times for each traffic-light combination.
        # Format: self.cars_time_tracker[(light_id_tuple)][car_id] = [waiting_time, start_time]
        self.cars_time_tracker: Dict[Tuple[int, ...], Dict[int, List[float]]] = defaultdict(dict)
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(junction).get_combinations()
        for comb in self.combinations:
            self.cars_time_tracker[comb] = {}

        # Holds the computed score for each combination.
        self.costs: Dict[Tuple[int, ...], float] = {}
        self.current_combination: Tuple[int, ...] = None

    def start(self) -> None:
        """
        Continuously run the traffic control loop, updating the traffic lights
        based on the combination with the highest weighted score.
        """
        while True:
            try:
                self.remove_unrelevant_cars()
                self.set_cars_time()
                self.calc_costs()

                if self.costs:
                    best_combination = max(self.costs, key=self.costs.get)
                    best_score = self.costs[best_combination]

                    # Use hysteresis to avoid rapid switching:
                    if self.current_combination is not None:
                        current_score = self.costs.get(self.current_combination, 0)
                        if (best_combination == self.current_combination or
                            (best_score - current_score) < self.hysteresis_threshold):
                            best_combination = self.current_combination

                    # Update traffic lights based on the selected combination.
                    for traffic_light in self.junction.get_traffic_lights():
                        if traffic_light.get_id() in best_combination:
                            traffic_light.green()
                        else:
                            traffic_light.red()

                    self.current_combination = best_combination

            except Exception as e:
                logging.error(f"Error in DynamicWeightedTrafficController loop: {e}")

            # Brief pause to reduce CPU usage.
            time.sleep(0.1)

    def remove_unrelevant_cars(self) -> None:
        """
        Remove cars from the tracking dictionary if they no longer exist in the junction.
        """
        try:
            roads = self.junction.get_roads()
            lanes = [lane for road in roads for lane in road.get_lanes()]
            cars = [car for lane in lanes for car in lane.get_cars()]
            existing_car_ids = {car.get_id() for car in cars}
        except Exception as e:
            logging.error(f"Error gathering existing cars: {e}")
            return

        for comb in self.cars_time_tracker:
            self.cars_time_tracker[comb] = {
                car_id: info
                for car_id, info in self.cars_time_tracker[comb].items()
                if car_id in existing_car_ids
            }

    def calc_costs(self) -> None:
        """
        Calculate the weighted score for each traffic-light combination.
        Score = alpha * (total waiting time) + beta * (number of waiting cars).
        """
        self.costs.clear()
        for combination, car_dict in self.cars_time_tracker.items():
            if car_dict:
                total_waiting = sum(info[0] for info in car_dict.values())
                count_cars = len(car_dict)
                score = self.alpha * total_waiting + self.beta * count_cars
                self.costs[combination] = score
            else:
                self.costs[combination] = 0.0

    def set_cars_time(self) -> None:
        """
        Update waiting times for each car on each traffic-light combination.
        """
        current_time = time.time()
        for comb in self.combinations:
            for traffic_light_id in comb:
                tl = self.junction.get_traffic_light_by_id(traffic_light_id)
                origins = tl.get_origins()
                road_id = origins[0] // 10
                road = self.junction.get_road_by_id(road_id)
                for lane in road.get_lanes_by_ids(origins):
                    for car in lane.cars:
                        car_id = car.get_id()
                        if car_id not in self.cars_time_tracker[comb]:
                            # Initialize waiting time and timestamp.
                            self.cars_time_tracker[comb][car_id] = [0.0, current_time]
                        else:
                            start_time = self.cars_time_tracker[comb][car_id][1]
                            self.cars_time_tracker[comb][car_id][0] = current_time - start_time
