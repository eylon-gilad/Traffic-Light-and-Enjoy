from typing import List

from utils.Lane import Lane


class TrafficLight:
    id: int = 0

    def __init__(self):
        """
        Represents a traffic light controlling lanes at an intersection.
        """
        self.origins: List[Lane] = []  # Lanes where traffic is originating
        self.destinations: List[Lane] = []  # Lanes where traffic is destined
        self.state: bool = True  # True (Green) or False (Red)
        self.id = TrafficLight.id
        TrafficLight.id += 1

    def toggle(self):
        """Toggles the state of the traffic light."""
        self.state = not self.state
