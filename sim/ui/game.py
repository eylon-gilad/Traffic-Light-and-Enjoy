import pygame
import sys
from sim.simulation import StaticIntersectionSimulation

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Color definitions
BACKGROUND_COLOR = (120, 180, 120)  # Grass/landscape
ASPHALT_COLOR = (50, 50, 50)         # Road surface
INTERSECTION_COLOR = (60, 60, 60)    # Intersection pavement
LANE_MARKING_COLOR = (255, 255, 255)  # Dashed lane markings
SIDEWALK_COLOR = (170, 170, 170)      # Sidewalk

# Set to True to display road and lane IDs on the screen for debugging.
DEBUG_IDS = True


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Static Intersection Simulation")
    clock = pygame.time.Clock()

    # Load car images and scale them.
    car_size = (40, 40)
    car_images = {}
    for i in range(1, 8):
        img = pygame.image.load(f"../../sim/assets/car{i}.png").convert_alpha()
        car_images[i] = pygame.transform.scale(img, car_size)

    simulation = StaticIntersectionSimulation()

    # Load and scale the background image.
    background_img = pygame.image.load("../../sim/assets/background.png").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background_img, (0, 0))
        draw_intersection(screen, simulation, car_images)
        if DEBUG_IDS:
            draw_ids_debug(screen, simulation)
        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()
    sys.exit()


def draw_intersection(screen, simulation, car_images):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    intersection_size = 150  # Size of the central junction area
    road_width = 4 * simulation.lane_width  # 4 lanes per road

    # Draw a sidewalk around the intersection.
    sidewalk_margin = 20
    sidewalk_rect = pygame.Rect(
        center_x - intersection_size // 2 - sidewalk_margin,
        center_y - intersection_size // 2 - sidewalk_margin,
        intersection_size + 2 * sidewalk_margin,
        intersection_size + 2 * sidewalk_margin,
    )
    pygame.draw.rect(screen, SIDEWALK_COLOR, sidewalk_rect)

    # Draw the intersection area.
    intersection_rect = pygame.Rect(
        center_x - intersection_size // 2,
        center_y - intersection_size // 2,
        intersection_size,
        intersection_size,
    )
    pygame.draw.rect(screen, INTERSECTION_COLOR, intersection_rect)

    # Pre-calculate road rectangles for the four roads based on entry_angle.
    # (These match our original layout: -90 = top, 90 = bottom, 0 = right, 180 = left.)
    north_rect = pygame.Rect(
        center_x - road_width // 2, 0, road_width, center_y - intersection_size // 2
    )
    south_rect = pygame.Rect(
        center_x - road_width // 2,
        center_y + intersection_size // 2,
        road_width,
        SCREEN_HEIGHT - (center_y + intersection_size // 2),
    )
    east_rect = pygame.Rect(
        center_x + intersection_size // 2,
        center_y - road_width // 2,
        SCREEN_WIDTH - (center_x + intersection_size // 2),
        road_width,
    )
    west_rect = pygame.Rect(
        0, center_y - road_width // 2, center_x - intersection_size // 2, road_width
    )

    # Draw the road surfaces.
    pygame.draw.rect(screen, ASPHALT_COLOR, north_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, south_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, east_rect)
    pygame.draw.rect(screen, ASPHALT_COLOR, west_rect)

    # Draw dashed lane markings (vertical for north/south, horizontal for east/west).
    for i in range(1, 4):
        x = north_rect.x + i * simulation.lane_width
        draw_dashed_line(
            screen,
            LANE_MARKING_COLOR,
            (x, north_rect.top),
            (x, north_rect.bottom),
            dash_length=10,
            gap_length=5,
        )
        x = south_rect.x + i * simulation.lane_width
        draw_dashed_line(
            screen,
            LANE_MARKING_COLOR,
            (x, south_rect.top),
            (x, south_rect.bottom),
            dash_length=10,
            gap_length=5,
        )
    for i in range(1, 4):
        y = east_rect.y + i * simulation.lane_width
        draw_dashed_line(
            screen,
            LANE_MARKING_COLOR,
            (east_rect.left, y),
            (east_rect.right, y),
            dash_length=10,
            gap_length=5,
        )
        y = west_rect.y + i * simulation.lane_width
        draw_dashed_line(
            screen,
            LANE_MARKING_COLOR,
            (west_rect.left, y),
            (west_rect.right, y),
            dash_length=10,
            gap_length=5,
        )

    # Draw traffic lights based on each traffic light’s entry_angle.
    for tl in simulation.get_traffic_lights():
        draw_traffic_light(
            screen,
            center_x,
            center_y,
            intersection_size,
            road_width,
            simulation.lane_width,
            tl,
        )

    # Draw the cars for each road.
    for road in simulation.get_roads():
        # Map the road's entry_angle to the corresponding rectangle and rotation.
        if road.entry_angle == -90:
            road_rect = north_rect
            rotation_angle = -90
        elif road.entry_angle == 90:
            road_rect = south_rect
            rotation_angle = 90
        elif road.entry_angle == 0:
            road_rect = east_rect
            rotation_angle = 0
        elif road.entry_angle == 180:
            road_rect = west_rect
            rotation_angle = 180
        else:
            continue

        lanes = road.get_lanes()
        for lane_index, lane in enumerate(lanes):
            for car in lane.get_cars():
                img = car_images[car.img_index]

                if road.entry_angle == -90:
                    x = road_rect.x + simulation.lane_width / 2 + lane_index * simulation.lane_width
                    y = road_rect.bottom - car.get_dist()
                elif road.entry_angle == 90:
                    x = road_rect.x + simulation.lane_width / 2 + lane_index * simulation.lane_width
                    y = road_rect.y + car.get_dist()
                elif road.entry_angle == 0:
                    x = road_rect.x + car.get_dist()
                    y = road_rect.y + simulation.lane_width / 2 + lane_index * simulation.lane_width
                elif road.entry_angle == 180:
                    x = road_rect.right - car.get_dist()
                    y = road_rect.y + simulation.lane_width / 2 + lane_index * simulation.lane_width

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
    Draws a traffic light near the junction based on the traffic light’s entry_angle.
    The positioning logic is similar to before but now uses tl.entry_angle.
    """
    light_width, light_height = 10, 30  # Housing dimensions
    light_circle_radius = 5
    offset = 5

    if tl.entry_angle == -90:
        x = center_x - road_width / 2 + lane_width
        y = center_y - intersection_size / 2 - light_height - offset
    elif tl.entry_angle == 90:
        x = center_x + road_width / 2 - lane_width - light_width
        y = center_y + intersection_size / 2 + offset
    elif tl.entry_angle == 0:
        x = center_x + intersection_size / 2 + offset
        y = center_y - road_width / 2 + lane_width
    elif tl.entry_angle == 180:
        x = center_x - intersection_size / 2 - light_height - offset
        y = center_y + road_width / 2 - lane_width - light_width
    else:
        x, y = center_x, center_y

    # For vertical roads (entry_angle -90 or 90) the housing is drawn vertically.
    if tl.entry_angle in (-90, 90):
        housing = pygame.Rect(x, y, light_width, light_height)
    else:
        housing = pygame.Rect(x, y, light_height, light_width)

    pygame.draw.rect(screen, (20, 20, 20), housing)  # Draw housing
    light_color = (0, 255, 0) if tl.state else (255, 0, 0)
    circle_center = housing.center
    pygame.draw.circle(screen, light_color, circle_center, light_circle_radius)


def draw_ids_debug(screen, simulation):
    """
    (Optional) Draws the road and lane IDs on the screen for debugging.
    Roads have IDs of the form 11RR and lanes have IDs of the form 11RRLL.
    """
    font = pygame.font.SysFont("Arial", 12)
    for road in simulation.get_roads():
        # Position debug text based on the road's entry_angle.
        if road.entry_angle == -90:
            pos = (SCREEN_WIDTH // 2, 30)
        elif road.entry_angle == 90:
            pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        elif road.entry_angle == 0:
            pos = (SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2)
        elif road.entry_angle == 180:
            pos = (50, SCREEN_HEIGHT // 2)
        else:
            pos = (center_x, center_y)
        road_text = font.render(f"Road ID: {road.id}", True, (255, 255, 0))
        screen.blit(road_text, road_text.get_rect(center=pos))

        # For each lane, display the lane ID along the lane center.
        lanes = road.get_lanes()
        for idx, lane in enumerate(lanes):
            if road.entry_angle in (-90, 90):
                lane_x = (
                    SCREEN_WIDTH // 2 - (2 * simulation.lane_width)
                    + simulation.lane_width / 2
                    + idx * simulation.lane_width
                )
                lane_y = pos[1] + 20 if road.entry_angle == -90 else pos[1] - 20
                lane_pos = (lane_x, lane_y)
            else:
                lane_y = (
                    SCREEN_HEIGHT // 2 - (2 * simulation.lane_width)
                    + simulation.lane_width / 2
                    + idx * simulation.lane_width
                )
                lane_x = pos[0] - 20 if road.entry_angle == 180 else pos[0] + 20
                lane_pos = (lane_x, lane_y)
            lane_text = font.render(f"{lane.id}", True, (0, 255, 255))
            screen.blit(lane_text, lane_text.get_rect(center=lane_pos))


if __name__ == "__main__":
    main()
