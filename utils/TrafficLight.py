from typing import List

from utils.Lane import Lane


class TrafficLight:

    def __init__(
        self,
        id: int = 0,
        origins: List[Lane] = [],
        destinations: list[int] = [],
        state: bool = False,
    ):
        """
        Represents a traffic light controlling lanes at an intersection.
        """
        self.origins: List[int] = origins  # Lanes where traffic is originating
        self.destinations: List[int] = destinations  # Lanes where traffic is destined
        self.state: bool = state  # True (Green) or False (Red)
        self.id = id

    def set_origins(self, origins: List[Lane]) -> None:
        """Sets the lanes where traffic is originating."""
        self.origins = origins

    def set_destinations(self, destinations: List[Lane]) -> None:
        """Sets the lanes where traffic is going."""
        self.destinations = destinations

    def get_destinations(self) -> List[Lane]:
        return self.destinations

    def get_origins(self) -> List[Lane]:
        return self.origins

    def get_state(self) -> bool:
        return self.state

    def green(self) -> None:
        self.state = True

    def red(self) -> None:
        self.state = False
