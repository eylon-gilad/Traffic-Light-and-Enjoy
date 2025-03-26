import random

from typing import List, Dict
from collections import defaultdict

from utils.Lane import Lane


class LanesGenerator:
    """
    Generates lanes for given roads (need only to pass road ids)
    """
    MIN_LANES_IN_ROAD = 2
    MAX_LANES_IN_ROAD = 3

    def __init__(self, road_ids: List[int]):
        self.road_ids: List[int] = road_ids

        # [key=road id, value=list of the lanes in this road]
        self.lanes_of_roads: Dict[int, List[Lane]] = self.__generate_lanes_for_roads()

    def get_lanes_for_road(self, road_id: int) -> List[Lane]:
        """
        Get lanes that generated for a specific road
        """
        return self.lanes_of_roads[road_id]

    def __generate_lanes_for_roads(self) -> Dict[int, List[Lane]]:
        """
        Generate random lanes for the given roads
        """
        lanes_of_roads: Dict[int, List[Lane]] = defaultdict(list)

        num_of_lanes_in_road: List[int] = LanesGenerator.__generate_num_of_lanes_in_road(len(self.road_ids))

        # Create for each road the amount of lanes that was generated
        for i, num_of_lanes in enumerate(num_of_lanes_in_road):
            lanes: List[Lane] = []
            current_lane_index: int = 0

            # Create "num_of_lanes" lanes for the road
            for _ in range(num_of_lanes):
                lanes.append(Lane(
                    lane_id=int(str(self.road_ids[i]) + str(current_lane_index)),
                    car_creation=random.uniform(0.003, 0.013),
                    lane_max_vel=random.gauss(150, 1/3)
                ))

                current_lane_index += 1

            lanes_of_roads[self.road_ids[i]] = lanes

        return lanes_of_roads

    @staticmethod
    def __generate_num_of_lanes_in_road(num_of_roads: int) -> List[int]:
        """
        Returns a list with random num of lanes in each road
        Num of lanes in all roads together is maximum "max_total_lanes"
        """

        result: List[int] = []
        for _ in range(num_of_roads):
            result.append(random.randint(LanesGenerator.MIN_LANES_IN_ROAD, LanesGenerator.MAX_LANES_IN_ROAD))

        return result
