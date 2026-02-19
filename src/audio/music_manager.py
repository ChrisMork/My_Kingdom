"""
Music manager for My Kingdom.
Handles background music playback with volume control and looping.
"""

import pygame
import json
from pathlib import Path
from src.core.logger import logger


class MusicManager:
    """Manage background music with volume control."""

    def __init__(self):
        pygame.mixer.init()

        self.music_dir = Path(__file__).parent.parent.parent / "assets" / "audio" / "music"
        self.settings_file = Path(__file__).parent.parent.parent / "settings.json"

        # Music tracks
        self.tracks = {
            'menu': self.music_dir / "menu_theme.wav",
            'gameplay': self.music_dir / "gameplay_theme.wav"
        }

        # Current state
        self.current_track = None
        self.is_playing = False

        # Load settings
        self.load_settings()

        logger.info("Music manager initialized")

    def load_settings(self):
        """Load music settings from file."""
        default_settings = {
            'music_enabled': True,
            'music_volume': 0.5,  # 0.0 to 1.0
        }

        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.music_enabled = settings.get('music_enabled', default_settings['music_enabled'])
                    self.music_volume = settings.get('music_volume', default_settings['music_volume'])
            else:
                self.music_enabled = default_settings['music_enabled']
                self.music_volume = default_settings['music_volume']
                self.save_settings()
        except Exception as e:
            logger.error(f"Failed to load music settings: {e}")
            self.music_enabled = default_settings['music_enabled']
            self.music_volume = default_settings['music_volume']

        pygame.mixer.music.set_volume(self.music_volume)
        logger.info(f"Music settings loaded: enabled={self.music_enabled}, volume={self.music_volume:.2f}")

    def save_settings(self):
        """Save music settings to file."""
        settings = {
            'music_enabled': self.music_enabled,
            'music_volume': self.music_volume
        }

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            logger.info("Music settings saved")
        except Exception as e:
            logger.error(f"Failed to save music settings: {e}")

    def play(self, track_name, loops=-1):
        """
        Play a music track.

        Args:
            track_name: 'menu' or 'gameplay'
            loops: -1 for infinite loop, 0 for once, etc.
        """
        if not self.music_enabled:
            logger.info("Music is disabled")
            return

        if track_name not in self.tracks:
            logger.warning(f"Unknown track: {track_name}")
            return

        track_path = self.tracks[track_name]
        if not track_path.exists():
            logger.warning(f"Music file not found: {track_path}")
            return

        try:
            # Stop current music if playing
            if self.is_playing:
                pygame.mixer.music.fadeout(1000)  # 1 second fade out

            # Load and play new track
            pygame.mixer.music.load(str(track_path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)

            self.current_track = track_name
            self.is_playing = True

            logger.info(f"Playing music: {track_name}")
        except Exception as e:
            logger.error(f"Failed to play music {track_name}: {e}")

    def stop(self, fade_ms=1000):
        """Stop the currently playing music."""
        if self.is_playing:
            pygame.mixer.music.fadeout(fade_ms)
            self.is_playing = False
            self.current_track = None
            logger.info("Music stopped")

    def pause(self):
        """Pause the music."""
        if self.is_playing:
            pygame.mixer.music.pause()
            logger.info("Music paused")

    def unpause(self):
        """Unpause the music."""
        if self.is_playing:
            pygame.mixer.music.unpause()
            logger.info("Music unpaused")

    def set_volume(self, volume):
        """
        Set music volume.

        Args:
            volume: 0.0 (silent) to 1.0 (full volume)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        self.save_settings()
        logger.info(f"Music volume set to {self.music_volume:.2f}")

    def toggle_enabled(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled

        if not self.music_enabled:
            self.stop(fade_ms=500)
        else:
            # Resume music if we have a track selected
            if self.current_track:
                self.play(self.current_track)

        self.save_settings()
        logger.info(f"Music {'enabled' if self.music_enabled else 'disabled'}")

        return self.music_enabled


# Global music manager instance
_music_manager = None


def get_music_manager():
    """Get the global music manager instance."""
    global _music_manager
    if _music_manager is None:
        _music_manager = MusicManager()
    return _music_manager
