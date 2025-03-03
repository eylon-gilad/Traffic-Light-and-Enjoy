# Lane.py
from typing import List

from utils.Car import Car


class Lane:
    def __init__(
            self,
            id: int = 0,
            cars: List[Car] = None,
            car_creation: float = 0.0,
            lane_len: int = 50,
            lane_max_vel: float = 30.0,
            max_decel: float = 3.0,
            max_accel: float = 2.0,
    ) -> None:
        """
        Represents a lane on a road where cars drive.

        :param id: Unique identifier for the lane
        :param cars: List of Car objects currently in this lane
        :param car_creation: Rate parameter used for car creation (lambda in expovariate)
        :param lane_len: Physical length of the lane (for spacing calculations)
        :param lane_max_vel: The speed limit or max velocity
        :param max_decel: Maximum deceleration rate for cars in this lane
        :param max_accel: Maximum acceleration rate for cars in this lane
        """
        self.id = id
        self.cars: List[Car] = cars if cars is not None else []
        self.car_creation = car_creation
        self.LENGTH = lane_len
        self.max_vel = lane_max_vel
        self.max_decel = max_decel
        self.max_accel = max_accel

    def get_id(self) -> int:
        return self.id

    def get_cars(self) -> List[Car]:
        return self.cars

    def set_cars(self, cars: List[Car]) -> None:
        self.cars = cars

    def get_car_creation(self) -> float:
        return self.car_creation

    def add_car(self, new_car: Car) -> None:
        self.cars.append(new_car)

    def remove_car(self, car: Car) -> None:
        if car in self.cars:
            self.cars.remove(car)
