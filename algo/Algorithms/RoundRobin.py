import time
from utils import Junction, TrafficLight
from typing import List
from algo.Algorithms.BaseAlgorithm import BaseAlgorithm


class RoundRobinController(BaseAlgorithm):
    """
    Controls traffic lights in a junction
    """

    def __init__(self, junction: Junction):
        """
        Constructor
        :param junction: object that represents a junction
        """

        super().__init__(junction)
        self.current_traffic_light_id = 100
        self.time_interval = 5

    def start(self):
        """
        Starts the algorithm
        """
        is_first_time = True
        while True:
            if self.junction is None:
                continue

            if is_first_time:
                self.current_traffic_light_id = self.junction.get_traffic_lights()[0].id
                is_first_time = False

            lights: List[TrafficLight] = self.junction.get_traffic_lights()
            print(self.junction)
            for light in lights:
                if light.id == self.current_traffic_light_id:
                    light.state = True
                else:
                    light.state = False

            self.current_traffic_light_id = self.get_next_traffic_light_id()

            time.sleep(self.time_interval)

    def get_next_traffic_light_id(self):
        """
        Get the id of next traffic light in the round-robin
        """

        lights: List[TrafficLight] = self.junction.get_traffic_lights()

        for i, light in enumerate(lights):
            if light.id == self.current_traffic_light_id:
                return lights[(i + 1) % len(lights)].id

    # def get_current_state(self):
    #     """
    #     Get the current state of the traffic lights - red or green
    #     """
    #
    #     return self.junction.get_traffic_lights()
