"""
Lane.py

This module defines the Lane class, representing a lane on a road where cars travel.
It holds a list of cars and various parameters for car generation and movement.
"""

from typing import List, Optional
from utils.Car import Car


class Lane:
    def __init__(
        self,
        id: int = 0,
        cars: Optional[List[Car]] = None,
        car_creation: float = 0.0,
        lane_len: int = 400,
        lane_max_vel: float = 150.0,
        max_decel: float = 100,
        max_accel: float = 100,
    ) -> None:
        """
        Initializes a Lane object.

        Args:
            id (int): Unique identifier for the lane.
            cars (Optional[List[Car]]): List of Car objects currently in the lane.
            car_creation (float): Rate parameter for car creation (lambda for Poisson process).
            lane_len (int): Physical length of the lane.
            lane_max_vel (float): Maximum allowed velocity in the lane.
            max_decel (float): Maximum deceleration rate.
            max_accel (float): Maximum acceleration rate.
        """
        self.id: int = id
        self.cars: List[Car] = cars if cars is not None else []
        self.car_creation: float = car_creation
        self.LENGTH: int = lane_len
        self.max_vel: float = lane_max_vel
        self.max_decel: float = max_decel
        self.max_accel: float = max_accel

    def get_id(self) -> int:
        """Returns the lane's unique identifier."""
        return self.id

    def get_cars(self) -> List[Car]:
        """Returns the list of cars currently in the lane."""
        return self.cars

    def set_cars(self, cars: List[Car]) -> None:
        """
        Sets the list of cars in the lane.

        Args:
            cars (List[Car]): New list of cars.
        """
        self.cars = cars

    def get_car_creation(self) -> float:
        """
        Returns the car creation rate for the lane.

        Returns:
            float: The car creation rate.
        """
        return self.car_creation

    def add_car(self, new_car: Car) -> None:
        """
        Adds a new car to the lane.

        Args:
            new_car (Car): The car to add.
        """
        self.cars.append(new_car)

    def remove_car(self, car: Car) -> None:
        """
        Removes a car from the lane if it exists.

        Args:
            car (Car): The car to remove.
        """
        if car in self.cars:
            self.cars.remove(car)
