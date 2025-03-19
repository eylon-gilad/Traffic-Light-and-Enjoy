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
from sim.creator.create_sim import direction_to_index
from utils.RoadEnum import RoadEnum
from sim.Generator.JunctionGenerator import JunctionGenerator

#########################
# SCREEN / RENDER CONFIG
#########################
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 800
CY: int = SCREEN_HEIGHT // 2
CX: int = SCREEN_WIDTH // 2

BACKGROUND_COLOR: Tuple[int, int, int] = (120, 180, 120)  # Fallback background color

# Road/lane geometry constants
LANE_WIDTH: int = 50
LANE_GAP: int = 10

# We keep ROAD_TOTAL_WIDTH=120 only for draw_traffic_light references
ROAD_TOTAL_WIDTH: int = 120

# Colors
ASPHALT_COLOR: Tuple[int, int, int] = (50, 50, 50)
INTERSECTION_COLOR: Tuple[int, int, int] = (60, 60, 60)
LANE_MARKING_COLOR: Tuple[int, int, int] = (255, 255, 255)
CAR_DEBUG_COLOR: Tuple[int, int, int] = (255, 0, 0)

FPS: int = 60

# ------------------------------
# NEW: Local "yellow" logic data
# ------------------------------
light_prev_states: Dict[int, bool] = {}
light_green_times: Dict[int, float] = {}
YELLOW_DELAY = 1.0  # seconds of "yellow" after turning green


def get_road_total_width(num_lanes: int) -> int:
    """
    Computes total width from the number of lanes, lane width, margin, and gap.
    """
    return num_lanes * LANE_WIDTH


def get_road_width_from_id(sim: Sim, road_id: int) -> int:
    """
    Gets the total road width in pixels for a particular road_id in the simulation.
    """
    return get_road_total_width(len(sim.get_junctions()[0].get_road_by_id(road_id).get_lanes()))


def get_num_lanes_from_id(sim: Sim, road_id: int) -> int:
    """
    Returns the number of lanes for a particular road_id in the simulation.
    """
    return len(sim.get_junctions()[0].get_road_by_id(road_id).get_lanes())


#########################
# MAIN GAME LOOP
#########################
def main() -> None:
    """
    Initializes Pygame, sets up the simulation, and enters the main game loop.
    Handles events, rendering, and graceful shutdown.

    Press 'D' to toggle debug mode (bounding boxes, lane labels, etc.).
    Press 'ESC' or close the window to exit.
    """
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Junction Simulation")

    clock: pygame.time.Clock = pygame.time.Clock()
    show_debug: bool = False
    running: bool = True

    # Create a small font for debug text
    debug_font = pygame.font.SysFont(None, 18)

    # Attempt to load a background image; if unavailable, fallback to a solid color.
    try:
        bg_image: pygame.Surface = pygame.image.load(
            "../assets/background.png"
        ).convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        bg_image = None

    # Build the simulation with a plus-junction configuration.
    sim: Sim = Sim(junctions=[JunctionGenerator.generate_junction()], if_ui=True)
    sim.start()  # Start the simulation thread in the background

    # Load car images from assets.
    car_images: Dict[int, pygame.Surface] = load_car_images(
        num_images=8, folder="../assets/", size=(40, 40)
    )

    def get_len_lanes(road_id: int) -> int:
        return len(sim.get_junctions()[0].get_road_by_id(road_id=road_id).get_lanes())

    # We define the SHIFT dictionary so we can pass it to draw_full_road() and compute_car_position().
    shifts = {
        "NORTH": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.NORTH, sim.get_junctions()[0]))),
        "SOUTH": 10,
        "WEST": 10,
        "EAST": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.EAST, sim.get_junctions()[0]))),
    }

    while running:
        dt: float = clock.tick(FPS) / 1000.0  # Delta time in seconds
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

        # Render the junction and simulation elements
        draw_junction_ui(screen, sim, car_images, shifts, show_debug, debug_font)

        pygame.display.flip()

    sim.stop()
    pygame.quit()
    sys.exit()

#########################
# LOAD CAR IMAGES
#########################
def load_car_images(
        num_images: int = 8, folder: str = "../assets/", size: Tuple[int, int] = (40, 40)
) -> Dict[int, pygame.Surface]:
    """
    Loads car images from the specified folder. If an image is not found,
    creates a placeholder surface.
    """
    images: Dict[int, pygame.Surface] = {}
    for i in range(1, num_images + 1):
        try:
            path: str = f"{folder}/car{i}.png"
            img: pygame.Surface = pygame.image.load(path).convert_alpha()
            images[i] = pygame.transform.scale(img, size)
        except Exception:
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
        shifts: Dict[str, int],
        show_debug: bool = False,
        debug_font: pygame.font.Font = None,
) -> None:
    """
    Draws the entire junction UI, including roads, cars, and traffic lights.
    If show_debug is True, additional debug info is drawn (lane IDs, bounding boxes, etc.).
    """
    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return
    junction: Junction = junctions[0]

    # 1) Draw the roads
    for road in junction.get_roads():
        draw_full_road(screen, road, shifts)

    # 2) Draw the intersection box
    start_y = CY - get_road_total_width(len(sim.get_junctions()[0]
                  .get_road_by_id(direction_to_index(RoadEnum.NORTH, junction))
                  .get_lanes())) - 10
    start_x = CX - get_road_total_width(len(sim.get_junctions()[0]
                  .get_road_by_id(direction_to_index(RoadEnum.EAST, junction))
                  .get_lanes())) - 10
    end_y = (get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction)) +
             get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, junction)) +
             2*10 + LANE_GAP / 4)
    end_x = (get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, junction)) +
             get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction)) +
             2*10 + LANE_GAP / 4)

    intersection_rect = pygame.Rect(start_y, start_x, end_y, end_x)
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)

    # 3) Draw the cars
    for road in junction.get_roads():
        for lane_idx, lane in enumerate(road.get_lanes()):
            for car in lane.get_cars():
                if not hasattr(car, "img_index"):
                    # Assign a random image index if none is set
                    car.img_index = random.randint(1, len(car_images))
                car_img: pygame.Surface = car_images[car.img_index]

                x, y, angle = compute_car_position(
                    road, lane_idx, lane, car, shifts, sim, junction
                )
                rotated = pygame.transform.rotate(car_img, angle)
                rect = rotated.get_rect(center=(int(x), int(y)))
                screen.blit(rotated, rect)

                # If debug, draw bounding box
                if show_debug:
                    pygame.draw.rect(screen, CAR_DEBUG_COLOR, rect, 1)

    # 4) Draw the traffic lights
    for tl in junction.get_traffic_lights():
        draw_traffic_light(screen, sim, tl, shifts)

        # Optionally label traffic lights in debug mode
        if show_debug and debug_font is not None:
            draw_traffic_light_id(screen, tl, sim, debug_font, shifts)

    # 5) If debug mode is on, draw lane info
    if show_debug and debug_font is not None:
        for road in junction.get_roads():
            for lane_idx, lane in enumerate(road.get_lanes()):
                draw_lane_debug_info(screen, road, lane_idx, lane, shifts, sim, debug_font)


def draw_lane_debug_info(
    screen: pygame.Surface,
    road: Road,
    lane_idx: int,
    lane: Lane,
    shifts: Dict[str, int],
    sim: Sim,
    font: pygame.font.Font
) -> None:
    """
    Draws text in the middle of each lane with:
     - Lane ID
     - Number of cars in this lane
    """
    dist_mid = lane.LENGTH / 2.0  # place the text roughly halfway along lane
    x, y, _ = compute_position_at_dist(road, lane_idx, dist_mid, shifts, sim)

    debug_text = f"{lane.get_id()} ({len(lane.get_cars())}) - {lane.get_car_creation()}"
    text_surf = font.render(debug_text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)


def compute_position_at_dist(
    road: Road,
    lane_idx: int,
    dist: float,
    shifts: Dict[str, int],
    sim: Sim
) -> Tuple[float, float, float]:
    """
    Similar to compute_car_position, but we specify the distance ourselves.
    Returns (x, y, angle). Used for debugging lane info (placing text).
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    num_lanes = len(road.get_lanes())

    # Lane-center offsets for each lane index, reversed
    lane_offsets = [
        LANE_WIDTH * (num_lanes - 1 - i) + (LANE_WIDTH // 2)
        for i in range(num_lanes)
    ]
    lane_center_offset = lane_offsets[lane_idx]
    shift = shifts.get(direction_str, 0)

    x, y, angle = 0.0, 0.0, 0.0
    length = road.get_lanes()[0].LENGTH if road.get_lanes() else 400

    if direction_str == "NORTH":
        angle = -90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY - get_road_width_from_id(sim, road_id=road.get_id()) - 10
        # The lane extends from (shift_y - length) to shift_y
        y = (shift_y - length) + dist

    elif direction_str == "SOUTH":
        angle = 90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY + get_road_width_from_id(sim, road_id=road.get_id()) + 10
        y = shift_y + (length - dist)

    elif direction_str == "EAST":
        angle = 180
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX + get_road_width_from_id(sim, road_id=road.get_id()) + 10
        x = shift_x + (length - dist)

    elif direction_str == "WEST":
        angle = 0
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX - get_road_width_from_id(sim, road_id=road.get_id()) - 10
        x = (shift_x - length) + dist

    return x, y, angle


###########################################
# DRAW A FULL ROAD ACROSS THE INTERSECTION
###########################################
def draw_full_road(
        screen: pygame.Surface,
        road: Road,
        shifts: Dict[str, int]
) -> None:
    """
    Draws a full road (including lanes) across the intersection for a given direction,
    using a shift offset to handle different lane counts on parallel roads.
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    num_lanes = len(road.get_lanes())
    lane_len = road.get_lanes()[0].LENGTH if road.get_lanes() else 400

    road_width = get_road_total_width(num_lanes)
    total_length = 2 * lane_len

    shift = shifts.get(direction_str, 0)

    if direction_str == "NORTH":
        left = CX + shift
        top = 0
        width = road_width
        height = total_length
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction_str == "SOUTH":
        left = CX + shift
        top = 0
        width = road_width
        height = total_length
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction_str == "EAST":
        left = 0
        top = CY + shift
        width = total_length
        height = road_width
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_horizontal(screen, left, top, width, height)

    elif direction_str == "WEST":
        left = 0
        top = CY + shift
        width = total_length
        height = road_width
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_horizontal(screen, left, top, width, height)


###########################################
# LANE BOUNDARIES FOR VERTICAL/HORIZONTAL
###########################################
def draw_lane_boundaries_vertical(
        screen: pygame.Surface,
        left: int,
        top: int,
        width: int,
        height: int
) -> None:
    """
    Draws vertical road boundaries and interior lane lines for a vertical road.
    """
    x_left: int = left
    x_right: int = left + width
    y_top: int = SCREEN_HEIGHT
    y_bot: int = 0

    while x_left <= x_right:
        pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_left, y_bot), 2)
        x_left += LANE_WIDTH


def draw_lane_boundaries_horizontal(
        screen: pygame.Surface,
        left: int,
        top: int,
        width: int,
        height: int
) -> None:
    """
    Draws horizontal road boundaries and interior lane lines for a horizontal road.
    """
    x_left: int = 0
    x_right: int = SCREEN_WIDTH
    y_top: int = top
    y_bot: int = top + height

    while y_top <= y_bot:
        pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_right, y_top), 2)
        y_top += LANE_WIDTH


####################################
# DRAW TRAFFIC LIGHT
####################################
def draw_traffic_light(
        screen: pygame.Surface,
        sim: Sim,
        tl: TrafficLight,
        shifts: Dict[str, int]
) -> None:
    """
    Renders a traffic light near the center of the intersection,
    showing a local "yellow" color if the light turned green < YELLOW_DELAY seconds ago.
    """
    global light_prev_states, light_green_times, YELLOW_DELAY

    # Check the previous known state for this light
    tl_id = tl.get_id()
    old_state = light_prev_states.get(tl_id, False)  # default: red
    new_state = tl.get_state()                      # current server state

    # If the light just switched from red->green, record time
    if old_state is False and new_state is True:
        light_green_times[tl_id] = time.time()

    light_prev_states[tl_id] = new_state

    # Decide color
    if new_state is True:
        # It's "green", but check how long it's been green
        turned_green_at = light_green_times.get(tl_id, 0.0)
        time_since_green = time.time() - turned_green_at
        if time_since_green < YELLOW_DELAY:
            # Draw it yellow if it's been green for < 1 second
            color = (255, 255, 0)  # YELLOW
        else:
            color = (0, 255, 0)    # GREEN
    else:
        color = (255, 0, 0)       # RED

    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return
    junction: Junction = junctions[0]

    origins = tl.get_origins()
    if not origins:
        return

    direction_val = junction.get_road_by_id(origins[0] // 10).get_from_side()
    min_lane_in_road = min(l.get_id() for l in junction.get_road_by_id(origins[0] // 10).get_lanes())

    lw: int = 12
    lh: int = 30

    # We'll invert lane indexing here too
    num_lanes_in_road = get_num_lanes_from_id(sim, road_id=direction_to_index(direction_val, junction))
    lane_offsets = [
        LANE_WIDTH * (num_lanes_in_road - 1 - i)
        for i in range(num_lanes_in_road)
    ]

    if direction_val == RoadEnum.NORTH:
        start_x = CX + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        y = CY - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.EAST, junction)) - 4 * LANE_GAP
        for origin in origins:
            offset_idx = origin - min_lane_in_road
            x = start_x + lane_offsets[offset_idx]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.EAST:
        start_y = CY + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        x = CX + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.SOUTH, junction)) + 1.25 * LANE_GAP
        for origin in origins:
            offset_idx = origin - min_lane_in_road
            y = start_y + lane_offsets[offset_idx]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.SOUTH:
        start_x = CX + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        y = CY + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.WEST, junction)) + 1.25 * LANE_GAP
        for origin in origins:
            offset_idx = origin - min_lane_in_road
            x = start_x + lane_offsets[offset_idx]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.WEST:
        start_y = CY + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        x = CX - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.NORTH, junction)) - 2.25 * LANE_GAP
        for origin in origins:
            offset_idx = origin - min_lane_in_road
            y = start_y + lane_offsets[offset_idx]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)
    else:
        # fallback if direction is missing
        x, y = CX, CY
        housing = pygame.Rect(x, y, lw, lh)
        pygame.draw.rect(screen, (20, 20, 20), housing)
        pygame.draw.circle(screen, color, housing.center, 5)


def draw_traffic_light_id(
    screen: pygame.Surface,
    tl: TrafficLight,
    sim: Sim,
    font: pygame.font.Font,
    shifts: Dict[str, int]
) -> None:
    """
    (Debug) Displays the traffic light's ID near its first origin lane.
    """
    junctions: List[Junction] = sim.get_junctions()
    if not junctions or not tl.get_origins():
        return

    junction: Junction = junctions[0]
    lane_id = tl.get_origins()[0]
    road_id = lane_id // 10
    road = junction.get_road_by_id(road_id)
    direction_val = road.get_from_side()

    min_lane_in_road = min(l.get_id() for l in road.get_lanes())
    offset_idx = lane_id - min_lane_in_road

    lw: int = 12
    direction_str = RoadEnum(direction_val).name
    shift = shifts.get(direction_str, 0)

    label_text = f"TL ID: {tl.get_id()}"
    text_surf = font.render(label_text, True, (0, 0, 0))
    label_rect = text_surf.get_rect()

    if direction_val == RoadEnum.NORTH:
        start_x = CX + shift + (LANE_WIDTH - lw) / 2
        y = CY - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.EAST, junction)) - 4 * LANE_GAP
        x = start_x + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x, y - 10)
        screen.blit(text_surf, label_rect)

    elif direction_val == RoadEnum.EAST:
        start_y = CY + shift + (LANE_WIDTH - lw) / 2
        x = CX + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.SOUTH, junction)) + 1.25 * LANE_GAP
        y = start_y + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x + 25, y)
        screen.blit(text_surf, label_rect)

    elif direction_val == RoadEnum.SOUTH:
        start_x = CX + shift + (LANE_WIDTH - lw) / 2
        y = CY + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.WEST, junction)) + 1.25 * LANE_GAP
        x = start_x + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x, y + 20)
        screen.blit(text_surf, label_rect)

    elif direction_val == RoadEnum.WEST:
        start_y = CY + shift + (LANE_WIDTH - lw) / 2
        x = CX - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.NORTH, junction)) - 2.25 * LANE_GAP
        y = start_y + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x - 25, y)
        screen.blit(text_surf, label_rect)


####################################
# CAR POSITION & ANGLE
####################################
def compute_car_position(
        road: Road,
        lane_idx: int,
        lane: Lane,
        car: Car,
        shifts: Dict[str, int],
        sim: Sim,
        junction: Junction
) -> Tuple[float, float, float]:
    """
    Computes the (x, y, angle) of a car on a dynamic-width road,
    applying the correct horizontal/vertical shift based on direction.
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    dist = car.get_dist()
    num_lanes = len(road.get_lanes())

    # Lane-center offsets for each lane index, reversed
    lane_offsets = [
        LANE_WIDTH * (num_lanes - 1 - i) + (LANE_WIDTH // 2)
        for i in range(num_lanes)
    ]
    lane_center_offset = lane_offsets[lane_idx]
    shift = shifts.get(direction_str, 0)

    x, y, angle = 0.0, 0.0, 0.0

    if direction_str == "NORTH":
        angle = -90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.EAST, junction)) - 10

        if dist >= 0:
            top_of_road = shift_y - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            y = top_of_road + frac * lane.LENGTH
        else:
            y = shift_y + abs(dist)

    elif direction_str == "SOUTH":
        angle = 90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.WEST, junction)) + 10

        if dist >= 0:
            bottom_of_road = shift_y + lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            y = bottom_of_road - frac * lane.LENGTH
        else:
            y = shift_y - abs(dist)

    elif direction_str == "EAST":
        angle = 180
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.SOUTH, junction)) + 10

        if dist >= 0:
            right_of_road = shift_x + lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = right_of_road - frac * lane.LENGTH
        else:
            x = shift_x - abs(dist)

    elif direction_str == "WEST":
        angle = 0
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.NORTH, junction)) - 10

        if dist >= 0:
            left_of_road = shift_x - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = left_of_road + frac * lane.LENGTH
        else:
            x = shift_x + abs(dist)

    return x, y, angle


if __name__ == "__main__":
    main()
