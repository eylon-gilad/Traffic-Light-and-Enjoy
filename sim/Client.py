import json
import logging
from typing import List, Dict, Any, Optional

from requests import get, post, RequestException, Response

from utils.Junction import Junction
from utils.TrafficLight import TrafficLight

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:
    """
    A client class responsible for communicating with a traffic-junction server.
    Sends requests to build junctions, retrieve traffic light states, and start
    traffic-light algorithms.

    Changes:
    - Added docstrings, type hints, and improved error handling/logging.
    - Preserved existing functionality.
    """

    JUNCTION_INFO_URL: str = "http://127.0.0.1:8080/junction-info"
    TRAFFIC_LIGHT_STATE_URL: str = "http://127.0.0.1:8080/traffic-light-state"
    START_ALGORITHM_URL: str = "http://127.0.0.1:8080/start-algorithm"
    BUILD_JUNCTION_URL: str = "http://127.0.0.1:8080/build-junction"

    @staticmethod
    def start_algorithm() -> None:
        """
        Send a GET request to start the traffic-light algorithm on the server.

        If the request fails (network issue or invalid response), logs the error
        instead of raising an exception.
        """
        logger.debug("Attempting to start traffic-light algorithm.")
        try:
            response: Response = get(Client.START_ALGORITHM_URL)
            response.raise_for_status()  # Raises HTTPError for bad HTTP responses
        except RequestException as e:
            logger.error(f"Network or HTTP error in start_algorithm: {e}")
        except Exception as e:
            # Catch-all for unforeseen exceptions; logs details for debugging
            logger.error(f"Unexpected error in start_algorithm: {e}")

    @staticmethod
    def send_build_junction(junction: Junction) -> None:
        """
        Send a POST request to build a junction on the server with the specified junction data.

        Args:
            junction (Junction): The junction object containing roads, lanes, and traffic lights.

        Logs response status code and JSON (or raw text if JSON is invalid).
        """
        logger.debug(f"Sending POST to build junction: {Client.BUILD_JUNCTION_URL}")
        junction_json: Dict = Client.__junction_to_build_junction_json(junction)

        try:
            response: Response = post(Client.BUILD_JUNCTION_URL, json=junction_json)
            logger.info(f"Build Junction - Status Code: {response.status_code}")

            try:
                logger.debug(f"Build Junction - Response JSON: {response.json()}")
            except ValueError:
                logger.debug(f"Build Junction - Response Text: {response.text}")
        except RequestException as e:
            logger.error(f"Error sending build_junction request: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in send_build_junction: {e}")

    @staticmethod
    def send_junction_info(junction: Junction) -> None:
        """
        Sends the junction information to the server via a POST request.

        Args:
            junction (Junction): The junction object to send.

        Logs response status code and JSON (or raw text if JSON is invalid).
        """
        logger.debug(f"Sending POST with junction info to: {Client.JUNCTION_INFO_URL}")
        junction_json: Dict = Client.__junction_to_junction_info_json(junction)

        try:
            response: Response = post(Client.JUNCTION_INFO_URL, json=junction_json)
            logger.info(f"Junction Info - Status Code: {response.status_code}")

            try:
                logger.debug(f"Junction Info - Response JSON: {response.json()}")
            except ValueError:
                logger.debug(f"Junction Info - Response Text: {response.text}")
        except RequestException as e:
            logger.error(f"Error sending junction info request: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in send_junction_info: {e}")

    @staticmethod
    def get_traffic_lights_states() -> List[TrafficLight]:
        """
        Retrieve the current traffic light states from the server with a GET request.

        Returns:
            List[TrafficLight]: A list of TrafficLight objects representing
            the current state of each traffic light.
        """
        logger.debug(f"Requesting traffic light states from: {Client.TRAFFIC_LIGHT_STATE_URL}")
        traffic_lights: List[TrafficLight] = []
        try:
            response: Response = get(Client.TRAFFIC_LIGHT_STATE_URL)
            logger.info(f"Traffic Light State - Status Code: {response.status_code}")

            try:
                response_data: List[Dict[str, Any]] = response.json()
                logger.debug(f"Traffic Light State - Response JSON: {response_data}")
                traffic_lights = Client.__parse_traffic_lights_response(response_data)
            except ValueError:
                logger.debug(f"Traffic Light State - Response Text: {response.text}")
        except RequestException as e:
            logger.error(f"Error retrieving traffic light states: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_traffic_lights_states: {e}")

        return traffic_lights

    @staticmethod
    def __parse_traffic_lights_response(response_json: List[Dict[str, Any]]) -> List[TrafficLight]:
        """
        Parse the response JSON containing traffic lights data and construct a list of TrafficLight objects.

        Args:
            response_json (Dict[str, Any]): Dictionary containing 'traffic_lights' key with traffic light data.

        Returns:
            List[TrafficLight]: A list of TrafficLight objects, each initialized with ID, origins, destinations, and state.
        """
        traffic_lights: List[TrafficLight] = []

        # Safely retrieve the traffic_lights data
        traffic_lights_data = response_json[0]["traffic_lights"]
        if not isinstance(traffic_lights_data, list):
            logger.error("Invalid traffic_lights data format.")
            return traffic_lights

        for tl in traffic_lights_data:
            try:
                traffic_lights.append(TrafficLight(
                    light_id=int(tl["traffic_light_index"]),
                    origins=list(tl["origins"]),
                    destinations=list(tl["destinations"]),
                    state=bool(tl["state"])
                ))
            except (KeyError, ValueError, TypeError) as ex:
                logger.error(f"Skipping malformed traffic light data: {tl}, Error: {ex}")
                # TODO: Confirm how to handle partial or malformed traffic light data
                continue

        return traffic_lights

    @staticmethod
    def __junction_to_junction_info_json(junction: Junction) -> Dict:
        """
        Convert a Junction object into a JSON string with the structure:

        {
            "junction": {
                "traffic_lights": [
                    {
                        "traffic_light_index": <int>,
                        "input_index": <list of int>,
                        "output_index": <list of int>,
                        "state": <int>  # 0 for red, 1 for green
                    }
                ],
                "total_roads": <int>,
                "roads": [
                    {
                        "road_index": <int>,
                        "num_lanes": <int>,
                        "congection_level": <int>,
                        "lanes": [
                            {
                                "lane_index": <int>,
                                "cars_creation": <float>,
                                "cars": [
                                    {
                                        "car_index": <int>,
                                        "dist": <list of float>,
                                        "velocity": <float>,
                                        "dest": <str>,
                                        "car_type": <str>
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        Args:
            junction (Junction): The junction object containing roads, lanes, traffic lights, etc.

        Returns:
            str: A JSON-formatted string representing the junction data.
        """
        junction_dict: Dict[str, Any] = {
            "junction": {
                "traffic_lights": [],
                "total_roads": len(junction.get_roads()),
                "roads": []
            }
        }

        # Populate traffic_lights
        for tl in junction.get_traffic_lights():
            traffic_light_state: int = 1 if tl.get_state() else 0
            junction_dict["junction"]["traffic_lights"].append({
                "traffic_light_index": tl.get_id(),
                "input_index": tl.get_origins(),
                "output_index": tl.get_destinations(),
                "state": traffic_light_state
            })

        # Populate roads
        for road in junction.get_roads():
            congection_level = getattr(road, "congection_level", 0)

            road_info: Dict[str, Any] = {
                "road_index": road.get_id(),
                "num_lanes": len(road.get_lanes()),
                "congection_level": congection_level,
                "lanes": []
            }

            for lane in road.get_lanes():
                lane_info: Dict[str, Any] = {
                    "lane_index": lane.get_id(),
                    "cars_creation": lane.get_car_creation(),
                    "cars": []
                }
                for car in lane.get_cars():
                    if car.get_dist() <= 0:
                        continue
                    car_info: Dict[str, Any] = {
                        "car_index": car.get_id(),
                        "dist": [car.get_dist()],
                        "velocity": car.get_velocity(),
                        "dest": str(car.get_dest()),
                        "car_type": car.get_car_type(),
                    }
                    lane_info["cars"].append(car_info)

                road_info["lanes"].append(lane_info)
            junction_dict["junction"]["roads"].append(road_info)

        return junction_dict

    @staticmethod
    def __junction_to_build_junction_json(junction: Junction) -> Dict:
        """
        Build a JSON representation of the given junction for server consumption.

        Example structure:
        {
            "junction": {
                "traffic_lights": [
                    {
                        "traffic_light_index": <int>,
                        "input_index": <list of int>,
                        "output_index": <list of int>,
                        "state": <bool or int>
                    }
                ],
                "total_roads": <int>,
                "roads": [
                    {
                        "road_index": <int>,
                        "num_lanes": <int>,
                        "congection_level": 0,
                        "lanes": [
                            {
                                "lane_index": <int>
                            }
                        ]
                    }
                ]
            }
        }

        Args:
            junction (Junction): The junction object containing roads, traffic lights, etc.

        Returns:
            str: A JSON-formatted string representing the junction data.
        """
        junction_dict: Dict[str, Any] = {
            "junction": {
                "traffic_lights": [],
                "total_roads": len(junction.get_roads()),
                "roads": []
            }
        }

        # Populate traffic lights data
        for traffic_light in junction.traffic_lights:
            junction_dict["junction"]["traffic_lights"].append({
                "traffic_light_index": traffic_light.id,
                "input_index": traffic_light.origins,
                "output_index": traffic_light.destinations,
                "state": traffic_light.state
            })

        # Populate roads data
        for road in junction.roads:
            road_info: Dict[str, Any] = {
                "road_index": road.id,
                "num_lanes": len(road.get_lanes()),
                "from": road.get_from_side().name,
                "to": road.get_to_side().name,
                "congection_level": 0,  # Intentionally left as 0 to match original code
                "lanes": []
            }

            for lane in road.lanes:
                lane_info: Dict[str, Any] = {
                    "lane_index": lane.id,
                }
                road_info["lanes"].append(lane_info)

            junction_dict["junction"]["roads"].append(road_info)

        return junction_dict
