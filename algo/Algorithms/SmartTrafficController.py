import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Road import Road


class SmartTrafficController(BaseAlgorithm):
    """
    An advanced traffic light controller that adaptively selects the best phase (combination of green lights)
    based on a predictive, fairness-aware scoring algorithm. It combines real-time vehicle data with a
    fairness mechanism to minimize overall congestion and prevent starvation of any direction.
    """

    def __init__(self,
                 junction: Junction,
                 alpha: float = 1.0,
                 beta: float = 5.0,
                 gamma: float = 1.0,
                 hysteresis_threshold: float = 10.0) -> None:
        """
        Initialize the SmartTrafficController with parameters for the scoring weights.

        :param junction: The Junction object this controller manages.
        :param alpha: Weight for total waiting time in the score calculation.
        :param beta: Weight for number of cars (traffic volume) in the score.
        :param gamma: Weight for fairness (time since last served) in the score.
        :param hysteresis_threshold: Minimum score difference required to switch phases.
        """
        super().__init__(junction)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.hysteresis_threshold = hysteresis_threshold

        # All possible non-conflicting traffic light combinations (phases) for this junction.
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(junction).get_combinations()

        # Data structure to track each car's waiting time for each combination.
        # Format: { combination: { car_id: [waiting_time, start_time] } }
        self.car_wait_times: Dict[Tuple[int, ...], Dict[int, List[float]]] = defaultdict(dict)
        for comb in self.combinations:
            self.car_wait_times[comb] = {}

        # Track the last time each combination was given green (for fairness calculation).
        # Initialize with the current time so that initially all phases are considered recently served.
        current_time = time.time()
        self.last_served_time: Dict[Tuple[int, ...], float] = {comb: current_time for comb in self.combinations}

        # Keep track of which combination is currently active (green). None at start (no phase chosen yet).
        self.current_combination: Tuple[int, ...] = None

    def start(self) -> None:
        """
        Main control loop that continuously evaluates traffic conditions and switches lights accordingly.
        """
        while True:
            try:
                # Update waiting times for all cars and remove any that have left the junction.
                self._update_car_wait_times()
                # Compute the priority score for each possible traffic light combination.
                scores = self._compute_phase_scores()
                if scores:
                    # Determine the best phase based on the computed scores.
                    best_combination = max(scores, key=scores.get)
                    best_score = scores[best_combination]

                    # Apply hysteresis: Only switch to a new phase if it's significantly better.
                    if self.current_combination is not None:
                        current_score = scores.get(self.current_combination, 0.0)
                        # If the currently active phase is not much worse than the best, continue it to avoid flicker.
                        if best_combination != self.current_combination and (
                                best_score - current_score) < self.hysteresis_threshold:
                            best_combination = self.current_combination
                            best_score = current_score  # (score unchanged for logging or reference)

                    # Activate the lights for the chosen combination and deactivate others.
                    for tl in self.junction.get_traffic_lights():
                        if tl.get_id() in best_combination:
                            tl.green()  # turn this traffic light green
                        else:
                            tl.red()  # ensure other lights are red
                    # Update the record of which combination is now active.
                    if best_combination != self.current_combination:
                        logging.info(f"Switching to combination {best_combination} with score {best_score:.2f}")
                    self.current_combination = best_combination
                    # Reset the last served time for this combination to now (it is being served at this moment).
                    self.last_served_time[best_combination] = time.time()
            except Exception as e:
                logging.error(f"Error in SmartTrafficController loop: {e}")
            # Pause briefly to avoid excessive CPU usage (and to simulate a time step).
            time.sleep(0.1)

    def _update_car_wait_times(self) -> None:
        """
        Refresh the waiting time data for all cars in the junction.
        - Adds new cars to the tracker with start time.
        - Updates waiting times for existing cars.
        - Removes entries for cars that have left the junction.
        """
        current_time = time.time()
        try:
            # Get all current cars in the junction across all roads and lanes.
            roads = self.junction.get_roads()
            lanes = [lane for road in roads for lane in road.get_lanes()]
            current_car_ids = {car.get_id() for lane in lanes for car in lane.get_cars()}
        except Exception as e:
            logging.error(f"Failed to gather current cars: {e}")
            return

        # Remove cars from tracking if they are no longer in the junction.
        for comb, car_dict in self.car_wait_times.items():
            # Keep only cars whose IDs are still present in the junction.
            self.car_wait_times[comb] = {cid: info for cid, info in car_dict.items() if cid in current_car_ids}

        # Update or initialize waiting time for each car currently in each combination's lanes.
        for comb in self.combinations:
            # For each traffic light in this combination, get all cars approaching that light.
            for tl_id in comb:
                tl = self.junction.get_traffic_light_by_id(tl_id)
                origin_lane_ids = tl.get_origins()  # lanes from which cars go through this traffic light
                road_id = origin_lane_ids[0] // 10  # derive the road id from the lane (assuming lane ID encoding)
                road: Road = self.junction.get_road_by_id(road_id)
                # Iterate through each relevant lane feeding this traffic light.
                for lane in road.get_lanes_by_ids(origin_lane_ids):
                    for car in lane.get_cars():
                        cid = car.get_id()
                        if cid not in self.car_wait_times[comb]:
                            # New car: start tracking its waiting time from now.
                            self.car_wait_times[comb][cid] = [0.0, current_time]  # [waiting_time, start_time]
                        else:
                            # Existing car: update its waiting time = current time - start time.
                            start_time = self.car_wait_times[comb][cid][1]
                            self.car_wait_times[comb][cid][0] = current_time - start_time

    def _compute_phase_scores(self) -> Dict[Tuple[int, ...], float]:
        """
        Calculate a priority score for each traffic light combination (phase).
        Returns a dictionary of scores for each combination.
        """
        scores: Dict[Tuple[int, ...], float] = {}
        current_time = time.time()
        for comb, car_dict in self.car_wait_times.items():
            # Calculate total waiting time and vehicle count for this phase.
            total_wait = sum(info[0] for info in car_dict.values())
            vehicle_count = len(car_dict)
            if vehicle_count == 0:
                # If no cars are present, the score is 0 (no immediate demand).
                scores[comb] = 0.0
            else:
                # Fairness component: time since this phase was last green.
                time_since_green = current_time - self.last_served_time.get(comb, current_time)
                fairness_bonus = self.gamma * time_since_green
                # Composite score = alpha * total_wait + beta * vehicle_count + fairness term.
                scores[comb] = (self.alpha * total_wait) + (self.beta * vehicle_count) + fairness_bonus
        return scores
