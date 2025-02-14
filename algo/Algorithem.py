import time
import threading
from utils import Junction


class TrafficLightController:
    def __init__(self, junction: Junction):
        self.junction = junction
        self.current_traffic_light_id = self.junction.get_traffic_lights()[0].id

    def start(self):
        while True:
            lights = self.junction.get_traffic_lights()

            for light in lights:
                if light.id == self.current_traffic_light_id:
                    light.state = True
                else:
                    light.state = False

            self.current_traffic_light_id = self.get_next_traffic_light_id()

            time.sleep(5)

    def get_next_traffic_light_id(self):
        lights = self.junction.get_traffic_lights()

        for i, light in enumerate(lights):
            if light.id == self.current_traffic_light_id:
                return lights[(i + 1) % len(lights)].id

    def get_current_state(self):
        return self.junction.get_traffic_lights()


class AlgoRunner:
    def __init__(self, junction: Junction):
        self.controller = TrafficLightController(junction)

    def run(self):
        thread = threading.Thread(target=self.controller.start)
        thread.start()

    def get_current_state(self):
        return self.controller.get_current_state()
