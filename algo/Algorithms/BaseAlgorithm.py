from abc import ABC, abstractmethod
from typing import List

from utils.Junction import Junction
from utils.TrafficLight import TrafficLight


class BaseAlgorithm(ABC):
    """
    An abstract base class for traffic light control algorithms.
    Concrete implementations must override the `start()` method.
    """

    def __init__(self, junction: Junction) -> None:
        """
        :param junction: The Junction object to control.
        """
        self.junction: Junction = junction

    def get_current_traffic_lights_state(self) -> List[TrafficLight]:
        """
        Retrieve the traffic lights associated with the current junction.

        :return: A list of TrafficLight objects for this junction.
        """
        return self.junction.get_traffic_lights()

    def set_junction_info(self, junction: Junction) -> None:
        """
        Update the reference to the current junction data.

        :param junction: A new Junction object.
        """
        self.junction = junction

    @abstractmethod
    def start(self) -> None:
        """
        Concrete classes must implement a continuous or scheduled
        logic that manages the traffic lights.
        """
        pass
