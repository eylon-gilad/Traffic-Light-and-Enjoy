from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.Lane import Lane
from typing import List, Dict


class TrafficLightsCombinator:
    combination: Dict[int: List[int]] = None

    def __init__(self, junction: Junction):
        self.junction = junction

        traffic_lights: List[TrafficLight] = junction.get_traffic_lights()
        for traffic_light in traffic_lights:
            possible_active_lights: List[int] = self.calc_possible_active_lights(traffic_light.id)
            TrafficLightsCombinator.combination[traffic_light.id] = possible_active_lights

    def calc_possible_active_lights(self, light_id: int) -> List[int]:
        """
        Function gets a specific traffic light and returns all
        traffic lights that can be active without causing collision
        """

    def not_entering_the_same_road(self, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
        for dest_1 in traffic_light_1.destinations:
            for dest_2 in traffic_light_2.destinations:
                road_id_1 = ((dest_1 // 10) % 10)
                road_id_2 = ((dest_2 // 10) % 10)
                if road_id_1 == road_id_2:
                    return False
        return True

    def turn_left_condition(self, traffic_light_1: TrafficLight, traffic_light_2: TrafficLight) -> bool:
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
        dest_roads_ids_1: List[int] = [(road_id // 10) for road_id in traffic_light_1.get_destinations()]
        dest_roads_ids_2: List[int] = [(road_id // 10) for road_id in traffic_light_2.get_destinations()]

        # Getting the destinations roads, by their ids
        dest_roads_1: List[Road] = [self.junction.get_road_by_id(dest_roads_id_1) for dest_roads_id_1 in dest_roads_ids_1]
        dest_roads_2: List[Road] = [self.junction.get_road_by_id(dest_roads_id_2) for dest_roads_id_2 in dest_roads_ids_2]

        # Getting the road destination direction
        to_side_dest_roads_1: List[RoadEnum] = [dest_road_1.get_to_side() for dest_road_1 in dest_roads_1]
        to_side_dest_roads_2: List[RoadEnum] = [dest_road_2.get_to_side() for dest_road_2 in dest_roads_2]

        if self.check_if_turn_left(from_side_origin_road_1, to_side_dest_roads_1):
            if (from_side_origin_road_1.name is not from_side_origin_road_2.name) and \
                    ((from_side_origin_road_1.value + from_side_origin_road_2.value) % 2 == 0):  # Checking opposite directions

                if self.check_if_continue_straight(from_side_origin_road_2, to_side_dest_roads_2):
                    return False

            if (from_side_origin_road_1.name is not from_side_origin_road_2.name) and \
                    ((from_side_origin_road_1.value + from_side_origin_road_2.value) % 2 == 1):  # Checking near directions

                if self.check_if_continue_straight(from_side_origin_road_2, to_side_dest_roads_2):
                    return False

                if self.check_if_turn_left(from_side_origin_road_2, to_side_dest_roads_2):
                    return False

        return True

    def check_if_turn_left(self, from_side: RoadEnum, to_sides: List[RoadEnum]):
        for to_side in to_sides:
            if from_side.name == RoadEnum.NORTH and to_side == RoadEnum.EAST:
                return True
            if from_side.name == RoadEnum.WEST and to_side == RoadEnum.NORTH:
                return True
            if from_side.name == RoadEnum.SOUTH and to_side == RoadEnum.WEST:
                return True
            if from_side.name == RoadEnum.EAST and to_side == RoadEnum.SOUTH:
                return True
        return False

    def check_if_continue_straight(self, from_side: RoadEnum, to_sides: List[RoadEnum]):
        for to_side in to_sides:
            if from_side.value + to_side.value % 2 == 0:
                return True
        return False
