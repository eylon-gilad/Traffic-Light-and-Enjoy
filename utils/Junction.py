from typing import List
from utils.Road import Road
from utils.Lane import Lane
from utils.TrafficLight import TrafficLight


class Junction:
    def __init__(
        self,
        id: int = 0,
        traffic_lights: List[TrafficLight] = [],
        roads: List[Road] = [],
    ) -> None:
        """
        Represents a traffic junction where roads meet.

        :param id: Unique identifier for the junction
        :param traffic_lights: List of TrafficLight objects controlling this junction
        :param roads: Roads connected to the junction
        """
        self.id = id
        self.traffic_lights = traffic_lights
        self.roads = roads

    def get_id(self) -> int:
        return self.id

    def get_traffic_lights(self) -> List[TrafficLight]:
        return self.traffic_lights

    def set_traffic_lights(self, traffic_lights: List[TrafficLight]) -> None:
        self.traffic_lights = traffic_lights

    def get_roads(self) -> List[Road]:
        return self.roads

    def set_roads(self, roads: List[Road]) -> None:
        """Sets the roads connected to the junction."""
        self.roads = roads

    def get_road_by_id(self, road_id: int) -> Road:
        for road in self.roads:
            if road.id == road_id:
                return road

    def get_lanes_by_ids(self, ids: List[int]) -> List[Lane]:
        lanes = []
        for lane in self.lanes:
            if lane.id in ids:
                lanes.append(lane)
        return lanes
