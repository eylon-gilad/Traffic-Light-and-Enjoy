from utils import Junction
from Algorithms.RoundRobin import RoundRobinController
import threading


class AlgoRunner:
    def __init__(self, junction: Junction):
        """
        Constructor
        :param junction: object that represents a junction
        """

        self.controller = RoundRobinController(junction)

    def run(self):
        """
        Runs the algorithm
        """

        thread = threading.Thread(target=self.controller.start)
        thread.start()

    def get_current_state(self):
        """
        Get current state of traffic lights
        """

        return self.controller.get_current_state()
