from typing import List

from utils.Road import Road


class Junction:
    id: int = 0

    def __init__(self):
        """
        Represents a traffic junction where roads meet.
        """
        self.roads: List[Road] = []
        self.id = Junction.id
        Junction.id += 1

    def add_road(self, road: Road):
        """Adds a road to the junction."""
        self.roads.append(road)
