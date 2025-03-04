"""
main.py

This module generates frames for a static intersection simulation and handles
the UI event loop. It loads assets, creates a simulation and junction, and displays
sequential frames of the simulation.
"""

import sys
import pygame
from typing import Dict

from sim.simulation import (
    StaticIntersectionSimulation,
)  # Assumes simulation module exists.
from sim.ui.game import draw_intersection, draw_ids_debug
from utils.Junction import Junction

# Screen dimensions
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

# Debug flag for displaying road and lane IDs.
DEBUG_IDS: bool = True


def generate_frame(
    junction: Junction,
    screen: pygame.Surface,
    simulation: StaticIntersectionSimulation,
    car_images: Dict[int, pygame.Surface],
    background_img: pygame.Surface,
) -> None:
    """
    Generates a new frame using the given Junction object.
    This function clears the current frame and draws the intersection (from simulation)
    based on the junction's current state.

    Args:
        junction (Junction): The junction whose state is to be rendered.
        screen (pygame.Surface): The display surface.
        simulation (StaticIntersectionSimulation): The simulation instance.
        car_images (Dict[int, pygame.Surface]): Dictionary of car images.
        background_img (pygame.Surface): The background image.
    """
    # Clear the frame by drawing the background image.
    screen.blit(background_img, (0, 0))

    # Draw the intersection using the existing drawing function.
    draw_intersection(screen, simulation, car_images)

    # Optionally, draw debug information (road & lane IDs).
    if DEBUG_IDS:
        draw_ids_debug(screen, simulation)

    # Update the display.
    pygame.display.flip()


def main() -> None:
    """
    Initializes Pygame, loads assets, creates the simulation and junction,
    and then displays five frames sequentially before entering an event loop.
    """
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Junction Frame Generator")
    clock: pygame.time.Clock = pygame.time.Clock()

    # Load and scale car images.
    car_size = (40, 40)
    car_images: Dict[int, pygame.Surface] = {}
    for i in range(1, 8):
        img: pygame.Surface = pygame.image.load(
            f"../../sim/assets/car{i}.png"
        ).convert_alpha()
        car_images[i] = pygame.transform.scale(img, car_size)

    # Load and scale the background image.
    background_img: pygame.Surface = pygame.image.load(
        "../../sim/assets/background.png"
    ).convert()
    background_img = pygame.transform.scale(
        background_img, (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    # Create the simulation and then a Junction using its roads and traffic lights.
    simulation: StaticIntersectionSimulation = StaticIntersectionSimulation()
    junction: Junction = Junction(
        id=1,
        traffic_lights=simulation.get_traffic_lights(),
        roads=simulation.get_roads(),
    )

    # Show five frames one by one.
    for frame in range(5):
        # TODO: Consider updating the junction state here for each frame if needed.
        generate_frame(junction, screen, simulation, car_images, background_img)
        pygame.time.wait(1000)  # Wait 1 second between frames.
        clock.tick(30)

    # After showing five frames, wait until the user closes the window.
    waiting: bool = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
