"""
Lane.py

This module defines the Lane class, representing a lane on a road where cars travel.
It holds a list of cars and various parameters for car generation and movement.

Changes:
- Added docstring for the class.
- Added type hints in the constructor and methods.
- Added a small TODO note when removing a car that doesn’t exist in the lane.
- Preserved existing functionality.
"""

import logging
from typing import List, Optional

from utils.Car import Car

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Lane:
    """
    Represents a single lane on a road, containing cars and parameters
    for handling traffic flow and car generation.
    """

    def __init__(
            self,
            lane_id: int = 0,
            cars: Optional[List[Car]] = None,
            car_creation: float = 0.0,
            lane_len: int = 400,
            lane_max_vel: float = 100.0,
    ) -> None:
        """
        Initialize a Lane object.

        Args:
            lane_id (int): Unique identifier for the lane.
            cars (Optional[List[Car]]): List of Car objects currently in the lane.
            car_creation (float): Rate parameter for car creation (lambda for Poisson process).
            lane_len (int): Physical length of the lane.
            lane_max_vel (float): Maximum allowed velocity in the lane.
        """
        self.id: int = lane_id
        self.cars: List[Car] = cars if cars is not None else []
        self.car_creation: float = car_creation
        self.LENGTH: int = lane_len
        self.max_vel: float = lane_max_vel
        # Derive maximum deceleration and acceleration from lane_max_vel (unchanged logic)
        self.max_decel: float = self.max_vel * 3
        self.max_accel: float = self.max_vel * 2

    def get_id(self) -> int:
        """
        Get the lane's unique identifier.

        Returns:
            int: The lane's ID.
        """
        return self.id

    def get_cars(self) -> List[Car]:
        """
        Get the list of cars currently in the lane.

        Returns:
            List[Car]: Cars in the lane.
        """
        return self.cars

    def set_cars(self, cars: List[Car]) -> None:
        """
        Set the list of cars in the lane.

        Args:
            cars (List[Car]): New list of cars.
        """
        self.cars = cars

    def get_car_creation(self) -> float:
        """
        Get the car creation rate for the lane.

        Returns:
            float: The car creation rate parameter.
        """
        return self.car_creation

    def add_car(self, new_car: Car) -> None:
        """
        Add a new car to the lane.

        Args:
            new_car (Car): The car to add.
        """
        self.cars.append(new_car)

    def remove_car(self, car: Car) -> None:
        """
        Remove a car from the lane if it exists.

        Args:
            car (Car): The car to remove.
        """
        if car in self.cars:
            self.cars.remove(car)
        else:
            # TODO: Confirm whether it's an error or normal scenario when removing a car not in the lane.
            logger.debug(f"Attempted to remove a car not in lane (Lane ID: {self.id}).")
