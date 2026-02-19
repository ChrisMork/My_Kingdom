"""
My Kingdom - A peaceful medieval city-building game
Main entry point

Double-click this file to start the game!
"""

import pygame
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import *
from src.core.logger import logger
from src.ui.menu import MainMenu
from src.core.game import Game


class MyKingdom:
    """Main game application."""

    def __init__(self):
        logger.info("=" * 60)
        logger.info("MY KINGDOM - Starting Application")
        logger.info("=" * 60)

        # Initialize Pygame
        pygame.init()
        logger.info("Pygame initialized")

        # Create window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        logger.info(f"Window created: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Set icon (using a simple colored surface for now)
        icon = pygame.Surface((32, 32))
        icon.fill(COLOR_ACCENT)
        pygame.display.set_icon(icon)

        self.current_state = STATE_MENU
        self.running = True

        logger.info("Application initialization complete")

    def run(self):
        """Main application loop."""
        logger.info("Starting main application loop")

        while self.running:
            if self.current_state == STATE_MENU:
                logger.info("Entering MENU state")
                menu = MainMenu(self.screen)
                next_state = menu.run()

                if next_state == "quit":
                    self.running = False
                elif isinstance(next_state, tuple):
                    # Handle new game or load game
                    action, save_name = next_state
                    if action == "new_game":
                        logger.info(f"Starting new game: {save_name}")
                        self.current_state = STATE_PLAYING
                        self.game_save_name = save_name
                        self.game_action = "new"
                    elif action == "load_game":
                        logger.info(f"Loading game: {save_name}")
                        self.current_state = STATE_PLAYING
                        self.game_save_name = save_name
                        self.game_action = "load"
                elif next_state == STATE_PLAYING:
                    # Legacy support
                    self.current_state = STATE_PLAYING
                    self.game_save_name = None
                    self.game_action = "new"

            elif self.current_state == STATE_PLAYING:
                logger.info("Entering PLAYING state")
                game = Game(self.screen, getattr(self, 'game_save_name', None), getattr(self, 'game_action', 'new'))
                next_state = game.run()

                if next_state == "quit":
                    self.running = False
                elif next_state == STATE_MENU:
                    self.current_state = STATE_MENU

        self.quit()

    def quit(self):
        """Clean up and exit."""
        logger.info("=" * 60)
        logger.info("MY KINGDOM - Shutting Down")
        logger.info("=" * 60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    try:
        app = MyKingdom()
        app.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)
