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
from sim.creator.create_sim import create_junction, index_to_directions, direction_to_index
from utils.RoadEnum import RoadEnum

#########################
# SCREEN / RENDER CONFIG
#########################
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 800
CY: int = SCREEN_HEIGHT // 2
CX: int = SCREEN_WIDTH // 2

BACKGROUND_COLOR: Tuple[int, int, int] = (120, 180, 120)  # Fallback background color

# Road/lane geometry constants
INTERSECTION_SIZE: int = 250  # Size of the square center area
LANE_WIDTH: int = 50
LANE_GAP: int = 10
LANE_MARGIN: int = 0
ROAD_C_GAP = 10

# We keep ROAD_TOTAL_WIDTH=120 only for draw_traffic_light references
ROAD_TOTAL_WIDTH: int = 120

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
    return num_lanes * LANE_WIDTH


def get_road_width_from_id(sim: Sim, road_id: int) -> int:
    return get_road_total_width(len(sim.get_junctions()[0].get_road_by_id(road_id).get_lanes()))


def get_num_lanes_from_id(sim: Sim, road_id: int) -> int:
    return len(sim.get_junctions()[0].get_road_by_id(road_id).get_lanes())


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
    pygame.display.set_caption("Junction Simulation")

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
    # sim: Sim = build_simple_plus_junction_sim()
    sim: Sim = dummy_build_junction()
    # sim.enable_time_based_lights(period_seconds=5.0)
    sim.start()  # Start the simulation thread in the background

    # Load car images from assets.
    car_images: Dict[int, pygame.Surface] = load_car_images(
        num_images=8, folder="../assets/", size=(40, 40)
    )

    def get_len_lanes(road_id: int) -> int:
        return len(sim.get_junctions()[0].get_road_by_id(road_id=road_id).get_lanes())

    # We define the SHIFT dictionary so we can pass it to draw_full_road() and compute_car_position().
    shifts = {
        "NORTH": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.WEST, sim.get_junctions()[0]))),
        "SOUTH": 10,
        "WEST": 10,
        "EAST": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.NORTH, sim.get_junctions()[0]))),
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
                lane_id=lane_id_start + i,
                lane_len = 400,  # e.g., 400 "units" from intersection outward
                car_creation = 0.01  # Probability of new car creation
            )
            for i in range(num_lanes)]

    # Define how many lanes each direction should have.
    road_configs = {
        RoadEnum.NORTH: 2,  # e.g., 3 lanes on the north road
        RoadEnum.EAST: 4,  # 2 lanes on the east road
        RoadEnum.SOUTH: 4,  # 1 lanes on the south road
        RoadEnum.WEST: 1,  # 2 lane on the west road
    }

    roads: List[Road] = []
    lane_id_base = 100

    # Build each road according to the lane counts in 'road_configs'.1
    for side, num_lanes in road_configs.items():
        road = Road(
            road_id=10 + side.value,  # Road ID = 0,1,2,3 for N,E,S,W
            lanes=make_lanes(lane_id_base, num_lanes)
        )
        setattr(road, "from_side", side.value)  # 0=NORTH,1=EAST,2=SOUTH,3=WEST
        lane_id_base += 10  # Jump lane IDs in blocks of 100
        roads.append(road)

    # Build traffic lights for each road approach
    # (NORTH & SOUTH start green, EAST & WEST start red)
    traffic_lights: List[TrafficLight] = []
    for side, road in zip(road_configs.keys(), roads):
        init_state = side in (RoadEnum.NORTH, RoadEnum.SOUTH)
        tl = TrafficLight(
            light_id=side.value + 10,  # e.g., 10, 11, 12, 13 for N,E,S,W
            origins=[lane.get_id() for lane in road.get_lanes()],
            state=init_state
        )
        traffic_lights.append(tl)

    # Create one Junction with these roads and traffic lights
    junction = Junction(
        junction_id=1,
        traffic_lights=traffic_lights,
        roads=roads
    )

    # Finally create and return the Sim instance
    sim = Sim(junctions=[junction], if_ui=True)
    # sim = Sim(junctions=[create_junction()], if_ui=True)
    return sim

def dummy_build_junction() -> Sim:
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
            lane_id_start,
            lane_len=400,  # Adjustable lane length.
            car_creation=0.01,
        )
        lane2 = Lane(
            lane_id_start + 1, lane_len=400, car_creation=0.01
        )
        return [lane1, lane2]

    road_north = Road(road_id=12, from_side=RoadEnum.NORTH, to_side=RoadEnum.SOUTH, lanes=make_lanes(123))
    setattr(road_north, "direction", "NORTH")

    road_south = Road(road_id=11, from_side=RoadEnum.SOUTH, to_side=RoadEnum.NORTH, lanes=make_lanes(111))
    setattr(road_south, "direction", "SOUTH")

    road_east = Road(road_id=14, from_side=RoadEnum.EAST, to_side=RoadEnum.WEST, lanes=make_lanes(147))
    setattr(road_east, "direction", "EAST")

    road_west = Road(road_id=13, from_side=RoadEnum.WEST, to_side=RoadEnum.EAST, lanes=make_lanes(135))
    setattr(road_west, "direction", "WEST")

    # Define traffic lights for each road approach.
    tl_1 = TrafficLight(light_id=1, origins=[111], destinations=[111], state=True)

    tl_8 = TrafficLight(light_id=1, origins=[112], destinations=[112], state=True)

    tl_2 = TrafficLight(light_id=2, origins=[135], destinations=[135], state=True)

    tl_3 = TrafficLight(light_id=3, origins=[136], destinations=[112], state=False)

    tl_4 = TrafficLight(light_id=4, origins=[124], destinations=[124, 148], state=False)

    tl_5 = TrafficLight(light_id=5, origins=[123], destinations=[123, 136], state=True)

    tl_6 = TrafficLight(light_id=6, origins=[148], destinations=[148, 111], state=True)

    tl_7 = TrafficLight(light_id=7, origins=[147], destinations=[147], state=False)

    # Create the junction with the roads and traffic lights.
    junction = Junction(
        junction_id=1,
        traffic_lights=[tl_1, tl_2, tl_3, tl_4, tl_5, tl_6, tl_7, tl_8],
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

    # 1) Draw the roads, passing 'shifts'
    for road in junction.get_roads():
        draw_full_road(screen, road, shifts)

    start_y = CY - get_road_total_width((len(sim.get_junctions()[0].get_road_by_id(direction_to_index(RoadEnum.WEST, junction)).get_lanes()))) - 10
    start_x = CX - get_road_total_width(len(sim.get_junctions()[0].get_road_by_id(direction_to_index(RoadEnum.NORTH, junction)).get_lanes())) - 10
    end_y = get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, junction)) + get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction)) + 2*10 + LANE_GAP / 4
    end_x = get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction)) + get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, junction)) + 2*10 + LANE_GAP / 4
    # 2) Draw the intersection box over the roads
    intersection_rect = pygame.Rect(
        start_y,
        start_x,
        end_y,
        end_x,
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
                    road, lane_idx, lane, car, shifts, sim,
                    screen
                )
                rotated = pygame.transform.rotate(car_img, angle)
                rect = rotated.get_rect(center=(int(x), int(y)))
                screen.blit(rotated, rect)

                if show_debug:
                    pygame.draw.rect(screen, CAR_DEBUG_COLOR, rect, 1)

    # 4) Draw the traffic lights
    for tl in junction.get_traffic_lights():
        draw_traffic_light(screen, sim, tl, shifts)


###########################################
# DRAW A FULL ROAD ACROSS THE INTERSECTION
###########################################
def draw_full_road(
        screen: pygame.Surface,
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

    # Dynamic road width
    road_width = get_road_total_width(num_lanes)
    # Extend beyond intersection on both sides
    total_length = 2 * lane_len

    # Shift offset for this direction
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
    y_top: int = 800
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
    x_right: int = 800
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
        shifts: dict
) -> None:
    """
    Renders a traffic light near the center of the intersection.
    """
    is_green: bool = tl.get_state()
    color: Tuple[int, int, int] = (0, 255, 0) if is_green else (255, 0, 0)

    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return
    junction: Junction = junctions[0]

    # Use the lane ID to figure out direction
    origins = tl.get_origins()
    if not origins:
        return

    direction_val = junction.get_road_by_id(origins[0] // 10).get_from_side()

    min_lane_in_road = min([lane.get_id() for lane in junction.get_road_by_id(origins[0] // 10).get_lanes()])

    lw: int = 12
    lh: int = 30

    lane_offsets = [
        LANE_WIDTH*i
        for i in range(get_num_lanes_from_id(sim, road_id=direction_to_index(direction_val, junction)))
    ]

    if direction_val == RoadEnum.NORTH:  # north
        start_x = CX + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        y = CY - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.NORTH, junction)) - 4*LANE_GAP

        for i, origin in enumerate(origins):
            x = start_x + lane_offsets[origin - min_lane_in_road]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.EAST:  # east
        start_y = CY + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        x = CX + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.EAST, junction)) + 1.25 * LANE_GAP

        for i, origin in enumerate(origins):
            y = start_y + lane_offsets[origin - min_lane_in_road]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.SOUTH:  # south
        start_x = CX + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        y = CY + get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.SOUTH, junction)) + 1.25 * LANE_GAP

        for i, origin in enumerate(origins):
            x = start_x + lane_offsets[origin - min_lane_in_road]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)

    elif direction_val == RoadEnum.WEST:  # west
        start_y = CY + shifts.get(RoadEnum(direction_val).name) + (LANE_WIDTH - lw) / 2
        x = CX - get_road_width_from_id(sim, road_id=direction_to_index(RoadEnum.WEST, junction)) - 2.25 * LANE_GAP

        for i, origin in enumerate(origins):
            y = start_y + lane_offsets[origin - min_lane_in_road]
            housing = pygame.Rect(x, y, lw, lh)
            pygame.draw.rect(screen, (20, 20, 20), housing)
            pygame.draw.circle(screen, color, housing.center, 5)
    else:
        x, y = CX, CY

    housing = pygame.Rect(x, y, lw, lh)
    pygame.draw.rect(screen, (20, 20, 20), housing)
    pygame.draw.circle(screen, color, housing.center, 5)


####################################
# CAR POSITION & ANGLE
####################################
def compute_car_position(
        road: Road,
        lane_idx: int,
        lane: Lane,
        car: Car,
        shifts: dict,
        sim,
        screen # TODO remove this just for debug
) -> Tuple[float, float, float]:
    """
    Computes the (x, y, angle) of a car on a dynamic-width road,
    applying the correct horizontal/vertical shift based on direction.
    """
    direction_int = getattr(road, "from_side", 0)
    direction_str = RoadEnum(direction_int).name
    dist = car.get_dist()
    num_lanes = len(road.get_lanes())
    half_int = INTERSECTION_SIZE // 2

    # Lane-center offsets for each lane index
    lane_offsets = [
        LANE_WIDTH*i + LANE_WIDTH // 2
        for i in range(num_lanes)
    ]
    # Clamp lane_idx safely
    lane_center_offset = lane_offsets[lane_idx]

    # Get the shift for this direction
    shift = shifts.get(direction_str, 0)

    x, y, angle = 0.0, 0.0, 0.0

    if direction_str == "NORTH":
        angle = -90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset

        shift_y = CY - get_road_width_from_id(sim, road_id=road.get_id()) - 10

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

        shift_y = CY + get_road_width_from_id(sim, road_id=road.get_id()) + 10

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

        shift_x = CX + get_road_width_from_id(sim, road_id=road.get_id()) + 10

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

        shift_x = CX - get_road_width_from_id(sim, road_id=road.get_id()) - 10

        if dist >= 0:
            left_of_road = shift_x - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = left_of_road + frac * lane.LENGTH
        else:
            x = shift_x + abs(dist)

    return x, y, angle


if __name__ == "__main__":
    main()
