"""
Main menu screen for My Kingdom.
Medieval-themed with a relaxing, positive vibe.
"""

import pygame
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *
from src.core.logger import logger
from src.audio.music_manager import get_music_manager


class Button:
    """A medieval-styled button for the menu."""

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


class MainMenu:
    """Main menu screen with medieval theme."""

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.next_state = None

        # Initialize fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, FONT_TITLE_SIZE)
        self.button_font = pygame.font.Font(None, FONT_BUTTON_SIZE)
        self.subtitle_font = pygame.font.Font(None, FONT_NORMAL_SIZE)

        # Load AI-generated complete menu scene
        assets_path = Path(__file__).parent.parent.parent / "assets" / "images" / "menu"
        try:
            # Try to load the AI-generated complete scene first
            complete_scene_path = assets_path / "complete_menu_scene.png"
            if complete_scene_path.exists():
                self.menu_background = pygame.image.load(str(complete_scene_path))
                # Scale to fit screen perfectly
                self.menu_background = pygame.transform.scale(self.menu_background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                logger.info("AI-generated menu background loaded successfully")
            else:
                # Fallback to old assets
                self.castle_bg = pygame.image.load(str(assets_path / "castle_background.png"))
                self.oak_tree = pygame.image.load(str(assets_path / "oak_tree.png"))
                self.knight = pygame.image.load(str(assets_path / "knight_resting.png"))
                self.campfire = pygame.image.load(str(assets_path / "campfire.png"))
                self.menu_background = None
                logger.info("Menu pixel art assets loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load menu assets: {e}")
            self.menu_background = None

        # Campfire animation (even though not used with AI background, needed for run loop)
        self.campfire_frame = 0
        self.campfire_timer = 0

        # Create buttons
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        start_y = WINDOW_HEIGHT // 2 - 40

        self.buttons = [
            Button(button_x, start_y, button_width, button_height, "New Game", self.button_font),
            Button(button_x, start_y + 80, button_width, button_height, "Load Game", self.button_font),
            Button(button_x, start_y + 160, button_width, button_height, "Settings", self.button_font),
            Button(button_x, start_y + 240, button_width, button_height, "Quit", self.button_font),
        ]

        # Initialize music manager and start menu music
        self.music_manager = get_music_manager()
        self.music_manager.play('menu')

        # Save selection state
        self.showing_save_input = False
        self.showing_load_menu = False
        self.save_name_input = ""
        self.available_saves = []
        self.selected_save_index = 0
        self.load_save_name = None

        logger.info("Main menu initialized")

    def handle_events(self):
        """Handle menu events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received from menu")
                self.running = False
                self.next_state = "quit"
                return

            # Handle save name input
            if self.showing_save_input:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.save_name_input.strip():
                            logger.info(f"Starting new game: {self.save_name_input}")
                            self.running = False
                            self.next_state = ("new_game", self.save_name_input)
                    elif event.key == pygame.K_ESCAPE:
                        self.showing_save_input = False
                        self.save_name_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.save_name_input = self.save_name_input[:-1]
                    elif event.unicode.isprintable() and len(self.save_name_input) < 30:
                        self.save_name_input += event.unicode
                return

            # Handle load menu
            if self.showing_load_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.showing_load_menu = False
                        self.selected_save_index = 0
                    elif event.key == pygame.K_UP:
                        self.selected_save_index = max(0, self.selected_save_index - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_save_index = min(len(self.available_saves) - 1, self.selected_save_index + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.available_saves:
                            save_name = self.available_saves[self.selected_save_index]['name']
                            logger.info(f"Loading game: {save_name}")
                            self.running = False
                            self.next_state = ("load_game", save_name)
                return

            # Check button clicks
            for i, button in enumerate(self.buttons):
                if button.handle_event(event):
                    if i == 0:  # New Game button
                        logger.info("New Game button clicked")
                        self.showing_save_input = True
                        self.save_name_input = ""
                    elif i == 1:  # Load Game button
                        logger.info("Load Game button clicked")
                        from src.systems.save_system import SaveSystem
                        save_system = SaveSystem()
                        self.available_saves = save_system.list_saves()
                        if self.available_saves:
                            self.showing_load_menu = True
                            self.selected_save_index = 0
                        else:
                            logger.info("No saves found")
                    elif i == 2:  # Settings button
                        logger.info("Settings button clicked")
                        from src.ui.settings_menu import SettingsMenu
                        settings = SettingsMenu(self.screen)
                        settings.run()
                        # Resume menu music after settings (in case it was toggled)
                        if self.music_manager.music_enabled and self.music_manager.current_track != 'menu':
                            self.music_manager.play('menu')
                    elif i == 3:  # Quit button
                        logger.info("Quit button clicked")
                        self.running = False
                        self.next_state = "quit"

    def draw(self):
        """Draw the main menu with AI-generated background."""
        # Draw AI-generated complete scene or fallback to layered assets
        if self.menu_background:
            # Use beautiful AI-generated background
            self.screen.blit(self.menu_background, (0, 0))
        else:
            # Fallback to old system
            if hasattr(self, 'castle_bg') and self.castle_bg:
                self.screen.blit(self.castle_bg, (0, 0))
            else:
                self.screen.fill(COLOR_BACKGROUND)

            if hasattr(self, 'oak_tree') and self.oak_tree:
                tree_width = self.oak_tree.get_width()
                tree_x = -(tree_width // 2)
                tree_y = 0
                self.screen.blit(self.oak_tree, (tree_x, tree_y))

            if hasattr(self, 'knight') and self.knight:
                knight_x = 180
                knight_y = WINDOW_HEIGHT - self.knight.get_height() + 15
                self.screen.blit(self.knight, (knight_x, knight_y))

            if hasattr(self, 'campfire') and self.campfire:
                flicker_offset = (self.campfire_frame % 2) * 2
                campfire_x = 440
                campfire_y = WINDOW_HEIGHT - self.campfire.get_height() + 20 - flicker_offset
                self.screen.blit(self.campfire, (campfire_x, campfire_y))

        # Subtle overlay for UI readability
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 20))
        self.screen.blit(overlay, (0, 0))

        # Title with shadow for better visibility
        title_text = self.title_font.render("My Kingdom", True, (40, 30, 20))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2 + 3, 103))
        self.screen.blit(title_text, title_rect)

        title_text = self.title_font.render("My Kingdom", True, (255, 240, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Subtitle with shadow
        subtitle_text = self.subtitle_font.render("Build Your Medieval Paradise", True, (20, 15, 10))
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2 + 2, 162))
        self.screen.blit(subtitle_text, subtitle_rect)

        subtitle_text = self.subtitle_font.render("Build Your Medieval Paradise", True, (240, 220, 190))
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Draw buttons with enhanced styling
        for button in self.buttons:
            button.draw(self.screen)

        # Footer text with shadow
        footer_font = pygame.font.Font(None, 20)
        footer_text = footer_font.render("A peaceful city-building experience", True, (20, 15, 10))
        footer_rect = footer_text.get_rect(center=(WINDOW_WIDTH // 2 + 1, WINDOW_HEIGHT - 49))
        self.screen.blit(footer_text, footer_rect)

        footer_text = footer_font.render("A peaceful city-building experience", True, (230, 220, 200))
        footer_rect = footer_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(footer_text, footer_rect)

        # Draw save name input dialog
        if self.showing_save_input:
            self._draw_save_input_dialog()

        # Draw load menu
        if self.showing_load_menu:
            self._draw_load_menu()

    def _draw_save_input_dialog(self):
        """Draw the save name input dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width = 500
        dialog_height = 200
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2

        # Draw dialog background
        pygame.draw.rect(self.screen, COLOR_ACCENT,
                        (dialog_x - 4, dialog_y - 4, dialog_width + 8, dialog_height + 8),
                        border_radius=12)
        pygame.draw.rect(self.screen, (60, 50, 40),
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        border_radius=10)

        # Title
        title_text = self.button_font.render("Enter Save Name", True, (255, 240, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, dialog_y + 40))
        self.screen.blit(title_text, title_rect)

        # Input box
        input_box_width = 400
        input_box_height = 50
        input_box_x = (WINDOW_WIDTH - input_box_width) // 2
        input_box_y = dialog_y + 80

        pygame.draw.rect(self.screen, (40, 35, 30),
                        (input_box_x, input_box_y, input_box_width, input_box_height),
                        border_radius=5)
        pygame.draw.rect(self.screen, COLOR_ACCENT,
                        (input_box_x, input_box_y, input_box_width, input_box_height),
                        2, border_radius=5)

        # Input text
        input_text = self.subtitle_font.render(self.save_name_input + "_", True, (255, 255, 255))
        input_rect = input_text.get_rect(midleft=(input_box_x + 15, input_box_y + input_box_height // 2))
        self.screen.blit(input_text, input_rect)

        # Instructions
        instruction_font = pygame.font.Font(None, 20)
        instruction_text = instruction_font.render("Press ENTER to start | ESC to cancel", True, (200, 190, 170))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, dialog_y + dialog_height - 30))
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_load_menu(self):
        """Draw the load game menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width = 600
        dialog_height = 400
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2

        # Draw dialog background
        pygame.draw.rect(self.screen, COLOR_ACCENT,
                        (dialog_x - 4, dialog_y - 4, dialog_width + 8, dialog_height + 8),
                        border_radius=12)
        pygame.draw.rect(self.screen, (60, 50, 40),
                        (dialog_x, dialog_y, dialog_width, dialog_height),
                        border_radius=10)

        # Title
        title_text = self.button_font.render("Load Game", True, (255, 240, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, dialog_y + 30))
        self.screen.blit(title_text, title_rect)

        # List saves
        list_font = pygame.font.Font(None, 28)
        start_y = dialog_y + 70
        for i, save in enumerate(self.available_saves[:8]):  # Show max 8 saves
            y = start_y + i * 40

            # Highlight selected
            if i == self.selected_save_index:
                highlight_rect = pygame.Rect(dialog_x + 20, y - 5, dialog_width - 40, 35)
                pygame.draw.rect(self.screen, COLOR_ACCENT, highlight_rect, border_radius=5)

            # Save name
            save_text = list_font.render(save['name'], True, (255, 255, 255) if i == self.selected_save_index else (200, 190, 170))
            self.screen.blit(save_text, (dialog_x + 30, y))

            # Timestamp
            timestamp_font = pygame.font.Font(None, 18)
            timestamp_text = timestamp_font.render(save['timestamp'][:19].replace('T', ' '), True, (150, 140, 120))
            self.screen.blit(timestamp_text, (dialog_x + 30, y + 20))

        # Instructions
        instruction_font = pygame.font.Font(None, 20)
        instruction_text = instruction_font.render("Use UP/DOWN arrows | ENTER to load | ESC to cancel", True, (200, 190, 170))
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, dialog_y + dialog_height - 30))
        self.screen.blit(instruction_text, instruction_rect)

    def run(self):
        """Run the main menu loop."""
        clock = pygame.time.Clock()

        while self.running:
            # Update campfire animation
            self.campfire_timer += 1
            if self.campfire_timer >= 15:  # Change frame every 15 ticks
                self.campfire_frame += 1
                self.campfire_timer = 0

            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        return self.next_state
