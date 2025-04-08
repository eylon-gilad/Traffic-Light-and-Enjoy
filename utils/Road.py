"""
Road.py

This module defines the Road class, representing a road in the traffic simulation.
A road can have multiple lanes and an indicator for congestion.

Changes:
- Improved docstrings and type hints.
- Preserved existing functionality (including misspelling "congection_level").
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
        from_side: Optional[RoadEnum] = None,
        to_side: Optional[RoadEnum] = None,
    ) -> None:
        """
        Initialize a Road object.

        Args:
            road_id (int): Unique identifier for the road.
            lanes (Optional[List[Lane]]): List of Lane objects on this road.
            congection_level (int): An integer indicating congestion (0 = low, higher = more congested).
            from_side (Optional[RoadEnum]): The side/direction from which the road originates.
            to_side (Optional[RoadEnum]): The side/direction where the road heads.
        """
        self.id: int = road_id
        self.lanes: List[Lane] = lanes if lanes is not None else []
        self.from_side: Optional[RoadEnum] = from_side
        self.to_side: Optional[RoadEnum] = to_side
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
        """
        Retrieve lanes from this road that match any of the provided lane IDs.

        Args:
            ids (List[int]): A list of lane IDs to find.

        Returns:
            List[Lane]: All matching Lane objects.
        """
        matching_lanes = []
        for lane in self.lanes:
            if lane.id in ids:
                matching_lanes.append(lane)
        return matching_lanes

    def set_lanes(self, lanes: List[Lane]) -> None:
        """
        Set the lanes on the road.

        Args:
            lanes (List[Lane]): A new list of Lane objects.
        """
        self.lanes = lanes

    def get_congection_level(self) -> int:
        """
        Get the current congestion level of the road.

        Returns:
            int: Congestion level (0 for low, higher means more congested).
        """
        return self.congection_level

    def set_congection_level(self, congection_level: int) -> None:
        """
        Set the congestion level of the road.

        Args:
            congection_level (int): New congestion level to set.
        """
        self.congection_level = congection_level

    def get_from_side(self) -> Optional[RoadEnum]:
        """
        Get the originating side of this road.

        Returns:
            Optional[RoadEnum]: The enum member indicating from which direction the road starts.
        """
        return self.from_side

    def get_to_side(self) -> Optional[RoadEnum]:
        """
        Get the terminating side of this road.

        Returns:
            Optional[RoadEnum]: The enum member indicating to which direction the road goes.
        """
        return self.to_side

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of this Road.
        """
        lanes_str = ", ".join(str(lane) for lane in self.lanes)
        return (
            f"Road(id={self.id}, "
            f"congection_level=[{self.congection_level}], lanes=[{lanes_str}])"
        )
