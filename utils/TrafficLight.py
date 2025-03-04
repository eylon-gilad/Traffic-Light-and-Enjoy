"""
TrafficLight.py

This module defines the TrafficLight class, representing a traffic light that controls lanes at an intersection.
"""

from typing import List, Optional


class TrafficLight:
    def __init__(
        self,
        id: int = 0,
        origins: Optional[List[int]] = None,
        destinations: Optional[List[int]] = None,
        state: bool = False,
    ) -> None:
        """
        Initializes a TrafficLight object.

        Args:
            id (int): Unique identifier for the traffic light.
            origins (Optional[List[int]]): List of lane IDs where traffic originates.
            destinations (Optional[List[int]]): List of lane IDs where traffic is directed.
            state (bool): True if the light is green, False if red.
        """
        self.id: int = id
        self.origins: List[int] = origins if origins is not None else []
        self.destinations: List[int] = destinations if destinations is not None else []
        self.state: bool = state

    def get_id(self) -> int:
        """Returns the traffic light's unique identifier."""
        return self.id

    def get_origins(self) -> List[int]:
        """Returns the list of origin lane IDs."""
        return self.origins

    def set_origins(self, origins: List[int]) -> None:
        """
        Sets the origin lane IDs.

        Args:
            origins (List[int]): New list of origin lane IDs.
        """
        self.origins = origins

    def get_destinations(self) -> List[int]:
        """Returns the list of destination lane IDs."""
        return self.destinations

    def set_destinations(self, destinations: List[int]) -> None:
        """
        Sets the destination lane IDs.

        Args:
            destinations (List[int]): New list of destination lane IDs.
        """
        self.destinations = destinations

    def get_state(self) -> bool:
        """Returns True if the traffic light is green; otherwise, False."""
        return self.state

    def green(self) -> None:
        """Sets the traffic light to green."""
        self.state = True

    def red(self) -> None:
        """Sets the traffic light to red."""
        self.state = False
