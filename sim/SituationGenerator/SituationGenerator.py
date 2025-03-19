import random
from typing import List, Optional

from utils.Junction import Junction
from utils.Road import Road
from utils.TrafficLight import TrafficLight
from utils.Lane import Lane
from utils.RoadEnum import RoadEnum

from LanesGenerator import LanesGenerator


class SituationGenerator:
    NEW_JUNCTION_ID = 1

    MAX_ROADS = 4
    MAX_LANES_IN_ROAD = 3

    @staticmethod
    def generate_junction():
        junction_id: int = SituationGenerator.NEW_JUNCTION_ID
        SituationGenerator.NEW_JUNCTION_ID += 1

        roads: List[Road] = SituationGenerator.create_roads(junction_id)
        traffic_lights: List[TrafficLight] = SituationGenerator.create_traffic_lights(roads)

        return Junction(
            junction_id=junction_id,
            roads=roads,
            traffic_lights=traffic_lights
        )

    @staticmethod
    def create_roads(junction_id: int) -> List[Road]:
        road_1_id: int = int(str(junction_id) + str(1))
        road_2_id: int = int(str(junction_id) + str(2))
        road_3_id: int = int(str(junction_id) + str(3))
        road_4_id: int = int(str(junction_id) + str(4))

        lanes_generator: LanesGenerator = LanesGenerator([road_1_id, road_2_id, road_3_id, road_4_id])

        return [
            Road(
                road_id=int(str(junction_id) + str(1)),
                lanes=lanes_generator.get_lanes_for_road(road_1_id),
                from_side=RoadEnum.SOUTH,
                to_side=RoadEnum.NORTH
            ),
            Road(
                road_id=int(str(junction_id) + str(2)),
                lanes=lanes_generator.get_lanes_for_road(road_2_id),
                from_side=RoadEnum.NORTH,
                to_side=RoadEnum.SOUTH
            ),
            Road(
                road_id=int(str(junction_id) + str(3)),
                lanes=lanes_generator.get_lanes_for_road(road_3_id),
                from_side=RoadEnum.WEST,
                to_side=RoadEnum.EAST
            ),
            Road(
                road_id=int(str(junction_id) + str(4)),
                lanes=lanes_generator.get_lanes_for_road(road_4_id),
                from_side=RoadEnum.EAST,
                to_side=RoadEnum.WEST
            ),
        ]

    @staticmethod
    def create_traffic_lights(roads: list[Road]) -> list[TrafficLight]:
        traffic_lights: List[TrafficLight] = []
        current_light_id: int = 1

        for road in roads:
            for lane in road.get_lanes():
                possible_destinations: List[int] = SituationGenerator.find_possible_destinations(roads, road, lane.id)
                random_destinations: List[int] = random.sample(
                    possible_destinations,
                    random.randint(1, len(possible_destinations))
                )

                traffic_lights.append(TrafficLight(
                    light_id=current_light_id,
                    origins=[lane.get_id()],
                    destinations=random_destinations
                ))

                current_light_id += 1

        return traffic_lights

    @staticmethod
    def find_possible_destinations(roads: list[Road], current_road: Road, origin_id: int) -> List[int]:
        """
        Find all possible destinations of traffic light
        that its origin is "origin_id"
        """
        possible_destinations: List[int] = [origin_id]  # Always can go straight

        if SituationGenerator.is_rightest_lane(current_road, origin_id):
            possible_destinations.append(SituationGenerator.get_right_to_right_lane(roads, origin_id))

        if SituationGenerator.is_leftest_lane(current_road, origin_id):
            possible_destinations.append(SituationGenerator.get_left_to_left_lane(roads, origin_id))

        return possible_destinations

    @staticmethod
    def is_rightest_lane(road: Road, origin_id: int) -> bool:
        """
        Returns if given lane is rightest in its road
        """
        if (origin_id // 10) % 10 == 1 or (origin_id // 10) % 10 == 3:
            return origin_id == min([lane.get_id() for lane in road.get_lanes()])

        return origin_id == max([lane.get_id() for lane in road.get_lanes()])

    @staticmethod
    def is_leftest_lane(road: Road, origin_id: int):
        """
        Returns if given lane is leftest in its road
        """
        if (origin_id // 10) % 10 == 1 or (origin_id // 10) % 10 == 3:
            return origin_id == max([lane.get_id() for lane in road.get_lanes()])

        return origin_id == min([lane.get_id() for lane in road.get_lanes()])

    @staticmethod
    def get_right_to_right_lane(roads: list[Road], origin_id: int) -> int:
        """
        If a car turns to the right, it can only go to the closest lane
        This function return this closest lane on the right
        """
        if (origin_id // 10) % 10 == 1:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 3)
            return min([lane.get_id() for lane in relevant_road.get_lanes()])
        elif (origin_id // 10) % 10 == 2:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 4)
            return max([lane.get_id() for lane in relevant_road.get_lanes()])
        elif (origin_id // 10) % 10 == 3:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 2)
            return max([lane.get_id() for lane in relevant_road.get_lanes()])
        else:  # (origin_id // 10) % 10 == 4
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 1)
            return min([lane.get_id() for lane in relevant_road.get_lanes()])

    @staticmethod
    def get_left_to_left_lane(roads: list[Road], origin_id: int) -> int:
        """
        If a car turns to the left, it can only go to the closest lane
        This function return this closest lane on the left
        """
        if (origin_id // 10) % 10 == 1:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 4)
            return min([lane.get_id() for lane in relevant_road.get_lanes()])
        elif (origin_id // 10) % 10 == 2:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 3)
            return max([lane.get_id() for lane in relevant_road.get_lanes()])
        elif (origin_id // 10) % 10 == 3:
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 1)
            return max([lane.get_id() for lane in relevant_road.get_lanes()])
        else:  # (origin_id // 10) % 10 == 4
            relevant_road: Road = SituationGenerator.find_road_by_index(roads, 2)
            return min([lane.get_id() for lane in relevant_road.get_lanes()])

    @staticmethod
    def find_road_by_index(roads: list[Road], road_index: int) -> Road:
        for road in roads:
            if road.get_id() % 10 == road_index:
                return road


if __name__ == "__main__":
    junction = SituationGenerator.generate_junction()

    print(junction.__str__())
