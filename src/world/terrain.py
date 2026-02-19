"""
Terrain types for the world.
"""

from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *


class TerrainType(Enum):
    """Different terrain types in the world."""
    GRASS = "grass"
    WATER = "water"
    SAND = "sand"
    FOREST = "forest"
    STONE = "stone"
    DIRT = "dirt"


class Tile:
    """A single tile in the world."""

    def __init__(self, x, y, terrain_type=TerrainType.GRASS):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.building = None
        self.resource = None
        self.decorations = []  # List of Decoration objects
        # Add variation seed based on position for consistent random variation
        self.variation = (x * 7 + y * 13) % 3
        self.micro_variation = (x * 3 + y * 5) % 5

    def get_color(self):
        """Get the color for this tile with variation."""
        if self.terrain_type == TerrainType.GRASS:
            return COLOR_GRASS_VARIANTS[self.variation % len(COLOR_GRASS_VARIANTS)]
        elif self.terrain_type == TerrainType.WATER:
            return COLOR_WATER_BASE
        elif self.terrain_type == TerrainType.SAND:
            return COLOR_SAND_VARIANTS[self.variation % len(COLOR_SAND_VARIANTS)]
        elif self.terrain_type == TerrainType.FOREST:
            return COLOR_FOREST_BASE
        elif self.terrain_type == TerrainType.STONE:
            return COLOR_STONE_VARIANTS[self.variation % len(COLOR_STONE_VARIANTS)]
        elif self.terrain_type == TerrainType.DIRT:
            return COLOR_DIRT_VARIANTS[self.variation % len(COLOR_DIRT_VARIANTS)]
        return (255, 255, 255)

    def get_shadow_color(self):
        """Get a darker version of the tile color for shadows."""
        base = self.get_color()
        return tuple(max(0, int(c * 0.7)) for c in base)

    def get_highlight_color(self):
        """Get a lighter version of the tile color for highlights."""
        base = self.get_color()
        return tuple(min(255, int(c * 1.2)) for c in base)

    def is_buildable(self):
        """Check if this tile can have buildings placed on it."""
        return self.terrain_type in [TerrainType.GRASS, TerrainType.DIRT] and self.building is None
