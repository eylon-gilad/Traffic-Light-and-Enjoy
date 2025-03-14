from typing import List
from utils.Lane import Lane
from utils.RoadEnum import RoadEnum


class Road:
    def __init__(
        self, id: int = 0, lanes: List[Lane] = [], congection_level: int = 0,
            from_side: RoadEnum = None, to_side: RoadEnum = None
    ) -> None:
        """
        Represents a road in the simulation.

        :param id: Unique identifier for the road
        :param lanes: List of Lane objects on this road
        :param congection_level: An integer indicating congestion (0 = low, higher = more congestion)
        """
        self.id = id
        self.lanes: List[Lane] = lanes
        self.congection_level = congection_level
        self.from_side = from_side
        self.to_side = to_side

    def get_id(self) -> int:
        return self.id

    def get_lanes(self) -> List[Lane]:
        return self.lanes

    def get_lanes_by_ids(self, ids: List[int]) -> List[Lane]:
        lanes = []
        for lane in self.lanes:
            if lane.id in ids:
                lanes.append(lane)
        return lanes

    def set_lanes(self, lanes: List[Lane]) -> None:
        """Sets the lanes on the road."""
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
