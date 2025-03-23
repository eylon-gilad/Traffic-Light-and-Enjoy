"""
config.py

Holds constants and configuration settings for the Pygame-based junction simulation.
"""

from typing import Tuple

# Screen dimensions
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 800

# Center points
CY: int = SCREEN_HEIGHT // 2
CX: int = SCREEN_WIDTH // 2

# Colors
BACKGROUND_COLOR: Tuple[int, int, int] = (120, 180, 120)  # Fallback background color
ASPHALT_COLOR: Tuple[int, int, int] = (50, 50, 50)
INTERSECTION_COLOR: Tuple[int, int, int] = (60, 60, 60)
LANE_MARKING_COLOR: Tuple[int, int, int] = (255, 255, 255)
CAR_DEBUG_COLOR: Tuple[int, int, int] = (255, 0, 0)

# Road/lane geometry constants
LANE_WIDTH: int = 50
LANE_GAP: int = 10
ROAD_TOTAL_WIDTH: int = 120  # Kept mainly for reference in traffic-light draws.

# Frame rate
FPS: int = 60


def get_road_total_width(num_lanes: int) -> int:
    """
    Computes total road width based on lane count.
    """
    return num_lanes * LANE_WIDTH
