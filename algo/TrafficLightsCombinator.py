from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from typing import List, Dict
from collections import defaultdict

import itertools


class TrafficLightsCombinator:
    combinations: List[tuple] = []

    @staticmethod
    def calc_possible_active_lights(junction):
        traffic_lights: List[TrafficLight] = junction.get_traffic_lights()
        possible_combinations: Dict[int, List[int]] = defaultdict(list)

        for traffic_light_1 in traffic_lights:
            for traffic_light_2 in traffic_lights:
                if TrafficLightsCombinator.not_entering_the_same_road(traffic_light_1, traffic_light_2) and \
                        TrafficLightsCombinator.not_intersect_on_straight(junction, traffic_light_1, traffic_light_2) and \
                        TrafficLightsCombinator.not_intersect_on_turn_left(junction, traffic_light_1, traffic_light_2):
                    possible_combinations[traffic_light_1.id].append(traffic_light_2.id)

        # Remove yourself
        for key, value in possible_combinations.items():
            if key in value:
                value.remove(key)

        TrafficLightsCombinator.combinations = TrafficLightsCombinator.find_max_combinations(possible_combinations)

    @staticmethod
    def power_set(s):
        return [set(subset) for r in range(len(s) + 1) for subset in itertools.combinations(s, r)]

    @staticmethod
    def find_max_combinations(possible_combinations):
        # Convert the input dictionary into a list of sets, where each set contains an item and its related items
        item_sets = []
        for item, relations in possible_combinations.items():
            related_items = {item} | set(relations)
            item_sets.append(related_items)

        # Create the power sets of the item_sets
        power_sets = [TrafficLightsCombinator.power_set(s) for s in item_sets]

        # Initialize a list to store subsets that are not contained in any other item set
        valid_subsets = []

        # Check if any power set subset is contained in another power set
        for i, power_set in enumerate(power_sets):
            for subset in power_set:
                for j in range(len(power_sets)):
                    if j != i:
                        if set(subset).issubset(item_sets[j]):
                            valid_subsets.append(subset)

        # Sort and remove duplicates from the valid subsets list
        valid_subsets = [tuple(sorted(subset)) for subset in valid_subsets]
        valid_subsets = list(set(valid_subsets))

        # Remove subsets that are contained within other subsets
        removable_indices = []
        for i in range(len(valid_subsets)):
            for j in range(len(valid_subsets)):
                if i != j:
                    if set(valid_subsets[i]).issubset(set(valid_subsets[j])):
                        removable_indices.append(i)

        # Generate the final list of valid subsets, excluding the removable ones
        final_subsets = [valid_subsets[i] for i in range(len(valid_subsets)) if i not in removable_indices]

        # Check for the specific condition on the final subsets and remove some based on the relation in the original dictionary
        removable_indices = []
        for i in range(len(final_subsets) - 1):
            if not set(final_subsets[i][1:]).issubset(set(tuple(possible_combinations[final_subsets[i][0]]))):
                removable_indices.append(i)

        # Generate the final list of subsets, excluding the ones marked for removal
        final_valid_subsets = [final_subsets[i] for i in range(len(final_subsets)) if i not in removable_indices]
        return final_valid_subsets

    @staticmethod
    def not_entering_the_same_road(traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        origin_road_id_1 = traffic_light_1.origins[0] // 10
        origin_road_id_2 = traffic_light_2.origins[0] // 10

        for dest_1 in traffic_light_1.get_destinations():
            for dest_2 in traffic_light_2.get_destinations():
                dest_road_id_1 = dest_1 // 10
                dest_road_id_2 = dest_2 // 10

                if origin_road_id_1 != origin_road_id_2 and dest_road_id_1 == dest_road_id_2:
                    return False

        return True

    @staticmethod
    def not_intersect_on_straight(junction: Junction, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        # Getting origin road id
        origin_road_id_1 = (traffic_light_1.get_origins()[0] // 10)
        origin_road_id_2 = (traffic_light_2.get_origins()[0] // 10)

        # Getting the road by id
        origin_road_1: Road = junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = junction.get_road_by_id(origin_road_id_2)

        # Getting the road origin direction
        from_side_origin_road_1: RoadEnum = origin_road_1.get_from_side()
        from_side_origin_road_2: RoadEnum = origin_road_2.get_from_side()

        # Getting destinations roads ids
        dest_roads_ids_1: List[int] = [(lane_id // 10) for lane_id in traffic_light_1.get_destinations()]
        dest_roads_ids_2: List[int] = [(lane_id // 10) for lane_id in traffic_light_2.get_destinations()]

        # Getting the destinations roads, by their ids
        dest_roads_1: List[Road] = [junction.get_road_by_id(dest_roads_id_1) for dest_roads_id_1 in dest_roads_ids_1]
        dest_roads_2: List[Road] = [junction.get_road_by_id(dest_roads_id_2) for dest_roads_id_2 in dest_roads_ids_2]

        # Getting the road destination direction
        to_side_dest_roads_1: List[RoadEnum] = [dest_road_1.get_to_side() for dest_road_1 in dest_roads_1]
        to_side_dest_roads_2: List[RoadEnum] = [dest_road_2.get_to_side() for dest_road_2 in dest_roads_2]

        # Check if roads are perpendicular
        if (from_side_origin_road_1.value + from_side_origin_road_2.value) % 2 == 1:
            # Check if roads are straight
            if TrafficLightsCombinator.check_if_continue_straight(from_side_origin_road_1, to_side_dest_roads_1) and \
                    TrafficLightsCombinator.check_if_continue_straight(from_side_origin_road_2, to_side_dest_roads_2):
                return False

        return True

    @staticmethod
    def not_intersect_on_turn_left(junction: Junction, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        # Getting origin road id
        origin_road_id_1 = (traffic_light_1.get_origins()[0] // 10)
        origin_road_id_2 = (traffic_light_2.get_origins()[0] // 10)

        # Getting the road by id
        origin_road_1: Road = junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = junction.get_road_by_id(origin_road_id_2)

        # Getting the road origin direction
        from_side_origin_road_1: RoadEnum = origin_road_1.get_from_side()
        from_side_origin_road_2: RoadEnum = origin_road_2.get_from_side()

        # Getting destinations roads ids
        dest_roads_ids_1: List[int] = [(lane_id // 10) for lane_id in traffic_light_1.get_destinations()]
        dest_roads_ids_2: List[int] = [(lane_id // 10) for lane_id in traffic_light_2.get_destinations()]

        # Getting the destinations roads, by their ids
        dest_roads_1: List[Road] = [junction.get_road_by_id(dest_roads_id_1) for dest_roads_id_1 in dest_roads_ids_1]
        dest_roads_2: List[Road] = [junction.get_road_by_id(dest_roads_id_2) for dest_roads_id_2 in dest_roads_ids_2]

        # Getting the road destination direction
        to_side_dest_roads_1: List[RoadEnum] = [dest_road_1.get_to_side() for dest_road_1 in dest_roads_1]
        to_side_dest_roads_2: List[RoadEnum] = [dest_road_2.get_to_side() for dest_road_2 in dest_roads_2]

        if TrafficLightsCombinator.check_if_turn_left(from_side_origin_road_1, to_side_dest_roads_1):
            if from_side_origin_road_1 == from_side_origin_road_2 or \
                    TrafficLightsCombinator.check_if_turn_only_right(from_side_origin_road_2, to_side_dest_roads_2):
                return True
            else:
                return False
        elif TrafficLightsCombinator.check_if_turn_left(from_side_origin_road_2, to_side_dest_roads_2):
            if from_side_origin_road_1 == from_side_origin_road_2 or \
                    TrafficLightsCombinator.check_if_turn_only_right(from_side_origin_road_1, to_side_dest_roads_1):
                return True
            else:
                return False

        return True

    @staticmethod
    def check_if_turn_left(from_side: RoadEnum, to_sides: List[RoadEnum]):
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
    def check_if_continue_straight(from_side: RoadEnum, to_sides: List[RoadEnum]):
        for to_side in to_sides:
            if (from_side.value + to_side.value) % 2 == 0:
                return True
        return False

    @staticmethod
    def check_if_turn_only_right(from_side: RoadEnum, to_sides: List[RoadEnum]):
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
