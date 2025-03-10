from utils import Junction
from Algorithms.RoundRobin import RoundRobinController
from Algorithms.ExpCarsOnTime import ExpCarsOnTimeController
import threading
from TrafficLightsCombinator import TrafficLightsCombinator


class AlgoRunner:
    def __init__(self, junction: Junction):
        """
        Constructor
        :param junction: object that represents a junction
        """
        TrafficLightsCombinator.calc_possible_active_lights(junction)
        # self.controller = RoundRobinController(junction)
        self.controller = ExpCarsOnTimeController(junction)
        self.lock = threading.Lock()

    def run(self):
        """
        Runs the algorithm
        """
        # with self.lock:
        thread = threading.Thread(target=self.controller.start)
        thread.start()

    def get_current_state(self):
        """
        Get current state of traffic lights
        """

        return self.controller.get_current_traffic_lights_state()

    def set_junction_info(self, junction):
        # Which algo to call.
        with self.lock:
            self.controller.set_junction_info(junction)
