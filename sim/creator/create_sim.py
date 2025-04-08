import json
import random
from utils.Lane import Lane
from utils.Junction import Junction
from utils.Road import Road
from utils.RoadEnum import RoadEnum
from utils.TrafficLight import TrafficLight

VELOCITY_OPTIONS: list[int] = [30, 50, 80, 100, 110, 120]
RED_LIGHT: bool = False


def random_remove_traffic_lights(amount_road: int = 4) -> list[tuple[int, int]]:
    """
    Randomly selects singular lights to remove from the junction.

    :param amount_road: The number of roads that lights could lead to (default is 4).
    :return: A list of pairs representing traffic lights to be removed.
    """
    remove_lights: list[tuple[int, int]] = []
    remove_amount: int = random.randint(0, amount_road**2 - 1)

    for _ in range(remove_amount):
        road_pair: tuple[int, int] = (
            random.randint(0, amount_road),
            random.randint(0, amount_road),
        )
        if road_pair[0] != road_pair[1]:
            remove_lights.append(road_pair)
    return remove_lights


def get_random_array_numbers(largest_size: int) -> list[int]:
    """
    Generates an array of random numbers.

    :param largest_size: The highest possible number in the array.
    :return: An array of random numbers between 0 and largest_size.
    """
    a_size: int = random.randint(1, largest_size - 1)
    a: list[int] = list(range(largest_size))
    random.shuffle(a)
    return a[:a_size]


def random_merge_lights(amount_road: int = 4) -> list[tuple[list[int], list[int]]]:
    """
    Randomly creates non-singular lights in the junction.

    :param amount_road: The number of possible directions traffic can lead to.
    :return: A list of traffic lights represented by the roads they control.
    """
    merged_lights: list[tuple[list[int], list[int]]] = []
    merged_amount: int = random.randint(0, amount_road**2 - 1)
    for _ in range(merged_amount):
        inputs: list[int] = get_random_array_numbers(amount_road)
        outputs: list[int] = get_random_array_numbers(amount_road)
        merged_lights.append((inputs, outputs))
    return merged_lights


def create_light(
    jun_index: int = 1,
    traffic_light_index: int = None,
    input_index: list[int] = None,
    output_index: list[int] = None,
    state: bool = RED_LIGHT,
) -> TrafficLight:
    """
    Creates a traffic light object.

    :param jun_index: The junction index.
    :param traffic_light_index: The traffic light index.
    :param input_index: The roads where cars are entering.
    :param output_index: The roads where cars will exit.
    :param state: The state of the light (red=0, green=1).
    :return: A TrafficLight object.
    """
    if traffic_light_index is None or input_index is None or output_index is None:
        raise ValueError("Missing parameters for 'create_light' function.")

    input_index = [jun_index * 10 + x for x in input_index]
    output_index = [jun_index * 10 + x for x in output_index]

    return TrafficLight(traffic_light_index, input_index, output_index, state)


def create_all_lights(
    jun_index: int = 1,
    amount_road: int = 4,
    black_list: list[tuple[int, int]] = None,
    merged_lights: list[tuple[list[int], list[int]]] = None,
) -> list[TrafficLight]:
    """
    Creates an array of all the traffic lights.

    :param jun_index: The junction index.
    :param amount_road: The number of possible roads the lights affect.
    :param black_list: Specific traffic lights that are not needed.
    :param merged_lights: Lights with more than one input/output.
    :return: A list of all traffic lights in this situation.
    """
    if black_list is None:
        black_list = []
    if merged_lights is None:
        merged_lights = []

    counter = 0
    all_traffic_lights: list[TrafficLight] = []

    for inputs, outputs in merged_lights:
        traffic_light = create_light(jun_index, counter, inputs, outputs, RED_LIGHT)
        all_traffic_lights.append(traffic_light)
        counter += 1
        for i in inputs:
            for j in outputs:
                black_list.append((i, j))

    for i in range(amount_road):
        for j in range(amount_road):
            if (i, j) not in black_list:
                all_traffic_lights.append(
                    create_light(jun_index, counter, [i], [j], RED_LIGHT)
                )
                counter += 1

    return all_traffic_lights


def create_lanes(road_index: int = 1, amount_lanes: int = 3) -> list[Lane]:
    """
    Creates all the needed lanes in a certain road.

    :param road_index: The index of the road.
    :param amount_lanes: The number of lanes to create.
    :return: A list of Lane objects in a certain road.
    """
    lanes: list[Lane] = []
    for i in range(amount_lanes):
        lane_index = road_index * 10 + i
        cars_creation = random.randint(1, 100)
        max_vel = random.choice(VELOCITY_OPTIONS)
        lane = Lane(lane_index, car_creation=cars_creation, lane_max_vel=max_vel)
        lanes.append(lane)
    return lanes


def create_roads(junction_index: int = 1, amount_road: int = 4) -> list[Road]:
    """
    Creates all the roads in a certain junction.

    :param junction_index: The index of the junction.
    :param amount_road: The number of roads to create.
    :return: A list of Road objects.
    """
    roads: list[Road] = []
    for i in range(amount_road):
        index = junction_index * 10 + i
        directions = index_to_directions(i)
        road = Road(
            index,
            create_lanes(index, 3),
            congection_level=0,
            from_side=directions[0],
            to_side=directions[1],
        )

        roads.append(road)
    return roads


def index_to_directions(road_index: int):
    """
    returning directions from index
    :input: the road index
    :output: two direction where the road starts and end
    """

    index_direction = [0, 2, 1, 3]
    from_direction = index_direction[road_index]
    if road_index % 2 == 0:
        to_directions = index_direction[road_index + 1]
    else:
        to_directions = index_direction[road_index - 1]

    return from_direction, to_directions


def create_junction(junction_index: int = 1) -> Junction:
    """
    Creates a junction object.

    :param junction_index: The index of the junction.
    :return: A Junction object.
    """
    total_roads = 4
    merged_lights = random_merge_lights(total_roads)
    remove_light = random_remove_traffic_lights(total_roads)
    return Junction(
        junction_index,
        create_all_lights(junction_index, total_roads, remove_light, merged_lights),
        create_roads(junction_index, total_roads),
    )


def create_all_json() -> str:
    """
    Creates all the needed objects and converts them into JSON.

    :return: JSON data for a certain simulation.
    """
    all_data = {"junction": create_junction()}
    return json.dumps(all_data, indent=4)


def direction_to_index(direction: RoadEnum, junction: Junction):
    """
    returning index from directions
    :input: two direction where the road starts and end
    :output: the road index
    """
    for road in junction.get_roads():
        if road.from_side == direction:
            return road.get_id()
    # return junction_id * 10 + dirction_index[direction] + 1


def main() -> None:
    test = create_junction(1)
    print(test)


if __name__ == "__main__":
    main()
