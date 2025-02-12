from typing import List

from utils.Car import Car


class Lane:

    def __init__(self, id: int = 0, cars: List[Car] = []):
        """
        Represents a lane on a road where cars drive.
        """
        self.cars: List[Car] = []
        self.id = id

    def set_cars(self, cars: List[Car]) -> None:
        """Sets the cars in the lane."""
        self.cars = cars

    def get_cars(self) -> List[Car]:
        return self.cars

    def get_id(self) -> int:
        return self.id
