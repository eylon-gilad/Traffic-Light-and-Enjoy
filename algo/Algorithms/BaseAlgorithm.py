from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from typing import List
from abc import ABC, abstractmethod


class BaseAlgorithm(ABC):
    def __init__(self, junction):
        self.junction: Junction = junction

    def get_current_traffic_lights_state(self) -> List[TrafficLight]:
        return self.junction.get_traffic_lights()

    def set_junction_info(self, junction: Junction) -> None:
        self.junction = junction

    @abstractmethod
    def start(self) -> None:
        pass
