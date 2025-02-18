from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from utils.Road import Road
from utils.Lane import Lane
from typing import List, Dict


class TrafficLightsCombinator:
    combination: Dict[int: List[int]] = None

    def __init__(self, junction: Junction):
        self.junction = junction

        traffic_lights: List[TrafficLight] = junction.get_traffic_lights()
        for traffic_light in traffic_lights:
            possible_active_lights: List[int] = self.calc_possible_active_lights(traffic_light.id)
            TrafficLightsCombinator.combination[traffic_light.id] = possible_active_lights

    def calc_possible_active_lights(self, light_id: int) -> List[int]:
        """
        Function gets a specific traffic light and returns all
        traffic lights that can be active without causing collision
        """
        pass
