"""
rendering.py

Provides functions for drawing roads, cars, traffic lights, and debug overlays.
"""

import random
import math
from typing import Dict, Tuple, List

import pygame

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CX, CY,
    BACKGROUND_COLOR, ASPHALT_COLOR, INTERSECTION_COLOR,
    LANE_MARKING_COLOR, CAR_DEBUG_COLOR,
    LANE_WIDTH, LANE_GAP,
    get_road_total_width,
)
from sim.Sim import Sim
from utils.RoadEnum import RoadEnum
from utils.TrafficLight import TrafficLight
from utils.Junction import Junction
from utils.Road import Road
from utils.Lane import Lane
from utils.Car import Car
from sim.ui.assets import  load_tl_image


def draw_game_screen(
    screen: pygame.Surface,
    sim: Sim,
    car_images: Dict[int, pygame.Surface],
    bg_image: pygame.Surface,
    show_debug: bool,
    debug_font: pygame.font.Font
) -> None:
    """
    The main rendering function.
    - Fills or draws background
    - Renders roads, cars, traffic lights
    - Renders debug if needed
    """
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)

    # We only handle one junction for simplicity
    junctions: List[Junction] = sim.get_junctions()
    if not junctions:
        return

    junction: Junction = junctions[0]

    # Precompute shifts used to align roads (see original logic).
    # For brevity, assume you have a function to get correct shift dictionary.
    shifts = _compute_shifts(sim, junction)

    # 1) Draw roads
    for road in junction.get_roads():
        _draw_full_road(screen, road, shifts)

    # 2) Draw intersection box
    _draw_intersection(screen, sim, junction)

    # 3) Draw traffic lights
    for tl in junction.get_traffic_lights():
        _draw_traffic_light(screen, sim, tl, shifts)
        if show_debug:
            _draw_traffic_light_id(screen, tl, sim, shifts, debug_font)

    # 4) Draw cars
    for road in junction.get_roads():
        for lane_idx, lane in enumerate(road.get_lanes()):
            for car in lane.get_cars():
                if not hasattr(car, "img_index"):
                    car.img_index = random.randint(1, len(car_images))
                car_img: pygame.Surface = car_images[car.img_index]

                x, y, angle = _compute_car_position(road, lane_idx, lane, car, shifts, sim)
                rotated = pygame.transform.rotate(car_img, angle)

                # Flip the sprite horizontally when facing EAST
                if RoadEnum(road.get_from_side()).name == "EAST":
                    rotated = pygame.transform.flip(rotated, True, False)

                rect = rotated.get_rect(center=(int(x), int(y)))
                screen.blit(rotated, rect)

                # Debug bounding box
                if show_debug:
                    pygame.draw.rect(screen, CAR_DEBUG_COLOR, rect, 1)

    # 5) If debug, draw lane info
    if show_debug:
        for road in junction.get_roads():
            for lane_idx, lane in enumerate(road.get_lanes()):
                _draw_lane_debug_info(
                    screen, road, lane_idx, lane, shifts, sim, debug_font
                )


def _compute_shifts(sim: Sim, junction: Junction) -> dict:
    """
    Produce a dictionary of how much to shift each direction's starting point
    based on total road widths. (Example logic borrowed from your original code.)
    """
    from sim.creator.create_sim import direction_to_index

    def get_len_lanes(road_id: int) -> int:
        return len(junction.get_road_by_id(road_id).get_lanes())

    return {
        "NORTH": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.NORTH, junction))),
        "SOUTH": 10,
        "WEST": 10,
        "EAST": -10 - get_road_total_width(get_len_lanes(direction_to_index(RoadEnum.EAST, junction))),
    }


def _draw_full_road(screen: pygame.Surface, road: Road, shifts: dict) -> None:
    """
    Draws a continuous asphalt rectangle + lane boundaries for each direction.
    """
    direction_str = RoadEnum(road.get_from_side()).name
    num_lanes = len(road.get_lanes())
    lane_len = road.get_lanes()[0].LENGTH if road.get_lanes() else 400

    # Big enough rect to cover intersection + approach
    road_width = get_road_total_width(num_lanes)
    total_length = 2 * lane_len
    shift = shifts.get(direction_str, 0)

    if direction_str in ["NORTH", "SOUTH"]:
        left = CX + shift
        top = 0
        width = road_width
        height = total_length
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        _draw_lane_boundaries_vertical(screen, left, top, width, height)
    else:  # EAST, WEST
        left = 0
        top = CY + shift
        width = SCREEN_WIDTH
        height = road_width
        pygame.draw.rect(screen, ASPHALT_COLOR, (left, top, width, height))
        _draw_lane_boundaries_horizontal(screen, left, top, width, height)


def _draw_lane_boundaries_vertical(
    screen: pygame.Surface,
    left: int,
    top: int,
    width: int,
    height: int
) -> None:
    x_left: int = left
    x_right: int = left + width
    y_bot: int = 0
    y_top: int = SCREEN_HEIGHT

    while x_left <= x_right:
        pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_left, y_bot), 2)
        x_left += LANE_WIDTH


def _draw_lane_boundaries_horizontal(
    screen: pygame.Surface,
    left: int,
    top: int,
    width: int,
    height: int
) -> None:
    y_top: int = top
    y_bot: int = top + height
    x_left: int = 0
    x_right: int = SCREEN_WIDTH

    while y_top <= y_bot:
        pygame.draw.line(screen, LANE_MARKING_COLOR, (x_left, y_top), (x_right, y_top), 2)
        y_top += LANE_WIDTH


def _draw_intersection(screen: pygame.Surface, sim: Sim, junction: Junction) -> None:
    """
    Draw the intersection rectangle on top of the roads.
    """
    from sim.creator.create_sim import direction_to_index

    # Start coords
    start_y = CY - _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction)) - 10
    start_x = CX - _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction)) - 10

    end_y = (
        _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction))
        + _get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, junction))
        + 2*10 + LANE_GAP / 4
    )
    end_x = (
        _get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, junction))
        + _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction))
        + 2*10 + LANE_GAP / 4
    )

    intersection_rect = pygame.Rect(start_y, start_x, end_y, end_x)
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)


def _get_road_width_from_id(sim: Sim, road_id: int) -> int:
    """
    Returns the total width (pixels) of a road by ID.
    """
    junction = sim.get_junctions()[0]
    road = junction.get_road_by_id(road_id)
    return get_road_total_width(len(road.get_lanes()))


def _compute_car_position(
    road: Road,
    lane_idx: int,
    lane: Lane,
    car: Car,
    shifts: dict,
    sim: Sim
) -> Tuple[float, float, float]:
    """
    Returns (x, y, angle) for a car, factoring in direction and shifts.
    """
    from sim.creator.create_sim import direction_to_index

    direction_int = road.get_from_side()
    direction_str = RoadEnum(direction_int).name
    dist = car.get_dist()
    num_lanes = len(road.get_lanes())

    # For each lane index, figure out the lane-center offset (reverse index so left lane is index 0 visually).
    lane_offsets = [
        LANE_WIDTH * (num_lanes - 1 - i) + (LANE_WIDTH // 2)
        for i in range(num_lanes)
    ]
    lane_center_offset = lane_offsets[lane_idx]
    shift = shifts.get(direction_str, 0)

    x = y = 0.0
    angle = 0.0

    if direction_str == "NORTH":
        angle = -90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY - _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, sim.get_junctions()[0])) - 10

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
        shift_y = CY + _get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, sim.get_junctions()[0])) + 10

        if dist >= 0:
            bottom_of_road = shift_y + lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            y = bottom_of_road - frac * lane.LENGTH
        else:
            y = shift_y - abs(dist)

    elif direction_str == "EAST":
        angle = 0
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX + _get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, sim.get_junctions()[0])) + 10

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
        shift_x = CX - _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, sim.get_junctions()[0])) - 10

        if dist >= 0:
            left_of_road = shift_x - lane.LENGTH
            frac = (lane.LENGTH - dist) / lane.LENGTH
            x = left_of_road + frac * lane.LENGTH
        else:
            x = shift_x + abs(dist)

    return x, y, angle


def _draw_lane_debug_info(
    screen: pygame.Surface,
    road: Road,
    lane_idx: int,
    lane: Lane,
    shifts: dict,
    sim: Sim,
    font: pygame.font.Font
) -> None:
    """
    Draws text (lane ID, car count) near the midpoint of each lane.
    """
    dist_mid = lane.LENGTH / 2.0
    x, y, _ = _compute_position_at_dist(road, lane_idx, dist_mid, shifts, sim)

    debug_text = f"{lane.get_id()} ({road.from_side.value})"
    text_surf = font.render(debug_text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(x, y))
    screen.blit(text_surf, text_rect)


def _compute_position_at_dist(
    road: Road,
    lane_idx: int,
    dist: float,
    shifts: dict,
    sim: Sim
) -> Tuple[float, float, float]:
    """
    Helper for positioning debug text in the lane center.
    """
    from sim.creator.create_sim import direction_to_index

    direction_str = RoadEnum(road.get_from_side()).name
    num_lanes = len(road.get_lanes())
    lane_offsets = [
        LANE_WIDTH * (num_lanes - 1 - i) + (LANE_WIDTH // 2)
        for i in range(num_lanes)
    ]
    lane_center_offset = lane_offsets[lane_idx]
    shift = shifts.get(direction_str, 0)
    length = road.get_lanes()[0].LENGTH if road.get_lanes() else 400

    x = y = angle = 0.0

    if direction_str == "NORTH":
        angle = -90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY - _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, sim.get_junctions()[0])) - 10
        y = (shift_y - length) + dist

    elif direction_str == "SOUTH":
        angle = 90
        left_boundary = CX + shift
        x = left_boundary + lane_center_offset
        shift_y = CY + _get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, sim.get_junctions()[0])) + 10
        y = shift_y + (length - dist)

    elif direction_str == "EAST":
        angle = 180
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX + _get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, sim.get_junctions()[0])) + 10
        x = shift_x + (length - dist)

    elif direction_str == "WEST":
        angle = 0
        top_boundary = CY + shift
        y = top_boundary + lane_center_offset
        shift_x = CX - _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, sim.get_junctions()[0])) - 10
        x = (shift_x - length) + dist

    return x, y, angle


def _draw_traffic_light(
    screen: pygame.Surface,
    sim: Sim,
    tl: TrafficLight,
    shifts: dict
) -> None:
    """
    Renders a traffic light near the intersection center.
    """
    from sim.creator.create_sim import direction_to_index

    is_green: bool = tl.get_state()
    color: Tuple[int, int, int] = (255, 255, 0) if tl.get_is_yellow() else (0, 255, 0) if is_green else (255, 0, 0)

    junction = sim.get_junctions()[0] if sim.get_junctions() else None
    if not junction or not tl.get_origins():
        return

    road_id = tl.get_origins()[0] // 10
    road = junction.get_road_by_id(road_id)
    direction_val = road.get_from_side()

    min_lane_in_road = min(l.get_id() for l in road.get_lanes())
    num_lanes_in_road = len(road.get_lanes())

    lane_offsets = [LANE_WIDTH * (num_lanes_in_road - 1 - i) for i in range(num_lanes_in_road)]
    direction_str = RoadEnum(direction_val).name

    lw: int = 12
    lh: int = 30

    turns: str = ""
    for dest in tl.get_destinations():
        for origin in tl.get_origins():
            cur_road: Road = junction.get_road_by_id(origin // 10)
            dest_road: Road = junction.get_road_by_id(dest // 10)

            turn_type = (dest_road.get_from_side().value - cur_road.get_from_side().value) % 4

            if origin in tl.get_destinations() and "straight" not in turns:
                turns += "straight"
            if turn_type == 1 and "right" not in turns:  # Turn right
                turns += "right"
            if turn_type == 3 and "left" not in turns:  # Turn left
                turns += "left"


    # Positioning logic similar to your original code
    if direction_val == RoadEnum.NORTH:
        y = CY - _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction)) - 4 * LANE_GAP
        for origin in tl.get_origins():
            offset_idx = origin - min_lane_in_road

            c_lane = CX + shifts.get(direction_str) + lane_offsets[offset_idx] + LANE_WIDTH / 2

            pygame.draw.circle(screen, color, (c_lane, y + 10), 15)

            image = load_tl_image(turn=turns, size=(30, 30))
            image = pygame.transform.rotate(image, 180)
            screen.blit(image, (c_lane - 15, y - 5))

    elif direction_val == RoadEnum.EAST:
        x = CX + _get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, junction)) + 1.25 * LANE_GAP
        for origin in tl.get_origins():
            offset_idx = origin - min_lane_in_road

            c_lane = CY + shifts.get(direction_str) + lane_offsets[offset_idx] + LANE_WIDTH / 2

            pygame.draw.circle(screen, color, (x + 15, c_lane), 15)

            image = load_tl_image(turn=turns, size=(30, 30))
            image = pygame.transform.rotate(image, 90)
            screen.blit(image, (x, c_lane - 15))

    elif direction_val == RoadEnum.SOUTH:
        start_x = CX + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        y = CY + _get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, junction)) + 1.25 * LANE_GAP
        for origin in tl.get_origins():
            offset_idx = origin - min_lane_in_road

            c_lane = CX + shifts.get(direction_str) + lane_offsets[offset_idx] + LANE_WIDTH / 2

            pygame.draw.circle(screen, color, (c_lane, y + 15), 15)

            image = load_tl_image(turn=turns, size=(30, 30))
            screen.blit(image, (c_lane - 15, y))

    elif direction_val == RoadEnum.WEST:
        start_y = CY + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        x = CX - _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction)) - 2.25 * LANE_GAP
        for origin in tl.get_origins():
            offset_idx = origin - min_lane_in_road

            c_lane = CY + shifts.get(direction_str) + lane_offsets[offset_idx] + LANE_WIDTH / 2

            pygame.draw.circle(screen, color, (x - 2, c_lane), 15)

            image = load_tl_image(turn=turns, size=(30, 30))
            image = pygame.transform.rotate(image, 270)
            screen.blit(image, (x - 17, c_lane - 15))


def _draw_traffic_light_id(
    screen: pygame.Surface,
    tl: TrafficLight,
    sim: Sim,
    shifts: dict,
    font: pygame.font.Font
) -> None:
    """
    Draws the traffic light ID near its position, for debugging.
    """
    from sim.creator.create_sim import direction_to_index

    junction = sim.get_junctions()[0] if sim.get_junctions() else None
    if not junction or not tl.get_origins():
        return

    lane_id = tl.get_origins()[0]
    road_id = lane_id // 10
    road = junction.get_road_by_id(road_id)
    direction_val = road.get_from_side()
    direction_str = RoadEnum(direction_val).name

    min_lane_in_road = min(l.get_id() for l in road.get_lanes())
    offset_idx = lane_id - min_lane_in_road

    label_text = f"TL ID: {tl.get_id()}"
    text_surf = font.render(label_text, True, (0, 0, 0))
    label_rect = text_surf.get_rect()

    lw: int = 12
    if direction_val == RoadEnum.NORTH:
        start_x = CX + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        y = CY - _get_road_width_from_id(sim, direction_to_index(RoadEnum.EAST, junction)) - 4 * LANE_GAP
        x = start_x + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x, y - 10)

    elif direction_val == RoadEnum.EAST:
        start_y = CY + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        x = CX + _get_road_width_from_id(sim, direction_to_index(RoadEnum.SOUTH, junction)) + 1.25 * LANE_GAP
        y = start_y + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x + 25, y)

    elif direction_val == RoadEnum.SOUTH:
        start_x = CX + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        y = CY + _get_road_width_from_id(sim, direction_to_index(RoadEnum.WEST, junction)) + 1.25 * LANE_GAP
        x = start_x + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x, y + 20)

    elif direction_val == RoadEnum.WEST:
        start_y = CY + shifts.get(direction_str) + (LANE_WIDTH - lw) / 2
        x = CX - _get_road_width_from_id(sim, direction_to_index(RoadEnum.NORTH, junction)) - 2.25 * LANE_GAP
        y = start_y + (LANE_WIDTH * (offset_idx))
        label_rect.center = (x - 25, y)

    screen.blit(text_surf, label_rect)
