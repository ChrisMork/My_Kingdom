"""
Save/Load system for My Kingdom.
Implements best practices from research:
- JSON for human-readability and safety
- Versioned save format for compatibility
- Incremental/auto-save support
- Campaign management
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import gzip

from src.core.logger import logger


class SaveSystem:
    """
    Manages game saving and loading.

    Design principles (from research):
    - Use JSON (safe, human-readable, debuggable)
    - Version saves for compatibility
    - Support multiple save slots
    - Compress large saves
    """

    SAVE_VERSION = "1.0"
    SAVE_DIR = Path("saves")

    def __init__(self):
        # Ensure save directory exists
        self.SAVE_DIR.mkdir(exist_ok=True)
        logger.info(f"Save system initialized. Save directory: {self.SAVE_DIR.absolute()}")

    def save_game(
        self,
        save_name: str,
        world_data: dict,
        compress: bool = True
    ) -> bool:
        """
        Save the complete game state.

        Args:
            save_name: Name of the save file
            world_data: Complete world state (tiles, buildings, citizens, etc.)
            compress: Whether to compress the save file

        Returns:
            True if save successful
        """
        try:
            # Create save data structure
            save_data = {
                'version': self.SAVE_VERSION,
                'save_name': save_name,
                'timestamp': datetime.now().isoformat(),
                'world': world_data
            }

            # Determine file path
            if compress:
                file_path = self.SAVE_DIR / f"{save_name}.sav.gz"
            else:
                file_path = self.SAVE_DIR / f"{save_name}.json"

            # Save to file
            if compress:
                # Compressed JSON
                json_str = json.dumps(save_data, indent=2)
                with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
            else:
                # Plain JSON
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2)

            logger.info(f"Game saved successfully: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[dict]:
        """
        Load a saved game.

        Args:
            save_name: Name of the save file

        Returns:
            World data dictionary or None if load failed
        """
        try:
            # Try compressed first
            compressed_path = self.SAVE_DIR / f"{save_name}.sav.gz"
            json_path = self.SAVE_DIR / f"{save_name}.json"

            save_data = None

            if compressed_path.exists():
                with gzip.open(compressed_path, 'rt', encoding='utf-8') as f:
                    save_data = json.load(f)
                logger.info(f"Loaded compressed save: {compressed_path}")

            elif json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                logger.info(f"Loaded uncompressed save: {json_path}")

            else:
                logger.error(f"Save file not found: {save_name}")
                return None

            # Verify version
            if save_data['version'] != self.SAVE_VERSION:
                logger.warning(f"Save version mismatch: {save_data['version']} != {self.SAVE_VERSION}")
                # Could implement migration here

            return save_data['world']

        except Exception as e:
            logger.error(f"Failed to load game: {e}")
            return None

    def list_saves(self) -> List[Dict[str, str]]:
        """
        List all available save files.

        Returns:
            List of save metadata dicts
        """
        saves = []

        for file_path in self.SAVE_DIR.glob("*.sav.gz"):
            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    save_data = json.load(f)

                saves.append({
                    'name': save_data['save_name'],
                    'timestamp': save_data['timestamp'],
                    'version': save_data['version'],
                    'file': file_path.name,
                    'compressed': True
                })
            except Exception as e:
                logger.warning(f"Could not read save file {file_path}: {e}")

        for file_path in self.SAVE_DIR.glob("*.json"):
            if file_path.stem.endswith('.sav'):
                continue  # Skip .sav.json files

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)

                saves.append({
                    'name': save_data['save_name'],
                    'timestamp': save_data['timestamp'],
                    'version': save_data['version'],
                    'file': file_path.name,
                    'compressed': False
                })
            except Exception as e:
                logger.warning(f"Could not read save file {file_path}: {e}")

        # Sort by timestamp (newest first)
        saves.sort(key=lambda s: s['timestamp'], reverse=True)

        logger.info(f"Found {len(saves)} save files")
        return saves

    def delete_save(self, save_name: str) -> bool:
        """
        Delete a save file.

        Args:
            save_name: Name of the save to delete

        Returns:
            True if deleted successfully
        """
        try:
            compressed_path = self.SAVE_DIR / f"{save_name}.sav.gz"
            json_path = self.SAVE_DIR / f"{save_name}.json"

            deleted = False

            if compressed_path.exists():
                compressed_path.unlink()
                deleted = True
                logger.info(f"Deleted save: {compressed_path}")

            if json_path.exists():
                json_path.unlink()
                deleted = True
                logger.info(f"Deleted save: {json_path}")

            if not deleted:
                logger.warning(f"Save not found for deletion: {save_name}")

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete save: {e}")
            return False

    def save_exists(self, save_name: str) -> bool:
        """Check if a save file exists."""
        compressed_path = self.SAVE_DIR / f"{save_name}.sav.gz"
        json_path = self.SAVE_DIR / f"{save_name}.json"

        return compressed_path.exists() or json_path.exists()

    def get_auto_save_name(self) -> str:
        """Get auto-save filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"autosave_{timestamp}"

    def auto_save(self, world_data: dict) -> bool:
        """
        Perform an auto-save.

        Args:
            world_data: Complete world state

        Returns:
            True if save successful
        """
        save_name = self.get_auto_save_name()
        return self.save_game(save_name, world_data, compress=True)

    def clean_old_auto_saves(self, keep_count: int = 5):
        """
        Delete old auto-saves, keeping only the most recent.

        Args:
            keep_count: Number of auto-saves to keep
        """
        auto_saves = [
            s for s in self.list_saves()
            if s['name'].startswith('autosave_')
        ]

        # Sort by timestamp
        auto_saves.sort(key=lambda s: s['timestamp'], reverse=True)

        # Delete old ones
        for save in auto_saves[keep_count:]:
            self.delete_save(save['name'])

        if len(auto_saves) > keep_count:
            logger.info(f"Cleaned up {len(auto_saves) - keep_count} old auto-saves")
