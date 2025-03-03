"""
Road.py

This module defines the Road class, representing a road in the traffic simulation.
A road consists of multiple lanes.
"""

from typing import List
from utils.Lane import Lane


class Road:
    def __init__(self, id: int = 0, lanes: List[Lane] = None) -> None:
        """
        Initializes a Road object.

        Args:
            id (int): Unique identifier for the road.
            lanes (List[Lane], optional): List of Lane objects on the road.
        """
        self.id: int = id
        self.lanes: List[Lane] = lanes if lanes is not None else []

    def get_id(self) -> int:
        """Returns the road's unique identifier."""
        return self.id

    def get_lanes(self) -> List[Lane]:
        """Returns the list of lanes on the road."""
        return self.lanes

    def set_lanes(self, lanes: List[Lane]) -> None:
        """
        Sets the lanes for the road.

        Args:
            lanes (List[Lane]): New list of lanes.
        """
        self.lanes = lanes
