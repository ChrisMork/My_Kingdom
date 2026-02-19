"""
Generate a preview image of the main menu.
This renders the menu exactly as it appears in-game and saves it as a PNG.
"""

import pygame
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *
from src.ui.menu import MainMenu


def generate_menu_preview():
    """Render the menu and save it as a preview image."""
    print("Generating main menu preview...")

    # Initialize pygame
    pygame.init()

    # Create a surface (offscreen rendering)
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Create menu instance
    menu = MainMenu(screen)

    # Render the menu once
    menu.draw()

    # Save the preview
    preview_path = Path(__file__).parent.parent.parent / "menu_preview.png"
    pygame.image.save(screen, str(preview_path))

    print(f"\nSUCCESS! Menu preview saved to: {preview_path}")
    print("  You can now view this image to see your main menu!")

    pygame.quit()


if __name__ == "__main__":
    generate_menu_preview()
