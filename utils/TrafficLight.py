"""
TrafficLight.py

This module defines the TrafficLight class, representing a traffic light that controls lanes at an intersection.

Changes:
- Added docstring for the class and methods.
- Added type hints.
- Preserved existing functionality.
"""

from typing import List, Optional


class TrafficLight:
    """
    Represents a traffic light controlling specific origin and destination lanes.
    Each traffic light has an ID, a list of origin lane IDs, a list of destination lane IDs,
    and a boolean state indicating green or red.
    """

    def __init__(
            self,
            light_id: int = 0,
            origins: Optional[List[int]] = None,
            destinations: Optional[List[int]] = None,
            state: bool = False,
    ) -> None:
        """
        Initialize a TrafficLight object.

        Args:
            light_id (int): Unique identifier for the traffic light.
            origins (Optional[List[int]]): List of lane IDs where traffic originates.
            destinations (Optional[List[int]]): List of lane IDs where traffic is directed.
            state (bool): True if the light is green, False if red.
        """
        self.id: int = light_id
        self.origins: List[int] = origins if origins is not None else []
        self.destinations: List[int] = destinations if destinations is not None else []
        self.state: bool = state

    def get_id(self) -> int:
        """
        Get the traffic light's unique identifier.

        Returns:
            int: The unique ID of the traffic light.
        """
        return self.id

    def get_origins(self) -> List[int]:
        """
        Get the list of origin lane IDs.

        Returns:
            List[int]: Lane IDs where traffic originates.
        """
        return self.origins

    def set_origins(self, origins: List[int]) -> None:
        """
        Set the origin lane IDs.

        Args:
            origins (List[int]): New list of origin lane IDs.
        """
        self.origins = origins

    def get_destinations(self) -> List[int]:
        """
        Get the list of destination lane IDs.

        Returns:
            List[int]: Lane IDs where traffic is directed.
        """
        return self.destinations

    def set_destinations(self, destinations: List[int]) -> None:
        """
        Set the destination lane IDs.

        Args:
            destinations (List[int]): New list of destination lane IDs.
        """
        self.destinations = destinations

    def get_state(self) -> bool:
        """
        Get the current state of the traffic light.

        Returns:
            bool: True if the light is green; otherwise, False.
        """
        return self.state

    def green(self) -> None:
        """
        Set the traffic light to green.
        """
        self.state = True

    def red(self) -> None:
        """
        Set the traffic light to red.
        """
        self.state = False
