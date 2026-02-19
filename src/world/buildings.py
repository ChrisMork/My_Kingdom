"""
Building system for My Kingdom.
Handles 2.5D buildings and structures in the game world.
"""

import pygame
from pathlib import Path
from src.core.logger import logger
from src.world.building_renderer import BuildingRenderer


class Building:
    """Represents a single building in the world."""

    def __init__(self, building_type, x, y, width=2, height=2):
        """
        Initialize a building.

        Args:
            building_type: Type of building (house_small, well, etc.)
            x: Grid x position
            y: Grid y position
            width: Width in tiles
            height: Height in tiles
        """
        self.type = building_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = None
        self.blocking = True  # Buildings block movement

    def get_footprint(self):
        """Get the tiles this building occupies."""
        tiles = []
        for dy in range(self.height):
            for dx in range(self.width):
                tiles.append((self.x + dx, self.y + dy))
        return tiles


class BuildingManager:
    """Manages all buildings in the world."""

    def __init__(self):
        self.buildings = []
        self.renderer = BuildingRenderer()
        self.tile_size = 32
        self.sprite_cache = {}  # Cache rendered sprites at different sizes

    def load_building_sprites(self):
        """Initialize building renderer (no sprites to load - we draw them)."""
        logger.info("Building renderer initialized - using procedural generation")

    def add_building(self, building_type, x, y):
        """
        Add a building to the world.

        Args:
            building_type: Type of building
            x: Grid x position
            y: Grid y position

        Returns:
            Building instance or None if placement failed
        """
        # Get building dimensions
        width, height = self.renderer.get_building_dimensions(building_type)

        building = Building(building_type, x, y, width, height)

        # Check if placement is valid (not overlapping)
        if self.can_place_building(building):
            self.buildings.append(building)
            logger.info(f"Placed {building_type} at ({x}, {y})")
            return building
        else:
            logger.warning(f"Cannot place {building_type} at ({x}, {y}) - overlapping")
            return None

    def can_place_building(self, building):
        """Check if a building can be placed without overlapping."""
        new_footprint = set(building.get_footprint())

        for existing in self.buildings:
            existing_footprint = set(existing.get_footprint())
            if new_footprint & existing_footprint:  # If there's overlap
                return False

        return True

    def get_building_at(self, x, y):
        """Get the building at a specific tile position."""
        for building in self.buildings:
            if (x, y) in building.get_footprint():
                return building
        return None

    def render(self, screen, camera_x, camera_y, zoom=1.0):
        """
        Render all buildings.

        Args:
            screen: Pygame surface to draw on
            camera_x: Camera x offset in pixels
            camera_y: Camera y offset in pixels
            zoom: Zoom level
        """
        zoomed_tile_size = int(self.tile_size * zoom)

        for building in self.buildings:
            # Generate or get cached sprite for this building at this size
            cache_key = (building.type, zoomed_tile_size)
            if cache_key not in self.sprite_cache:
                # Render the building procedurally
                self.sprite_cache[cache_key] = self.renderer.render_building(
                    building.type,
                    zoomed_tile_size
                )

            sprite = self.sprite_cache[cache_key]
            if sprite:
                # Calculate screen position
                # Buildings are rendered with their bottom-left at the grid position
                screen_x = int(building.x * zoomed_tile_size - camera_x)
                screen_y = int(building.y * zoomed_tile_size - camera_y)

                # Get sprite dimensions
                sprite_height = sprite.get_height()

                # Offset to make building appear to sit on the ground (2.5D effect)
                # The sprite height is usually taller than the footprint
                y_offset = sprite_height - (zoomed_tile_size * building.height)
                screen_y -= y_offset

                screen.blit(sprite, (screen_x, screen_y))

    def generate_random_village(self, world_width, world_height, num_buildings=10):
        """Generate a random village with buildings."""
        import random

        # Define building types to spawn
        building_pool = [
            "house_small",
            "house_small",
            "house_small",
            "well",
        ]

        placed = 0
        attempts = 0
        max_attempts = num_buildings * 10

        while placed < num_buildings and attempts < max_attempts:
            attempts += 1

            # Random position (avoid edges)
            x = random.randint(5, world_width - 10)
            y = random.randint(5, world_height - 10)

            # Random building type
            building_type = random.choice(building_pool)

            # Try to place
            if self.add_building(building_type, x, y):
                placed += 1

        logger.info(f"Generated village with {placed} buildings (attempted {attempts} placements)")
