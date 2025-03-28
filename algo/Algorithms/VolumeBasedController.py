import logging
import time
from typing import Dict, List, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Road import Road


class VolumeBasedController(BaseAlgorithm):
    """
    VolumeBasedController adjusts traffic lights based on the total number of cars waiting
    on the roads feeding into each traffic-light combination. For each combination, the score is
    calculated as the sum of the car counts across the associated roads. The combination with the highest
    score is activated, which aims to ease congestion on busier roads.
    """

    def __init__(self, junction: Junction) -> None:
        """
        Initialize the controller with a given junction.

        :param junction: The Junction object that contains roads and traffic lights.
        """
        super().__init__(junction)
        # Retrieve possible combinations of traffic lights from the combinator
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(junction).get_combinations()
        # Dictionary to store the computed car volume score for each combination
        self.scores: Dict[Tuple[int, ...], int] = {}

    def start(self) -> None:
        """
        Main loop that periodically computes road volumes and updates the traffic light patterns.
        """
        while True:
            try:
                self.compute_scores()
                self.apply_best_combination()
            except Exception as e:
                logging.error(f"Error in VolumeBasedController loop: {e}")
            # Pause briefly to prevent high CPU usage
            time.sleep(0.1)

    def compute_scores(self) -> None:
        """
        Compute a score for each traffic-light combination based on the total number of cars
        present on the roads associated with that combination.
        """
        self.scores.clear()
        for comb in self.combinations:
            score = 0
            seen_roads = set()  # To avoid counting the same road multiple times
            for traffic_light_id in comb:
                tl = self.junction.get_traffic_light_by_id(traffic_light_id)
                origins = tl.get_origins()  # List of origin lane IDs associated with this traffic light
                road_id = origins[0] // 10  # Deduce road id from the first origin
                if road_id not in seen_roads:
                    road: Road = self.junction.get_road_by_id(road_id)
                    # Get the lanes that feed into the traffic light based on origins
                    lanes = road.get_lanes_by_ids(origins)
                    for lane in lanes:
                        # Retrieve the list of cars (using get_cars() if available)
                        cars = lane.get_cars() if hasattr(lane, "get_cars") else lane.cars
                        score += len(cars)
                    seen_roads.add(road_id)
            self.scores[comb] = score

    def apply_best_combination(self) -> None:
        """
        Select the traffic-light combination with the highest car volume score and set those lights to green.
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
