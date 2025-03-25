"""
main.py

The main entry point that initializes Pygame, sets up the simulation and UI,
and enters the core game loop.
"""

import pygame
import sys

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from assets import load_background_image, load_car_images
from events import handle_events
from rendering import draw_game_screen
from sim.Sim import Sim
from sim.Generator.JunctionGenerator import JunctionGenerator


def main() -> None:
    """
    Initializes Pygame, sets up the simulation, and enters the main game loop.

    Key controls:
      - ESC to exit
      - D to toggle debug mode
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Junction Simulation")

    clock = pygame.time.Clock()
    show_debug = False
    running = True

    # Load assets
    bg_image = load_background_image()
    car_images = load_car_images(num_images=8, folder="../assets/", size=(40, 40))
    debug_font = pygame.font.SysFont(None, 18)

    # Build the simulation (plus-junction) and start it

    sim = Sim(junctions=[JunctionGenerator.generate_junction()], if_ui=True)
    sim.start()
    while running:




        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds (currently unused, but could pass to sim updates)

        # Handle events (quit, toggle debug)
        running, show_debug = handle_events(show_debug)

        # Render everything
        draw_game_screen(
            screen=screen,
            sim=sim,
            car_images=car_images,
            bg_image=bg_image,
            show_debug=show_debug,
            debug_font=debug_font
        )

        pygame.display.flip()

    # Cleanup
    sim.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
