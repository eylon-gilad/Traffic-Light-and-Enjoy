import time
from typing import Dict, Any

import requests

# TODO: Possibly integrate these tests into a formal testing framework.

build_junction_json: Dict[str, Any] = {
    "junction": {
        "traffic_lights": [
            {
                "traffic_light_index": 1,
                "input_index": [111, 112],
                "output_index": [111, 112],
                "state": 0
            },
            {
                "traffic_light_index": 2,
                "input_index": [135],
                "output_index": [135],
                "state": 0
            },
            {
                "traffic_light_index": 3,
                "input_index": [136],
                "output_index": [112],
                "state": 0
            },
            {
                "traffic_light_index": 4,
                "input_index": [124],
                "output_index": [148, 124],
                "state": 0
            },
            {
                "traffic_light_index": 5,
                "input_index": [123],
                "output_index": [123, 136],
                "state": 0
            },
            {
                "traffic_light_index": 6,
                "input_index": [148],
                "output_index": [148, 111],
                "state": 0
            },
            {
                "traffic_light_index": 7,
                "input_index": [147],
                "output_index": [147],
                "state": 0
            }
        ],
        "total_roads": 4,
        "roads": [
            {
                "from": "SOUTH",
                "to": "NORTH",
                "road_index": 11,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 111
                    },
                    {
                        "lane_index": 112
                    }
                ]
            },
            {
                "from": "NORTH",
                "to": "SOUTH",
                "road_index": 12,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 123
                    },
                    {
                        "lane_index": 124
                    }
                ]
            },
            {
                "from": "WEST",
                "to": "EAST",
                "road_index": 13,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 135
                    },
                    {
                        "lane_index": 136
                    }
                ]
            },
            {
                "from": "EAST",
                "to": "WEST",
                "road_index": 14,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 147
                    },
                    {
                        "lane_index": 148
                    }
                ]
            }
        ]
    }
}

junction_info_json: Dict[str, Any] = {
    "junction": {
        "traffic_lights": [
            {
                "traffic_light_index": 1,
                "input_index": [111, 112],
                "output_index": [111, 112],
                "state": 0
            },
            {
                "traffic_light_index": 2,
                "input_index": [135],
                "output_index": [135],
                "state": 0
            },
            {
                "traffic_light_index": 3,
                "input_index": [136],
                "output_index": [112],
                "state": 0
            },
            {
                "traffic_light_index": 4,
                "input_index": [124],
                "output_index": [148, 124],
                "state": 0
            },
            {
                "traffic_light_index": 5,
                "input_index": [123],
                "output_index": [123, 136],
                "state": 0
            },
            {
                "traffic_light_index": 6,
                "input_index": [148],
                "output_index": [148, 111],
                "state": 0
            },
            {
                "traffic_light_index": 7,
                "input_index": [147],
                "output_index": [147],
                "state": 0
            }
        ],
        "total_roads": 4,
        "roads": [
            {
                "road_index": 11,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 111,
                        "cars_creation": 3,
                        "cars": [
                            {
                                "car_index": 1001,
                                "dist": [0.2, 1.1],
                                "velocity": 30.0,
                                "dest": "road_20",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 1002,
                                "dist": [0.5, 1.5],
                                "velocity": 25.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE"
                            },
                            {
                                "car_index": 1003,
                                "dist": [2.2, 2.7],
                                "velocity": 10.0,
                                "dest": "road_30",
                                "car_type": "CAR"
                            }
                        ]
                    },
                    {
                        "lane_index": 112,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 1004,
                                "dist": [1.2],
                                "velocity": 12.0,
                                "dest": "road_10",
                                "car_type": "PEDESTRIAN"
                            },
                            {
                                "car_index": 1005,
                                "dist": [1.8, 2.0, 2.1],
                                "velocity": 8.0,
                                "dest": "road_40",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 12,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 123,
                        "cars_creation": 3,
                        "cars": [
                            {
                                "car_index": 2001,
                                "dist": [0.0],
                                "velocity": 0.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE"
                            },
                            {
                                "car_index": 2002,
                                "dist": [0.3, 0.7, 1.2],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 2003,
                                "dist": [1.5, 2.0],
                                "velocity": 7.0,
                                "dest": "road_30",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 124,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 2004,
                                "dist": [2.1, 2.5],
                                "velocity": 9.0,
                                "dest": "road_20",
                                "car_type": "PEDESTRIAN"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 13,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 135,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 3001,
                                "dist": [0.1],
                                "velocity": 15.0,
                                "dest": "road_20",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 3002,
                                "dist": [0.6, 1.4],
                                "velocity": 18.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 136,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 3003,
                                "dist": [2.2, 3.0],
                                "velocity": 12.0,
                                "dest": "road_40",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 14,
                "num_lanes": 2,
                "congection_level": 1,
                "lanes": [
                    {
                        "lane_index": 147,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 4001,
                                "dist": [2.0],
                                "velocity": 40.0,
                                "dest": "road_30",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 4002,
                                "dist": [2.1, 2.6],
                                "velocity": 10.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 148,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 4003,
                                "dist": [1.0, 1.4],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

dummy_data: Dict[str, Any] = {
    "junction": {
        "traffic_lights": [
            {
                "traffic_light_index": 1,
                "input_index": [111, 112],
                "output_index": [111, 112],
                "state": 0
            },
            {
                "traffic_light_index": 2,
                "input_index": [135],
                "output_index": [135],
                "state": 0
            },
            {
                "traffic_light_index": 3,
                "input_index": [136],
                "output_index": [112],
                "state": 0
            },
            {
                "traffic_light_index": 4,
                "input_index": [124],
                "output_index": [148, 124],
                "state": 0
            },
            {
                "traffic_light_index": 5,
                "input_index": [123],
                "output_index": [123, 136],
                "state": 0
            },
            {
                "traffic_light_index": 6,
                "input_index": [148],
                "output_index": [148, 111],
                "state": 0
            },
            {
                "traffic_light_index": 7,
                "input_index": [147],
                "output_index": [147],
                "state": 0
            }
        ],
        "total_roads": 4,
        "roads": [
            {
                "road_index": 11,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 111,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 1009,
                                "dist": [0.2, 1.1],
                                "velocity": 30.0,
                                "dest": "road_20",
                                "car_type": "CAR"
                            }
                        ]
                    },
                    {
                        "lane_index": 112,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 4561,
                                "dist": [1.2],
                                "velocity": 12.0,
                                "dest": "road_10",
                                "car_type": "PEDESTRIAN"
                            },
                            {
                                "car_index": 4562,
                                "dist": [1.8, 2.0, 2.1],
                                "velocity": 8.0,
                                "dest": "road_40",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 12,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 123,
                        "cars_creation": 3,
                        "cars": [
                            {
                                "car_index": 2001,
                                "dist": [0.0],
                                "velocity": 0.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE"
                            },
                            {
                                "car_index": 4564,
                                "dist": [0.3, 0.7, 1.2],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 4565,
                                "dist": [1.5, 2.0],
                                "velocity": 7.0,
                                "dest": "road_30",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 124,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 4566,
                                "dist": [2.1, 2.5],
                                "velocity": 9.0,
                                "dest": "road_20",
                                "car_type": "PEDESTRIAN"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 13,
                "num_lanes": 2,
                "congection_level": 5,
                "lanes": [
                    {
                        "lane_index": 135,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 4567,
                                "dist": [0.1],
                                "velocity": 15.0,
                                "dest": "road_20",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 4568,
                                "dist": [0.6, 1.4],
                                "velocity": 18.0,
                                "dest": "road_10",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 136,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 4569,
                                "dist": [2.2, 3.0],
                                "velocity": 12.0,
                                "dest": "road_40",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            },
            {
                "road_index": 14,
                "num_lanes": 2,
                "congection_level": 1,
                "lanes": [
                    {
                        "lane_index": 147,
                        "cars_creation": 2,
                        "cars": [
                            {
                                "car_index": 4570,
                                "dist": [2.0],
                                "velocity": 40.0,
                                "dest": "road_30",
                                "car_type": "CAR"
                            },
                            {
                                "car_index": 4571,
                                "dist": [2.1, 2.6],
                                "velocity": 10.0,
                                "dest": "road_20",
                                "car_type": "AMBULANCE"
                            }
                        ]
                    },
                    {
                        "lane_index": 148,
                        "cars_creation": 1,
                        "cars": [
                            {
                                "car_index": 4572,
                                "dist": [1.0, 1.4],
                                "velocity": 5.0,
                                "dest": "road_10",
                                "car_type": "CAR"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

JUNCTION_INFO_URL = "http://127.0.0.1:8080/junction-info"
TRAFFIC_LIGHT_STATE_URL = "http://127.0.0.1:8080/traffic-light-state"
START_ALGORITHM_URL = "http://127.0.0.1:8080/start-algorithm"
BUILD_JUNCTION_URL = "http://127.0.0.1:8080/build-junction"


def test_build_junction() -> None:
    """
    Tests building a junction without populated cars in any lane.
    """
    print(f"Sending POST to: {BUILD_JUNCTION_URL}")
    response = requests.post(BUILD_JUNCTION_URL, json=build_junction_json)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)
    print()


def test_start_algorithm() -> None:
    """
    Tests starting the ExpCarsOnTimeController or whichever algorithm is chosen in AlgoRunner.
    """
    print(f"Sending GET to: {START_ALGORITHM_URL}")
    response = requests.get(START_ALGORITHM_URL)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)


def test_post_junction_info(data: Dict[str, Any]) -> None:
    """
    Sends updated junction data (possibly with cars in lanes) to the '/junction-info' endpoint.
    """
    print(f"Sending POST to: {JUNCTION_INFO_URL}")
    response = requests.post(JUNCTION_INFO_URL, json=data)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)
    print()


def test_get_traffic_light_state() -> None:
    """
    Fetches the current traffic light states from the server.
    """
    print(f"Sending GET to: {TRAFFIC_LIGHT_STATE_URL}")
    response = requests.get(TRAFFIC_LIGHT_STATE_URL)
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:", response.json())
    except ValueError:
        print("Response Text:", response.text)
    print()


def repeated_get_traffic_light_state(url: str, iterations: int = 100, delay: float = 5.0) -> None:
    """
    Repeatedly calls the '/traffic-light-state' endpoint to observe changes over time.
    """
    print(f"Will GET {iterations} times from {url}, every {delay} seconds.")
    for i in range(iterations):
        print(f"Request #{i + 1}")
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
    # 1. Build a junction without cars
    test_build_junction()

    # 2. Start the algorithm
    test_start_algorithm()

    # 3. POST new junction data with cars
    test_post_junction_info(data=junction_info_json)

    # 4. Check traffic light states
    test_get_traffic_light_state()
    time.sleep(5)

    # 5. Post more data
    test_post_junction_info(data=dummy_data)
    time.sleep(5)

    # 6. Check traffic light states again
    test_get_traffic_light_state()

    # 7. Optionally do repeated calls
    # repeated_get_traffic_light_state(TRAFFIC_LIGHT_STATE_URL, iterations=100, delay=5.0)
