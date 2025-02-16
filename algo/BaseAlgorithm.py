from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from typing import List
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    def __init__(self):
        self.junction: Junction = None
        self.traffic_lights: List[TrafficLight] = None

    def get_current_traffic_lights_state(self) -> List[TrafficLight]:
        return self.traffic_lights

    def set_junction_info(self, junction: Junction) -> None:
        self.junction = junction

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def __calculate_next_state(self) -> None:
        pass
