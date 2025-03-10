from typing import List

from algo.TrafficLightsCombinator import TrafficLightsCombinator
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.TrafficLight import TrafficLight


def main() -> None:
    """
    Run two simple tests for TrafficLightsCombinator using
    pre-built dummy junctions.
    """
    test1()
    test2()


def test1() -> None:
    """
    Build a dummy junction and print the valid traffic lights combinations.
    """
    junction: Junction = build_junction1()
    tlc: TrafficLightsCombinator = TrafficLightsCombinator(junction)
    print(tlc.get_combinations())


def test2() -> None:
    """
    Build another dummy junction and print the valid traffic lights combinations.
    """
    junction: Junction = build_junction2()
    tlc: TrafficLightsCombinator = TrafficLightsCombinator(junction)
    print(tlc.get_combinations())


def build_junction1() -> Junction:
    """
    Construct a sample Junction object with certain roads and lights.
    """
    j_id: int = 1
    traffic_lights: List[TrafficLight] = build_traffic_lights1()
    roads: List[Road] = build_roads()
    return Junction(junction_id=j_id, traffic_lights=traffic_lights, roads=roads)


def build_junction2() -> Junction:
    """
    Construct a second sample Junction object with different lights.
    """
    j_id: int = 1
    traffic_lights: List[TrafficLight] = build_traffic_lights2()
    roads: List[Road] = build_roads()
    return Junction(junction_id=j_id, traffic_lights=traffic_lights, roads=roads)


def build_traffic_lights1() -> List[TrafficLight]:
    """
    Create a set of traffic lights with specified origins/destinations.
    """
    return [
        TrafficLight(light_id=1, origins=[111, 112], destinations=[111, 112], state=False),
        TrafficLight(light_id=2, origins=[135], destinations=[135], state=False),
        TrafficLight(light_id=3, origins=[136], destinations=[111, 112], state=False),
        TrafficLight(light_id=4, origins=[124], destinations=[124, 147, 148], state=False),
        TrafficLight(light_id=5, origins=[123], destinations=[123, 136], state=False),
        TrafficLight(light_id=6, origins=[148], destinations=[148, 111, 112], state=False),
        TrafficLight(light_id=7, origins=[147], destinations=[147], state=False),
    ]


def build_traffic_lights2() -> List[TrafficLight]:
    """
    Create another set of traffic lights with different origins/destinations.
    """
    return [
        TrafficLight(light_id=1, origins=[111], destinations=[111, 135], state=False),
        TrafficLight(light_id=2, origins=[112], destinations=[112, 147, 148], state=False),
        TrafficLight(light_id=3, origins=[135], destinations=[123, 124], state=False),
        TrafficLight(light_id=4, origins=[136], destinations=[136], state=False),
        TrafficLight(light_id=5, origins=[124], destinations=[124], state=False),
        TrafficLight(light_id=6, origins=[123], destinations=[123, 135, 136], state=False),
        TrafficLight(light_id=7, origins=[148], destinations=[111, 112], state=False),
        TrafficLight(light_id=8, origins=[147], destinations=[123, 124], state=False),
    ]


def build_roads() -> List[Road]:
    """
    Create a set of roads with specific lane configurations.
    """
    return [
        Road(
            road_id=11,
            lanes=[Lane(lane_id=111), Lane(lane_id=112)],
            congection_level=5,
            from_side=RoadEnum.SOUTH,
            to_side=RoadEnum.NORTH,
        ),
        Road(
            road_id=12,
            lanes=[Lane(lane_id=123), Lane(lane_id=124)],
            congection_level=5,
            from_side=RoadEnum.NORTH,
            to_side=RoadEnum.SOUTH,
        ),
        Road(
            road_id=13,
            lanes=[Lane(lane_id=135), Lane(lane_id=136)],
            congection_level=5,
            from_side=RoadEnum.WEST,
            to_side=RoadEnum.EAST,
        ),
        Road(
            road_id=14,
            lanes=[Lane(lane_id=147), Lane(lane_id=148)],
            congection_level=5,
            from_side=RoadEnum.EAST,
            to_side=RoadEnum.WEST,
        ),
    ]


if __name__ == "__main__":
    main()
