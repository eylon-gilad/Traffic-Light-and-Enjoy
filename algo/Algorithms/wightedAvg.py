import logging
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction


class wightedAvg(BaseAlgorithm):
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
        # Tracks waiting times for each traffic-light combination:
        # self.cars_time_tracker[(light_id_tuple)][car_id] = [time_waiting, start_time]
        self.cars_time_tracker: Dict[Tuple[int, ...], Dict[int, List[float]]] = (
            defaultdict(dict)
        )
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(
            junction
        ).get_combinations()
        for comb in self.combinations:
            self.cars_time_tracker[comb] = {}
        # Holds the final cost for each combination
        self.costs: Dict[Tuple[int, ...], float] = {}

    def start(self) -> None:
        """
        Continuously run the cost-based traffic control logic.
        Chooses the combination with the highest cost and sets the corresponding traffic lights to green.
        """
        while True:
            try:
                self.remove_unrelevant_cars()
                self.set_cars_time()
                self.calc_costs()
                logging.info(self.cars_time_tracker)

                if self.costs:
                    best_combination = max(self.costs, key=self.costs.get)
                    for traffic_light in self.junction.get_traffic_lights():
                        if traffic_light.get_id() in best_combination:
                            traffic_light.green()
                        else:
                            traffic_light.red()
            except Exception as e:
                logging.error(f"Error in ExpCarsOnTimeController loop: {e}")
            # Pause briefly to reduce CPU usage
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
            logging.error(f"Failed gathering existing cars: {e}")
            return

        for comb in self.cars_time_tracker:
            self.cars_time_tracker[comb] = {
                car_id: info
                for car_id, info in self.cars_time_tracker[comb].items()
                if car_id in existing_car_ids
            }
        logging.debug("Updated car tracker after removal.")

    def calc_costs(self) -> None:
        """
        Calculate a cost function for each traffic-light combination based on the average waiting time.
        """
        self.costs.clear()
        for combination, car_dict in self.cars_time_tracker.items():
            if car_dict:
                waiting_times = [info[0] for info in car_dict.values()]
                avg_time = sum(waiting_times) / len(waiting_times)
                # Formula: cost = (number of cars + 1)^(average waiting time + 1)
                self.costs[combination] = (len(car_dict) + 1) ** (avg_time + 1)

    def set_cars_time(self) -> None:
        """
        Update the waiting time for each car on each traffic-light combination.
        """
        current_time = time.time()  # Cache current time once per iteration
        for comb in self.combinations:
            for traffic_light_id in comb:
                tl = self.junction.get_traffic_light_by_id(traffic_light_id)
                origins = tl.get_origins()
                road_id = origins[0] // 10
                road = self.junction.get_road_by_id(road_id)
                # Track waiting times for cars on lanes leading to this traffic light
                for lane in road.get_lanes_by_ids(origins):
                    for car in lane.cars:
                        car_id = car.get_id()
                        if car_id not in self.cars_time_tracker[comb]:
                            # Initialize waiting time and start time
                            self.cars_time_tracker[comb][car_id] = [0.0, current_time]
                        else:
                            start_time = self.cars_time_tracker[comb][car_id][1]
                            self.cars_time_tracker[comb][car_id][0] = (
                                current_time - start_time
                            )
