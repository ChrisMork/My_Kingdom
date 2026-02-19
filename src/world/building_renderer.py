"""
Procedural 2.5D building renderer for My Kingdom.
Draws buildings programmatically to match the terrain style.
"""

import pygame
import random
from pathlib import Path
from src.core.logger import logger


class BuildingRenderer:
    """Renders 2.5D buildings procedurally."""

    def __init__(self):
        self.building_types = {
            "house_small": self.draw_small_house,
            "house_ai": self.draw_ai_house,  # AI-generated house
            "well": self.draw_well,
        }
        self.ai_sprites = {}
        self._load_ai_sprites()

    def draw_small_house(self, size):
        """
        Draw a small medieval house in 2.5D style.

        Args:
            size: Base tile size in pixels

        Returns:
            Pygame surface with the building
        """
        # House is 2x2 tiles wide but taller for 2.5D effect
        width = size * 2
        height = int(size * 2.5)

        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Colors - warm medieval palette
        wall_color = (139, 90, 60)  # Brown stone/wood
        wall_shadow = (100, 65, 45)
        wall_highlight = (160, 110, 80)
        roof_color = (120, 80, 40)  # Dark thatch
        roof_shadow = (80, 50, 25)
        roof_highlight = (140, 100, 50)
        door_color = (60, 40, 20)
        window_color = (40, 60, 80)  # Dark blue

        # Draw the building from back to front for proper 2.5D

        # Back wall (top part visible in 2.5D)
        back_wall_height = int(size * 0.8)
        pygame.draw.rect(surface, wall_shadow,
                        (size * 0.2, height - size * 2 - back_wall_height,
                         width * 0.6, back_wall_height))

        # Main walls (front-facing)
        wall_height = int(size * 1.2)
        # Left wall (slightly darker for depth)
        pygame.draw.polygon(surface, wall_shadow, [
            (0, height - wall_height),
            (size * 0.3, height - wall_height - size * 0.2),
            (size * 0.3, height - size * 0.2),
            (0, height)
        ])

        # Front wall
        front_rect = pygame.Rect(size * 0.3, height - wall_height, width - size * 0.3, wall_height)
        pygame.draw.rect(surface, wall_color, front_rect)

        # Add wall texture (horizontal planks/stones)
        for i in range(4):
            y = height - wall_height + i * (wall_height // 4)
            pygame.draw.line(surface, wall_highlight,
                           (size * 0.3, y), (width, y), 1)

        # Roof (2.5D angled)
        roof_points = [
            (0, height - wall_height - size * 0.3),  # Left bottom
            (width // 2, height - size * 2),  # Peak
            (width, height - wall_height - size * 0.3),  # Right bottom
            (width, height - wall_height),  # Right top
            (0, height - wall_height)  # Left top
        ]
        pygame.draw.polygon(surface, roof_color, roof_points)

        # Roof shadow (left side)
        left_roof = [
            (0, height - wall_height - size * 0.3),
            (width // 2, height - size * 2),
            (width // 2, height - wall_height - size * 0.5),
            (0, height - wall_height)
        ]
        pygame.draw.polygon(surface, roof_shadow, left_roof)

        # Roof highlight (right side)
        right_roof = [
            (width // 2, height - size * 2),
            (width, height - wall_height - size * 0.3),
            (width, height - wall_height),
            (width // 2, height - wall_height - size * 0.5)
        ]
        pygame.draw.polygon(surface, roof_highlight, right_roof)

        # Door
        door_width = size // 3
        door_height = size // 2
        door_x = width // 2 - door_width // 2
        door_y = height - door_height - 2
        pygame.draw.rect(surface, door_color,
                        (door_x, door_y, door_width, door_height))
        # Door frame
        pygame.draw.rect(surface, wall_shadow,
                        (door_x, door_y, door_width, door_height), 2)

        # Window
        window_size = size // 4
        window_x = width - size // 2 - window_size
        window_y = height - wall_height + size // 4
        pygame.draw.rect(surface, window_color,
                        (window_x, window_y, window_size, window_size))
        # Window cross
        pygame.draw.line(surface, wall_shadow,
                        (window_x, window_y + window_size // 2),
                        (window_x + window_size, window_y + window_size // 2), 2)
        pygame.draw.line(surface, wall_shadow,
                        (window_x + window_size // 2, window_y),
                        (window_x + window_size // 2, window_y + window_size), 2)

        return surface

    def draw_well(self, size):
        """
        Draw a stone well in 2.5D style.

        Args:
            size: Base tile size in pixels

        Returns:
            Pygame surface with the building
        """
        # Well is 1x1 tile but has height for 2.5D
        width = size
        height = int(size * 1.8)

        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Colors
        stone_color = (120, 120, 130)
        stone_shadow = (80, 80, 90)
        stone_highlight = (150, 150, 160)
        wood_color = (100, 70, 50)
        wood_shadow = (70, 50, 35)
        rope_color = (140, 120, 80)
        water_color = (40, 80, 120)

        # Well base (cylindrical stone structure)
        base_height = int(size * 0.8)
        base_y = height - base_height

        # Draw cylinder (front face)
        pygame.draw.ellipse(surface, stone_shadow,
                          (size * 0.1, base_y - size * 0.1, size * 0.8, size * 0.3))

        # Cylinder walls
        pygame.draw.rect(surface, stone_color,
                        (size * 0.1, base_y, size * 0.8, base_height))

        # Left side (darker for depth)
        pygame.draw.rect(surface, stone_shadow,
                        (size * 0.1, base_y, size * 0.15, base_height))

        # Right side (lighter)
        pygame.draw.rect(surface, stone_highlight,
                        (size * 0.75, base_y, size * 0.15, base_height))

        # Top opening (water visible)
        pygame.draw.ellipse(surface, water_color,
                          (size * 0.2, base_y, size * 0.6, size * 0.25))

        # Stone texture
        for i in range(3):
            y = base_y + i * (base_height // 3)
            pygame.draw.line(surface, stone_shadow,
                           (size * 0.1, y), (size * 0.9, y), 1)

        # Wooden roof support posts
        post_width = size // 10
        # Left post
        pygame.draw.rect(surface, wood_shadow,
                        (size * 0.15, base_y - size * 0.8, post_width, size * 0.8))
        # Right post
        pygame.draw.rect(surface, wood_color,
                        (size * 0.75, base_y - size * 0.8, post_width, size * 0.8))

        # Roof beam
        beam_points = [
            (size * 0.1, base_y - size * 0.75),
            (size * 0.9, base_y - size * 0.75),
            (size * 0.85, base_y - size * 0.85),
            (size * 0.15, base_y - size * 0.85)
        ]
        pygame.draw.polygon(surface, wood_color, beam_points)

        # Roof (small peaked roof)
        roof_points = [
            (0, base_y - size * 0.7),
            (size // 2, base_y - size),
            (size, base_y - size * 0.7)
        ]
        pygame.draw.polygon(surface, wood_shadow, roof_points)

        # Rope hanging from roof
        rope_x = size // 2
        pygame.draw.line(surface, rope_color,
                        (rope_x, base_y - size * 0.75),
                        (rope_x, base_y + size * 0.1), 2)

        # Bucket at end of rope
        bucket_size = size // 5
        pygame.draw.ellipse(surface, wood_shadow,
                          (rope_x - bucket_size // 2, base_y,
                           bucket_size, bucket_size // 2))

        return surface

    def render_building(self, building_type, tile_size):
        """
        Render a building of the specified type.

        Args:
            building_type: Type of building to render
            tile_size: Size of a tile in pixels

        Returns:
            Pygame surface with the rendered building
        """
        if building_type in self.building_types:
            return self.building_types[building_type](tile_size)
        else:
            logger.warning(f"Unknown building type: {building_type}")
            return None

    def _load_ai_sprites(self):
        """Load AI-generated sprites and make backgrounds transparent."""
        assets_dir = Path("assets/images/world")

        ai_building_files = {
            "house_ai": "house_small.png",
        }

        for building_type, filename in ai_building_files.items():
            sprite_path = assets_dir / filename
            if sprite_path.exists():
                try:
                    # Load the image
                    original = pygame.image.load(str(sprite_path)).convert_alpha()

                    # Make white background transparent
                    # Create a new surface with alpha
                    clean_surface = pygame.Surface(original.get_size(), pygame.SRCALPHA)

                    # Copy pixels, making white transparent
                    for x in range(original.get_width()):
                        for y in range(original.get_height()):
                            color = original.get_at((x, y))
                            # If pixel is mostly white (R, G, B all > 240), make it transparent
                            if color[0] > 240 and color[1] > 240 and color[2] > 240:
                                clean_surface.set_at((x, y), (0, 0, 0, 0))
                            else:
                                clean_surface.set_at((x, y), color)

                    self.ai_sprites[building_type] = clean_surface
                    logger.info(f"Loaded AI sprite: {building_type} with transparent background")
                except Exception as e:
                    logger.error(f"Failed to load AI sprite {building_type}: {e}")

    def draw_ai_house(self, size):
        """
        Render AI-generated house with transparent background.

        Args:
            size: Base tile size in pixels

        Returns:
            Pygame surface with the building
        """
        if "house_ai" not in self.ai_sprites:
            logger.warning("AI house sprite not loaded, using procedural fallback")
            return self.draw_small_house(size)

        # AI house is 2x2 tiles
        target_width = size * 2

        # Get original sprite
        original = self.ai_sprites["house_ai"]

        # Calculate height maintaining aspect ratio
        aspect_ratio = original.get_height() / original.get_width()
        target_height = int(target_width * aspect_ratio)

        # Scale the sprite
        scaled = pygame.transform.smoothscale(original, (target_width, target_height))

        return scaled

    def get_building_dimensions(self, building_type):
        """Get the tile dimensions for a building type."""
        dimensions = {
            "house_small": (2, 2),
            "house_ai": (2, 2),
            "well": (1, 1),
        }
        return dimensions.get(building_type, (1, 1))
