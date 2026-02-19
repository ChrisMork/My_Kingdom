"""
Procedural world generation for My Kingdom.
Creates a peaceful, medieval-themed world with varied terrain.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.world.terrain import Tile, TerrainType
from src.world.decorations import DecorationGenerator
from src.core.logger import logger
from config.settings import WORLD_WIDTH, WORLD_HEIGHT


class PerlinNoise:
    """Simple Perlin-like noise generator for terrain."""

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation *= 2

    def fade(self, t):
        """Fade function for smooth interpolation."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        """Linear interpolation."""
        return a + t * (b - a)

    def gradient(self, hash_val, x, y):
        """Calculate gradient."""
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise(self, x, y):
        """Generate 2D Perlin noise."""
        X = int(x) & 255
        Y = int(y) & 255

        x -= int(x)
        y -= int(y)

        u = self.fade(x)
        v = self.fade(y)

        a = self.permutation[X] + Y
        aa = self.permutation[a]
        ab = self.permutation[a + 1]
        b = self.permutation[X + 1] + Y
        ba = self.permutation[b]
        bb = self.permutation[b + 1]

        res = self.lerp(v,
                       self.lerp(u, self.gradient(self.permutation[aa], x, y),
                                self.gradient(self.permutation[ba], x - 1, y)),
                       self.lerp(u, self.gradient(self.permutation[ab], x, y - 1),
                                self.gradient(self.permutation[bb], x - 1, y - 1)))

        return (res + 1) / 2  # Normalize to 0-1


class WorldGenerator:
    """Generates a procedural world for the game."""

    def __init__(self, width=WORLD_WIDTH, height=WORLD_HEIGHT, seed=None):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        self.noise = PerlinNoise(self.seed)
        self.tiles = []

        logger.info(f"World generator initialized with seed: {self.seed}")
        logger.info(f"World size: {self.width}x{self.height}")

    def generate(self):
        """Generate the world terrain."""
        logger.info("Starting world generation...")

        self.tiles = []

        # Generate base terrain using Perlin noise
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Multiple octaves of noise for varied terrain
                elevation = (
                    self.noise.noise(x * 0.05, y * 0.05) * 0.5 +
                    self.noise.noise(x * 0.1, y * 0.1) * 0.25 +
                    self.noise.noise(x * 0.2, y * 0.2) * 0.15 +
                    self.noise.noise(x * 0.4, y * 0.4) * 0.1
                )

                # Moisture map for variety
                moisture = (
                    self.noise.noise(x * 0.08 + 1000, y * 0.08 + 1000) * 0.6 +
                    self.noise.noise(x * 0.15 + 1000, y * 0.15 + 1000) * 0.4
                )

                # Determine terrain type based on elevation and moisture
                terrain = self._get_terrain_type(elevation, moisture)
                tile = Tile(x, y, terrain)
                row.append(tile)

            self.tiles.append(row)

        # Add some forests in clusters
        self._add_forests()

        # Smooth water edges
        self._smooth_terrain()

        # Add decorations to bring life to the world
        self._add_decorations()

        logger.info("World generation completed")
        self._log_terrain_stats()

        return self.tiles

    def _add_decorations(self):
        """Add decorative objects to tiles for visual variety."""
        logger.info("Adding decorations to world...")
        decoration_gen = DecorationGenerator(self.seed)

        decoration_count = 0
        for row in self.tiles:
            for tile in row:
                decorations = decoration_gen.generate_decorations_for_tile(tile)
                tile.decorations = decorations
                decoration_count += len(decorations)

        logger.info(f"Added {decoration_count} decorations to the world")

    def _get_terrain_type(self, elevation, moisture):
        """Determine terrain type based on elevation and moisture."""
        if elevation < 0.35:
            return TerrainType.WATER
        elif elevation < 0.4:
            return TerrainType.SAND
        elif elevation < 0.7:
            if moisture > 0.6:
                return TerrainType.FOREST
            else:
                return TerrainType.GRASS
        elif elevation < 0.8:
            return TerrainType.DIRT
        else:
            return TerrainType.STONE

    def _add_forests(self):
        """Add forest patches to the world."""
        num_forests = random.randint(15, 25)

        for _ in range(num_forests):
            center_x = random.randint(0, self.width - 1)
            center_y = random.randint(0, self.height - 1)

            if self.tiles[center_y][center_x].terrain_type == TerrainType.GRASS:
                radius = random.randint(3, 8)

                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = center_x + dx, center_y + dy

                        if (0 <= nx < self.width and 0 <= ny < self.height):
                            distance = (dx * dx + dy * dy) ** 0.5
                            if distance <= radius and random.random() > 0.3:
                                if self.tiles[ny][nx].terrain_type == TerrainType.GRASS:
                                    self.tiles[ny][nx].terrain_type = TerrainType.FOREST

    def _smooth_terrain(self):
        """Smooth terrain transitions for a more natural look."""
        # Create a copy for checking neighbors
        original = [[tile.terrain_type for tile in row] for row in self.tiles]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if original[y][x] == TerrainType.WATER:
                    # Check if surrounded by non-water
                    neighbors = [
                        original[y - 1][x], original[y + 1][x],
                        original[y][x - 1], original[y][x + 1]
                    ]
                    if all(n != TerrainType.WATER for n in neighbors):
                        self.tiles[y][x].terrain_type = TerrainType.GRASS

    def _log_terrain_stats(self):
        """Log statistics about the generated terrain."""
        terrain_counts = {}

        for row in self.tiles:
            for tile in row:
                terrain_type = tile.terrain_type.value
                terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1

        total_tiles = self.width * self.height
        logger.info("Terrain distribution:")
        for terrain, count in sorted(terrain_counts.items()):
            percentage = (count / total_tiles) * 100
            logger.info(f"  {terrain}: {count} tiles ({percentage:.1f}%)")

    def get_tile(self, x, y):
        """Get a tile at the specified coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
