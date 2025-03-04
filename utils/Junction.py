"""
Junction.py

This module defines the Junction class, representing a traffic junction where roads meet.
A junction contains roads and associated traffic lights.
"""

from typing import List, Optional
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight


class Junction:
    def __init__(
        self,
        id: int = 0,
        traffic_lights: Optional[List[TrafficLight]] = None,
        roads: Optional[List[Road]] = None,
    ) -> None:
        """
        Initializes a Junction object.

        Args:
            id (int): Unique identifier for the junction.
            traffic_lights (Optional[List[TrafficLight]]): List of TrafficLight objects controlling this junction.
            roads (Optional[List[Road]]): List of roads connected to the junction.
        """
        self.id: int = id
        self.traffic_lights: List[TrafficLight] = (
            traffic_lights if traffic_lights is not None else []
        )
        self.roads: List[Road] = roads if roads is not None else []

    def get_id(self) -> int:
        """Returns the junction's unique identifier."""
        return self.id

    def get_traffic_lights(self) -> List[TrafficLight]:
        """Returns the list of traffic lights at the junction."""
        return self.traffic_lights

    def set_traffic_lights(self, traffic_lights: List[TrafficLight]) -> None:
        """
        Sets the traffic lights for the junction.

        Args:
            traffic_lights (List[TrafficLight]): New list of traffic lights.
        """
        self.traffic_lights = traffic_lights

    def get_roads(self) -> List[Road]:
        """Returns the list of roads connected to the junction."""
        return self.roads

    def set_roads(self, roads: List[Road]) -> None:
        """
        Sets the roads for the junction.

        Args:
            roads (List[Road]): New list of roads.
        """
        self.roads = roads

    def get_road_by_id(self, road_id: int) -> Optional[Road]:
        """
        Retrieves a road by its unique identifier.

        Args:
            road_id (int): The unique identifier for the road.

        Returns:
            Optional[Road]: The Road object if found, otherwise None.
        """
        for road in self.roads:
            if road.get_id() == road_id:
                return road
        return None

    def get_lanes(self) -> List[Lane]:
        """
        Returns all lanes from all roads in the junction.

        Returns:
            List[Lane]: A list of all Lane objects in the junction.
        """
        all_lanes: List[Lane] = []
        for road in self.roads:
            all_lanes.extend(road.get_lanes())
        return all_lanes

    def get_lanes_by_ids(self, lane_ids: List[int]) -> List[Lane]:
        """
        Returns the lanes that match any of the IDs in lane_ids.

        Args:
            lane_ids (List[int]): List of lane IDs to search for.

        Returns:
            List[Lane]: A list of Lane objects with matching IDs.
        """
        result: List[Lane] = []
        for lane in self.get_lanes():
            if lane.get_id() in lane_ids:
                result.append(lane)
        return result
