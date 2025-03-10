"""
Road.py

This module defines the Road class, representing a road in the traffic simulation.
A road can have multiple lanes and an indicator for congestion.

Changes:
- Added docstring for the class and its methods.
- Added type hints for the constructor and methods.
- Preserved existing functionality.
"""

from typing import List, Optional

from utils.Lane import Lane
from utils.RoadEnum import RoadEnum


class Road:
    """
    Represents a road in the simulation, identified by an ID.
    The road can have multiple lanes, and can track a 'congection_level'
    indicating how congested the road is.
    """

    def __init__(
            self,
            road_id: int = 0,
            lanes: Optional[List[Lane]] = None,
            congection_level: int = 0,
            from_side: RoadEnum = None, to_side: RoadEnum = None
    ) -> None:
        """
        Initialize a Road object.

        Args:
            road_id (int): Unique identifier for the road.
            lanes (Optional[List[Lane]]): List of Lane objects on this road.
            congection_level (int): An integer indicating congestion (0 = low, higher = more congested).
            from_side (Optional[int]): (Unused here) Additional data about where the road originates.
            to_side (Optional[int]): (Unused here) Additional data about where the road goes.
        """
        self.id: int = road_id
        self.lanes: List[Lane] = lanes if lanes is not None else []
        self.from_side = from_side
        self.to_side = to_side
        # Keeping the attribute name as provided to avoid breaking existing code.
        self.congection_level: int = congection_level

    def get_id(self) -> int:
        """
        Get the road's unique identifier.

        Returns:
            int: The unique ID of the road.
        """
        return self.id

    def get_lanes(self) -> List[Lane]:
        """
        Get the list of lanes that belong to this road.

        Returns:
            List[Lane]: A list of Lane objects on this road.
        """
        return self.lanes

    def get_lanes_by_ids(self, ids: List[int]) -> List[Lane]:
        lanes = []
        for lane in self.lanes:
            if lane.id in ids:
                lanes.append(lane)
        return lanes

    def set_lanes(self, lanes: List[Lane]) -> None:
        """
        Set the lanes on the road.

        Args:
            lanes (List[Lane]): A new list of Lane objects.
        """
        self.lanes = lanes

    def get_congection_level(self) -> int:
        return self.congection_level

    def set_congection_level(self, congection_level: int) -> None:
        self.congection_level = congection_level

    def get_from_side(self) -> RoadEnum:
        return self.from_side

    def get_to_side(self) -> RoadEnum:
        return self.to_side

    def __str__(self):
        lanes_str = ", ".join(str(lane) for lane in self.lanes)
        return (
            f"Road(id={self.id}, "
            f"congection_level=[{self.congection_level}], lanes=[{lanes_str}])"
        )
