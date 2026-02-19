"""
Advanced tile renderer with beautiful effects for a top-down hero game aesthetic.
"""

import pygame
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *
from src.world.terrain import TerrainType


class TileRenderer:
    """Renders tiles with beautiful effects and details."""

    def __init__(self):
        self.frame_count = 0  # For animations
        self.world = None  # Reference to world for neighbor checking

    def set_world(self, world):
        """Set world reference for terrain blending."""
        self.world = world

    def update(self):
        """Update animation frame counter."""
        self.frame_count += 1

    def get_neighbors(self, tile_x, tile_y):
        """Get neighboring tiles for blending."""
        if self.world is None:
            return []

        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tile_x + dx, tile_y + dy
                if 0 <= ny < len(self.world) and 0 <= nx < len(self.world[0]):
                    neighbors.append(self.world[ny][nx])
        return neighbors

    def blend_color(self, base_color, neighbor_color, strength=0.3):
        """Blend two colors together."""
        return tuple(int(base_color[i] * (1 - strength) + neighbor_color[i] * strength)
                    for i in range(3))

    def get_blended_color(self, tile, neighbors):
        """Return pure base color - no blending for clean uniform biomes."""
        # Simply return the base color with no blending at all
        return tile.get_color()

    def draw_tile(self, surface, tile, x, y, size, zoom):
        """Draw a single tile with all visual enhancements and blending."""
        # Get neighbors for blending
        neighbors = self.get_neighbors(tile.x, tile.y)

        # Get blended base color
        blended_color = self.get_blended_color(tile, neighbors)

        # Draw base terrain with blended color
        if tile.terrain_type == TerrainType.GRASS:
            self._draw_grass(surface, tile, x, y, size, blended_color)
        elif tile.terrain_type == TerrainType.WATER:
            self._draw_water(surface, tile, x, y, size, blended_color)
        elif tile.terrain_type == TerrainType.SAND:
            self._draw_sand(surface, tile, x, y, size, blended_color)
        elif tile.terrain_type == TerrainType.FOREST:
            self._draw_forest(surface, tile, x, y, size, zoom, blended_color)
        elif tile.terrain_type == TerrainType.STONE:
            self._draw_stone(surface, tile, x, y, size, blended_color)
        elif tile.terrain_type == TerrainType.DIRT:
            self._draw_dirt(surface, tile, x, y, size, blended_color)

        # Draw decorations on top of terrain
        if size >= 6:  # Only draw decorations if tiles are large enough
            for decoration in tile.decorations:
                decoration.draw(surface, x, y, size)

    def _draw_grass(self, surface, tile, x, y, size, blended_color):
        """Draw grass with blended color and texture."""
        # Draw grass with the pre-blended color
        pygame.draw.rect(surface, blended_color, (x, y, size, size))

        # Add subtle texture with darker patches
        if size >= 8:
            if tile.micro_variation in [0, 2]:
                # Make darker version of blended color
                tuft_color = tuple(max(0, int(c * 0.7)) for c in blended_color)
                tuft_size = max(2, size // 8)
                offset = (tile.variation * 3) % (size - tuft_size)
                pygame.draw.rect(surface, tuft_color,
                               (x + offset, y + offset, tuft_size, tuft_size))

    def _draw_water(self, surface, tile, x, y, size, blended_color):
        """Draw water with slow animation and shine effects."""
        # Slow animated water depth (reduced speed from 0.1 to 0.03)
        wave_offset = math.sin((self.frame_count + tile.x + tile.y) * 0.03) * 0.15

        # Slightly vary the blended color with wave animation
        if wave_offset > 0:
            animated_color = tuple(min(255, int(c * 1.1)) for c in blended_color)
        else:
            animated_color = tuple(max(0, int(c * 0.95)) for c in blended_color)

        pygame.draw.rect(surface, animated_color, (x, y, size, size))

        # Add slow shimmer effect (reduced speed from 0.08 to 0.025)
        if size >= 8:
            shimmer_intensity = (math.sin((self.frame_count + tile.x * 2 + tile.y * 3) * 0.025) + 1) / 2
            if shimmer_intensity > 0.7:
                shimmer_size = max(2, size // 6)
                shimmer_x = x + (tile.variation * 5) % (size - shimmer_size)
                shimmer_y = y + (tile.micro_variation * 3) % (size - shimmer_size)
                shimmer_color = COLOR_WATER_SHINE
                pygame.draw.rect(surface, shimmer_color,
                               (shimmer_x, shimmer_y, shimmer_size, shimmer_size))

    def _draw_sand(self, surface, tile, x, y, size, blended_color):
        """Draw sand with blended color and texture."""
        # Base sand with blended color
        pygame.draw.rect(surface, blended_color, (x, y, size, size))

        # Add grain texture
        if size >= 8:
            grain_color = tile.get_shadow_color()
            # Scattered grain pixels
            for i in range(3):
                grain_x = x + ((tile.x + i * 7) % (size - 1))
                grain_y = y + ((tile.y + i * 5) % (size - 1))
                pygame.draw.rect(surface, grain_color, (grain_x, grain_y, 1, 1))

        # Highlight
        if size >= 4:
            highlight_color = tile.get_highlight_color()
            pygame.draw.line(surface, highlight_color, (x, y), (x + size // 3, y), 1)

    def _draw_forest(self, surface, tile, x, y, size, zoom, blended_color):
        """Draw forest with blended color and tree details."""
        # Base forest floor with blended color
        pygame.draw.rect(surface, blended_color, (x, y, size, size))

        # Draw trees when zoomed in enough
        if size >= 12 and zoom >= 0.5:
            # Tree crown (dark green circle)
            tree_size = max(6, size // 2)
            tree_x = x + size // 2
            tree_y = y + size // 2

            # Shadow under tree
            shadow_offset = 2
            pygame.draw.circle(surface, COLOR_FOREST_DARK,
                             (tree_x + shadow_offset, tree_y + shadow_offset),
                             tree_size // 2)

            # Tree crown
            pygame.draw.circle(surface, COLOR_FOREST_LIGHT,
                             (tree_x, tree_y), tree_size // 2)

            # Tree trunk (only if large enough)
            if size >= 16:
                trunk_width = max(2, size // 8)
                trunk_height = max(3, size // 6)
                trunk_x = tree_x - trunk_width // 2
                trunk_y = tree_y + tree_size // 4
                pygame.draw.rect(surface, COLOR_TREE_TRUNK,
                               (trunk_x, trunk_y, trunk_width, trunk_height))
        elif size >= 6:
            # Simple tree representation when smaller
            tree_color = COLOR_FOREST_LIGHT
            center_x = x + size // 2
            center_y = y + size // 2
            tree_radius = max(2, size // 4)
            pygame.draw.circle(surface, tree_color, (center_x, center_y), tree_radius)

        # Darker edges for depth
        if size >= 4:
            edge_color = COLOR_FOREST_DARK
            pygame.draw.line(surface, edge_color, (x, y + size - 1), (x + size - 1, y + size - 1), 1)
            pygame.draw.line(surface, edge_color, (x + size - 1, y), (x + size - 1, y + size - 1), 1)

    def _draw_stone(self, surface, tile, x, y, size, blended_color):
        """Draw stone with blended color and texture."""
        # Base stone with blended color
        pygame.draw.rect(surface, blended_color, (x, y, size, size))

        # Add rocky texture
        if size >= 8:
            # Create rock-like patterns
            dark_color = tile.get_shadow_color()
            light_color = tile.get_highlight_color()

            # Random rock cracks/patterns
            pattern = (tile.x + tile.y) % 4
            if pattern == 0:
                pygame.draw.line(surface, dark_color,
                               (x + 2, y), (x + size - 3, y + size - 1), 1)
            elif pattern == 1:
                pygame.draw.rect(surface, light_color,
                               (x + size // 4, y + size // 4, size // 2, size // 2))

        # Stone edge shadows for 3D effect
        if size >= 6:
            shadow = tile.get_shadow_color()
            pygame.draw.line(surface, shadow, (x, y + size - 1), (x + size - 1, y + size - 1), 2)
            pygame.draw.line(surface, shadow, (x + size - 1, y), (x + size - 1, y + size - 1), 2)

    def _draw_dirt(self, surface, tile, x, y, size, blended_color):
        """Draw dirt with blended color and texture."""
        # Base dirt with blended color
        pygame.draw.rect(surface, blended_color, (x, y, size, size))

        # Add soil texture
        if size >= 8:
            dark_color = tile.get_shadow_color()
            # Soil clumps
            for i in range(2):
                clump_x = x + ((tile.x + i * 11) % (size - 2))
                clump_y = y + ((tile.y + i * 7) % (size - 2))
                clump_size = max(2, size // 10)
                pygame.draw.rect(surface, dark_color,
                               (clump_x, clump_y, clump_size, clump_size))

        # Subtle highlight
        if size >= 4:
            highlight_color = tile.get_highlight_color()
            pygame.draw.line(surface, highlight_color, (x, y), (x + size // 4, y), 1)
