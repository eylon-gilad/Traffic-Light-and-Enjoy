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
from sim.creator.create_sim import create_junction, index_to_directions
from utils.RoadEnum import RoadEnum

#########################
# SCREEN / RENDER CONFIG
#########################
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 800

BACKGROUND_COLOR: Tuple[int, int, int] = (120, 180, 120)  # Fallback background color

# Road/lane geometry constants
INTERSECTION_SIZE: int = 250  # Size of the square center area
LANE_WIDTH: int = 50
LANE_GAP: int = 10
LANE_MARGIN: int = 5

# We keep ROAD_TOTAL_WIDTH=120 only for draw_traffic_light references
ROAD_TOTAL_WIDTH: int = 120

# SHIFT offsets to avoid overlapping roads at the intersection.
SHIFT_X_NORTH: int = -65  # Shift north road to the left
SHIFT_X_SOUTH: int = 65   # Shift south road to the right
SHIFT_Y_EAST: int = 65    # Shift east road downward
SHIFT_Y_WEST: int = -65   # Shift west road upward

# Colors
ASPHALT_COLOR: Tuple[int, int, int] = (50, 50, 50)
INTERSECTION_COLOR: Tuple[int, int, int] = (60, 60, 60)
LANE_MARKING_COLOR: Tuple[int, int, int] = (255, 255, 255)
CAR_DEBUG_COLOR: Tuple[int, int, int] = (255, 0, 0)

FPS: int = 60


def get_road_total_width(num_lanes: int) -> int:
    """
    Computes total width from the number of lanes, lane width, margin, and gap.
    """
    return (2 * LANE_MARGIN) + (num_lanes * LANE_WIDTH) + ((num_lanes - 1) * LANE_GAP)


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
    pygame.display.set_caption("Plus-Junction: Dynamic Lanes Demo")

    clock: pygame.time.Clock = pygame.time.Clock()
    show_debug: bool = False
    running: bool = True

    # Attempt to load a background image; if unavailable, fallback to a solid color.
    try:
        bg_image: pygame.Surface = pygame.image.load(
            "../assets/background.png"
        ).convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        bg_image = None

    # Build the simulation with a plus-junction configuration.
    sim: Sim = build_simple_plus_junction_sim()
    sim.enable_time_based_lights(period_seconds=5.0)
    sim.start()  # Start the simulation thread in the background

    # Load car images from assets.
    car_images: Dict[int, pygame.Surface] = load_car_images(
        num_images=8, folder="../assets/", size=(40, 40)
    )

    # We define the SHIFT dictionary so we can pass it to draw_full_road() and compute_car_position().
    shifts = {
        "NORTH": SHIFT_X_NORTH,
        "SOUTH": SHIFT_X_SOUTH,
        "EAST": SHIFT_Y_EAST,
        "WEST": SHIFT_Y_WEST,
    }

    while running:
        dt: float = clock.tick(FPS) / 1000.0  # Delta time in seconds (unused here)
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

        # Render the junction and simulation elements, now passing 'shifts'.
        draw_junction_ui(screen, sim, car_images, shifts, show_debug)
        pygame.display.flip()

    sim.stop()
    pygame.quit()
    sys.exit()


#########################
# BUILD THE JUNCTION
#########################
def build_simple_plus_junction_sim() -> Sim:
    """
    Creates a plus-junction simulation with dynamic lane counts for each road
    (NORTH, EAST, SOUTH, WEST). Returns a Sim instance.
    """

    # Helper function to generate a specified number of lanes.
    def make_lanes(lane_id_start: int, num_lanes: int) -> List[Lane]:
        return [
            Lane(
                id=lane_id_start + i,
                lane_len=400,       # e.g., 400 "units" from intersection outward
                car_creation=0.01   # Probability of new car creation
            )
            for i in range(num_lanes)
        ]

    # Define how many lanes each direction should have.
    road_configs = {
        RoadEnum.NORTH: 3,  # e.g., 3 lanes on the north road
        RoadEnum.EAST: 2,   # 2 lanes on the east road
        RoadEnum.SOUTH: 1,  # 1 lanes on the south road
        RoadEnum.WEST: 2,   # 2 lane on the west road
    }

    roads: List[Road] = []
    lane_id_base = 100

    # Build each road according to the lane counts in 'road_configs'.
    for side, num_lanes in road_configs.items():
        road = Road(
            id=side.value,                        # Road ID = 0,1,2,3 for N,E,S,W
            lanes=make_lanes(lane_id_base, num_lanes)
        )
        setattr(road, "from_side", side.value)    # 0=NORTH,1=EAST,2=SOUTH,3=WEST
        lane_id_base += 100                       # Jump lane IDs in blocks of 100
        roads.append(road)

    # Build traffic lights for each road approach
    # (NORTH & SOUTH start green, EAST & WEST start red)
    traffic_lights: List[TrafficLight] = []
    for side, road in zip(road_configs.keys(), roads):
        init_state = side in (RoadEnum.NORTH, RoadEnum.SOUTH)
        tl = TrafficLight(
            id=side.value + 10,  # e.g., 10, 11, 12, 13 for N,E,S,W
            origins=[lane.get_id() for lane in road.get_lanes()],
            state=init_state
        )
        traffic_lights.append(tl)

    # Create one Junction with these roads and traffic lights
    junction = Junction(
        id=99,
        traffic_lights=traffic_lights,
        roads=roads
    )

    # Finally create and return the Sim instance
    sim = Sim(junctions=[junction], if_ui=True)
    return sim


#########################
# TIME-BASED LIGHTS
#########################
def enable_time_based_lights(self: Sim, period_seconds: float = 5.0) -> None:
    """
    Monkey-patches the Sim instance to toggle all traffic lights every specified period.
    """
    original_update_lights = self._Sim__update_traffic_lights

    def new_update_lights() -> None:
        now = time.time()
        if not hasattr(self, "_light_cycle_start"):
            self._light_cycle_start = now
        elapsed = now - self._light_cycle_start
        if elapsed >= period_seconds:
            for junction in self.get_junctions():
                for tl in junction.get_traffic_lights():
                    if tl.get_state():
                        tl.red()
                    else:
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
) -> None:
    """
    Draws the entire junction UI, including roads, cars, and traffic lights.
    """
    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return
    junction: Junction = junctions[0]

    cx: int = SCREEN_WIDTH // 2
    cy: int = SCREEN_HEIGHT // 2

    # 1) Draw the roads, passing 'shifts'
    for road in junction.get_roads():
        draw_full_road(screen, cx, cy, road, shifts)

    # 2) Draw the intersection box over the roads
    intersection_rect = pygame.Rect(
        cx - (INTERSECTION_SIZE // 2),
        cy - (INTERSECTION_SIZE // 2),
        INTERSECTION_SIZE,
        INTERSECTION_SIZE,
    )
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)

    # 3) Draw the cars
    for road in junction.get_roads():
        for lane_idx, lane in enumerate(road.get_lanes()):
            for car in lane.get_cars():
                if not hasattr(car, "img_index"):
                    car.img_index = random.randint(1, len(car_images))
                car_img: pygame.Surface = car_images[car.img_index]

                x, y, angle = compute_car_position(
                    cx, cy, road, lane_idx, lane, car, shifts
                )
                rotated = pygame.transform.rotate(car_img, angle)
                rect = rotated.get_rect(center=(int(x), int(y)))
                screen.blit(rotated, rect)

                if show_debug:
                    pygame.draw.rect(screen, CAR_DEBUG_COLOR, rect, 1)

    # 4) Draw the traffic lights
    for tl in junction.get_traffic_lights():
        draw_traffic_light(screen, cx, cy, tl)


###########################################
# DRAW A FULL ROAD ACROSS THE INTERSECTION
###########################################
def draw_full_road(
    screen: pygame.Surface,
    cx: int,
    cy: int,
    road: Road,
    shifts: dict
) -> None:
    """
    Draws a full road (including lanes) across the intersection for a given direction,
    using a shift offset to handle different lane counts on parallel roads.
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    num_lanes = len(road.get_lanes())
    lane_len = road.get_lanes()[0].LENGTH if road.get_lanes() else 400
    half_int = INTERSECTION_SIZE // 2

    # Dynamic road width
    road_width = get_road_total_width(num_lanes)
    # Extend beyond intersection on both sides
    total_length = INTERSECTION_SIZE + 2 * lane_len

    # Shift offset for this direction
    shift = shifts.get(direction_str, 0)

    if direction_str == "NORTH":
        left = cx - (road_width // 2) + shift
        top = cy - half_int - lane_len
        width = road_width
        height = total_length

        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction_str == "SOUTH":
        left = cx - (road_width // 2) + shift
        top = cy - half_int - lane_len
        width = road_width
        height = total_length

        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_vertical(screen, left, top, width, height)

    elif direction_str == "EAST":
        left = cx - half_int - lane_len
        top = cy - (road_width // 2) + shift
        width = total_length
        height = road_width

        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        draw_lane_boundaries_horizontal(screen, left, top, width, height)

    elif direction_str == "WEST":
        left = cx - half_int - lane_len
        top = cy - (road_width // 2) + shift
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
    y_top: int = top
    y_bot: int = top + height

    # We assume exactly 2 interior lines (for 3-lane roads), but if you want
    # to handle an arbitrary number of lanes, you should loop. For now, this
    # code is your original approach for 2-lane roads. You can expand it if needed.
    boundary1: int = x_left + LANE_MARGIN + LANE_WIDTH
    boundary2: int = boundary1 + LANE_GAP + LANE_WIDTH

    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_left, y_bot), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_right, y_top), (x_right, y_bot), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (boundary1, y_top), (boundary1, y_bot), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (boundary2, y_top), (boundary2, y_bot), 2)


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
    x_left: int = left
    x_right: int = left + width
    y_top: int = top
    y_bot: int = top + height

    boundary1: int = y_top + LANE_MARGIN + LANE_WIDTH
    boundary2: int = boundary1 + LANE_GAP + LANE_WIDTH

    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_right, y_top), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_bot), (x_right, y_bot), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, boundary1), (x_right, boundary1), 2)
    pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, boundary2), (x_right, boundary2), 2)


####################################
# DRAW TRAFFIC LIGHT
####################################
def draw_traffic_light(
    screen: pygame.Surface,
    cx: int,
    cy: int,
    tl: TrafficLight
) -> None:
    """
    Renders a traffic light near the center of the intersection.
    """
    is_green: bool = tl.get_state()
    color: Tuple[int, int, int] = (0, 255, 0) if is_green else (255, 0, 0)

    # Use the lane ID to figure out direction
    origins = tl.get_origins()
    if not origins:
        return
    direction_val = index_to_directions((origins[0] // 100) - 1)[0]

    lw: int = 12
    lh: int = 30
    offset: int = 10
    half_int: int = INTERSECTION_SIZE // 2
    half_road: int = ROAD_TOTAL_WIDTH // 2

    if direction_val == 0:  # north
        x: int = cx - half_road + 10
        y: int = cy - half_int - lh - offset
    elif direction_val == 1:  # east
        x = cx + half_road - lw - 10
        y = cy + half_int + offset
    elif direction_val == 2:  # south
        x = cx + half_int + offset
        y = cy + half_road + 10
    elif direction_val == 3:  # west
        x = cx - half_int - lh - offset
        y = cy - half_road - lh - 10
    else:
        x, y = cx, cy

    housing = pygame.Rect(x, y, lw, lh)
    pygame.draw.rect(screen, (20, 20, 20), housing)
    pygame.draw.circle(screen, color, housing.center, 5)


####################################
# CAR POSITION & ANGLE
####################################
def compute_car_position(
    cx: int,
    cy: int,
    road: Road,
    lane_idx: int,
    lane: Lane,
    car: Car,
    shifts: dict
) -> Tuple[float, float, float]:
    """
    Computes the (x, y, angle) of a car on a dynamic-width road,
    applying the correct horizontal/vertical shift based on direction.
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    dist = car.get_dist()
    num_lanes = len(road.get_lanes())
    road_width = get_road_total_width(num_lanes)
    half_int = INTERSECTION_SIZE // 2

    # Lane-center offsets for each lane index
    lane_offsets = [
        LANE_MARGIN + (LANE_WIDTH / 2) + i * (LANE_WIDTH + LANE_GAP)
        for i in range(num_lanes)
    ]
    # Clamp lane_idx safely
    lane_idx = max(0, min(lane_idx, num_lanes - 1))
    lane_center_offset = lane_offsets[lane_idx]

    # Get the shift for this direction
    shift = shifts.get(direction_str, 0)

    x, y, angle = 0.0, 0.0, 0.0

    if direction_str == "NORTH":
        angle = -90
        left_boundary = cx - (road_width // 2) + shift
        x = left_boundary + lane_center_offset
        if dist >= 0:
            top_of_road = (cy - half_int) - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            y = top_of_road + frac * ((cy - half_int) - top_of_road)
        else:
            y = (cy - half_int) + abs(dist)

    elif direction_str == "SOUTH":
        angle = 90
        left_boundary = cx - (road_width // 2) + shift
        x = left_boundary + lane_center_offset
        if dist >= 0:
            bottom_of_road = (cy + half_int) + lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            y = bottom_of_road - frac * (bottom_of_road - (cy + half_int))
        else:
            y = (cy + half_int) - abs(dist)

    elif direction_str == "EAST":
        angle = 180
        top_boundary = cy - (road_width // 2) + shift
        y = top_boundary + lane_center_offset
        if dist >= 0:
            right_of_road = (cx + half_int) + lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = right_of_road - frac * (right_of_road - (cx + half_int))
        else:
            x = (cx + half_int) - abs(dist)

    elif direction_str == "WEST":
        angle = 0
        top_boundary = cy - (road_width // 2) + shift
        y = top_boundary + lane_center_offset
        if dist >= 0:
            left_of_road = (cx - half_int) - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = left_of_road + frac * ((cx - half_int) - left_of_road)
        else:
            x = (cx - half_int) + abs(dist)

    return x, y, angle


if __name__ == "__main__":
    main()
