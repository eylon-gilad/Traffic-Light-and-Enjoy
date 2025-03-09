import requests
from typing import List, Dict

from utils.Junction import Junction
from utils.TrafficLight import TrafficLight


class Client:
    START_ALGORITH_URL = "http://127.0.0.1:8080/start-algorithm"
    UPDATE_JUNCTION_URL = "http://127.0.0.1:8080/junction-info"
    GET_TRAFFIC_LIGHTS_URL = "http://127.0.0.1:8080/traffic-light-state"

    @staticmethod
    def start_algorithm(junction: Junction) -> List[TrafficLight]:
        response = requests.get(Client.START_ALGORITH_URL)
        return Client.parse_traffic_lights_response(response.json())

    @staticmethod
    def parse_traffic_lights_response(json: Dict) -> List[TrafficLight]:
        pass




