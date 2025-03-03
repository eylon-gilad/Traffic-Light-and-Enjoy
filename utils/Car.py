from typing import List


class Car:
    def __init__(
        self, id: int, dist: float, velocity: float, dest: int, car_type: str
    ) -> None:
        """
        Represents a car in the simulation.

        :param id: Unique identifier for the car
        :param dist: List of distances from the junction
        :param velocity: Speed of the car
        :param dest: Destination road or lane ID as a string
        :param car_type: Type of the car ("CAR", "AMBULANCE", "PEDESTRIAN", etc.)
        """
        self.id = id
        self.dist = dist
        self.velocity = velocity
        self.dest = dest
        self.car_type = car_type

    def get_id(self) -> int:
        return self.id

    def get_dist(self) -> float:
        return self.dist

    def get_velocity(self) -> float:
        return self.velocity

    def get_dest(self) -> int:
        return self.dest

    def get_car_type(self) -> str:
        return self.car_type

    def set_dist(self, dist: float) -> None:
        self.dist = dist

    def set_velocity(self, velocity: float) -> None:
        self.velocity = velocity

    def set_dest(self, dest: str) -> None:
        self.dest = dest

    def set_car_type(self, car_type: str) -> None:
        self.car_type = car_type
