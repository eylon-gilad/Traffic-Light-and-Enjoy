"""
Car.py

This module defines the Car class, which represents a car in the traffic simulation.
Each Car instance holds its unique identifier, distance along the lane, velocity,
destination lane/road, and type.

Changes:
- Added/clarified docstring for the class and methods.
- Added type hints to all methods (PEP 484).
- Preserved existing functionality.
"""

class Car:
    """
    Represents a single car in the traffic simulation.
    Each car has an ID, distance along the lane, velocity,
    destination lane/road, and a type (e.g., "CAR", "AMBULANCE").
    """

    def __init__(self, car_id: int, dist: float, velocity: float, dest: int, car_type: str, origin: int = 0) -> None:
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
        self.origin: int = origin
        self.car_type: str = car_type

        self.is_turning: bool = False
        self.turn_end: int = 0
        self.half_turn: bool = False
        self.angle: float = 0.0

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

    def get_is_turning(self) -> bool:
        """ Get the turning status of the car.
        Returns:
        bool: Whether the car is currently turning.
        """
        return self.is_turning

    def get_turn_end(self) -> int:
        """ Get the end of the turning maneuver.
        Returns:
        int: The turning end point or identifier.
        """
        return self.turn_end

    def get_half_turn(self) -> bool:
        """ Get the half-turn status of the car.
        Returns:
        bool: Whether the car is in a half-turn state.
        """
        return self.half_turn

    def get_angle(self) -> float:
        """ Get the current angle of the car.
        Returns:
        float: The car's current angle.
        """
        return self.angle

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

    def set_is_turning(self, is_turning: bool) -> None:
        """ Set the turning status of the car.
        Args:
        is_turning (bool): New turning status.
        """
        self.is_turning = is_turning

    def set_turn_end(self, turn_end: int) -> None:
        """ Set the end of the turning maneuver.
        Args:
        turn_end (int): New turning end point or identifier.
        """
        self.turn_end = turn_end

    def set_half_turn(self, half_turn: bool) -> None:
        """ Set the half-turn status of the car.
        Args:
        half_turn (bool): New half-turn status.
        """
        self.half_turn = half_turn

    def set_angle(self, angle: float) -> None:
        """ Set the car's angle.
        Args:
        angle (float): New angle value.
        """
        self.angle = angle

    def __str__(self) -> str:
        """
        Provide a human-readable string representation of this Car.
        """
        return (
            f"Car(id={self.id}, dist={self.dist}, "
            f"velocity={self.velocity}, dest='{self.dest}', car_type='{self.car_type}')"
        )
