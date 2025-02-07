from typing import List

from utils.Car import Car


class Lane:
    def __init__(self):
        """
        Represents a lane on a road where cars drive.
        """
        self.cars: List[Car] = []

    def add_car(self, car: Car):
        """Adds a car to the lane."""
        self.cars.append(car)
