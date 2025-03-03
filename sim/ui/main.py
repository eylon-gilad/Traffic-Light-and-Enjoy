# main.py

import sys
import pygame
from sim.simulation import StaticIntersectionSimulation
from sim.ui.game import draw_intersection, draw_ids_debug
from utils.Junction import Junction

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set to True if you want to display debug IDs (roads and lanes)
DEBUG_IDS = True


def generate_frame(junction, screen, simulation, car_images, background_img):
    """
    Generates a new frame using the given Junction object.
    This function clears the current frame and draws the intersection (from simulation)
    based on the junction's current state.
    """
    # Clear the frame by drawing the background image.
    screen.blit(background_img, (0, 0))

    # Draw the intersection using our existing drawing function.
    # (Our simulation object holds the roads/traffic lights used by the junction.)
    draw_intersection(screen, simulation, car_images)

    # Optionally, draw debug information (road & lane IDs)
    if DEBUG_IDS:
        draw_ids_debug(screen, simulation)

    # Update the display.
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Junction Frame Generator")
    clock = pygame.time.Clock()

    # Load and scale car images.
    car_size = (40, 40)
    car_images = {}
    for i in range(1, 8):
        img = pygame.image.load(f"../../sim/assets/car{i}.png").convert_alpha()
        car_images[i] = pygame.transform.scale(img, car_size)

    # Load and scale the background image.
    background_img = pygame.image.load("../../sim/assets/background.png").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create the simulation and then a Junction using its roads and traffic lights.
    simulation = StaticIntersectionSimulation()
    junction = Junction(
        id=1,
        traffic_lights=simulation.get_traffic_lights(),
        roads=simulation.get_roads(),
    )

    # Show five frames one by one.
    for frame in range(5):
        # (Optionally, update the junction state here for each frame.)
        generateFrame(junction, screen, simulation, car_images, background_img)
        pygame.time.wait(1000)  # Wait 1 second between frames.
        clock.tick(30)

    # After showing five frames, wait until the user closes the window.
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
