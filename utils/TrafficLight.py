# TrafficLight.py
from typing import List

class TrafficLight:
    def __init__(
            self,
            id: int = 0,
            origins: List[int] = None,
            destinations: List[int] = None,
            state: bool = False,
    ) -> None:
        """
        Represents a traffic light controlling lanes at an intersection.

        :param id: Unique identifier for the traffic light
        :param origins: List of lane IDs where traffic originates
        :param destinations: List of lane IDs where traffic is directed
        :param state: True if light is green, False if red
        """
        self.id = id
        self.origins = origins if origins is not None else []
        self.destinations = destinations if destinations is not None else []
        self.state = state

    def get_id(self) -> int:
        return self.id

    def get_origins(self) -> List[int]:
        return self.origins

    def set_origins(self, origins: List[int]) -> None:
        self.origins = origins

    def get_destinations(self) -> List[int]:
        return self.destinations

    def set_destinations(self, destinations: List[int]) -> None:
        self.destinations = destinations

    def get_state(self) -> bool:
        return self.state

    def green(self) -> None:
        self.state = True

    def red(self) -> None:
        self.state = False
