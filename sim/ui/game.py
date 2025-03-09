"""
game.py

This module implements the main game loop for the plus-junction simulation using Pygame.
It sets up the display, builds the junction simulation, handles user input,
and renders the simulation (roads, cars, traffic lights) on the screen.
"""

import pygame
import sys
import time
import random
from typing import Dict, Tuple, List
from sim.Sim import Sim
from utils.Junction import Junction
from utils.Road import Road
from utils.Lane import Lane
from utils.Car import Car
from utils.TrafficLight import TrafficLight
from sim.creator.create_sim import create_junction

#########################
# SCREEN / RENDER CONFIG
#########################
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 800

BACKGROUND_COLOR: Tuple[int, int, int] = (120, 180, 120)  # Fallback background color

# Road/lane geometry constants
INTERSECTION_SIZE: int = 250  # Size of the square center area
ROAD_TOTAL_WIDTH: int = 120  # Total width (for two lanes) for each road
LANE_WIDTH: int = 50
LANE_GAP: int = 10
LANE_MARGIN: int = 5
NUM_LANES: int = 2

# SHIFT offsets to avoid overlapping roads at the intersection.
SHIFT_X_NORTH: int = -65  # Shift north road to the left
SHIFT_X_SOUTH: int = 65  # Shift south road to the right
SHIFT_Y_EAST: int = 65  # Shift east road downward
SHIFT_Y_WEST: int = -65  # Shift west road upward

# Colors
ASPHALT_COLOR: Tuple[int, int, int] = (50, 50, 50)
INTERSECTION_COLOR: Tuple[int, int, int] = (60, 60, 60)
LANE_MARKING_COLOR: Tuple[int, int, int] = (255, 255, 255)
CAR_DEBUG_COLOR: Tuple[int, int, int] = (255, 0, 0)

FPS: int = 60


#########################
# MAIN GAME LOOP
#########################
def main() -> None:
    """
    Initializes Pygame, sets up the simulation, and enters the main game loop.
    Handles events, rendering, and graceful shutdown.
    """
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Plus-Junction: Full Roads Across the Intersection")

    clock: pygame.time.Clock = pygame.time.Clock()
    show_debug: bool = False
    running: bool = True

    # Attempt to load a background image; if unavailable, fallback to a solid color.
    try:
        bg_image: pygame.Surface = pygame.image.load(
            "../assets/background.png"
        ).convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:  # FIXME: too broad exception

        bg_image = None  # FIXME: incorrect type probably should exit here

    # Build the simulation with a simple plus-junction configuration.
    sim: Sim = build_simple_plus_junction_sim()
    sim.enable_time_based_lights(
        period_seconds=5.0
    )  # FIXME: this function does not exist and shouldn't be called here
    sim.start()  # Start the simulation thread in the background

    # Load car images from assets.
    car_images: Dict[int, pygame.Surface] = load_car_images(
        num_images=8, folder="../assets/", size=(40, 40)
    )

    while running:
        dt: float = (
            clock.tick(FPS) / 1000.0
        )  # Delta time in seconds.  #FIXME: dt is not used
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    show_debug = not show_debug

        # Render background.
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(BACKGROUND_COLOR)

        # Render the junction and simulation elements.
        draw_junction_ui(screen, sim, car_images, show_debug)
        pygame.display.flip()

    sim.stop()
    pygame.quit()
    sys.exit()


#########################
# BUILD THE JUNCTION
#########################
def build_simple_plus_junction_sim() -> Sim:
    """
    Creates a simple plus-junction simulation with one junction and four roads
    (North, South, East, West), each with two lanes.

    Returns:
        Sim: The simulation instance configured with the junction and roads.
    """

    def make_lanes(lane_id_start: int) -> list:
        """
        Helper function to create two lanes for a road.

        Args:
            lane_id_start (int): The starting ID for the first lane.

        Returns:
            list: A list containing two Lane objects.
        """
        lane1 = Lane(
            id=lane_id_start,
            lane_len=400,  # Adjustable lane length.
            car_creation=0.01,
        )
        lane2 = Lane(
            id=lane_id_start + 1, lane_len=400, car_creation=0.01
        )
        return [lane1, lane2]

    road_north = Road(id=1, lanes=make_lanes(100))
    setattr(road_north, "direction", "north")
    

    road_south = Road(id=2, lanes=make_lanes(200))
    setattr(road_south, "direction", "south")

    road_east = Road(id=3, lanes=make_lanes(300))
    setattr(road_east, "direction", "east")

    road_west = Road(id=4, lanes=make_lanes(400))
    setattr(road_west, "direction", "west")

    # Define traffic lights for each road approach.
    tl_north = TrafficLight(id=10, origins=[100, 101], state=True)
    setattr(tl_north, "direction", "north")

    tl_south = TrafficLight(id=11, origins=[200, 201], state=True)
    setattr(tl_south, "direction", "south")

    tl_east = TrafficLight(id=12, origins=[300, 301], state=False)
    setattr(tl_east, "direction", "east")

    tl_west = TrafficLight(id=13, origins=[400, 401], state=False)
    setattr(tl_west, "direction", "west")

    # Create the junction with the roads and traffic lights.
    junction = Junction(
        id=99,
        traffic_lights=[tl_north, tl_south, tl_east, tl_west],
        roads=[road_north, road_south, road_east, road_west],
    )

    # Create and return the simulation instance.
    sim: Sim = Sim(junctions=[junction], if_ui=True)
    return sim


#########################
# TIME-BASED LIGHTS
#########################
def enable_time_based_lights(self: Sim, period_seconds: float = 5.0) -> None:
    """
    Monkey-patches the Sim instance to toggle all traffic lights every specified period.

    Args:
        self (Sim): The simulation instance to modify.
        period_seconds (float): The time interval in seconds for toggling lights.
    """
    original_update_lights = (
        self._Sim__update_traffic_lights
    )  # FIXME: original_update_lights is not used

    def new_update_lights() -> None:
        """
        New update function to flip the state of each traffic light after the period has elapsed.
        """
        now = time.time()
        if not hasattr(self, "_light_cycle_start"):
            self._light_cycle_start = now
        elapsed = now - self._light_cycle_start
        if elapsed >= period_seconds:
            # Toggle every traffic light in every junction.
            # Green -> Red, Red -> wait 0.5s and then Green
            for junction in self.get_junctions():
                for tl in junction.get_traffic_lights():
                    if tl.get_state():
                        tl.red()
                    else:
                        # Wait for 0.5s before turning green. (Simulates a yellow light)
                        # if now - self._light_cycle_start >= period_seconds + 0.5:
                        #     tl.green()
                        # this docent work
                        tl.green()

            self._light_cycle_start = now

    self._Sim__update_traffic_lights = new_update_lights


# Monkey-patch the Sim class with the new time-based lights functionality.
Sim.enable_time_based_lights = enable_time_based_lights


#########################
# LOAD CAR IMAGES
#########################
def load_car_images(
    num_images: int = 8, folder: str = "../assets/", size: Tuple[int, int] = (40, 40)
) -> Dict[int, pygame.Surface]:
    """
    Loads car images from the specified folder. If an image is not found,
    creates a placeholder surface.

    Args:
        num_images (int): Number of car images to load.
        folder (str): Path to the folder containing the images.
        size (Tuple[int, int]): Desired size for each image.

    Returns:
        Dict[int, pygame.Surface]: A dictionary mapping image indices to Pygame surfaces.
    """
    images: Dict[int, pygame.Surface] = {}
    for i in range(1, num_images + 1):
        try:
            path: str = f"{folder}/car{i}.png"
            img: pygame.Surface = pygame.image.load(path).convert_alpha()
            images[i] = pygame.transform.scale(img, size)
        except Exception:  # FIXME: too broad exception
            # Create a fallback surface with a solid color.
            surf: pygame.Surface = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill((255, 140, 0))
            images[i] = surf
    return images


#########################
# DRAWING LOGIC
#########################
def draw_junction_ui(
    screen: pygame.Surface,
    sim: Sim,
    car_images: Dict[int, pygame.Surface],
    show_debug: bool = False,
) -> None:
    """
    Draws the entire junction UI, including roads, cars, and traffic lights.

    Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        sim (Sim): The simulation instance.
        car_images (Dict[int, pygame.Surface]): Dictionary of car images.
        show_debug (bool): Flag to show debug outlines for cars.
    """
    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return
    junction: Junction = junctions[0]

    cx: int = SCREEN_WIDTH // 2
    cy: int = SCREEN_HEIGHT // 2

    # 1) Draw the roads.
    for road in junction.get_roads():
        draw_full_road(screen, cx, cy, road)

    # 2) Draw the intersection box over the roads and cars.
    intersection_rect = pygame.Rect(
        cx - (INTERSECTION_SIZE // 2),
        cy - (INTERSECTION_SIZE // 2),
        INTERSECTION_SIZE,
        INTERSECTION_SIZE,
    )
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)

    # 3) Draw the cars.
    for road in junction.get_roads():
        direction: str = getattr(road, "direction", None)
        for lane_idx, lane in enumerate(road.get_lanes()):
            for car in lane.get_cars():
                if not hasattr(car, "img_index"):
                    car.img_index = random.randint(1, len(car_images))
                car_img: pygame.Surface = car_images[car.img_index]

                x, y, angle = compute_car_position(
                    cx, cy, direction, lane_idx, lane, car
                )
                rotated = pygame.transform.rotate(car_img, angle)
                rect = rotated.get_rect(center=(int(x), int(y)))
                screen.blit(rotated, rect)

                if show_debug:
                    pygame.draw.rect(screen, CAR_DEBUG_COLOR, rect, 1)

    # 4) Draw the traffic lights.
    for tl in junction.get_traffic_lights():
        draw_traffic_light(screen, cx, cy, tl)


###########################################
# DRAW A FULL ROAD ACROSS THE INTERSECTION
###########################################
def draw_full_road(screen: pygame.Surface, cx: int, cy: int, road: Road) -> None:
    """
    Draws a full road (including lanes) across the intersection for a given direction.

    Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        cx (int): X-coordinate of the center.
        cy (int): Y-coordinate of the center.
        road (Road): The road object to draw.
    """
    direction: str = getattr(road, "direction", None)
    lane_len: int = road.get_lanes()[0].LENGTH  # Example lane length.
    half_int: int = INTERSECTION_SIZE // 2
    half_road: int = ROAD_TOTAL_WIDTH // 2

    # Total length includes the portion before, the intersection, and after.
    total_length: int = INTERSECTION_SIZE + 2 * lane_len

    if direction == "north":
        shift_x: int = SHIFT_X_NORTH
        top: int = cy - half_int - lane_len
        left: int = (cx - half_road) + shift_x
        width: int = ROAD_TOTAL_WIDTH
        height: int = total_length

        road_rect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, ASPHALT_COLOR, road_rect)
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction == "south":
        shift_x = SHIFT_X_SOUTH  # FIXME: duplicate code
        top = cy - half_int - lane_len
        left = (cx - half_road) + shift_x
        width = ROAD_TOTAL_WIDTH
        height = total_length

        road_rect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, ASPHALT_COLOR, road_rect)
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction == "east":  # FIXME: duplicate code
        shift_y: int = SHIFT_Y_EAST
        left = cx - half_int - lane_len
        top = (cy - half_road) + shift_y
        width = total_length
        height = ROAD_TOTAL_WIDTH

        road_rect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, ASPHALT_COLOR, road_rect)
        draw_lane_boundaries_horizontal(screen, left, top, width, height)

    elif direction == "west":
        shift_y = SHIFT_Y_WEST  # FIXME: duplicate code
        left = cx - half_int - lane_len
        top = (cy - half_road) + shift_y
        width = total_length
        height = ROAD_TOTAL_WIDTH

        road_rect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, ASPHALT_COLOR, road_rect)
        draw_lane_boundaries_horizontal(screen, left, top, width, height)


###########################################
# LANE BOUNDARIES FOR VERTICAL/HORIZONTAL
###########################################
def draw_lane_boundaries_vertical(
    screen: pygame.Surface, left: int, top: int, width: int, height: int
) -> None:
    # FIXME: duplicate code
    """
    Draws vertical road boundaries and interior lane lines for a vertical road.

    Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        left (int): Left coordinate of the road rectangle.
        top (int): Top coordinate of the road rectangle.
        width (int): Width of the road rectangle.
        height (int): Height of the road rectangle.
    """
    x_left: int = left
    x_right: int = left + width
    y_top: int = top
    y_bot: int = top + height

    boundary1: int = x_left + LANE_MARGIN + LANE_WIDTH
    boundary2: int = boundary1 + LANE_GAP + LANE_WIDTH

    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_left, y_bot), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_right, y_top), (x_right, y_bot), 2)
    pygame.draw.line(
        screen, LANE_MARKING_COLOR, (boundary1, y_top), (boundary1, y_bot), 2
    )
    pygame.draw.line(
        screen, LANE_MARKING_COLOR, (boundary2, y_top), (boundary2, y_bot), 2
    )


def draw_lane_boundaries_horizontal(
    screen: pygame.Surface, left: int, top: int, width: int, height: int
) -> None:
    # FIXME: duplicate code
    """
    Draws horizontal road boundaries and interior lane lines for a horizontal road.

    Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        left (int): Left coordinate of the road rectangle.
        top (int): Top coordinate of the road rectangle.
        width (int): Width of the road rectangle.
        height (int): Height of the road rectangle.
    """
    x_left: int = left
    x_right: int = left + width
    y_top: int = top
    y_bot: int = top + height

    boundary1: int = y_top + LANE_MARGIN + LANE_WIDTH
    boundary2: int = boundary1 + LANE_GAP + LANE_WIDTH

    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_right, y_top), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_bot), (x_right, y_bot), 2)
    pygame.draw.line(
        screen, LANE_MARKING_COLOR, (x_left, boundary1), (x_right, boundary1), 2
    )
    pygame.draw.line(
        screen, LANE_MARKING_COLOR, (x_left, boundary2), (x_right, boundary2), 2
    )


####################################
# DRAW TRAFFIC LIGHT
####################################
def draw_traffic_light(
    screen: pygame.Surface, cx: int, cy: int, tl: TrafficLight
) -> None:
    """
    Renders a traffic light near the center of the intersection.

    Args:
        screen (pygame.Surface): The Pygame surface to draw on.
        cx (int): X-coordinate of the center.
        cy (int): Y-coordinate of the center.
        tl (TrafficLight): The traffic light object.
    """
    is_green: bool = tl.get_state()
    color: Tuple[int, int, int] = (0, 255, 0) if is_green else (255, 0, 0)
    direction: str = getattr(tl, "direction", "north")

    lw: int = 12
    lh: int = 30
    offset: int = 10
    half_int: int = INTERSECTION_SIZE // 2
    half_road: int = ROAD_TOTAL_WIDTH // 2

    if direction == "north":
        x: int = cx - half_road + 10
        y: int = cy - half_int - lh - offset
    elif direction == "south":
        x = cx + half_road - lw - 10
        y = cy + half_int + offset
    elif direction == "east":
        x = cx + half_int + offset
        y = cy + half_road + 10
    else:  # west
        x = cx - half_int - lh - offset
        y = cy - half_road - lh - 10

    housing = pygame.Rect(x, y, lw, lh)
    pygame.draw.rect(screen, (20, 20, 20), housing)
    pygame.draw.circle(screen, color, housing.center, 5)


####################################
# CAR POSITION & ANGLE
####################################
def compute_car_position(
    cx: int, cy: int, direction: str, lane_idx: int, lane: Lane, car: Car
) -> Tuple[float, float, float]:
    """
    Converts a car's distance along its lane into screen coordinates and rotation angle.

    Args:
        cx (int): Center X-coordinate of the screen.
        cy (int): Center Y-coordinate of the screen.
        direction (str): The road direction (e.g., "north", "south").
        lane_idx (int): The index of the lane in the road.
        lane (Lane): The lane object.
        car (Car): The car object.

    Returns:
        Tuple[float, float, float]: The computed (x, y, angle) for rendering the car.
    """
    dist: float = car.get_dist()
    full_dist: int = lane.LENGTH

    # Calculate lane center positions.
    lane_centers = [
        LANE_MARGIN + (LANE_WIDTH / 2),
        LANE_MARGIN + LANE_WIDTH + LANE_GAP + (LANE_WIDTH / 2),
    ]
    lane_center_offset: float = lane_centers[lane_idx]

    half_road: int = ROAD_TOTAL_WIDTH // 2
    half_int: int = INTERSECTION_SIZE // 2

    # Calculate the car's position based on the direction.
    if direction == "north":
        angle: float = -90
        shift_x: int = SHIFT_X_NORTH
        left_boundary: int = (cx - half_road) + shift_x
        x: float = left_boundary + lane_center_offset
        if dist >= 0:
            frac: float = (full_dist - dist) / full_dist
            top_of_road: float = (cy - half_int) - full_dist
            y: float = top_of_road + frac * ((cy - half_int) - top_of_road)
        else:
            # For distances beyond the intersection edge.
            y = (cy - half_int) + abs(dist)

    elif direction == "south":
        angle = 90
        shift_x = SHIFT_X_SOUTH
        left_boundary = (cx - half_road) + shift_x
        x = left_boundary + lane_center_offset
        if dist >= 0:  # FIXME: duplicate code
            frac = (full_dist - dist) / full_dist
            bottom_of_road: float = (cy + half_int) + full_dist
            y = bottom_of_road - frac * (bottom_of_road - (cy + half_int))
        else:
            y = (cy + half_int) - abs(dist)

    elif direction == "east":
        angle = 180
        shift_y: int = SHIFT_Y_EAST
        top_boundary: int = (cy - half_road) + shift_y
        y = top_boundary + lane_center_offset  # TODO: check this
        if dist >= 0:
            frac = (full_dist - dist) / full_dist
            right_of_road: float = (cx + half_int) + full_dist
            x = right_of_road - frac * (right_of_road - (cx + half_int))
        else:
            x = (cx + half_int) - abs(dist)

    else:  # west
        angle = 0
        shift_y = SHIFT_Y_WEST
        top_boundary = (cy - half_road) + shift_y
        y = top_boundary + lane_center_offset
        if dist >= 0:
            frac = (full_dist - dist) / full_dist
            left_of_road: float = (cx - half_int) - full_dist
            x = left_of_road + frac * ((cx - half_int) - left_of_road)
        else:
            x = (cx - half_int) + abs(dist)

    return x, y, angle


if __name__ == "__main__":
    main()
