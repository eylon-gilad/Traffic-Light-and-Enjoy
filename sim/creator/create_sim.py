import json
import random
from utils.Lane import Lane
from utils.Junction import Junction
from utils.Road import Road
from utils.TrafficLight import TrafficLight

VELOCOTY_OPTIONS=[30,50,80,100,110,120]
RED_LIGHT = 0


def random_remove_trraficlights(amount_road: int | None = 4):
    """
    randomly selects singular lights to remove from the junction
    input:amount_road(all the roads the lights could lead, which is how we represents lights)
    outputs: array of pairs which represent each trafficlight
    """
    create_all = 0
    remove_lights = []
    remove_amount = random.randint(create_all, amount_road ** 2 - 1)

    for i in range(remove_amount):
        road_pair = (
            random.randint(create_all, amount_road),
            random.randint(create_all, amount_road)
        )
        if road_pair[0] != road_pair[1]:
            remove_lights.append(road_pair)
    return remove_lights


def get_random_array_numbers(largest_size):
    """
    gives array of random numbers
    input: largest_size(the highest num)
    output: array of random numbers between 0-largest_size
    """
    merge_one = 1
    a_size = random.randint(merge_one, largest_size - 1)
    a = list(range(largest_size))
    random.shuffle(a)
    a = a[:a_size]
    return a


def random_marge_lights(amount_road: int | None = 4):
    """
    randomly create the non-singular lights in the junction
    input:amount_road(all possible directions, the traffic could lead to)
    output: array of traffic lights which is represented by the roads he controls(input) and leeds to(output)
    """
    dont_merge = 0

    merged_lights = []
    merged_amount = random.randint(dont_merge, amount_road ** 2 - 1)
    for i in range(merged_amount):
        inputs = get_random_array_numbers(amount_road)
        outputs = get_random_array_numbers(amount_road)
        merged_lights.append((inputs, outputs))
    return merged_lights


def create_light(jun_index: int = 1, traffic_light_index: int = None, input_index: list[int] = None,
                 output_index: list[int] = None,
                 state: bool = 0):
    """
    create the traffic light object
    input: 
    traffic_light_index,
    inputs_index(the roads the cars are in),
    output_index(roads the car will drive to),
    state(red-0 or green-1)

    output: traffic light object
    """
    if traffic_light_index is None or input_index is None or input_index is None:
        raise Exception("wrong use of func")


    input_index = [jun_index * 10 + x for x in input_index]
    output_index = [jun_index * 10 + x for x in output_index]

    traffic_light = TrafficLight(
        traffic_light_index,
        input_index,
        output_index,
        state
    )
    return traffic_light


def create_all_lights(jun_index: int = 1, amount_road: int | None = 4, black_list: list[tuple[int]] | None = [],
                      merged_lights: list[tuple[list, list]] | None = [([], [])]):
    """
    create array of all the traffic lights
    input:
    amount_road(the amount of possible roads the lights effects)
    black_list(specific traffic lights that we dont need- only singular input\output)
    merged_lights(lights with more than one input\output)
    output: array of all the traffic light in this situation
    """

    counter = 0
    all_traffic_lights = []
    removed_lights = black_list

    for (inputs, outputs) in merged_lights:
        traffic_light = create_light(jun_index,counter, inputs, outputs, RED_LIGHT)
        all_traffic_lights.append(traffic_light)
        counter += 1
        for i in inputs:
            for j in outputs:
                removed_lights.append((i, j))

    for i in range(amount_road):
        for j in range(amount_road):
            if (i, j) not in removed_lights:
                all_traffic_lights.append(create_light(jun_index, counter, [i], [j], RED_LIGHT))
                counter += 1

    return all_traffic_lights


def create_lanes(road_index: int = 1, amount_lanes: int = 3):
    """
    create all the needed lanes in a certain road
    input:amount_lanes(how much to create)
    output: array of the lane obj in a certain road
    """
    highest_car_reation = 100
    lowest_car_reation = 1
    lanes = []
    for i in range(amount_lanes):
        lane_index = road_index * 10 + i
        cars_creation = random.randint(lowest_car_reation, highest_car_reation)
        max_vel=VELOCOTY_OPTIONS[random.randint(0, len(VELOCOTY_OPTIONS)-1)]
        lane = Lane(
            lane_index,
            car_creation=cars_creation,
            lane_max_vel=max_vel
        )
        lanes.append(lane)
    return lanes


def create_roads(junction_index: int = 1, amount_road: int = 4):
    """
    create all the roads in a certain junction
    input:amount_road(how much to create)
    output: array of the road obj in a certain road
    """
    roads = []
    for i in range(amount_road):
        num_lanes = 3  # random.randint(1,4)
        index = junction_index * 10 + i
        road = Road(
            index,
            create_lanes(index, num_lanes)
        )
        roads.append(road)
    return roads


def create_junction(junction_index: int = 1):
    """
    create the junction obj
    input:junction_index
    output:junction obj
    """
    total_roads = 4  # random.randint(1,4)
    merged_lights = random_marge_lights(total_roads)
    remove_light = random_remove_trraficlights(total_roads)
    jun = Junction(
        junction_index,
        create_all_lights(junction_index, total_roads, remove_light, merged_lights),
        create_roads(junction_index, total_roads)
    )
    return jun


def create_all_json():
    """
    create all the needed objects and turn them into json
    input: none
    output: all the data for a certain sim in json
    """
    json_indetation = 4
    all_data = {"junction": create_junction()}
    return json.dumps(all_data, indent=json_indetation)


def main():
    test = create_junction(1)
    print(test)


if __name__ == "__main__":
    main()
