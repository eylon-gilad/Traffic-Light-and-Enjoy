from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from typing import List, Dict
from collections import defaultdict


class TrafficLightsCombinator:
    combination: Dict[int, List[int]] = defaultdict(list)

    def __init__(self, junction: Junction):
        self.junction = junction
        self.calc_possible_active_lights()

    def calc_possible_active_lights(self):
        traffic_lights: List[TrafficLight] = self.junction.get_traffic_lights()

        for traffic_light_1 in traffic_lights:
            for traffic_light_2 in traffic_lights:
                if self.not_entering_the_same_road(traffic_light_1, traffic_light_2) and \
                        self.not_intersect_on_straight(traffic_light_1, traffic_light_2) and \
                        self.not_intersect_on_turn_left(traffic_light_1, traffic_light_2):

                    TrafficLightsCombinator.combination[traffic_light_1.id].append(traffic_light_2.id)

        # Remove yourself
        for key, value in TrafficLightsCombinator.combination.items():
            if key in value:
                value.remove(key)

    def not_entering_the_same_road(self, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        origin_road_id_1 = traffic_light_1.origins[0] // 10
        origin_road_id_2 = traffic_light_2.origins[0] // 10

        for dest_1 in traffic_light_1.get_destinations():
            for dest_2 in traffic_light_2.get_destinations():
                dest_road_id_1 = dest_1 // 10
                dest_road_id_2 = dest_2 // 10

                if origin_road_id_1 != origin_road_id_2 and dest_road_id_1 == dest_road_id_2:
                    return False

        return True

    def not_intersect_on_straight(self, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        # Getting origin road id
        origin_road_id_1 = (traffic_light_1.get_origins()[0] // 10)
        origin_road_id_2 = (traffic_light_2.get_origins()[0] // 10)

        # Getting the road by id
        origin_road_1: Road = self.junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = self.junction.get_road_by_id(origin_road_id_2)

        # Getting the road origin direction
        from_side_origin_road_1: RoadEnum = origin_road_1.get_from_side()
        from_side_origin_road_2: RoadEnum = origin_road_2.get_from_side()

        # Getting destinations roads ids
        dest_roads_ids_1: List[int] = [(lane_id // 10) for lane_id in traffic_light_1.get_destinations()]
        dest_roads_ids_2: List[int] = [(lane_id // 10) for lane_id in traffic_light_2.get_destinations()]

        # Getting the destinations roads, by their ids
        dest_roads_1: List[Road] = [self.junction.get_road_by_id(dest_roads_id_1) for dest_roads_id_1 in dest_roads_ids_1]
        dest_roads_2: List[Road] = [self.junction.get_road_by_id(dest_roads_id_2) for dest_roads_id_2 in dest_roads_ids_2]

        # Getting the road destination direction
        to_side_dest_roads_1: List[RoadEnum] = [dest_road_1.get_to_side() for dest_road_1 in dest_roads_1]
        to_side_dest_roads_2: List[RoadEnum] = [dest_road_2.get_to_side() for dest_road_2 in dest_roads_2]

        # Check if roads are perpendicular
        if (from_side_origin_road_1.value + from_side_origin_road_2.value) % 2 == 1:
            # Check if roads are straight
            if self.check_if_continue_straight(from_side_origin_road_1, to_side_dest_roads_1) and \
                    self.check_if_continue_straight(from_side_origin_road_2, to_side_dest_roads_2):
                return False

        return True

    def not_intersect_on_turn_left(self, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        # Getting origin road id
        origin_road_id_1 = (traffic_light_1.get_origins()[0] // 10)
        origin_road_id_2 = (traffic_light_2.get_origins()[0] // 10)

        # Getting the road by id
        origin_road_1: Road = self.junction.get_road_by_id(origin_road_id_1)
        origin_road_2: Road = self.junction.get_road_by_id(origin_road_id_2)

        # Getting the road origin direction
        from_side_origin_road_1: RoadEnum = origin_road_1.get_from_side()
        from_side_origin_road_2: RoadEnum = origin_road_2.get_from_side()

        # Getting destinations roads ids
        dest_roads_ids_1: List[int] = [(lane_id // 10) for lane_id in traffic_light_1.get_destinations()]
        dest_roads_ids_2: List[int] = [(lane_id // 10) for lane_id in traffic_light_2.get_destinations()]

        # Getting the destinations roads, by their ids
        dest_roads_1: List[Road] = [self.junction.get_road_by_id(dest_roads_id_1) for dest_roads_id_1 in dest_roads_ids_1]
        dest_roads_2: List[Road] = [self.junction.get_road_by_id(dest_roads_id_2) for dest_roads_id_2 in dest_roads_ids_2]

        # Getting the road destination direction
        to_side_dest_roads_1: List[RoadEnum] = [dest_road_1.get_to_side() for dest_road_1 in dest_roads_1]
        to_side_dest_roads_2: List[RoadEnum] = [dest_road_2.get_to_side() for dest_road_2 in dest_roads_2]

        if self.check_if_turn_left(from_side_origin_road_1, to_side_dest_roads_1):
            if from_side_origin_road_1 == from_side_origin_road_2 or \
                    self.check_if_turn_only_right(from_side_origin_road_2, to_side_dest_roads_2):
                return True
            else:
                return False
        elif self.check_if_turn_left(from_side_origin_road_2, to_side_dest_roads_2):
            if from_side_origin_road_1 == from_side_origin_road_2 or \
                    self.check_if_turn_only_right(from_side_origin_road_1, to_side_dest_roads_1):
                return True
            else:
                return False

        return True

    def check_if_turn_left(self, from_side: RoadEnum, to_sides: List[RoadEnum]):
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

    def check_if_continue_straight(self, from_side: RoadEnum, to_sides: List[RoadEnum]):
        for to_side in to_sides:
            if (from_side.value + to_side.value) % 2 == 0:
                return True
        return False

    def check_if_turn_only_right(self, from_side: RoadEnum, to_sides: List[RoadEnum]):
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
