import logging
import random
import threading

from Algorithms.ExpCarsOnTime import ExpCarsOnTimeController
from TrafficLightsCombinator import TrafficLightsCombinator
from Algorithms.wightedAvg import wightedAvg
from algo.Algorithms.AdaptiveFlowController import AdaptiveFlowController
from algo.Algorithms.DynamicWeightedTrafficController import DynamicWeightedTrafficController
from algo.Algorithms.RoundRobin import RoundRobinController
from algo.Algorithms.VolumeBasedController import VolumeBasedController
from algo.Algorithms.SmartTrafficController import SmartTrafficController
from utils import Junction


class AlgoRunner:
    """
    Runs a chosen traffic light control algorithm in a separate thread.
    Maintains a reference to the junction being controlled, and updates
    algorithm behavior when new junction information is received.
    """

    def __init__(self, junction: Junction) -> None:
        """
        Initialize the AlgoRunner with a specific junction.

        :param junction: The Junction object to manage.
        """
        # Pre-calculate all possible active lights to ensure
        # the chosen algorithm has them precomputed if needed.
        TrafficLightsCombinator.calculate_possible_active_lights(junction)

        # Choose which controller to use.
        # A threading lock to ensure thread-safe operations on the controller. (random for now)
        all_controllers = [ExpCarsOnTimeController, wightedAvg, AdaptiveFlowController, DynamicWeightedTrafficController, RoundRobinController, VolumeBasedController, SmartTrafficController]
        # Randomly select one of the controllers.
        #selected_controller = random.choice(all_controllers)
        #print(selected_controller)
        # Initialize the selected controller with the junction.
        #self.controller = selected_controller(junction)
        #self.controller = DynamicWeightedTrafficController(junction)
        self.controller = SmartTrafficController(junction)
        #self.controller = AdaptiveFlowController(junction)
        #self.controller = RoundRobinController(junction)
        #self.controller = VolumeBasedController(junction)
        #self.controller = ExpCarsOnTimeController(junction)
        #self.controller = wightedAvg(junction)

        self.lock = threading.Lock()

    def run(self) -> None:
        """
        Start the algorithm in a separate thread.
        """
        # Launch the traffic control logic in a new thread.
        try:
            thread = threading.Thread(target=self.controller.start)
            thread.start()
        except Exception as e:
            logging.error(f"Failed to start controller thread: {e}")

    def get_current_state(self):
        """
        Retrieve the current state of the traffic lights from the controller.

        :return: The current list of TrafficLight objects.
        """
        return self.controller.get_current_traffic_lights_state()

    def set_junction_info(self, junction: Junction) -> None:
        """
        Update the underlying junction info used by the algorithm.

        :param junction: The new Junction object with updated data.
        """
        with self.lock:
            try:
                self.controller.set_junction_info(junction)
            except Exception as e:
                logging.error(f"Failed to update junction info in controller: {e}")
