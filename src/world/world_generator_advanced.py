"""
Advanced tiered world generation system.
Implements lessons from Songs of Syx, RimWorld, and Dwarf Fortress:
- Tiered generation: World → Region → Local (Songs of Syx)
- Biome system with climate (RimWorld)
- Fractal terrain with history (Dwarf Fortress approach)
- Semi-random with constraints (Songs of Syx)
"""

import numpy as np
from opensimplex import OpenSimplex
from dataclasses import dataclass
from typing import Tuple, List, Optional
import random

from src.world.terrain import Tile, TerrainType
from src.world.biomes import BiomeType, get_biome_from_climate, get_biome_properties
from src.core.logger import logger


@dataclass
class WorldTile:
    """A tile on the world map (large scale)."""
    x: int
    y: int
    elevation: float       # 0-1
    temperature: float     # -1 to 1 (cold to hot)
    rainfall: float        # 0-1 (dry to wet)
    biome: BiomeType


@dataclass
class RegionTile:
    """A tile on a region map (medium scale)."""
    x: int
    y: int
    elevation: float
    moisture: float
    biome: BiomeType
    terrain_type: TerrainType


class TieredWorldGenerator:
    """
    Multi-scale world generation system.

    Tier 1: World Map (e.g., 100x100 tiles, each representing a large region)
    Tier 2: Region Map (e.g., 50x50 tiles from one world tile)
    Tier 3: Local Map (detailed playable map from region)
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        random.seed(self.seed)

        # Multiple noise generators with different seeds for variety
        self.elevation_noise = OpenSimplex(seed=self.seed)
        self.temperature_noise = OpenSimplex(seed=self.seed + 1)
        self.rainfall_noise = OpenSimplex(seed=self.seed + 2)
        self.detail_noise = OpenSimplex(seed=self.seed + 3)

        logger.info(f"Tiered World Generator initialized with seed: {self.seed}")

    def generate_world_map(self, width: int = 100, height: int = 100) -> List[List[WorldTile]]:
        """
        Generate a world map (Tier 1).
        This represents the entire game world at a high level.

        Approach inspired by Dwarf Fortress: Fractal terrain + climate simulation
        """
        logger.info(f"Generating world map: {width}x{height}...")

        world_tiles = []

        for y in range(height):
            row = []
            for x in range(width):
                # Multi-octave noise for natural terrain (Dwarf Fortress approach)
                elevation = self._generate_elevation(x, y, width, height)

                # Temperature based on latitude (RimWorld approach)
                # Hotter at equator (middle), colder at poles (edges)
                latitude_factor = abs((y / height) - 0.5) * 2  # 0 at equator, 1 at poles
                base_temp = 1.0 - latitude_factor  # 1 at equator, 0 at poles

                # Add noise for variety
                temp_noise = self.temperature_noise.noise2(x * 0.02, y * 0.02)
                temperature = (base_temp * 0.7 + temp_noise * 0.3) * 2 - 1  # Scale to -1 to 1

                # Elevation affects temperature (higher = colder)
                temperature -= elevation * 0.5

                # Rainfall patterns
                rainfall = self._generate_rainfall(x, y, elevation)

                # Determine biome from climate
                biome = get_biome_from_climate(temperature, rainfall)

                tile = WorldTile(
                    x=x,
                    y=y,
                    elevation=elevation,
                    temperature=temperature,
                    rainfall=rainfall,
                    biome=biome
                )
                row.append(tile)

            world_tiles.append(row)

        self._log_world_stats(world_tiles, width, height)
        return world_tiles

    def generate_region_from_world_tile(
        self,
        world_tile: WorldTile,
        region_width: int = 50,
        region_height: int = 50,
        adjacent_world_tiles: Optional[dict] = None
    ) -> List[List[RegionTile]]:
        """
        Generate a detailed region from a world tile (Tier 2).

        Songs of Syx Approach: Use world tile as 'context' for semi-random generation.
        The region should resemble the world tile while being interesting and playable.

        Args:
            world_tile: The world tile this region is part of
            region_width: Width in tiles
            region_height: Height in tiles
            adjacent_world_tiles: Dict of adjacent tiles {'north': tile, 'south': tile, etc.}
                                 for ensuring continuity at borders
        """
        logger.info(f"Generating region from world tile ({world_tile.x}, {world_tile.y})...")
        logger.info(f"  Biome: {world_tile.biome.value}, Elevation: {world_tile.elevation:.2f}")

        region_tiles = []
        biome_props = get_biome_properties(world_tile.biome)

        # Use world tile position as offset for noise (ensures different regions are unique)
        offset_x = world_tile.x * region_width
        offset_y = world_tile.y * region_height

        for y in range(region_height):
            row = []
            for x in range(region_width):
                # Generate elevation constrained by world tile
                # SONGS OF SYX LESSON: "Semi-random with constraints"
                local_elevation = self._generate_constrained_elevation(
                    x, y, offset_x, offset_y,
                    world_tile.elevation,
                    adjacent_world_tiles
                )

                # Moisture influenced by world rainfall
                local_moisture = self._generate_constrained_moisture(
                    x, y, offset_x, offset_y,
                    world_tile.rainfall
                )

                # Determine terrain type from biome, elevation, and moisture
                terrain_type = self._get_terrain_from_biome(
                    biome_props,
                    local_elevation,
                    local_moisture
                )

                tile = RegionTile(
                    x=x,
                    y=y,
                    elevation=local_elevation,
                    moisture=local_moisture,
                    biome=world_tile.biome,
                    terrain_type=terrain_type
                )
                row.append(tile)

            region_tiles.append(row)

        # Post-processing for playability (Songs of Syx: ensure functionality)
        region_tiles = self._ensure_region_playability(region_tiles, biome_props)

        return region_tiles

    def generate_local_map(
        self,
        region_tiles: List[List[RegionTile]],
        chunk_x: int,
        chunk_y: int,
        chunk_width: int = 3,
        chunk_height: int = 3,
        local_width: int = 60,
        local_height: int = 60
    ) -> List[List[Tile]]:
        """
        Generate detailed local playable map from region (Tier 3).

        Songs of Syx Approach: Use chunk_width x chunk_height region tiles as context.
        "This is harder than pure random but creates better results" - Jake

        Args:
            region_tiles: The region map
            chunk_x, chunk_y: Top-left corner of the chunk in region coordinates
            chunk_width, chunk_height: Size of chunk to reference (typically 3x3)
            local_width, local_height: Size of generated local map
        """
        logger.info(f"Generating local map from region chunk ({chunk_x}, {chunk_y})...")

        # Extract the chunk we're using as reference
        region_height = len(region_tiles)
        region_width = len(region_tiles[0]) if region_height > 0 else 0

        chunk_tiles = []
        for cy in range(chunk_height):
            for cx in range(chunk_width):
                rx = min(chunk_x + cx, region_width - 1)
                ry = min(chunk_y + cy, region_height - 1)
                if 0 <= ry < region_height and 0 <= rx < region_width:
                    chunk_tiles.append(region_tiles[ry][rx])

        if not chunk_tiles:
            logger.error("No valid chunk tiles found!")
            return self._generate_fallback_map(local_width, local_height)

        # Analyze chunk to determine generation constraints
        avg_elevation = sum(t.elevation for t in chunk_tiles) / len(chunk_tiles)
        avg_moisture = sum(t.moisture for t in chunk_tiles) / len(chunk_tiles)
        primary_biome = max(set(t.biome for t in chunk_tiles), key=lambda b: sum(1 for t in chunk_tiles if t.biome == b))
        biome_props = get_biome_properties(primary_biome)

        logger.info(f"  Chunk analysis: Biome={primary_biome.value}, Avg Elev={avg_elevation:.2f}")

        # Generate local map
        local_tiles = []
        offset_x = chunk_x * 1000  # Large offset for unique noise
        offset_y = chunk_y * 1000

        for y in range(local_height):
            row = []
            for x in range(local_width):
                # Fine-detail elevation
                elevation = self._generate_local_elevation(
                    x, y, offset_x, offset_y,
                    avg_elevation
                )

                # Fine-detail moisture
                moisture = self._generate_local_moisture(
                    x, y, offset_x, offset_y,
                    avg_moisture
                )

                # Terrain type
                terrain_type = self._get_terrain_from_biome(
                    biome_props,
                    elevation,
                    moisture
                )

                tile = Tile(x, y, terrain_type)
                row.append(tile)

            local_tiles.append(row)

        # CRITICAL: Songs of Syx lesson - ensure entrance points and functionality
        local_tiles = self._ensure_local_playability(local_tiles, biome_props)

        # Add forests in clusters (from original code)
        local_tiles = self._add_forests(local_tiles, biome_props.tree_density)

        # Smooth transitions
        local_tiles = self._smooth_terrain(local_tiles)

        # Place resource nodes on tiles
        local_tiles = self._place_resource_nodes(local_tiles, biome_props)

        logger.info(f"Local map generated successfully")
        return local_tiles

    def _generate_elevation(self, x: int, y: int, width: int, height: int) -> float:
        """Generate elevation using multiple octaves of noise (Dwarf Fortress approach)."""
        # Multiple octaves for natural-looking terrain
        elevation = (
            self.elevation_noise.noise2(x * 0.02, y * 0.02) * 0.5 +
            self.elevation_noise.noise2(x * 0.04, y * 0.04) * 0.25 +
            self.elevation_noise.noise2(x * 0.08, y * 0.08) * 0.15 +
            self.elevation_noise.noise2(x * 0.16, y * 0.16) * 0.1
        )

        # Normalize to 0-1
        elevation = (elevation + 1) / 2

        # Optional: Island generation (lower at edges)
        # edge_distance = min(x, width - x, y, height - y) / min(width, height) * 2
        # elevation *= edge_distance

        return max(0, min(1, elevation))

    def _generate_rainfall(self, x: int, y: int, elevation: float) -> float:
        """Generate rainfall pattern."""
        rainfall = (
            self.rainfall_noise.noise2(x * 0.03, y * 0.03) * 0.6 +
            self.rainfall_noise.noise2(x * 0.06, y * 0.06) * 0.4
        )

        # Normalize to 0-1
        rainfall = (rainfall + 1) / 2

        # Higher elevations might trap moisture
        if elevation > 0.7:
            rainfall *= 1.2

        return max(0, min(1, rainfall))

    def _generate_constrained_elevation(
        self,
        x: int, y: int,
        offset_x: int, offset_y: int,
        target_elevation: float,
        adjacent_tiles: Optional[dict]
    ) -> float:
        """
        Generate elevation constrained to match world tile.
        Songs of Syx: "Control the randomness to resemble the world-map"
        """
        # Generate base noise
        noise = self.detail_noise.noise2(
            (x + offset_x) * 0.1,
            (y + offset_y) * 0.1
        )

        # Normalize to 0-1
        noise = (noise + 1) / 2

        # Blend with target (70% target, 30% noise for variety)
        elevation = target_elevation * 0.7 + noise * 0.3

        # Add fine detail
        detail = self.detail_noise.noise2(
            (x + offset_x) * 0.5,
            (y + offset_y) * 0.5
        ) * 0.1

        elevation += detail

        return max(0, min(1, elevation))

    def _generate_constrained_moisture(
        self,
        x: int, y: int,
        offset_x: int, offset_y: int,
        target_moisture: float
    ) -> float:
        """Generate moisture constrained to match world rainfall."""
        noise = self.rainfall_noise.noise2(
            (x + offset_x) * 0.12,
            (y + offset_y) * 0.12
        )

        noise = (noise + 1) / 2

        # Blend with target
        moisture = target_moisture * 0.6 + noise * 0.4

        return max(0, min(1, moisture))

    def _generate_local_elevation(
        self,
        x: int, y: int,
        offset_x: int, offset_y: int,
        avg_elevation: float
    ) -> float:
        """Generate fine-detail elevation for local map."""
        noise = (
            self.detail_noise.noise2((x + offset_x) * 0.15, (y + offset_y) * 0.15) * 0.5 +
            self.detail_noise.noise2((x + offset_x) * 0.3, (y + offset_y) * 0.3) * 0.3 +
            self.detail_noise.noise2((x + offset_x) * 0.6, (y + offset_y) * 0.6) * 0.2
        )

        noise = (noise + 1) / 2

        # Blend with average
        elevation = avg_elevation * 0.5 + noise * 0.5

        return max(0, min(1, elevation))

    def _generate_local_moisture(
        self,
        x: int, y: int,
        offset_x: int, offset_y: int,
        avg_moisture: float
    ) -> float:
        """Generate fine-detail moisture for local map."""
        noise = self.rainfall_noise.noise2(
            (x + offset_x) * 0.2,
            (y + offset_y) * 0.2
        )

        noise = (noise + 1) / 2

        moisture = avg_moisture * 0.4 + noise * 0.6

        return max(0, min(1, moisture))

    def _get_terrain_from_biome(
        self,
        biome_props,
        elevation: float,
        moisture: float
    ) -> TerrainType:
        """
        Determine terrain type based on biome properties, elevation, and moisture.
        RimWorld approach: Biome defines the rules, then local variation.
        """
        # Water at low elevations
        if elevation < 0.25:
            return TerrainType.WATER

        # Beach/sand transition
        if elevation < 0.30:
            return TerrainType.SAND

        # High elevation = stone/mountains (rare, only on high peaks)
        if elevation > 0.75:
            return TerrainType.STONE

        # Medium-high elevation = dirt/rocky ground
        if elevation > 0.65:
            return TerrainType.DIRT

        # Normal elevation - use biome properties
        # Forest if high moisture and biome supports it
        if moisture > 0.6 and random.random() < biome_props.tree_density:
            return TerrainType.FOREST

        # Default to grass (biome color will be applied during rendering)
        return TerrainType.GRASS

    def _ensure_region_playability(self, region_tiles: List[List[RegionTile]], biome_props) -> List[List[RegionTile]]:
        """
        Ensure the region is playable.
        Songs of Syx: "Entrance points and other things cannot be blocked"
        """
        # Ensure at least some buildable land
        buildable_count = sum(
            1 for row in region_tiles for tile in row
            if tile.terrain_type in [TerrainType.GRASS, TerrainType.DIRT]
        )

        total_tiles = len(region_tiles) * len(region_tiles[0])

        # If less than 30% buildable, adjust
        if buildable_count < total_tiles * 0.3:
            logger.warning("Region has too little buildable land, adjusting...")

            for row in region_tiles:
                for tile in row:
                    if tile.terrain_type == TerrainType.STONE and random.random() < 0.5:
                        tile.terrain_type = TerrainType.DIRT
                    elif tile.terrain_type == TerrainType.WATER and tile.elevation > 0.22 and random.random() < 0.3:
                        tile.terrain_type = TerrainType.GRASS

        return region_tiles

    def _ensure_local_playability(self, local_tiles: List[List[Tile]], biome_props) -> List[List[Tile]]:
        """
        Ensure the local map is playable.
        Songs of Syx: Ensure entrance points work and resources are accessible.
        """
        height = len(local_tiles)
        width = len(local_tiles[0]) if height > 0 else 0

        # Ensure edges have accessible entrance points (not all water or stone)
        for x in range(width):
            # Top edge
            if local_tiles[0][x].terrain_type == TerrainType.WATER:
                local_tiles[0][x].terrain_type = TerrainType.GRASS

            # Bottom edge
            if local_tiles[height - 1][x].terrain_type == TerrainType.WATER:
                local_tiles[height - 1][x].terrain_type = TerrainType.GRASS

        for y in range(height):
            # Left edge
            if local_tiles[y][0].terrain_type == TerrainType.WATER:
                local_tiles[y][0].terrain_type = TerrainType.GRASS

            # Right edge
            if local_tiles[y][width - 1].terrain_type == TerrainType.WATER:
                local_tiles[y][width - 1].terrain_type = TerrainType.GRASS

        # Ensure at least one large buildable area in center
        center_x, center_y = width // 2, height // 2
        for dy in range(-5, 6):
            for dx in range(-5, 6):
                x, y = center_x + dx, center_y + dy
                if 0 <= x < width and 0 <= y < height:
                    if local_tiles[y][x].terrain_type not in [TerrainType.GRASS, TerrainType.DIRT]:
                        local_tiles[y][x].terrain_type = TerrainType.GRASS

        return local_tiles

    def _add_forests(self, tiles: List[List[Tile]], tree_density: float) -> List[List[Tile]]:
        """Add forest clusters based on biome tree density."""
        if tree_density < 0.05:
            return tiles

        height = len(tiles)
        width = len(tiles[0]) if height > 0 else 0

        num_forests = int(20 * tree_density)

        for _ in range(num_forests):
            center_x = random.randint(0, width - 1)
            center_y = random.randint(0, height - 1)

            if tiles[center_y][center_x].terrain_type == TerrainType.GRASS:
                radius = random.randint(3, max(3, int(8 * tree_density)))

                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        nx, ny = center_x + dx, center_y + dy

                        if 0 <= nx < width and 0 <= ny < height:
                            distance = (dx * dx + dy * dy) ** 0.5
                            if distance <= radius and random.random() > 0.3:
                                if tiles[ny][nx].terrain_type == TerrainType.GRASS:
                                    tiles[ny][nx].terrain_type = TerrainType.FOREST

        return tiles

    def _smooth_terrain(self, tiles: List[List[Tile]]) -> List[List[Tile]]:
        """Smooth terrain transitions."""
        height = len(tiles)
        width = len(tiles[0]) if height > 0 else 0

        original = [[tile.terrain_type for tile in row] for row in tiles]

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if original[y][x] == TerrainType.WATER:
                    neighbors = [
                        original[y - 1][x], original[y + 1][x],
                        original[y][x - 1], original[y][x + 1]
                    ]
                    if all(n != TerrainType.WATER for n in neighbors):
                        tiles[y][x].terrain_type = TerrainType.GRASS

        return tiles

    def _place_resource_nodes(self, tiles: List[List[Tile]], biome_props) -> List[List[Tile]]:
        """
        Place resource nodes on appropriate tiles.
        Trees appear in forest/grass areas, stones near mountains/rocky areas, berry bushes in plains.
        """
        from src.entities.resource import Resource, ResourceType

        height = len(tiles)
        width = len(tiles[0]) if height > 0 else 0

        # Place tree resource nodes on some forest tiles
        for y in range(height):
            for x in range(width):
                tile = tiles[y][x]

                # Trees on forest tiles - ALL forest tiles have gatherable trees
                if tile.terrain_type == TerrainType.FOREST:
                    tile.resource = Resource(
                        resource_type=ResourceType.TREE,
                        x=x,
                        y=y
                    )

                # Stone nodes on grass/dirt tiles (scattered rocks that can be picked up)
                # Sparse - only 3% of grass/dirt tiles get stones
                elif tile.terrain_type in [TerrainType.GRASS, TerrainType.DIRT]:
                    random_value = random.random()
                    if random_value < 0.03:
                        # Stone nodes - gatherable rocks (3%)
                        tile.resource = Resource(
                            resource_type=ResourceType.STONE,
                            x=x,
                            y=y
                        )
                    elif random_value < 0.08:
                        # Berry bushes (5% of grass/dirt tiles)
                        tile.resource = Resource(
                            resource_type=ResourceType.BERRY_BUSH,
                            x=x,
                            y=y
                        )

        logger.info("Placed resource nodes on local map")
        return tiles

    def _generate_fallback_map(self, width: int, height: int) -> List[List[Tile]]:
        """Generate a simple fallback map if chunk is invalid."""
        logger.warning("Generating fallback map...")
        return [[Tile(x, y, TerrainType.GRASS) for x in range(width)] for y in range(height)]

    def _log_world_stats(self, world_tiles: List[List[WorldTile]], width: int, height: int):
        """Log statistics about world generation."""
        biome_counts = {}
        for row in world_tiles:
            for tile in row:
                biome_counts[tile.biome] = biome_counts.get(tile.biome, 0) + 1

        total = width * height
        logger.info("World generation complete!")
        logger.info("Biome distribution:")
        for biome, count in sorted(biome_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            logger.info(f"  {biome.value}: {count} tiles ({percentage:.1f}%)")
