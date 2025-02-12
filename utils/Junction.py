from typing import List

from utils.Road import Road


class Junction:

    def __init__(self, id: int = 0, roads: List[Road] = []):
        """
        Represents a traffic junction where roads meet.
        """
        self.roads: List[Road] = roads
        self.id = id

    def set_roads(self, roads: List[Road]) -> None:
        """Sets the roads connected to the junction."""
        self.roads = roads

    def get_id(self) -> int:
        return self.id

    def get_roads(self) -> List[Road]:
        return self.roads
