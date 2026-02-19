"""
World map system for My Kingdom.
Handles tile-based world rendering and management.
"""

import pygame
import json
from pathlib import Path
from src.core.logger import logger


class WorldMap:
    """Tile-based world map."""

    def __init__(self, width=50, height=50, tile_size=32):
        """
        Initialize world map.

        Args:
            width: Map width in tiles
            height: Map height in tiles
            tile_size: Size of each tile in pixels
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size

        # Map data: 2D array of tile types
        self.terrain_map = [["grass" for _ in range(width)] for _ in range(height)]

        # Objects on the map (trees, rocks, etc.)
        self.objects = []  # List of (x, y, object_type)

        # Loaded tile images
        self.tiles = {}
        self.object_images = {}

        # Camera position (in pixels)
        self.camera_x = 0
        self.camera_y = 0

        logger.info(f"World map created: {width}x{height} tiles")

    def load_assets(self):
        """Load all tile and object images."""
        assets_dir = Path("assets/images/world")

        if not assets_dir.exists():
            logger.warning("World assets directory not found. Generating placeholder tiles...")
            self._generate_placeholder_tiles()
            return

        # Load terrain tiles
        terrain_types = ["grass", "grass_flowers", "grass_dark", "dirt", "dirt_path",
                        "desert_sand", "stone_gray", "stone_path", "water_shallow",
                        "water_deep", "forest_floor", "snow"]

        for terrain in terrain_types:
            tile_path = assets_dir / f"{terrain}.png"
            if tile_path.exists():
                try:
                    self.tiles[terrain] = pygame.image.load(str(tile_path))
                    self.tiles[terrain] = pygame.transform.scale(
                        self.tiles[terrain], (self.tile_size, self.tile_size)
                    )
                    logger.info(f"Loaded tile: {terrain}")
                except Exception as e:
                    logger.error(f"Failed to load {terrain}: {e}")

        # Load object sprites
        objects = ["tree_oak", "tree_pine", "tree_small", "rock_large", "rock_small",
                  "bush_green", "house_small", "well"]

        for obj in objects:
            obj_path = assets_dir / f"{obj}.png"
            if obj_path.exists():
                try:
                    self.object_images[obj] = pygame.image.load(str(obj_path))
                    # Objects are typically 2x2 tiles
                    self.object_images[obj] = pygame.transform.scale(
                        self.object_images[obj], (self.tile_size * 2, self.tile_size * 2)
                    )
                    logger.info(f"Loaded object: {obj}")
                except Exception as e:
                    logger.error(f"Failed to load {obj}: {e}")

        logger.info(f"Loaded {len(self.tiles)} terrain tiles and {len(self.object_images)} objects")

    def _generate_placeholder_tiles(self):
        """Generate simple colored placeholder tiles."""
        colors = {
            "grass": (34, 139, 34),
            "dirt": (139, 69, 19),
            "water_shallow": (100, 150, 255),
            "stone_gray": (128, 128, 128),
        }

        for tile_name, color in colors.items():
            surface = pygame.Surface((self.tile_size, self.tile_size))
            surface.fill(color)
            # Add border for visibility
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
            self.tiles[tile_name] = surface

    def generate_simple_world(self):
        """Generate a simple procedural world for testing."""
        import random

        # Create some variety in terrain
        for y in range(self.height):
            for x in range(self.width):
                # Desert in the right side
                if x > self.width * 0.7:
                    self.terrain_map[y][x] = "desert_sand"
                # Water patches
                elif random.random() < 0.05:
                    self.terrain_map[y][x] = "water_shallow"
                # Stone paths
                elif random.random() < 0.03:
                    self.terrain_map[y][x] = "stone_path"
                # Grass variants
                elif random.random() < 0.2:
                    self.terrain_map[y][x] = "grass_flowers"
                else:
                    self.terrain_map[y][x] = "grass"

        # Add some objects
        for _ in range(100):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            obj_type = random.choice(["tree_oak", "tree_pine", "rock_large", "bush_green"])
            self.objects.append((x, y, obj_type))

        logger.info("Generated procedural world")

    def render(self, screen, screen_width, screen_height):
        """
        Render the visible portion of the map.

        Args:
            screen: Pygame surface to render to
            screen_width: Width of the screen
            screen_height: Height of the screen
        """
        # Calculate visible tile range
        start_x = max(0, int(self.camera_x // self.tile_size))
        start_y = max(0, int(self.camera_y // self.tile_size))
        end_x = min(self.width, int((self.camera_x + screen_width) // self.tile_size) + 2)
        end_y = min(self.height, int((self.camera_y + screen_height) // self.tile_size) + 2)

        # Render terrain tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.terrain_map[y][x]

                # Get tile image or use placeholder
                if tile_type in self.tiles:
                    tile_img = self.tiles[tile_type]
                elif "grass" in self.tiles:
                    tile_img = self.tiles["grass"]
                else:
                    continue

                # Calculate screen position
                screen_x = x * self.tile_size - self.camera_x
                screen_y = y * self.tile_size - self.camera_y

                screen.blit(tile_img, (screen_x, screen_y))

        # Render objects
        for obj_x, obj_y, obj_type in self.objects:
            # Check if object is in visible range
            if start_x <= obj_x < end_x and start_y <= obj_y < end_y:
                if obj_type in self.object_images:
                    obj_img = self.object_images[obj_type]
                    screen_x = obj_x * self.tile_size - self.camera_x
                    screen_y = obj_y * self.tile_size - self.camera_y - self.tile_size  # Offset for taller objects
                    screen.blit(obj_img, (screen_x, screen_y))

    def move_camera(self, dx, dy):
        """Move the camera by delta amounts."""
        self.camera_x += dx
        self.camera_y += dy

        # Clamp camera to map bounds
        max_x = self.width * self.tile_size - 1280  # Assuming screen width
        max_y = self.height * self.tile_size - 720   # Assuming screen height

        self.camera_x = max(0, min(self.camera_x, max(0, max_x)))
        self.camera_y = max(0, min(self.camera_y, max(0, max_y)))

    def save_map(self, filename):
        """Save the map to a JSON file."""
        data = {
            "width": self.width,
            "height": self.height,
            "terrain": self.terrain_map,
            "objects": self.objects
        }

        with open(filename, 'w') as f:
            json.dump(data, f)

        logger.info(f"Map saved to {filename}")

    def load_map(self, filename):
        """Load a map from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        self.width = data["width"]
        self.height = data["height"]
        self.terrain_map = data["terrain"]
        self.objects = [tuple(obj) for obj in data["objects"]]

        logger.info(f"Map loaded from {filename}")
