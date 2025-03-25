"""
assets.py

Handles asset loading such as images, fonts, etc.
"""

import pygame
from typing import Dict, Tuple, Optional

from sim.ui.config import SCREEN_WIDTH, SCREEN_HEIGHT


def load_background_image(path: str = "../assets/background.png") -> Optional[pygame.Surface]:
    """
    Loads and scales a background image. Returns None if loading fails.
    """
    try:
        bg_image = pygame.image.load(path).convert()
        return pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        return None


def load_tl_image(
        turn: str = "s",
        folder: str = "../assets/turns",
        size: Tuple[int, int] = (40, 40),
) -> pygame.Surface:
    """
    Loads and scales a background image. Returns None if loading fails.
    """
    path: str = f"{folder}/{turn}.png"
    tl_image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(tl_image, size)


def load_car_images(
        num_images: int = 8,
        folder: str = "../assets/",
        size: Tuple[int, int] = (40, 40),
) -> Dict[int, pygame.Surface]:
    """
    Loads car images from the specified folder.
    If an image is not found, creates a placeholder surface.
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
