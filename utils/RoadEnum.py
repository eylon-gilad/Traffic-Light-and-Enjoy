"""
RoadEnum.py

This module defines the RoadEnum enumeration for cardinal road directions.
"""

from enum import Enum


class RoadEnum(Enum):
    """
    Enumeration of cardinal directions for roads in the simulation.
    """

    NORTH: int = 0
    EAST: int = 1
    SOUTH: int = 2
    WEST: int = 3

    @classmethod
    def from_string(cls, name: str) -> "RoadEnum":
        """
        Parse a string into a RoadEnum member.

        Args:
            name (str): Name of the enum member (e.g. "NORTH", "EAST", etc.).

        Returns:
            RoadEnum: The corresponding enum member.

        Raises:
            ValueError: If the string doesn't match any valid enum name.
        """
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"{name} is not a valid member of {cls.__name__}")
