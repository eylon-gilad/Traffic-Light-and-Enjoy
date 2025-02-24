import json
import random

from utils.Car import Car
from utils.Junction import Junction
from utils.Lane import Lane
from utils.Road import Road
from utils.TrafficLight import TrafficLight


def random_remove_trraficLights(amount_road: int | None = 4):
    """
    randomlly selects singular lights to remove from the junction
    input:amount_road(all the roads the lights could leed, which is how we represents lights)
    outputs: array of pairs which represent each trafficlight
    """
    CREATE_ALL = 0
    remove_lights = []
    remove_amount = random.randint(CREATE_ALL, amount_road**2 - 1)

    for i in range(remove_amount):
        road_pair = (
            random.randint(CREATE_ALL, amount_road),
            random.randint(CREATE_ALL, amount_road),
        )
        remove_lights.append(road_pair)
    return remove_lights


def get_random_array_numbers(largest_size):
    """
    gives array of random numbers
    input: largest_size(the highest num)
    output: array of random numbers between 0-largest_size
    """
    MARGE_ONE = 1
    a_size = random.randint(MARGE_ONE, largest_size - 1)
    a = list(range(largest_size))
    random.shuffle(a)
    a = a[:a_size]
    return a


def random_marge_lights(amount_road: int | None = 4):
    """
    randonly create the non sigular lights in the junction
    input:amount_road(all possible directions, the traffic could leed to)
    output: array of trafic lights which is represented by the roads he controll(input) and leeds to(output)
    """
    DONT_MARGE = 0

    marged_lights = []
    marged_amount = random.randint(DONT_MARGE, amount_road**2 - 1)
    for i in range(marged_amount):
        inputs = get_random_array_numbers(amount_road)
        outputs = get_random_array_numbers(amount_road)
        marged_lights.append((inputs, outputs))
    return marged_lights


def create_light(
    traffic_light_index: int,
    input_index: list[int],
    output_index: list[int],
    state: bool | None = 0,
):
    """
    create the traffic light object
    input:
    traffic_light_index,
    inputs_index(the roads the cars are in),
    output_index(roads the car will drive to),
    state(red-0 or green-1)

    output: trafic light object
    """
    traffic_light = {}
    traffic_light["traffic_light_index"] = traffic_light_index
    if type(input_index) == int:
        traffic_light["input_index"] = [input_index]
        traffic_light["output_index"] = [output_index]
    else:
        traffic_light["input_index"] = input_index
        traffic_light["output_index"] = output_index
    traffic_light["state"] = state
    return traffic_light


def create_all_lights(
    amount_road: int | None = 4,
    black_list: list[tuple[int]] | None = [],
    merged_lights: list[tuple[list, list]] | None = [([], [])],
):
    """
    create array of all the traffic lights
    input:
    amount_road(the amout of possible roads the lights effects)
    black_list(specific trafic lights that we dont need- only singular input\output)
    merged_lights(lights with more than one input\output)
    output: array of all the traffic light in this situation
    """
    RED_LIGHT = 0
    counter = 0
    all_traffic_Lights = []
    removed_lights = black_list

    for inputs, outputs in merged_lights:
        traffic_light = create_light(counter, inputs, outputs, RED_LIGHT)
        all_traffic_Lights.append(traffic_light)
        counter += 1
        for i in inputs:
            for j in outputs:
                removed_lights.append((i, j))

    for i in range(1, amount_road + 1):
        for j in range(1, amount_road + 1):
            if (i, j) not in removed_lights:
                all_traffic_Lights.append(create_light(counter, i, j, RED_LIGHT))
                counter += 1

    return all_traffic_Lights


def create_lanes(amount_lanes: int | None = 3):
    """
    create all the needed lanes in a certain road
    input:amount_lanes(how much to create)
    output: array of the lane obj in a certain road
    """
    HIGHEST_PRECENTAGE = 100
    LOWEST_PRECENTAGE = 1
    lanes = []
    for i in range(1, amount_lanes + 1):
        lane = {}
        lane["lane_index"] = i
        # precentage of car creation, every sub-second
        lane["cars_creation"] = random.randint(LOWEST_PRECENTAGE, HIGHEST_PRECENTAGE)
        lanes.append(lane)
    return lanes


def create_roads(amount_road: int | None = 4):
    """
    create all the roads in a certaion junction
    input:amount_road(how much to create)
    output: array of the road obj in a certain road
    """
    roads = []
    for i in range(1, amount_road + 1):
        road = {}
        road["road_index"] = i
        road["num_lanes"] = 3  # random.randint(1,4)
        road["lanes"] = create_lanes(road["num_lanes"])
        roads.append(road)
    return roads


def create_junction(junction_index: int | None = 1):
    """
    create the junction obj
    input:junction_index
    output:junction obj
    """
    juanction = {}
    juanction["junction_index"] = junction_index
    juanction["total_roads"] = 4  # random.randint(1,4)
    juanction["roads"] = create_roads(juanction["total_roads"])
    marged_lights = random_marge_lights(juanction["total_roads"])
    remove_light = random_remove_trraficLights(juanction["total_roads"])
    juanction["traffic_lights"] = create_all_lights(
        juanction["total_roads"], remove_light, marged_lights
    )
    return juanction


def create_all_json():
    """
    create all the needed objects and turn them into json
    input: none
    output: all the data for a certain sim in json
    """
    JSON_INDETATION = 4
    all_data = {}
    all_data["junction"] = create_junction()
    return json.dumps(all_data, indent=JSON_INDETATION)


def main():
    for i in range(10):
        test = create_all_json()
        with open(f"sim\creator\examples\example{i}.json", "w") as f:
            f.write(test)
        print(test)


if __name__ == "__main__":
    main()
