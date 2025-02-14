from typing import List
from utils.Car import Car


class Lane:
    def __init__(self, id: int = 0, cars: List[Car] = []) -> None:
        """
        Represents a lane on a road where cars drive.

        :param id: Unique identifier for the lane
        :param cars: List of Car objects currently in this lane
        """
        self.id = id
        # Directly use the passed-in cars list (be mindful of mutable defaults in production)
        self.cars = cars

    def get_id(self) -> int:
        return self.id

    def get_cars(self) -> List[Car]:
        return self.cars

    def set_cars(self, cars: List[Car]) -> None:
        """Sets the cars in the lane."""
        self.cars = cars
