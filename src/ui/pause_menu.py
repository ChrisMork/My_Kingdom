"""
In-game pause menu for My Kingdom.
Accessed by pressing ESC during gameplay.
"""

import pygame
from config.settings import *
from src.core.logger import logger


class PauseMenuButton:
    """A button for the pause menu."""

    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def draw(self, screen):
        """Draw the button with medieval styling."""
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON

        # Draw button with border
        pygame.draw.rect(screen, COLOR_ACCENT, self.rect.inflate(6, 6), border_radius=8)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Draw text
        text_surface = self.font.render(self.text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """Handle mouse events."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return True
        return False


class PauseMenu:
    """In-game pause menu."""

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.result = None  # 'resume', 'save', 'load', 'settings', 'main_menu'

        # Initialize fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.button_font = pygame.font.Font(None, FONT_BUTTON_SIZE)

        # Create buttons
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        start_y = WINDOW_HEIGHT // 2 - 150

        self.buttons = [
            PauseMenuButton(button_x, start_y, button_width, button_height, "Resume", self.button_font),
            PauseMenuButton(button_x, start_y + 80, button_width, button_height, "Save Game", self.button_font),
            PauseMenuButton(button_x, start_y + 160, button_width, button_height, "Settings", self.button_font),
            PauseMenuButton(button_x, start_y + 240, button_width, button_height, "Main Menu", self.button_font),
        ]

        logger.info("Pause menu initialized")

    def handle_events(self):
        """Handle pause menu events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received from pause menu")
                self.running = False
                self.result = "quit"
                return

            # ESC key resumes game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC pressed - resuming game")
                    self.running = False
                    self.result = "resume"
                    return

            # Check button clicks
            for i, button in enumerate(self.buttons):
                if button.handle_event(event):
                    if i == 0:  # Resume
                        logger.info("Resume button clicked")
                        self.running = False
                        self.result = "resume"
                    elif i == 1:  # Save Game
                        logger.info("Save Game button clicked")
                        self.running = False
                        self.result = "save"
                    elif i == 2:  # Settings
                        logger.info("Settings button clicked")
                        from src.ui.settings_menu import SettingsMenu
                        settings = SettingsMenu(self.screen)
                        settings.run()
                        # Resume pause menu after settings
                    elif i == 3:  # Main Menu
                        logger.info("Main Menu button clicked")
                        self.running = False
                        self.result = "main_menu"

    def draw(self):
        """Draw the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Title with shadow
        title_text = self.title_font.render("PAUSED", True, (40, 30, 20))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2 + 3, 103))
        self.screen.blit(title_text, title_rect)

        title_text = self.title_font.render("PAUSED", True, (255, 240, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        # Hint text
        hint_font = pygame.font.Font(None, 20)
        hint_text = hint_font.render("Press ESC to resume", True, (200, 190, 170))
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(hint_text, hint_rect)

    def run(self):
        """Run the pause menu loop."""
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        return self.result
