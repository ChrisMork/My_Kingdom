"""
Cozy RimWorld-style renderer for the game.
Implements visual lessons from RimWorld for warm, inviting graphics.
"""

import pygame
import random
from typing import List, Tuple
from src.world.terrain import Tile, TerrainType
from src.world.biomes import BiomeType, get_biome_properties
from src.core.logger import logger


class CozyRenderer:
    """
    Renders the game world with a cozy, RimWorld-inspired aesthetic.

    Features:
    - Soft, pleasant color palettes
    - Subtle tile variation for organic feel
    - Gentle shadows and highlights
    - Atmospheric lighting based on biome
    """

    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size

        # Cache for rendered tiles (for performance)
        self.tile_cache = {}

        # Lighting and atmosphere
        self.time_of_day = 0.5  # 0 = midnight, 0.5 = noon, 1 = midnight
        self.current_biome = BiomeType.TEMPERATE_FOREST

        logger.info(f"Cozy renderer initialized with tile size: {tile_size}")

    def set_biome(self, biome: BiomeType):
        """Set the current biome for atmospheric rendering."""
        self.current_biome = biome
        # Clear cache when biome changes
        self.tile_cache.clear()
        logger.info(f"Renderer biome set to: {biome.value}")

    def set_time_of_day(self, time: float):
        """
        Set time of day for lighting.
        0.0 = midnight, 0.5 = noon, 1.0 = midnight again
        """
        self.time_of_day = time

    def render_tile(
        self,
        surface: pygame.Surface,
        tile: Tile,
        screen_x: int,
        screen_y: int,
        biome: BiomeType = None
    ):
        """
        Render a single tile with cozy aesthetics.

        Args:
            surface: Pygame surface to render to
            tile: The tile to render
            screen_x, screen_y: Screen position
            biome: Optional biome override
        """
        if biome is None:
            biome = self.current_biome

        # Get base color for terrain
        base_color = self._get_terrain_color(tile, biome)

        # Add variation based on tile position (consistent per tile)
        varied_color = self._add_tile_variation(base_color, tile.x, tile.y)

        # Apply lighting
        lit_color = self._apply_lighting(varied_color, biome)

        # Draw base tile
        tile_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
        pygame.draw.rect(surface, lit_color, tile_rect)

        # Add subtle details for visual interest
        self._add_tile_details(surface, tile, screen_x, screen_y, biome)

        # Add border for clarity (very subtle)
        border_color = self._darken_color(lit_color, 0.9)
        pygame.draw.rect(surface, border_color, tile_rect, 1)

    def render_tile_batch(
        self,
        surface: pygame.Surface,
        tiles: List[List[Tile]],
        camera_x: int,
        camera_y: int,
        screen_width: int,
        screen_height: int,
        biome: BiomeType = None
    ):
        """
        Efficiently render a batch of visible tiles.

        Args:
            surface: Pygame surface to render to
            tiles: 2D list of tiles
            camera_x, camera_y: Camera position in pixels
            screen_width, screen_height: Screen dimensions
            biome: Optional biome override
        """
        if not tiles or not tiles[0]:
            return

        height = len(tiles)
        width = len(tiles[0])

        # Calculate visible tile range
        start_x = max(0, int(camera_x // self.tile_size))
        start_y = max(0, int(camera_y // self.tile_size))
        end_x = min(width, int((camera_x + screen_width) // self.tile_size) + 2)
        end_y = min(height, int((camera_y + screen_height) // self.tile_size) + 2)

        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = tiles[y][x]
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y

                self.render_tile(surface, tile, screen_x, screen_y, biome)

    def _get_terrain_color(self, tile: Tile, biome: BiomeType) -> Tuple[int, int, int]:
        """
        Get base color for terrain type with biome influence.
        RimWorld approach: Base terrain + biome tint
        """
        biome_props = get_biome_properties(biome)

        if tile.terrain_type == TerrainType.GRASS:
            # Use biome-specific grass color
            return biome_props.base_grass_color

        elif tile.terrain_type == TerrainType.FOREST:
            # Darker grass for forest floor
            grass = biome_props.base_grass_color
            return self._darken_color(grass, 0.6)

        elif tile.terrain_type == TerrainType.WATER:
            # Nice blue water with depth variation
            depth_factor = 0.8 + (tile.variation * 0.2)
            return (
                int(65 * depth_factor),
                int(105 * depth_factor),
                int(225 * depth_factor)
            )

        elif tile.terrain_type == TerrainType.SAND:
            # Warm sandy color
            return (238, 214, 175)

        elif tile.terrain_type == TerrainType.DIRT:
            # Rich brown dirt
            return (139, 90, 60)

        elif tile.terrain_type == TerrainType.STONE:
            # Gray stone with variation
            base = 120 + tile.variation * 15
            return (base, base, base + 5)

        return (200, 200, 200)  # Fallback

    def _add_tile_variation(
        self,
        base_color: Tuple[int, int, int],
        x: int,
        y: int
    ) -> Tuple[int, int, int]:
        """
        Add subtle color variation to tiles for organic feel.
        Uses tile position as seed for consistency.
        """
        # Deterministic variation based on position
        random.seed(x * 7 + y * 13)

        variation = random.randint(-8, 8)

        varied = tuple(
            max(0, min(255, c + variation))
            for c in base_color
        )

        return varied

    def _apply_lighting(
        self,
        color: Tuple[int, int, int],
        biome: BiomeType
    ) -> Tuple[int, int, int]:
        """
        Apply atmospheric lighting based on time of day and biome.
        RimWorld approach: Subtle ambient tints for atmosphere
        """
        biome_props = get_biome_properties(biome)

        # Get biome ambient color
        ambient = biome_props.ambient_color

        # Blend base color with ambient (subtle)
        blend_factor = 0.1  # 10% ambient influence

        lit_color = tuple(
            int(c * (1 - blend_factor) + a * blend_factor)
            for c, a in zip(color, ambient)
        )

        # Time of day affects brightness (subtle)
        # 0.0 (midnight) = darker, 0.5 (noon) = normal, 1.0 (midnight) = darker
        brightness = 1.0 - abs(self.time_of_day - 0.5) * 0.3  # Max 15% darker at night

        lit_color = tuple(int(c * brightness) for c in lit_color)

        return tuple(max(0, min(255, c)) for c in lit_color)

    def _add_tile_details(
        self,
        surface: pygame.Surface,
        tile: Tile,
        screen_x: int,
        screen_y: int,
        biome: BiomeType
    ):
        """
        Add small details to tiles for visual interest.
        RimWorld approach: Small decorative elements
        """
        # Use tile position for deterministic details
        random.seed(tile.x * 11 + tile.y * 17)

        # Grass: Add small flower/grass tufts or berry bushes
        if tile.terrain_type == TerrainType.GRASS:
            # Check if this tile has a resource node
            if tile.resource and hasattr(tile.resource, 'resource_type'):
                from src.entities.resource import ResourceType
                if tile.resource.resource_type == ResourceType.BERRY_BUSH and not tile.resource.is_depleted:
                    self._draw_berry_bush(surface, screen_x, screen_y, biome)
                elif tile.resource.resource_type == ResourceType.STONE and not tile.resource.is_depleted:
                    self._draw_stone_node(surface, screen_x, screen_y)
            elif random.random() < 0.15:  # 15% chance for grass tufts
                self._draw_grass_tuft(surface, screen_x, screen_y, biome)

        # Dirt: Can have stone nodes or berry bushes
        elif tile.terrain_type == TerrainType.DIRT:
            if tile.resource and hasattr(tile.resource, 'resource_type'):
                from src.entities.resource import ResourceType
                if tile.resource.resource_type == ResourceType.STONE and not tile.resource.is_depleted:
                    self._draw_stone_node(surface, screen_x, screen_y)
                elif tile.resource.resource_type == ResourceType.BERRY_BUSH and not tile.resource.is_depleted:
                    self._draw_berry_bush(surface, screen_x, screen_y, biome)

        # Forest: Add tree (only if not depleted)
        elif tile.terrain_type == TerrainType.FOREST:
            # Don't draw tree if the resource has been depleted
            if tile.resource is None or not tile.resource.is_depleted:
                self._draw_simple_tree(surface, screen_x, screen_y, biome)

        # Stone: Add stone node (only if not depleted)
        elif tile.terrain_type == TerrainType.STONE:
            # Don't draw stone if the resource has been depleted
            if tile.resource is None or not tile.resource.is_depleted:
                self._draw_stone_node(surface, screen_x, screen_y)

    def _draw_grass_tuft(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        biome: BiomeType
    ):
        """Draw a small grass tuft or flower."""
        biome_props = get_biome_properties(biome)
        grass_color = self._lighten_color(biome_props.base_grass_color, 1.2)

        # Small grass tuft
        offset_x = random.randint(5, self.tile_size - 8)
        offset_y = random.randint(5, self.tile_size - 8)

        pygame.draw.circle(
            surface,
            grass_color,
            (x + offset_x, y + offset_y),
            2
        )

        # Sometimes add a tiny flower
        if random.random() < 0.3:
            flower_colors = [
                (255, 200, 220),  # Pink
                (255, 255, 180),  # Yellow
                (200, 180, 255),  # Purple
            ]
            flower_color = random.choice(flower_colors)
            pygame.draw.circle(
                surface,
                flower_color,
                (x + offset_x + 1, y + offset_y - 2),
                1
            )

    def _draw_simple_tree(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        biome: BiomeType
    ):
        """Draw a simple, cozy tree."""
        # Tree trunk (brown)
        trunk_color = (101, 67, 33)
        trunk_width = 4
        trunk_height = 8
        trunk_x = x + self.tile_size // 2 - trunk_width // 2
        trunk_y = y + self.tile_size // 2

        pygame.draw.rect(
            surface,
            trunk_color,
            (trunk_x, trunk_y, trunk_width, trunk_height)
        )

        # Tree canopy (dark green circle)
        canopy_color = (45, 106, 79)
        canopy_radius = 8
        canopy_center = (x + self.tile_size // 2, y + self.tile_size // 2 - 2)

        pygame.draw.circle(
            surface,
            canopy_color,
            canopy_center,
            canopy_radius
        )

        # Highlight on canopy (lighter green)
        highlight_color = (60, 140, 100)
        pygame.draw.circle(
            surface,
            highlight_color,
            (canopy_center[0] - 2, canopy_center[1] - 2),
            4
        )

    def _draw_berry_bush(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        biome: BiomeType
    ):
        """Draw a berry bush."""
        # Bush foliage (dark green blob)
        bush_color = (60, 120, 70)
        center_x = x + self.tile_size // 2
        center_y = y + self.tile_size // 2 + 2

        # Main bush body (rounded)
        pygame.draw.circle(surface, bush_color, (center_x, center_y), 7)
        pygame.draw.circle(surface, bush_color, (center_x - 4, center_y + 2), 5)
        pygame.draw.circle(surface, bush_color, (center_x + 4, center_y + 2), 5)

        # Add some berries (red dots)
        berry_color = (200, 40, 60)
        berry_positions = [
            (center_x - 3, center_y - 2),
            (center_x + 2, center_y - 1),
            (center_x - 1, center_y + 3),
            (center_x + 4, center_y + 1)
        ]
        for berry_x, berry_y in berry_positions:
            pygame.draw.circle(surface, berry_color, (berry_x, berry_y), 2)

    def _draw_stone_node(
        self,
        surface: pygame.Surface,
        x: int,
        y: int
    ):
        """Draw a stone resource node (larger rock)."""
        # Large gray rock
        rock_color = (110, 110, 115)
        center_x = x + self.tile_size // 2
        center_y = y + self.tile_size // 2

        # Main rock body (irregular shape using multiple circles)
        pygame.draw.circle(surface, rock_color, (center_x, center_y), 9)
        pygame.draw.circle(surface, rock_color, (center_x - 5, center_y + 2), 6)
        pygame.draw.circle(surface, rock_color, (center_x + 4, center_y - 1), 7)

        # Highlights (lighter gray)
        highlight_color = (140, 140, 145)
        pygame.draw.circle(surface, highlight_color, (center_x - 2, center_y - 3), 3)

        # Shadows (darker gray)
        shadow_color = (80, 80, 85)
        pygame.draw.circle(surface, shadow_color, (center_x + 3, center_y + 4), 2)

    def _draw_stone_detail(
        self,
        surface: pygame.Surface,
        x: int,
        y: int
    ):
        """Draw stone texture details."""
        # Small darker spots for rock texture
        dark_gray = (90, 90, 95)

        offset_x = random.randint(4, self.tile_size - 6)
        offset_y = random.randint(4, self.tile_size - 6)

        pygame.draw.circle(
            surface,
            dark_gray,
            (x + offset_x, y + offset_y),
            2
        )

    def _lighten_color(
        self,
        color: Tuple[int, int, int],
        factor: float
    ) -> Tuple[int, int, int]:
        """Lighten a color by a factor."""
        return tuple(min(255, int(c * factor)) for c in color)

    def _darken_color(
        self,
        color: Tuple[int, int, int],
        factor: float
    ) -> Tuple[int, int, int]:
        """Darken a color by a factor."""
        return tuple(max(0, int(c * factor)) for c in color)

    def render_minimap(
        self,
        surface: pygame.Surface,
        tiles: List[List[Tile]],
        minimap_x: int,
        minimap_y: int,
        minimap_width: int,
        minimap_height: int,
        camera_x: int,
        camera_y: int,
        screen_width: int,
        screen_height: int,
        biome: BiomeType = None
    ):
        """
        Render a minimap of the world.
        RimWorld-style: Small overview showing terrain and player position.
        """
        if not tiles or not tiles[0]:
            return

        world_height = len(tiles)
        world_width = len(tiles[0])

        # Scale factors
        scale_x = minimap_width / world_width
        scale_y = minimap_height / world_height

        # Draw background
        pygame.draw.rect(
            surface,
            (20, 20, 25),  # Dark background
            (minimap_x, minimap_y, minimap_width, minimap_height)
        )

        # Draw terrain (simplified)
        for y in range(world_height):
            for x in range(world_width):
                tile = tiles[y][x]
                color = self._get_minimap_color(tile)

                pixel_x = int(minimap_x + x * scale_x)
                pixel_y = int(minimap_y + y * scale_y)
                pixel_w = max(1, int(scale_x))
                pixel_h = max(1, int(scale_y))

                pygame.draw.rect(
                    surface,
                    color,
                    (pixel_x, pixel_y, pixel_w, pixel_h)
                )

        # Draw camera viewport rectangle
        viewport_x = int(minimap_x + (camera_x / self.tile_size) * scale_x)
        viewport_y = int(minimap_y + (camera_y / self.tile_size) * scale_y)
        viewport_w = int((screen_width / self.tile_size) * scale_x)
        viewport_h = int((screen_height / self.tile_size) * scale_y)

        pygame.draw.rect(
            surface,
            (255, 255, 255),  # White rectangle
            (viewport_x, viewport_y, viewport_w, viewport_h),
            2  # Border thickness
        )

        # Border around minimap
        pygame.draw.rect(
            surface,
            (100, 100, 110),
            (minimap_x, minimap_y, minimap_width, minimap_height),
            2
        )

    def _get_minimap_color(self, tile: Tile) -> Tuple[int, int, int]:
        """Get simplified color for minimap."""
        if tile.terrain_type == TerrainType.WATER:
            return (50, 80, 180)
        elif tile.terrain_type == TerrainType.FOREST:
            return (40, 90, 40)
        elif tile.terrain_type == TerrainType.GRASS:
            return (80, 150, 80)
        elif tile.terrain_type == TerrainType.SAND:
            return (200, 180, 140)
        elif tile.terrain_type == TerrainType.DIRT:
            return (120, 80, 50)
        elif tile.terrain_type == TerrainType.STONE:
            return (100, 100, 105)
        return (150, 150, 150)
