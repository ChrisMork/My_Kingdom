"""
Settings manager for My Kingdom.
Handles loading, saving, and managing game settings.
"""

import json
import pygame
from pathlib import Path
from src.core.logger import logger


class SettingsManager:
    """Manages all game settings with save/load functionality."""

    DEFAULT_SETTINGS = {
        # Graphics
        "graphics": {
            "resolution": [1280, 720],
            "fullscreen": False,
            "vsync": True,
            "show_fps": False,
            "particle_effects": True,
            "screen_shake": True,
            "shadow_quality": "medium",  # low, medium, high
            "texture_quality": "high",    # low, medium, high
        },

        # Audio
        "audio": {
            "master_volume": 100,
            "music_volume": 80,
            "sfx_volume": 90,
            "ambient_volume": 70,
            "ui_sounds": True,
            "mute_when_unfocused": True,
        },

        # Gameplay
        "gameplay": {
            "autosave": True,
            "autosave_interval": 5,  # minutes
            "difficulty": "normal",   # easy, normal, hard
            "tutorial_enabled": True,
            "pause_on_menu": True,
            "edge_scrolling": True,
            "scroll_speed": 5,        # 1-10
            "zoom_speed": 3,          # 1-10
            "show_hints": True,
            "show_tooltips": True,
            "tooltip_delay": 0.5,     # seconds
        },

        # Controls
        "controls": {
            "mouse_sensitivity": 5,   # 1-10
            "invert_camera_y": False,
            "keybindings": {
                "move_up": pygame.K_w,
                "move_down": pygame.K_s,
                "move_left": pygame.K_a,
                "move_right": pygame.K_d,
                "zoom_in": pygame.K_EQUALS,
                "zoom_out": pygame.K_MINUS,
                "pause": pygame.K_ESCAPE,
                "quicksave": pygame.K_F5,
                "quickload": pygame.K_F9,
                "screenshot": pygame.K_F12,
                "toggle_ui": pygame.K_TAB,
                "toggle_grid": pygame.K_g,
            }
        },

        # Accessibility
        "accessibility": {
            "colorblind_mode": "none",  # none, deuteranopia, protanopia, tritanopia
            "high_contrast": False,
            "large_text": False,
            "screen_reader": False,
            "reduce_motion": False,
        },

        # UI
        "ui": {
            "ui_scale": 1.0,          # 0.75, 1.0, 1.25, 1.5
            "show_minimap": True,
            "minimap_size": "medium",  # small, medium, large
            "clock_format": "24h",     # 12h, 24h
            "date_format": "mdy",      # mdy, dmy, ymd
            "temperature_unit": "C",   # C, F
        }
    }

    def __init__(self):
        """Initialize settings manager."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings_file = Path("settings.json")
        self.load_settings()

    def load_settings(self):
        """Load settings from file or create default."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    self._merge_settings(loaded_settings)
                logger.info("Settings loaded successfully")
            else:
                logger.info("No settings file found, using defaults")
                self.save_settings()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()

    def _merge_settings(self, loaded_settings):
        """Merge loaded settings with defaults to handle new settings."""
        for category, settings in self.DEFAULT_SETTINGS.items():
            if category in loaded_settings:
                if isinstance(settings, dict):
                    for key, default_value in settings.items():
                        if key in loaded_settings[category]:
                            self.settings[category][key] = loaded_settings[category][key]
                        else:
                            self.settings[category][key] = default_value
            else:
                self.settings[category] = settings

    def save_settings(self):
        """Save current settings to file."""
        try:
            # Convert pygame key constants to integers for JSON
            settings_to_save = self._prepare_for_json(self.settings)

            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            logger.info("Settings saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def _prepare_for_json(self, data):
        """Convert pygame constants to JSON-serializable format."""
        if isinstance(data, dict):
            return {k: self._prepare_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._prepare_for_json(item) for item in data]
        elif isinstance(data, int) and data > 1000:  # Likely a pygame constant
            return data
        return data

    def get(self, category, key):
        """Get a specific setting value."""
        return self.settings.get(category, {}).get(key)

    def set(self, category, key, value):
        """Set a specific setting value."""
        if category in self.settings:
            self.settings[category][key] = value
            return True
        return False

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        logger.info("Settings reset to defaults")

    def reset_category(self, category):
        """Reset a specific category to defaults."""
        if category in self.DEFAULT_SETTINGS:
            self.settings[category] = self.DEFAULT_SETTINGS[category].copy()
            logger.info(f"{category} settings reset to defaults")

    def apply_graphics_settings(self, screen):
        """Apply graphics settings to the game window."""
        try:
            resolution = self.get("graphics", "resolution")
            fullscreen = self.get("graphics", "fullscreen")
            vsync = self.get("graphics", "vsync")

            flags = pygame.SCALED
            if fullscreen:
                flags |= pygame.FULLSCREEN
            if vsync:
                flags |= pygame.DOUBLEBUF

            # Note: Resolution changes require restarting the game
            logger.info(f"Graphics settings applied: {resolution}, fullscreen={fullscreen}, vsync={vsync}")
        except Exception as e:
            logger.error(f"Failed to apply graphics settings: {e}")

    def apply_audio_settings(self):
        """Apply audio settings (placeholder - will be implemented with audio system)."""
        master = self.get("audio", "master_volume") / 100.0
        music = self.get("audio", "music_volume") / 100.0
        sfx = self.get("audio", "sfx_volume") / 100.0

        # When pygame.mixer is implemented:
        # pygame.mixer.music.set_volume(master * music)

        logger.info(f"Audio settings: master={master}, music={music}, sfx={sfx}")

    def get_resolution_options(self):
        """Get available resolution options."""
        return [
            [1280, 720],   # 720p
            [1600, 900],   # 900p
            [1920, 1080],  # 1080p
            [2560, 1440],  # 1440p
            [3840, 2160],  # 4K
        ]

    def get_keybinding_name(self, key_code):
        """Get human-readable name for a key code."""
        if key_code < 256:
            return chr(key_code).upper()

        key_names = {
            pygame.K_ESCAPE: "ESC",
            pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3",
            pygame.K_F4: "F4", pygame.K_F5: "F5", pygame.K_F6: "F6",
            pygame.K_F7: "F7", pygame.K_F8: "F8", pygame.K_F9: "F9",
            pygame.K_F10: "F10", pygame.K_F11: "F11", pygame.K_F12: "F12",
            pygame.K_TAB: "TAB", pygame.K_SPACE: "SPACE",
            pygame.K_RETURN: "ENTER", pygame.K_BACKSPACE: "BACKSPACE",
            pygame.K_LSHIFT: "L-SHIFT", pygame.K_RSHIFT: "R-SHIFT",
            pygame.K_LCTRL: "L-CTRL", pygame.K_RCTRL: "R-CTRL",
            pygame.K_LALT: "L-ALT", pygame.K_RALT: "R-ALT",
            pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
            pygame.K_EQUALS: "+", pygame.K_MINUS: "-",
        }

        return key_names.get(key_code, f"KEY_{key_code}")


# Global settings instance
settings_manager = SettingsManager()
