"""
events.py

Contains functions for handling user input and returning relevant flags
(e.g., toggling debug mode, quit signals).
"""

import pygame


def handle_events(show_debug: bool) -> (bool, bool):
    """
    Processes Pygame events and returns:
      (running, new_show_debug)
    - running: False if user wants to quit
    - new_show_debug: possibly toggled debug mode
    """
    running = True
    new_show_debug = show_debug

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_d:
                new_show_debug = not new_show_debug

    return running, new_show_debug
