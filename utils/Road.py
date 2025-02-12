from typing import List

from utils.Lane import Lane


class Road:
    id: int = 0

    def __init__(self, id: int = 0, lanes: List[Lane] = [], congection_level: int = 0):
        """
        Represents a road in the simulation.
        :param lanes: List of lanes on the road.
        """
        self.lanes: List[Lane] = lanes
        self.id = id
        self.congection_level = congection_level

    def set_lanes(self, lanes: List[Lane]) -> None:
        """Sets the lanes on the road."""
        self.lanes = lanes

    def get_lanes(self) -> List[Lane]:
        return self.lanes

    def get_id(self) -> int:
        return self.id

    def get_congection_level(self) -> int:
        return self.congection_level

    def set_congection_level(self, congection_level: int) -> None:
        self.congection_level = congection_level
