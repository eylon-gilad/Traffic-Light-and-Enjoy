from typing import List
from utils.Junction import Junction
from utils.TrafficLight import TrafficLight
from utils.Road import Road
from utils.Lane import Lane
from utils.RoadEnum import RoadEnum
from algo.TrafficLightsCombinator import TrafficLightsCombinator


def main():
    test1()
    test2()


def test1():
    junction: Junction = build_junction1()

    tlc: TrafficLightsCombinator = TrafficLightsCombinator(junction)
    print(TrafficLightsCombinator.combination)


def test2():
    junction: Junction = build_junction2()

    tlc: TrafficLightsCombinator = TrafficLightsCombinator(junction)
    print(TrafficLightsCombinator.combination)


def build_junction1() -> Junction:
    id: int = 1
    traffic_lights: List[TrafficLight] = build_traffic_lights1()
    roads: List[Road] = build_roads()

    return Junction(id=id, traffic_lights=traffic_lights, roads=roads)


def build_junction2() -> Junction:
    id: int = 1
    traffic_lights: List[TrafficLight] = build_traffic_lights2()
    roads: List[Road] = build_roads()

    return Junction(id=id, traffic_lights=traffic_lights, roads=roads)


def build_traffic_lights1() -> List[TrafficLight]:
    traffic_lights: List[TrafficLight] = \
        [TrafficLight(id=1, origins=[111, 112], destinations=[111, 112], state=False),
         TrafficLight(id=2, origins=[135], destinations=[135], state=False),
         TrafficLight(id=3, origins=[136], destinations=[111, 112], state=False),
         TrafficLight(id=4, origins=[124], destinations=[124, 147, 148], state=False),
         TrafficLight(id=5, origins=[123], destinations=[123, 136], state=False),
         TrafficLight(id=6, origins=[148], destinations=[148, 111, 112], state=False),
         TrafficLight(id=7, origins=[147], destinations=[147], state=False)]

    return traffic_lights


def build_traffic_lights2() -> List[TrafficLight]:
    traffic_lights: List[TrafficLight] = \
        [TrafficLight(id=1, origins=[111], destinations=[111, 135], state=False),
         TrafficLight(id=2, origins=[112], destinations=[112, 147, 148], state=False),
         TrafficLight(id=3, origins=[135], destinations=[123, 124], state=False),
         TrafficLight(id=4, origins=[136], destinations=[136], state=False),
         TrafficLight(id=5, origins=[124], destinations=[124], state=False),
         TrafficLight(id=6, origins=[123], destinations=[123, 135, 136], state=False),
         TrafficLight(id=7, origins=[148], destinations=[111, 112], state=False),
         TrafficLight(id=8, origins=[147], destinations=[123, 124], state=False)]

    return traffic_lights


def build_roads() -> List[Road]:
    roads: List[Road] = \
        [Road(id=11, lanes=[Lane(id=111), Lane(id=112)], congection_level=5, from_side=RoadEnum.SOUTH, to_side=RoadEnum.NORTH),
         Road(id=12, lanes=[Lane(id=123), Lane(id=124)], congection_level=5, from_side=RoadEnum.NORTH, to_side=RoadEnum.SOUTH),
         Road(id=13, lanes=[Lane(id=135), Lane(id=136)], congection_level=5, from_side=RoadEnum.WEST, to_side=RoadEnum.EAST),
         Road(id=14, lanes=[Lane(id=147), Lane(id=148)], congection_level=5, from_side=RoadEnum.EAST, to_side=RoadEnum.WEST)]

    return roads


if __name__ == "__main__":
    main()
