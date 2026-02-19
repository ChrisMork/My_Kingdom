"""
Decorative objects that bring life to the world.
Rocks, flowers, bushes, individual trees, etc.
"""

import random
import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *
from src.world.terrain import TerrainType


class Decoration:
    """A decorative object on a tile."""

    def __init__(self, decoration_type, x_offset=0, y_offset=0):
        self.type = decoration_type
        self.x_offset = x_offset  # Offset within tile
        self.y_offset = y_offset

    def draw(self, surface, x, y, size):
        """Draw the decoration."""
        draw_x = x + int(self.x_offset * size)
        draw_y = y + int(self.y_offset * size)

        if self.type == "rock_small":
            # Small gray rock
            rock_size = max(2, size // 6)
            pygame.draw.circle(surface, (100, 100, 100), (draw_x, draw_y), rock_size)
            pygame.draw.circle(surface, (120, 120, 120), (draw_x - 1, draw_y - 1), rock_size - 1)

        elif self.type == "rock_medium":
            # Medium rock
            rock_size = max(3, size // 4)
            pygame.draw.circle(surface, (90, 90, 90), (draw_x, draw_y), rock_size)
            pygame.draw.circle(surface, (110, 110, 110), (draw_x - 1, draw_y - 1), rock_size - 1)

        elif self.type == "flower_yellow":
            # Yellow flower
            if size >= 8:
                pygame.draw.circle(surface, (255, 220, 0), (draw_x, draw_y), max(1, size // 10))

        elif self.type == "flower_red":
            # Red flower
            if size >= 8:
                pygame.draw.circle(surface, (220, 60, 60), (draw_x, draw_y), max(1, size // 10))

        elif self.type == "flower_purple":
            # Purple flower
            if size >= 8:
                pygame.draw.circle(surface, (180, 100, 200), (draw_x, draw_y), max(1, size // 10))

        elif self.type == "bush":
            # Small green bush
            if size >= 6:
                bush_size = max(2, size // 5)
                pygame.draw.circle(surface, (60, 120, 60), (draw_x, draw_y), bush_size)

        elif self.type == "grass_tuft":
            # Grass tuft (darker green)
            if size >= 6:
                tuft_size = max(2, size // 8)
                pygame.draw.rect(surface, (70, 140, 70), (draw_x, draw_y, tuft_size, tuft_size))

        elif self.type == "tree_small":
            # Small individual tree
            if size >= 10:
                tree_size = max(3, size // 3)
                # Shadow
                pygame.draw.circle(surface, (40, 80, 40), (draw_x + 1, draw_y + 1), tree_size)
                # Tree crown
                pygame.draw.circle(surface, (60, 120, 60), (draw_x, draw_y), tree_size)
                # Trunk
                trunk_width = max(1, tree_size // 3)
                pygame.draw.rect(surface, (101, 67, 33),
                               (draw_x - trunk_width // 2, draw_y + tree_size // 2,
                                trunk_width, tree_size // 2))

        elif self.type == "stump":
            # Tree stump
            if size >= 8:
                stump_size = max(2, size // 6)
                pygame.draw.circle(surface, (90, 60, 30), (draw_x, draw_y), stump_size)
                pygame.draw.circle(surface, (110, 80, 50), (draw_x, draw_y), stump_size - 1)


class DecorationGenerator:
    """Generates decorations for tiles based on terrain type."""

    def __init__(self, seed=None):
        self.seed = seed
        if seed:
            random.seed(seed)

    def generate_decorations_for_tile(self, tile):
        """Generate appropriate decorations for a tile."""
        decorations = []

        # Use tile position as seed for consistent decoration placement
        tile_seed = (tile.x * 73 + tile.y * 37) % 100

        if tile.terrain_type == TerrainType.GRASS:
            # Grass has flowers, rocks, bushes
            if tile_seed < 15:  # 15% chance of decoration
                decoration_type = tile_seed % 7

                if decoration_type == 0:
                    decorations.append(Decoration("rock_small", 0.3, 0.4))
                elif decoration_type == 1:
                    decorations.append(Decoration("flower_yellow", 0.6, 0.3))
                elif decoration_type == 2:
                    decorations.append(Decoration("flower_red", 0.4, 0.7))
                elif decoration_type == 3:
                    decorations.append(Decoration("flower_purple", 0.5, 0.5))
                elif decoration_type == 4:
                    decorations.append(Decoration("bush", 0.6, 0.6))
                elif decoration_type == 5:
                    decorations.append(Decoration("grass_tuft", 0.3, 0.3))
                elif decoration_type == 6:
                    decorations.append(Decoration("tree_small", 0.5, 0.5))

        elif tile.terrain_type == TerrainType.FOREST:
            # Forest has tree stumps, rocks, mushrooms
            if tile_seed < 10:  # 10% chance
                decoration_type = tile_seed % 3

                if decoration_type == 0:
                    decorations.append(Decoration("stump", 0.4, 0.6))
                elif decoration_type == 1:
                    decorations.append(Decoration("rock_medium", 0.5, 0.4))
                elif decoration_type == 2:
                    decorations.append(Decoration("bush", 0.3, 0.7))

        elif tile.terrain_type == TerrainType.STONE:
            # Mountains have rocks
            if tile_seed < 25:  # 25% chance
                if tile_seed % 2 == 0:
                    decorations.append(Decoration("rock_medium", 0.4, 0.5))
                else:
                    decorations.append(Decoration("rock_small", 0.6, 0.4))

        elif tile.terrain_type == TerrainType.SAND:
            # Beach has small rocks, shells (represented as rocks for now)
            if tile_seed < 8:  # 8% chance
                decorations.append(Decoration("rock_small", 0.5, 0.5))

        return decorations
