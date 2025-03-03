# Road.py
from typing import List

from utils.Lane import Lane


class Road:
    def __init__(self, id: int = 0, lanes: List[Lane] = None) -> None:
        """
        Represents a road in the simulation.

        :param id: Unique identifier for the road
        :param lanes: List of Lane objects on this road
        """
        self.id = id
        self.lanes: List[Lane] = lanes if lanes is not None else []

    def get_id(self) -> int:
        return self.id

    def get_lanes(self) -> List[Lane]:
        return self.lanes

    def set_lanes(self, lanes: List[Lane]) -> None:
        self.lanes = lanes
