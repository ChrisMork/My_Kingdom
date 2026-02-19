"""Script to create the settings menu file."""
from pathlib import Path

settings_menu_code = '''"""
Settings menu for My Kingdom with music controls.
"""

import pygame
from config.settings import *
from src.core.logger import logger
from src.audio.music_manager import get_music_manager


class Slider:
    """A draggable slider for volume control."""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.track_rect = pygame.Rect(x, y + height // 3, width, height // 3)
        self.handle_radius = height // 2
        self.handle_x = self._value_to_x(initial_val)

    def _value_to_x(self, value):
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(ratio * self.rect.width)

    def _x_to_value(self, x):
        ratio = (x - self.rect.x) / self.rect.width
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_pos = (self.handle_x, self.rect.centery)
            distance = ((event.pos[0] - handle_pos[0]) ** 2 + (event.pos[1] - handle_pos[1]) ** 2) ** 0.5
            if distance <= self.handle_radius + 5:
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_x = max(self.rect.x, min(self.rect.x + self.rect.width, event.pos[0]))
                self.value = self._x_to_value(self.handle_x)
                return True
        return False

    def draw(self, screen, font):
        label_surf = font.render(self.label, True, (255, 240, 200))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 30))
        pygame.draw.rect(screen, (80, 70, 60), self.track_rect, border_radius=5)
        filled_width = self.handle_x - self.rect.x
        filled_rect = pygame.Rect(self.rect.x, self.track_rect.y, filled_width, self.track_rect.height)
        pygame.draw.rect(screen, COLOR_ACCENT, filled_rect, border_radius=5)
        handle_color = (255, 220, 150) if self.dragging else (200, 180, 140)
        pygame.draw.circle(screen, handle_color, (self.handle_x, self.rect.centery), self.handle_radius)
        pygame.draw.circle(screen, COLOR_ACCENT, (self.handle_x, self.rect.centery), self.handle_radius, 2)
        value_text = f"{int(self.value * 100)}%"
        value_surf = font.render(value_text, True, (255, 255, 255))
        screen.blit(value_surf, (self.rect.x + self.rect.width + 20, self.rect.y + 5))


class Toggle:
    """A toggle switch for on/off settings."""

    def __init__(self, x, y, width, height, initial_state, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        self.label = label
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                self.state = not self.state
                return True
        return False

    def draw(self, screen, font):
        label_surf = font.render(self.label, True, (255, 240, 200))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 30))
        bg_color = COLOR_ACCENT if self.state else (80, 70, 60)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.rect.height // 2)
        switch_x = self.rect.x + self.rect.width - self.rect.height + 5 if self.state else self.rect.x + 5
        switch_color = (255, 255, 255) if self.state else (150, 140, 130)
        pygame.draw.circle(screen, switch_color, (switch_x + self.rect.height // 2 - 5, self.rect.centery), self.rect.height // 2 - 5)
        state_text = "ON" if self.state else "OFF"
        state_surf = font.render(state_text, True, (255, 255, 255))
        screen.blit(state_surf, (self.rect.x + self.rect.width + 20, self.rect.y + 5))


class SettingsMenu:
    """Settings menu for controlling game options."""

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.music_manager = get_music_manager()
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.label_font = pygame.font.Font(None, 28)
        self.button_font = pygame.font.Font(None, 32)
        center_x = WINDOW_WIDTH // 2
        self.music_toggle = Toggle(center_x - 100, 200, 80, 40, self.music_manager.music_enabled, "Music")
        self.volume_slider = Slider(center_x - 200, 300, 400, 40, 0.0, 1.0, self.music_manager.music_volume, "Music Volume")
        self.back_button_rect = pygame.Rect(center_x - 100, 450, 200, 60)
        self.back_button_hovered = False
        logger.info("Settings menu initialized")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if self.music_toggle.handle_event(event):
                self.music_manager.toggle_enabled()
            if self.volume_slider.handle_event(event):
                self.music_manager.set_volume(self.volume_slider.value)
            if event.type == pygame.MOUSEMOTION:
                self.back_button_hovered = self.back_button_rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_button_hovered and event.button == 1:
                    self.running = False

    def draw(self):
        self.screen.fill((30, 25, 20))
        title_text = self.title_font.render("Settings", True, (255, 240, 200))
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        self.music_toggle.draw(self.screen, self.label_font)
        self.volume_slider.draw(self.screen, self.label_font)
        button_color = (140, 110, 80) if self.back_button_hovered else (100, 80, 60)
        pygame.draw.rect(self.screen, COLOR_ACCENT, self.back_button_rect.inflate(6, 6), border_radius=8)
        pygame.draw.rect(self.screen, button_color, self.back_button_rect, border_radius=8)
        button_text = self.button_font.render("Back", True, (255, 240, 200))
        button_text_rect = button_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(button_text, button_text_rect)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        logger.info("Settings menu closed")
'''

# Write the settings menu file
Path('src/ui/settings_menu.py').write_text(settings_menu_code)
print('Settings menu created successfully!')
