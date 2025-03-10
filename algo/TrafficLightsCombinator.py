import itertools
from collections import defaultdict
from typing import List, Dict, Set, Tuple, DefaultDict

from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.TrafficLight import TrafficLight


class TrafficLightsCombinator:
    """
    Responsible for calculating valid combinations of traffic lights
    that can be green simultaneously without creating intersecting paths.
    """

    combinations: List[Tuple[int, ...]] = []

    def __init__(self, junction: Junction) -> None:
        """
        Initialize the TrafficLightsCombinator with a given junction.

        :param junction: The Junction object to evaluate.
        """
        self.junction: Junction = junction
        self.combinations: List[Tuple[int, ...]] = self.calculate_possible_active_lights(self.junction)

    def get_combinations(self) -> List[Tuple[int, ...]]:
        """
        Retrieve the list of valid traffic-light combinations.

        :return: A list of tuples, each tuple representing a valid combination
                 of traffic light IDs.
        """
        return self.combinations

    @staticmethod
    def calculate_possible_active_lights(junction: Junction) -> List[Tuple[int, ...]]:
        """
        Find and return a list of valid combinations of traffic lights
        that can be active at the same time without causing intersection.

        :param junction: The Junction object containing traffic lights and roads.
        :return: A list of tuples, where each tuple represents a valid combination.
        """
        traffic_lights: List[TrafficLight] = junction.get_traffic_lights()
        possible_combinations: DefaultDict[int, List[int]] = defaultdict(list)

        # Compare every traffic light to every other to see if they can safely be on together.
        for traffic_light_1 in traffic_lights:
            for traffic_light_2 in traffic_lights:
                if (TrafficLightsCombinator.not_entering_the_same_road(traffic_light_1, traffic_light_2)
                        and TrafficLightsCombinator.not_intersect_on_straight(junction, traffic_light_1,
                                                                              traffic_light_2)
                        and TrafficLightsCombinator.not_intersect_on_turn_left(junction, traffic_light_1,
                                                                               traffic_light_2)):
                    possible_combinations[traffic_light_1.id].append(traffic_light_2.id)

        # Remove self from its own possible list.
        for key, value in possible_combinations.items():
            if key in value:
                value.remove(key)

        return TrafficLightsCombinator.find_max_combinations(possible_combinations)

    @staticmethod
    def power_set(s: Set[int]) -> List[Set[int]]:
        """
        Generate the power set of a given set s.

        :param s: A set of integers.
        :return: A list of subsets (as sets).
        """
        return [set(subset) for r in range(len(s) + 1) for subset in itertools.combinations(s, r)]

    @staticmethod
    def find_max_combinations(possible_combinations: Dict[int, List[int]]) -> List[Tuple[int, ...]]:
        """
        Determine the largest valid subsets from the possible combinations.

        :param possible_combinations: A dictionary mapping each traffic light
                                      ID to a list of traffic lights that can
                                      safely be active simultaneously.
        :return: A list of tuple subsets representing maximal valid combinations.
        """
        item_sets: List[Set[int]] = []
        for item, relations in possible_combinations.items():
            related_items = {item} | set(relations)
            item_sets.append(related_items)

        # Create the power sets of the item_sets
        power_sets = [TrafficLightsCombinator.power_set(s) for s in item_sets]

        # Collect subsets that appear to be valid or contained within others
        valid_subsets = []
        for i, p_set in enumerate(power_sets):
            for subset in p_set:
                for j, candidate_items in enumerate(item_sets):
                    if j != i:
                        if subset.issubset(candidate_items):
                            valid_subsets.append(subset)

        # Sort and remove duplicates
        valid_subsets = [tuple(sorted(subset)) for subset in valid_subsets]
        valid_subsets = list(set(valid_subsets))

        # Remove subsets contained within other subsets
        removable_indices = []
        for i in range(len(valid_subsets)):
            for j in range(len(valid_subsets)):
                if i != j:
                    if set(valid_subsets[i]).issubset(set(valid_subsets[j])):
                        removable_indices.append(i)

        final_subsets = [
            valid_subsets[i] for i in range(len(valid_subsets)) if i not in removable_indices
        ]

        # Additional filtering based on the original dictionary
        removable_indices = []
        for i in range(len(final_subsets) - 1):
            first_item = final_subsets[i][0]
            # TODO: Investigate if we need more robust checks for multi-item combos
            # in possible_combinations. The original logic removes subsets if
            # the subset minus the first item is not in possible_combinations.
            if not set(final_subsets[i][1:]).issubset(set(possible_combinations[first_item])):
                removable_indices.append(i)

        final_valid_subsets = [
            final_subsets[i] for i in range(len(final_subsets)) if i not in removable_indices
        ]
        return final_valid_subsets

    @staticmethod
    def not_entering_the_same_road(tl1: TrafficLight, tl2: TrafficLight) -> bool:
        """
        Check whether two traffic lights do NOT enter the same road.

        :param tl1: The first traffic light.
        :param tl2: The second traffic light.
        :return: True if they do not enter the same road; False otherwise.
        """
        origin_road_id_1 = tl1.origins[0] // 10
        origin_road_id_2 = tl2.origins[0] // 10

        for dest_1 in tl1.get_destinations():
            for dest_2 in tl2.get_destinations():
                dest_road_id_1 = dest_1 // 10
                dest_road_id_2 = dest_2 // 10

                if origin_road_id_1 != origin_road_id_2 and dest_road_id_1 == dest_road_id_2:
                    return False

        return True

    @staticmethod
    def not_intersect_on_straight(junction: Junction, tl1: TrafficLight, tl2: TrafficLight) -> bool:
        """
        Check if two traffic lights do not create an intersection
        when both are going straight across perpendicular roads.

        :param junction: The Junction containing roads.
        :param tl1: The first traffic light.
        :param tl2: The second traffic light.
        :return: True if no intersection occurs on a straight path; False otherwise.
        """
        origin_road_id_1 = tl1.get_origins()[0] // 10
        origin_road_id_2 = tl2.get_origins()[0] // 10

        origin_road_1: Road = junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = junction.get_road_by_id(origin_road_id_2)

        from_side_1: RoadEnum = origin_road_1.get_from_side()
        from_side_2: RoadEnum = origin_road_2.get_from_side()

        # Gather destinations
        dest_roads_ids_1 = [(lane_id // 10) for lane_id in tl1.get_destinations()]
        dest_roads_ids_2 = [(lane_id // 10) for lane_id in tl2.get_destinations()]
        dest_roads_1 = [junction.get_road_by_id(rid) for rid in dest_roads_ids_1]
        dest_roads_2 = [junction.get_road_by_id(rid) for rid in dest_roads_ids_2]
        to_side_dest_1 = [rd.get_to_side() for rd in dest_roads_1]
        to_side_dest_2 = [rd.get_to_side() for rd in dest_roads_2]

        # Check if roads are perpendicular and both lights go straight
        if (from_side_1.value + from_side_2.value) % 2 == 1:
            if (TrafficLightsCombinator.check_if_continue_straight(from_side_1, to_side_dest_1)
                    and TrafficLightsCombinator.check_if_continue_straight(from_side_2, to_side_dest_2)):
                return False

        return True

    @staticmethod
    def not_intersect_on_turn_left(junction: Junction, tl1: TrafficLight, tl2: TrafficLight) -> bool:
        """
        Check whether two traffic lights do not intersect if at least one is turning left.

        :param junction: The Junction containing roads.
        :param tl1: The first traffic light.
        :param tl2: The second traffic light.
        :return: True if no intersection on left turns; False otherwise.
        """
        origin_road_id_1 = tl1.get_origins()[0] // 10
        origin_road_id_2 = tl2.get_origins()[0] // 10

        origin_road_1: Road = junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = junction.get_road_by_id(origin_road_id_2)

        from_side_1: RoadEnum = origin_road_1.get_from_side()
        from_side_2: RoadEnum = origin_road_2.get_from_side()

        dest_roads_ids_1 = [(lane_id // 10) for lane_id in tl1.get_destinations()]
        dest_roads_ids_2 = [(lane_id // 10) for lane_id in tl2.get_destinations()]

        dest_roads_1 = [junction.get_road_by_id(rid) for rid in dest_roads_ids_1]
        dest_roads_2 = [junction.get_road_by_id(rid) for rid in dest_roads_ids_2]

        to_side_dest_1 = [rd.get_to_side() for rd in dest_roads_1]
        to_side_dest_2 = [rd.get_to_side() for rd in dest_roads_2]

        # If tl1 or tl2 is turning left, check certain conditions.
        if TrafficLightsCombinator.check_if_turn_left(from_side_1, to_side_dest_1):
            if (from_side_1 == from_side_2
                    or TrafficLightsCombinator.check_if_turn_only_right(from_side_2, to_side_dest_2)):
                return True
            return False
        elif TrafficLightsCombinator.check_if_turn_left(from_side_2, to_side_dest_2):
            if (from_side_1 == from_side_2
                    or TrafficLightsCombinator.check_if_turn_only_right(from_side_1, to_side_dest_1)):
                return True
            return False

        return True

    @staticmethod
    def check_if_turn_left(from_side: RoadEnum, to_sides: List[RoadEnum]) -> bool:
        """
        Check if the traffic movement from from_side to any of the to_sides is a left turn.
        """
        for to_side in to_sides:
            if from_side == RoadEnum.NORTH and to_side == RoadEnum.EAST:
                return True
            if from_side == RoadEnum.WEST and to_side == RoadEnum.NORTH:
                return True
            if from_side == RoadEnum.SOUTH and to_side == RoadEnum.WEST:
                return True
            if from_side == RoadEnum.EAST and to_side == RoadEnum.SOUTH:
                return True
        return False

    @staticmethod
    def check_if_continue_straight(from_side: RoadEnum, to_sides: List[RoadEnum]) -> bool:
        """
        Check if the traffic movement is effectively going straight across.

        :param from_side: The originating side (N, E, S, W).
        :param to_sides: The list of road sides.
        :return: True if any destination side is directly opposite from_side.
        """
        for to_side in to_sides:
            if (from_side.value + to_side.value) % 2 == 0:
                return True
        return False

    @staticmethod
    def check_if_turn_only_right(from_side: RoadEnum, to_sides: List[RoadEnum]) -> bool:
        """
        Check if from_side to all of the to_sides is strictly a right turn.

        :return: True if every movement is a right turn, else False.
        """
        for to_side in to_sides:
            if from_side == RoadEnum.WEST and to_side != RoadEnum.SOUTH:
                return False
            if from_side == RoadEnum.SOUTH and to_side != RoadEnum.EAST:
                return False
            if from_side == RoadEnum.EAST and to_side != RoadEnum.NORTH:
                return False
            if from_side == RoadEnum.NORTH and to_side != RoadEnum.WEST:
                return False

        return True
