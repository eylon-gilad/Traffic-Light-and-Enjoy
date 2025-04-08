import logging
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Road import Road


class AdaptiveFlowController(BaseAlgorithm):
    """
    AdaptiveFlowController dynamically adjusts traffic light patterns by computing a priority score for each
    traffic-light combination. The score is based on both the average waiting time of vehicles and the number
    of vehicles (density) present. An exponential decay is used to smooth waiting time updates, leading to more
    stable decisions and potentially faster throughput.
    """

    def __init__(self, junction: Junction) -> None:
        super().__init__(junction)
        # For each combination, track car statuses:
        # self.car_status[combination][car_id] = (current_waiting_time, start_time)
        self.car_status: Dict[Tuple[int, ...], Dict[int, Tuple[float, float]]] = (
            defaultdict(dict)
        )
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(
            junction
        ).get_combinations()
        for comb in self.combinations:
            self.car_status[comb] = {}
        # Will hold the computed score for each combination
        self.scores: Dict[Tuple[int, ...], float] = {}

        # Parameters for scoring
        self.wait_weight: float = 1.2  # Weight for average waiting time
        self.density_weight: float = 1.0  # Weight for the number of cars
        self.decay_factor: float = (
            0.8  # Exponential decay for smoothing waiting time updates
        )

    def start(self) -> None:
        """
        Main control loop:
         - Update the status of each car in relevant lanes.
         - Compute scores based on waiting times and vehicle density.
         - Activate the best traffic light combination.
        """
        while True:
            try:
                self.update_car_status()
                self.compute_scores()
                self.apply_best_pattern()
            except Exception as e:
                logging.error(f"Error in AdaptiveFlowController loop: {e}")
            # Brief pause to avoid high CPU usage
            time.sleep(0.1)

    def update_car_status(self) -> None:
        """
        Update the waiting time for each car in each traffic light combination.
        Also removes cars that are no longer present in the junction.
        """
        try:
            roads = self.junction.get_roads()
            lanes = [lane for road in roads for lane in road.get_lanes()]
            current_car_ids = {
                car.get_id() for lane in lanes for car in lane.get_cars()
            }
        except Exception as e:
            logging.error(f"Error fetching current cars: {e}")
            return

        current_time = time.time()
        for comb in self.combinations:
            # Remove cars that no longer exist
            self.car_status[comb] = {
                cid: (wait, start)
                for cid, (wait, start) in self.car_status[comb].items()
                if cid in current_car_ids
            }
            # For each traffic light in the combination, update car waiting times
            for tl_id in comb:
                tl = self.junction.get_traffic_light_by_id(tl_id)
                origins = tl.get_origins()
                road_id = origins[0] // 10
                road = self.junction.get_road_by_id(road_id)
                for lane in road.get_lanes_by_ids(origins):
                    for car in lane.cars:
                        cid = car.get_id()
                        if cid in self.car_status[comb]:
                            prev_wait, start_time = self.car_status[comb][cid]
                            new_wait = current_time - start_time
                            # Smooth waiting time with an exponential decay
                            updated_wait = (
                                self.decay_factor * prev_wait
                                + (1 - self.decay_factor) * new_wait
                            )
                            self.car_status[comb][cid] = (updated_wait, start_time)
                        else:
                            # New car: initialize waiting time
                            self.car_status[comb][cid] = (0.0, current_time)

    def compute_scores(self) -> None:
        """
        For each traffic-light combination, compute a score based on a weighted sum of
        the average waiting time and the density (number of vehicles) present.
        """
        self.scores.clear()
        for comb, car_data in self.car_status.items():
            if not car_data:
                self.scores[comb] = 0.0
                continue
            total_wait = sum(wait for wait, _ in car_data.values())
            avg_wait = total_wait / len(car_data)
            density = len(car_data)
            # Score calculation: weighted sum of average waiting time and car density
            score = self.wait_weight * avg_wait + self.density_weight * density
            self.scores[comb] = score

    def apply_best_pattern(self) -> None:
        """
        Identify the traffic-light combination with the highest score and set those lights to green.
        All other traffic lights are set to red.
        """
        if not self.scores:
            return
        best_combination = max(self.scores, key=self.scores.get)
        for traffic_light in self.junction.get_traffic_lights():
            if traffic_light.get_id() in best_combination:
                traffic_light.green()
            else:
                traffic_light.red()
