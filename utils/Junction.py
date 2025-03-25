"""
Junction.py

This module defines the Junction class, representing a traffic junction where roads meet.
A junction contains roads and associated traffic lights.

Changes:
- Refined docstrings for the class.
- Added missing docstring for get_traffic_light_by_id.
- Added type hints.
- Preserved existing functionality.
"""

from typing import List, Optional

from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight
from utils.Car import Car


class Junction:
    """
    Represents a traffic junction where multiple roads and traffic lights converge.
    Manages associated roads and traffic lights.
    """

    def __init__(
            self,
            junction_id: int = 0,
            traffic_lights: Optional[List[TrafficLight]] = None,
            roads: Optional[List[Road]] = None,
    ) -> None:
        """
        Initialize a Junction object.

        Args:
            junction_id (int): Unique identifier for the junction.
            traffic_lights (Optional[List[TrafficLight]]): List of TrafficLight objects controlling this junction.
            roads (Optional[List[Road]]): List of Road objects connected to the junction.
        """
        self.id: int = junction_id
        self.traffic_lights: List[TrafficLight] = traffic_lights if traffic_lights is not None else []
        self.roads: List[Road] = roads if roads is not None else []

    def get_id(self) -> int:
        """
        Get the junction's unique identifier.

        Returns:
            int: The unique identifier of the junction.
        """
        return self.id

    def get_traffic_lights(self) -> List[TrafficLight]:
        """
        Get the list of traffic lights at the junction.

        Returns:
            List[TrafficLight]: Traffic lights controlling this junction.
        """
        return self.traffic_lights

    def get_traffic_light_by_lane_id(self, lane_id: int) -> TrafficLight:
        """
        Get the traffic light that points to the lane.

        Returns:
            List[TrafficLight]: Traffic lights controlling this lane.
        """
        for traffic_light in self.traffic_lights:
            if lane_id in traffic_light.get_origins():
                return traffic_light

    def set_traffic_lights(self, traffic_lights: List[TrafficLight]) -> None:
        """
        Set the traffic lights for the junction.

        Args:
            traffic_lights (List[TrafficLight]): New list of traffic lights.
        """
        self.traffic_lights = traffic_lights

    def get_roads(self) -> List[Road]:
        """
        Get the list of roads connected to the junction.

        Returns:
            List[Road]: Roads linked to this junction.
        """
        return self.roads

    def get_traffic_light_by_id(self, traffic_light_id: int) -> Optional[TrafficLight]:
        """
        Retrieve a traffic light from the junction by its unique identifier.

        Args:
            traffic_light_id (int): The unique identifier of the traffic light.

        Returns:
            Optional[TrafficLight]: The traffic light if found; otherwise None.
        """
        for traffic_light in self.traffic_lights:
            if traffic_light.id == traffic_light_id:
                return traffic_light
        return None  # TODO: Confirm if returning None is acceptable or if an exception should be raised.

    def set_roads(self, roads: List[Road]) -> None:
        """
        Set the roads for the junction.

        Args:
            roads (List[Road]): New list of roads.
        """
        self.roads = roads

    def get_road_by_id(self, road_id: int) -> Optional[Road]:
        """
        Retrieve a road by its unique identifier.

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
        Get all lanes from all roads in the junction.

        Returns:
            List[Lane]: A list of all Lane objects associated with the junction.
        """
        all_lanes: List[Lane] = []
        for road in self.roads:
            all_lanes.extend(road.get_lanes())
        return all_lanes

    def get_lanes_by_ids(self, lane_ids: List[int]) -> List[Lane]:
        """
        Retrieve lanes that match any of the provided lane IDs.

        Args:
            lane_ids (List[int]): List of lane IDs to search for.

        Returns:
            List[Lane]: A list of Lane objects matching the given IDs.
        """
        result: List[Lane] = []
        for lane in self.get_lanes():
            if lane.get_id() in lane_ids:
                result.append(lane)
        return result

    def get_all_cars(self):
        cars: List[Car] = []

        for road in self.roads:
            for lane in road.get_lanes():
                for car in lane.get_cars():
                    cars.append(car)

        return cars

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of this Junction.
        """
        roads_str = ", ".join(str(road) for road in self.roads)
        tls_str = ", ".join(str(tl) for tl in self.traffic_lights)
        return (
            f"Junction(id={self.id}, "
            f"traffic_lights=[{tls_str}], roads=[{roads_str}])"
        )
