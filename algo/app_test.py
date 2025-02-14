import requests
import time
from typing import Dict, Any

# Large dummy data with 4 roads, multiple lanes, traffic lights, etc.
dummy_data: Dict[str, Any] = {
    "junction": {
        "traffic_lights": [
            {
                "traffic_light_index": 100,
                "input_index": [101, 201],
                "output_index": [102, 301],
                "state": 1,
            },
            {
                "traffic_light_index": 200,
                "input_index": [302, 402],
                "output_index": [202, 303],
                "state": 0,
            },
            {
                "traffic_light_index": 300,
                "input_index": [203, 301],
                "output_index": [304, 401],
                "state": 1,
            },
            {
                "traffic_light_index": 400,
                "input_index": [101, 302],
                "output_index": [102, 303],
                "state": 1,
            },
            {
                "traffic_light_index": 500,
                "input_index": [304],
                "output_index": [404],
                "state": 0,
            },
            {
                "traffic_light_index": 600,
                "input_index": [201, 401],
                "output_index": [202, 402],
                "state": 1,
            },
        ],
        "total_roads": 4,
        "roads": [
            {
                "road_index": 10,
                "num_lanes": 3,
                "congection_level": 2,
                "lanes": [
                    {
                        "lane_index": 101,
                        "cars_creation": 5,
                        "cars": [
                            {
                                "car_index": 1001,
                                "dist": [0.2, 1.1],
                                "velocity": 30.0,
                                "dest": "road_20",
                                "car_type": "CAR",
                            },
                            {
                                "car_index": 1002,
                                "dist": [0.5, 1.5],
                                "velocity": 25.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE",
                            },
                            {
                                "car_index": 1003,
                                "dist": [2.2, 2.7],
                                "velocity": 10.0,
                                "dest": "road_30",
                                "car_type": "CAR",
                            },
                        ],
                    },
                    {
                        "lane_index": 102,
                        "cars_creation": 3,
                        "cars": [
                            {
                                "car_index": 1004,
                                "dist": [1.2],
                                "velocity": 12.0,
                                "dest": "road_10",
                                "car_type": "PEDESTRIAN",
                            },
                            {
                                "car_index": 1005,
                                "dist": [1.8, 2.0, 2.1],
                                "velocity": 8.0,
                                "dest": "road_40",
                                "car_type": "CAR",
                            },
                        ],
                    },
                    {
                        "lane_index": 103,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 1006,
                                "dist": [3.1],
                                "velocity": 15.0,
                                "dest": "road_20",
                                "car_type": "CAR",
                            }
                        ],
                    },
                ],
            },
            {
                "road_index": 20,
                "num_lanes": 2,
                "congection_level": 0,
                "lanes": [
                    {
                        "lane_index": 201,
                        "cars_creation": 4,
                        "cars": [
                            {
                                "car_index": 2001,
                                "dist": [0.0],
                                "velocity": 0.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE",
                            },
                            {
                                "car_index": 2002,
                                "dist": [0.3, 0.7, 1.2],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR",
                            },
                            {
                                "car_index": 2003,
                                "dist": [1.5, 2.0],
                                "velocity": 7.0,
                                "dest": "road_30",
                                "car_type": "AMBULANCE",
                            },
                        ],
                    },
                    {
                        "lane_index": 202,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 2004,
                                "dist": [2.1, 2.5],
                                "velocity": 9.0,
                                "dest": "road_20",
                                "car_type": "PEDESTRIAN",
                            }
                        ],
                    },
                ],
            },
            {
                "road_index": 30,
                "num_lanes": 4,
                "congection_level": 3,
                "lanes": [
                    {
                        "lane_index": 301,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 3001,
                                "dist": [0.1],
                                "velocity": 15.0,
                                "dest": "road_20",
                                "car_type": "CAR",
                            },
                            {
                                "car_index": 3002,
                                "dist": [0.6, 1.4],
                                "velocity": 18.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE",
                            },
                        ],
                    },
                    {
                        "lane_index": 302,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 3003,
                                "dist": [2.2, 3.0],
                                "velocity": 12.0,
                                "dest": "road_40",
                                "car_type": "CAR",
                            }
                        ],
                    },
                    {
                        "lane_index": 303,
                        "cars_creation": 3,
                        "cars": [
                            {
                                "car_index": 3004,
                                "dist": [1.0],
                                "velocity": 20.0,
                                "dest": "road_10",
                                "car_type": "CAR",
                            },
                            {
                                "car_index": 3005,
                                "dist": [1.5, 2.6],
                                "velocity": 11.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE",
                            },
                            {
                                "car_index": 3006,
                                "dist": [3.1, 3.5],
                                "velocity": 0.0,
                                "dest": "road_30",
                                "car_type": "PEDESTRIAN",
                            },
                        ],
                    },
                    {
                        "lane_index": 304,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 3007,
                                "dist": [2.4],
                                "velocity": 22.5,
                                "dest": "road_40",
                                "car_type": "CAR",
                            }
                        ],
                    },
                ],
            },
            {
                "road_index": 40,
                "num_lanes": 3,
                "congection_level": 1,
                "lanes": [
                    {
                        "lane_index": 401,
                        "cars_creation": 5,
                        "cars": [
                            {
                                "car_index": 4001,
                                "dist": [2.0],
                                "velocity": 40.0,
                                "dest": "road_30",
                                "car_type": "CAR",
                            },
                            {
                                "car_index": 4002,
                                "dist": [2.1, 2.6],
                                "velocity": 10.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE",
                            },
                        ],
                    },
                    {
                        "lane_index": 402,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 4003,
                                "dist": [1.0, 1.4],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR",
                            }
                        ],
                    },
                    {
                        "lane_index": 404,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 4004,
                                "dist": [0.0],
                                "velocity": 0.0,
                                "dest": "road_30",
                                "car_type": "PEDESTRIAN",
                            }
                        ],
                    },
                ],
            },
        ],
    }
}

POST_URL = "http://127.0.0.1:8080/junction-info"
GET_URL = "http://127.0.0.1:8080/traffic-light-state"


def test_post_junction_info() -> None:
    """
    Sends dummy_data to the '/junction-info' endpoint to create/modify
    the Junction object on the server.
    """
    print(f"Sending POST to: {POST_URL}")
    response = requests.post(POST_URL, json=dummy_data)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)
    print()


def test_get_traffic_light_state() -> None:
    """
    Fetches the current traffic light states from the server at '/traffic-light-state'.
    """
    print(f"Sending GET to: {GET_URL}")
    response = requests.get(GET_URL)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)
    print()


def repeated_get_traffic_light_state(
    url: str, iterations: int = 100, delay: float = 5.0
) -> None:
    """
    Repeatedly GET the /traffic-light-state endpoint `iterations` times,
    waiting `delay` seconds between each call.

    :param url: The URL of the traffic-light-state endpoint.
    :param iterations: Number of times to call the endpoint.
    :param delay: Delay (in seconds) between successive calls.
    """
    print(f"Will GET {iterations} times from {url}, every {delay} seconds.")
    for i in range(iterations):
        print(f"Request #{i+1}")
        try:
            response = requests.get(url)
            print("Status Code:", response.status_code)
            try:
                print("Response JSON:", response.json())
            except ValueError:
                print("Response Text:", response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error during GET request: {e}")

        time.sleep(delay)
    print("Finished repeated GET requests.\n")


if __name__ == "__main__":
    # 1. POST the large dummy data to set up the junction
    test_post_junction_info()

    # 2. Perform an immediate single GET request to see if data is there
    test_get_traffic_light_state()

    # 3. Repeatedly call GET /traffic-light-state 100 times every 5 seconds
    repeated_get_traffic_light_state(GET_URL, iterations=100, delay=5.0)
