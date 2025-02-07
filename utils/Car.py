from typing import List


class Car:
    id: int = 0

    def __init__(self, dist: List[float], velocity: float, dest: str, car_type: str):
        """
        Represents a car in the simulation.
        :param dist: List of distances from the junction.
        :param velocity: Speed of the car.
        :param dest: Destination road ID.
        :param car_type: Type of the car ('CAR', 'AMBULANCE', or 'PEDESTRIAN').
        """
        self.dist = dist
        self.velocity = velocity
        self.dest = dest
        self.car_type = car_type
        self.id = Car.id
        Car.id += 1
