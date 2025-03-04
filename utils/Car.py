"""
Car.py

This module defines the Car class, which represents a car in the traffic simulation.
Each Car instance holds its unique identifier, distance along the lane, velocity,
destination lane/road, and type.
"""


class Car:
    def __init__(
        self, id: int, dist: float, velocity: float, dest: int, car_type: str
    ) -> None:
        """
        Initializes a Car object.

        Args:
            id (int): Unique identifier for the car.
            dist (float): Distance from the lane's start or end (context-dependent).
            velocity (float): Current speed of the car.
            dest (int): Destination lane/road ID.
            car_type (str): Type of car (e.g., "CAR", "AMBULANCE").
        """
        self.id: int = id
        self.dist: float = dist
        self.velocity: float = velocity
        self.dest: int = dest
        self.car_type: str = car_type

    def get_id(self) -> int:
        """Returns the car's unique identifier."""
        return self.id

    def get_dist(self) -> float:
        """Returns the current distance of the car along the lane."""
        return self.dist

    def get_velocity(self) -> float:
        """Returns the current velocity of the car."""
        return self.velocity

    def get_dest(self) -> int:
        """Returns the destination lane/road ID for the car."""
        return self.dest

    def get_car_type(self) -> str:
        """Returns the type of the car."""
        return self.car_type

    def set_dist(self, dist: float) -> None:
        """
        Sets the car's distance along the lane.

        Args:
            dist (float): New distance value.
        """
        self.dist = dist

    def set_velocity(self, velocity: float) -> None:
        """
        Sets the car's velocity.

        Args:
            velocity (float): New velocity value.
        """
        self.velocity = velocity

    def set_dest(self, dest: int) -> None:
        """
        Sets the car's destination lane/road ID.

        Args:
            dest (int): New destination ID.
        """
        self.dest = dest

    def set_car_type(self, car_type: str) -> None:
        """
        Sets the car's type.

        Args:
            car_type (str): New car type.
        """
        self.car_type = car_type
