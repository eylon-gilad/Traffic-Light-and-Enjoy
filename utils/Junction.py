# Junction.py
from typing import List

from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight


class Junction:
    def __init__(
            self,
            id: int = 0,
            traffic_lights: List[TrafficLight] = None,
            roads: List[Road] = None,
    ) -> None:
        """
        Represents a traffic junction where roads meet.

        :param id: Unique identifier for the junction
        :param traffic_lights: List of TrafficLight objects controlling this junction
        :param roads: Roads connected to the junction
        """
        self.id = id
        self.traffic_lights = traffic_lights if traffic_lights is not None else []
        self.roads = roads if roads is not None else []

    def get_id(self) -> int:
        return self.id

    def get_traffic_lights(self) -> List[TrafficLight]:
        return self.traffic_lights

    def set_traffic_lights(self, traffic_lights: List[TrafficLight]) -> None:
        self.traffic_lights = traffic_lights

    def get_roads(self) -> List[Road]:
        return self.roads

    def set_roads(self, roads: List[Road]) -> None:
        self.roads = roads

    def get_road_by_id(self, road_id: int) -> Road:
        for road in self.roads:
            if road.get_id() == road_id:
                return road
        return None

    def get_lanes(self) -> List[Lane]:
        """
        Returns all lanes from all roads in this junction.
        """
        all_lanes = []
        for road in self.roads:
            all_lanes.extend(road.get_lanes())
        return all_lanes

    def get_lanes_by_ids(self, lane_ids: List[int]) -> List[Lane]:
        """
        Returns the lanes that match any of the IDs in lane_ids.
        """
        result = []
        for lane in self.get_lanes():
            if lane.get_id() in lane_ids:
                result.append(lane)
        return result
