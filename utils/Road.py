from typing import List

from utils.Lane import Lane


class Road:
    id: int = 0

    def __init__(self, num_lanes: int = 1):
        """
        Represents a road with multiple lanes.
        :param num_lanes: Number of lanes on the road (default is 1).
        """
        self.id = Road.id
        Road.id += 1
        self.lanes: List[Lane] = [Lane() for _ in range(num_lanes)]
