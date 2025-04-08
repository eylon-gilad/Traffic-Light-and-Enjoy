"""
Lane.py

This module defines the Lane class, representing a lane on a road where cars travel.
It holds a list of cars and various parameters for car generation and movement.

Changes:
- Expanded docstrings and type hints for methods.
- Added TODO note in remove_car if the car does not exist in the lane.
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
            lane_len (int): Physical length of the lane in simulation units.
            lane_max_vel (float): Maximum allowed velocity in the lane.
        """
        self.id: int = lane_id
        self.cars: List[Car] = cars if cars is not None else []
        self.car_creation: float = car_creation
        self.LENGTH: int = lane_len
        self.max_vel: float = lane_max_vel
        # Keep original logic for max_decel and max_accel:
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
            float: The car creation rate parameter (cars/second).
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

        TODO:
            Confirm whether it's an error or normal scenario when removing a car
            that isn't currently in this lane.
        """
        if car in self.cars:
            self.cars.remove(car)
        else:
            logger.debug(f"Attempted to remove a car not in lane (Lane ID: {self.id}).")

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of this Lane.
        """
        cars_str = ", ".join(str(car) for car in self.cars)
        return f"Lane(id={self.id}, cars=[{cars_str}])"
