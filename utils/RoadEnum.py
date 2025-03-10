"""
RoadEnum.py

This module defines the RoadEnum enumeration for cardinal road directions.
"""

from enum import Enum


class RoadEnum(Enum):
    NORTH: int = 0
    EAST: int = 1
    SOUTH: int = 2
    WEST: int = 3

    @classmethod
    def from_string(cls, name: str):
        """ Custom method to parse a string to an enum member """
        try:
            return cls[name]
        except KeyError:
            raise ValueError(f"{name} is not a valid member of {cls.__name__}")
