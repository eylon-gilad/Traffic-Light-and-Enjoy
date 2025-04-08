import logging
import time
from typing import List, Dict, Tuple

from algo.Algorithms.BaseAlgorithm import BaseAlgorithm
from utils.Junction import Junction
from utils.TrafficLight import TrafficLight

from algo.TrafficLightsCombinator import TrafficLightsCombinator


class RoundRobinController(BaseAlgorithm):
    """
    A simple round-robin traffic lights controller.
    Cycles through all traffic lights in a fixed interval.
    """

    def __init__(self, junction: Junction) -> None:
        """
        :param junction: The Junction object to control.
        """
        super().__init__(junction)
        self.current_traffic_light_id: int = 100
        self.time_interval: float = 1  # Interval in seconds
        self.combinations: List[Tuple[int, ...]] = TrafficLightsCombinator(
            junction
        ).get_combinations()

    def start(self) -> None:
        """
        Continuously cycle through traffic lights, turning them on one by one.
        """
        is_first_time = True
        i = 0
        while True:
            try:
                if self.junction is None:
                    time.sleep(0.1)
                    continue

                if is_first_time:
                    # Initialize to the first traffic light's ID
                    all_lights = self.junction.get_traffic_lights()
                    if not all_lights:
                        logging.warning("No traffic lights available in junction.")
                        time.sleep(0.1)
                        continue
                    self.current_traffic_light_id = all_lights[0].id
                    is_first_time = False

                lights: List[TrafficLight] = self.junction.get_traffic_lights()
                logging.debug(f"Junction: {self.junction}")
                for light in lights:
                    if light.id in self.combinations[i % len(self.combinations)]:
                        light.state = True
                    else:
                        light.state = False

                self.current_traffic_light_id = self.get_next_traffic_light_id()
                time.sleep(self.time_interval)
                i += 1
            except Exception as e:
                logging.error(f"Error in RoundRobinController loop: {e}")
                # Keep running despite errors

    def get_next_traffic_light_id(self) -> int:
        """
        Determine the ID of the next traffic light in the round-robin cycle.
        """
        lights: List[TrafficLight] = self.junction.get_traffic_lights()

        for i, light in enumerate(lights):
            if light.id == self.current_traffic_light_id:
                return lights[(i + 1) % len(lights)].id

        # TODO: Potential edge case if the current light ID isn't found in the list
        # For now, default to the first in the list if something goes wrong.
        if lights:
            return lights[0].id
        return self.current_traffic_light_id
