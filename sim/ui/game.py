# sim/ui/game.py

import pygame
import sys
from sim.simulation import StaticIntersectionSimulation

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Color definitions
BACKGROUND_COLOR = (120, 180, 120)  # Grass/landscape
ASPHALT_COLOR = (50, 50, 50)  # Road surface
INTERSECTION_COLOR = (60, 60, 60)  # Intersection pavement
LANE_MARKING_COLOR = (255, 255, 255)  # Dashed lane markings
SIDEWALK_COLOR = (170, 170, 170)  # Sidewalk


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Static Intersection Simulation")

    # Define a fixed small size for car images
    car_size = (40, 40)
    car_images = {}
    for i in range(1, 8):
        img = pygame.image.load(f"../../sim/assets/car{i}.png").convert_alpha()
        car_images[i] = pygame.transform.scale(img, car_size)

    simulation = StaticIntersectionSimulation()

    # Load and scale the background image
    background_img = pygame.image.load("../../sim/assets/background.png").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    screen.blit(background_img, (0, 0))

    draw_intersection(screen, simulation, car_images)
    pygame.display.flip()

    # Wait until the user closes the window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

    pygame.quit()
    sys.exit()


def draw_intersection(screen, simulation, car_images):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    intersection_size = 150  # Size of the central junction area
    road_width = 4 * simulation.lane_width  # 4 lanes per road

    # Draw a sidewalk around the intersection for realism
    sidewalk_margin = 20
    sidewalk_rect = pygame.Rect(center_x - intersection_size // 2 - sidewalk_margin,
                                center_y - intersection_size // 2 - sidewalk_margin,
                                intersection_size + 2 * sidewalk_margin,
                                intersection_size + 2 * sidewalk_margin)
    pygame.draw.rect(screen, SIDEWALK_COLOR, sidewalk_rect)

    # Draw the intersection (junction) area
    intersection_rect = pygame.Rect(center_x - intersection_size // 2,
                                    center_y - intersection_size // 2,
                                    intersection_size,
                                    intersection_size)
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)

    # Define incoming road arms (only the approaches, not exiting)
    north_rect = pygame.Rect(center_x - road_width // 2,
                             0,
                             road_width,
                             center_y - intersection_size // 2)
    south_rect = pygame.Rect(center_x - road_width // 2,
                             center_y + intersection_size // 2,
                             road_width,
                             SCREEN_HEIGHT - (center_y + intersection_size // 2))
    east_rect = pygame.Rect(center_x + intersection_size // 2,
                            center_y - road_width // 2,
                            SCREEN_WIDTH - (center_x + intersection_size // 2),
                            road_width)
    west_rect = pygame.Rect(0,
                            center_y - road_width // 2,
                            center_x - intersection_size // 2,
                            road_width)

    pygame.draw.rect(screen, ASPHALT_COLOR, north_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, south_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, east_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, west_rect)

    # Draw dashed lane markings between lanes.
    # For horizontal roads (north and south), draw vertical dashed lines at lane boundaries.
    for i in range(1, 4):
        x = north_rect.x + i * simulation.lane_width
        draw_dashed_line(screen, LANE_MARKING_COLOR, (x, north_rect.top), (x, north_rect.bottom), dash_length=10,
                         gap_length=5)
        x = south_rect.x + i * simulation.lane_width
        draw_dashed_line(screen, LANE_MARKING_COLOR, (x, south_rect.top), (x, south_rect.bottom), dash_length=10,
                         gap_length=5)
    # For vertical roads (east and west), draw horizontal dashed lines at lane boundaries.
    for i in range(1, 4):
        y = east_rect.y + i * simulation.lane_width
        draw_dashed_line(screen, LANE_MARKING_COLOR, (east_rect.left, y), (east_rect.right, y), dash_length=10,
                         gap_length=5)
        y = west_rect.y + i * simulation.lane_width
        draw_dashed_line(screen, LANE_MARKING_COLOR, (west_rect.left, y), (west_rect.right, y), dash_length=10,
                         gap_length=5)

    # Draw traffic lights near the junction for each approach
    for tl in simulation.get_traffic_lights():
        draw_traffic_light(screen, center_x, center_y, intersection_size, road_width, simulation.lane_width, tl)

    # Draw cars for each road (using the car's distance from the junction)
    for road in simulation.get_roads():
        direction = road.direction  # 'north', 'south', 'east', or 'west'
        lanes = road.get_lanes()
        for lane_index, lane in enumerate(lanes):
            for car in lane.get_cars():
                img = car_images[car.img_index]

                if direction == 'north':
                    rotation_angle = -90  # Cars entering from north point downward
                    x = north_rect.x + simulation.lane_width / 2 + lane_index * simulation.lane_width
                    y = north_rect.bottom - car.get_dist()[0]
                elif direction == 'south':
                    rotation_angle = 90  # Cars entering from south point upward
                    x = south_rect.x + simulation.lane_width / 2 + lane_index * simulation.lane_width
                    y = south_rect.y + car.get_dist()[0]
                elif direction == 'east':
                    rotation_angle = 0  # Cars entering from east point westward (rotate 0°)
                    x = east_rect.x + car.get_dist()[0]
                    y = east_rect.y + simulation.lane_width / 2 + lane_index * simulation.lane_width
                elif direction == 'west':
                    rotation_angle = 180  # Cars entering from west point eastward
                    x = west_rect.right - car.get_dist()[0]
                    y = west_rect.y + simulation.lane_width / 2 + lane_index * simulation.lane_width
                rotated_img = pygame.transform.rotate(img, rotation_angle)
                rect = rotated_img.get_rect(center=(int(x), int(y)))
                screen.blit(rotated_img, rect)


def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10, gap_length=5):
    x1, y1 = start_pos
    x2, y2 = end_pos
    from math import hypot
    distance = hypot(x2 - x1, y2 - y1)
    dash_count = int(distance // (dash_length + gap_length))
    for i in range(dash_count + 1):
        start_x = x1 + (x2 - x1) * (i * (dash_length + gap_length)) / distance
        start_y = y1 + (y2 - y1) * (i * (dash_length + gap_length)) / distance
        end_x = x1 + (x2 - x1) * (i * (dash_length + gap_length) + dash_length) / distance
        end_y = y1 + (y2 - y1) * (i * (dash_length + gap_length) + dash_length) / distance
        pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 2)


def draw_traffic_light(screen, center_x, center_y, intersection_size, road_width, lane_width, tl):
    """
    Draw a traffic light near the junction for a given approach.
    For realism, we place:
      - North: on the left side of the north approach.
      - South: on the right side of the south approach.
      - East: on the top side of the east approach.
      - West: on the bottom side of the west approach.
    """
    light_width, light_height = 10, 30  # Traffic light housing dimensions
    light_circle_radius = 5
    offset = 5  # offset from the junction edge

    if tl.direction == 'north':
        x = center_x - road_width / 2 + lane_width
        y = center_y - intersection_size / 2 - light_height - offset
    elif tl.direction == 'south':
        x = center_x + road_width / 2 - lane_width - light_width
        y = center_y + intersection_size / 2 + offset
    elif tl.direction == 'east':
        x = center_x + intersection_size / 2 + offset
        y = center_y - road_width / 2 + lane_width
    elif tl.direction == 'west':
        x = center_x - intersection_size / 2 - light_height - offset
        y = center_y + road_width / 2 - lane_width - light_width
    # For north and south, the housing is vertical; for east and west, horizontal.
    if tl.direction in ['north', 'south']:
        housing = pygame.Rect(x, y, light_width, light_height)
    else:
        housing = pygame.Rect(x, y, light_height, light_width)

    pygame.draw.rect(screen, (20, 20, 20), housing)  # Draw housing
    light_color = (0, 255, 0) if tl.state else (255, 0, 0)
    circle_center = housing.center
    pygame.draw.circle(screen, light_color, circle_center, light_circle_radius)


if __name__ == "__main__":
    main()
