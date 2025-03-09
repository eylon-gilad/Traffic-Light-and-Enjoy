"""
Car.py

This module defines the Car class, which represents a car in the traffic simulation.
Each Car instance holds its unique identifier, distance along the lane, velocity,
destination lane/road, and type.

Changes:
- Added/updated docstring for the class.
- Added type hints to all methods.
- Preserved existing functionality.
"""


class Car:
    """
    Represents a single car in the traffic simulation.
    Each car has an ID, distance along the lane, velocity,
    destination lane/road, and a type (e.g., "CAR", "AMBULANCE").
    """

    def __init__(self, car_id: int, dist: float, velocity: float, dest: int, car_type: str) -> None:
        """
        Initialize a Car object.

        Args:
            car_id (int): Unique identifier for the car.
            dist (float): Distance from the lane's start or end (context-dependent).
            velocity (float): Current speed of the car.
            dest (int): Destination lane/road ID.
            car_type (str): Type of car (e.g., "CAR", "AMBULANCE").
        """
        self.id: int = car_id
        self.dist: float = dist
        self.velocity: float = velocity
        self.dest: int = dest
        self.car_type: str = car_type

    def get_id(self) -> int:
        """
        Get the car's unique identifier.

        Returns:
            int: The car's ID.
        """
        return self.id

    def get_dist(self) -> float:
        """
        Get the current distance of the car along the lane.

        Returns:
            float: The current distance along the lane.
        """
        return self.dist

    def get_velocity(self) -> float:
        """
        Get the current velocity of the car.

        Returns:
            float: The car's velocity.
        """
        return self.velocity

    def get_dest(self) -> int:
        """
        Get the destination lane/road ID for the car.

        Returns:
            int: The destination lane/road ID.
        """
        return self.dest

    def get_car_type(self) -> str:
        """
        Get the type of the car.

        Returns:
            str: The car type (e.g., "CAR", "AMBULANCE").
        """
        return self.car_type

    def set_dist(self, dist: float) -> None:
        """
        Set the car's distance along the lane.

        Args:
            dist (float): New distance value.
        """
        self.dist = dist

    def set_velocity(self, velocity: float) -> None:
        """
        Set the car's velocity.

        Args:
            velocity (float): New velocity value.
        """
        self.velocity = velocity

    def set_dest(self, dest: int) -> None:
        """
        Set the car's destination lane/road ID.

        Args:
            dest (int): New destination ID.
        """
        self.dest = dest

    def set_car_type(self, car_type: str) -> None:
        """
        Set the car's type.

        Args:
            car_type (str): New car type.
        """
        self.car_type = car_type
