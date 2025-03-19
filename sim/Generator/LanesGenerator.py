import random

from typing import List, Dict
from collections import defaultdict

from utils.Lane import Lane


class LanesGenerator:
    """
    Generates lanes for given roads (need only to pass road ids)
    """
    MAX_TOTAL_LANES = 10
    MIN_LANES_IN_ROAD = 1
    MAX_LANES_IN_ROAD = 4

    def __init__(self, road_ids: List[int]):
        self.road_ids: List[int] = road_ids
        self.current_lane_index = 0

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

        num_of_lanes_in_road: List[int] = LanesGenerator.__generate_num_of_lanes_in_road(
            len(self.road_ids),
            LanesGenerator.MAX_TOTAL_LANES,
            LanesGenerator.MIN_LANES_IN_ROAD,
            LanesGenerator.MAX_LANES_IN_ROAD
        )

        # Create for each road the amount of lanes that was generated
        for i, num_of_lanes in enumerate(num_of_lanes_in_road):
            lanes: List[Lane] = []

            # Create "num_of_lanes" lanes for the road
            for _ in range(num_of_lanes):
                lanes.append(Lane(
                    lane_id=int(str(self.road_ids[i]) + str(self.current_lane_index))
                ))

                self.current_lane_index += 1

            lanes_of_roads[self.road_ids[i]] = lanes

        return lanes_of_roads

    @staticmethod
    def __generate_num_of_lanes_in_road(num_of_roads: int, max_total_lanes: int,
                                        min_lanes_in_road: int, max_lanes_in_road: int) -> List[int]:
        """
        Returns a list with random num of lanes in each road
        Num of lanes in all roads together is maximum "max_total_lanes"
        """
        result: List[int] = []
        remaining_sum: int = max_total_lanes

        for _ in range(num_of_roads):
            max_possible: int = min(max_lanes_in_road,
                                    remaining_sum - (num_of_roads - len(result) - 1) * min_lanes_in_road)
            min_possible: int = min_lanes_in_road
            if remaining_sum - (num_of_roads - len(result) - 1) * min_lanes_in_road < min_lanes_in_road:
                num: int = min_lanes_in_road
            else:
                num: int = random.randint(min_possible, max_possible)
            result.append(num)
            remaining_sum -= num

        random.shuffle(result)
        return result
