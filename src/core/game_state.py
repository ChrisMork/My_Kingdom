"""
Complete game state manager for My Kingdom.
Integrates world generation, citizens, buildings, resources, and save/load.
"""

import pygame
import random
from typing import List, Optional, Dict, Tuple
from pathlib import Path

from src.world.world_generator_advanced import TieredWorldGenerator
from src.world.cozy_renderer import CozyRenderer
from src.world.biomes import BiomeType
from src.world.terrain import Tile, TerrainType
from src.entities.citizen import Citizen, generate_citizen_name
from src.entities.building import Building, BuildingType, BuildingState, BUILDING_DEFINITIONS
from src.entities.resource import Resource
from src.systems.job_manager import JobManager
from src.systems.save_system import SaveSystem
from src.core.logger import logger


class GameState:
    """
    Complete game state including world, citizens, buildings, and resources.

    This is the main game logic controller that integrates all systems.
    """

    def __init__(self, tile_size: int = 32):
        # World generation
        self.generator = None  # Created when starting new game
        self.world_seed = None
        self.world_tiles: List[List[WorldTile]] = []
        self.region_tiles = []
        self.local_tiles: List[List[Tile]] = []
        self.current_biome = BiomeType.TEMPERATE_FOREST

        # Rendering
        self.renderer = CozyRenderer(tile_size=tile_size)
        self.tile_size = tile_size

        # Entities
        self.citizens: List[Citizen] = []
        self.buildings: List[Building] = []
        self.resource_nodes: List[Resource] = []  # Resource nodes in the world
        self.next_citizen_id = 1
        self.next_building_id = 1

        # Resources (Songs of Syx / DF approach)
        self.resources: Dict[str, int] = {
            'wood': 100,  # Start with some resources
            'stone': 50,
            'food': 100,
        }

        # Storage capacity system
        self.max_storage_capacity = 500  # Wagon base capacity
        self.storage_capacity_per_warehouse = 2000  # Additional capacity per warehouse

        # Systems
        self.job_manager = JobManager()
        self.save_system = SaveSystem()

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # View system (Songs of Syx approach: World → Region → Local)
        self.current_view = "local"  # "world", "region", or "local"
        self.world_camera_x = 0
        self.world_camera_y = 0
        self.region_camera_x = 0
        self.region_camera_y = 0
        self.local_camera_x = 0
        self.local_camera_y = 0

        # Current region/local position in world
        self.current_region_x = 0  # Which region we're viewing
        self.current_region_y = 0
        self.current_local_x = 0   # Which local area within region
        self.current_local_y = 0

        # UI state
        self.selected_building_type: Optional[BuildingType] = None
        self.is_placing_building = False
        self.placement_preview_x = 0
        self.placement_preview_y = 0

        # Game time
        self.game_time = 0.0  # In seconds
        self.paused = False
        self.game_speed = 1.0  # 1.0 = normal, 2.0 = 2x, etc.

        # Current save name
        self.current_save_name: Optional[str] = None

        logger.info("Game state initialized")

    def new_game(self, save_name: str, seed: Optional[int] = None, selected_tile_coords: Optional[Tuple[int, int]] = None, region_coords: Optional[Tuple[int, int]] = None):
        """
        Start a new game.

        Args:
            save_name: Name for this campaign
            seed: World generation seed (None for random)
            selected_tile_coords: Optional (x, y) coordinates of selected world tile
            region_coords: Optional (x, y) coordinates of selected region tile
        """
        logger.info(f"=== STARTING NEW GAME: {save_name} ===")

        self.current_save_name = save_name

        # Use pre-generated world/generator from selection screen if available
        if hasattr(self, '_preview_region_tiles') and self._preview_region_tiles is not None:
            logger.info("Using pre-generated world and tiles from selection screen")
            # World, generator, and seed already set by _show_world_selection
        else:
            # Generate world (fallback if no preview available)
            self.world_seed = seed if seed is not None else random.randint(0, 999999)
            self.generator = TieredWorldGenerator(seed=self.world_seed)

            logger.info("Generating large world map...")
            self.world_tiles = self.generator.generate_world_map(width=150, height=150)

        # Select starting location
        if selected_tile_coords:
            # Use player-selected coordinates
            logger.info(f"Using player-selected location: {selected_tile_coords}")
            start_tile = self.world_tiles[selected_tile_coords[1]][selected_tile_coords[0]]
        else:
            # Auto-select a good location (fallback)
            logger.info("Auto-selecting starting location...")
            start_tile = self._find_good_starting_location()

        self.current_biome = start_tile.biome

        # Store which world tile we're at (for showing position on world map)
        self.current_region_x = start_tile.x
        self.current_region_y = start_tile.y

        # Use pre-generated region tiles if available
        if hasattr(self, '_preview_region_tiles') and self._preview_region_tiles is not None:
            logger.info("Using pre-generated region tiles from preview")
            self.region_tiles = self._preview_region_tiles
        else:
            # Generate region around starting location (fallback)
            logger.info(f"Generating starting region (biome: {start_tile.biome.value})...")
            self.region_tiles = self.generator.generate_region_from_world_tile(
                start_tile,
                region_width=80,  # Larger region
                region_height=80
            )

        # Store which chunk within the region we're at (from selection or default to center)
        if region_coords:
            self.current_local_x = region_coords[0]
            self.current_local_y = region_coords[1]
            logger.info(f"Using selected region coordinates: ({region_coords[0]}, {region_coords[1]})")
        else:
            self.current_local_x = 40  # Center of region
            self.current_local_y = 40

        # Use pre-generated local tiles if available
        if hasattr(self, '_preview_local_tiles') and self._preview_local_tiles is not None:
            logger.info("Using pre-generated local tiles from preview - terrain will match preview!")
            self.local_tiles = self._preview_local_tiles
            # Clean up preview data
            delattr(self, '_preview_region_tiles')
            delattr(self, '_preview_local_tiles')
        else:
            # Generate local playable map (fallback)
            logger.info("Generating local playable map...")
            self.local_tiles = self.generator.generate_local_map(
                self.region_tiles,
                chunk_x=self.current_local_x,
                chunk_y=self.current_local_y,
                chunk_width=3,
                chunk_height=3,
                local_width=100,  # Larger playable area
                local_height=100
            )

        # Set up renderer
        self.renderer.set_biome(self.current_biome)

        # Create starting citizens (RimWorld starts with 3, let's start with 5)
        logger.info("Creating starting citizens...")
        self._create_starting_citizens(count=5)

        # Collect resource nodes from tiles
        logger.info("Collecting resource nodes from world...")
        self._collect_resource_nodes()

        # Spawn starting wagon stockpile
        logger.info("Spawning wagon stockpile...")
        self._spawn_starting_wagon()

        # Center camera on settlement in local view
        self.local_camera_x = (len(self.local_tiles[0]) * self.tile_size) // 2 - 640
        self.local_camera_y = (len(self.local_tiles) * self.tile_size) // 2 - 360
        self.camera_x = self.local_camera_x
        self.camera_y = self.local_camera_y

        # Center world camera on our starting world tile (world view uses 8x8 tiles)
        WORLD_TILE_SIZE = 8
        self.world_camera_x = (self.current_region_x * WORLD_TILE_SIZE) - 640 + (WORLD_TILE_SIZE // 2)
        self.world_camera_y = (self.current_region_y * WORLD_TILE_SIZE) - 360 + (WORLD_TILE_SIZE // 2)

        # Center region camera on our local area within the region
        self.region_camera_x = (self.current_local_x * self.tile_size) - 640 + (self.tile_size // 2)
        self.region_camera_y = (self.current_local_y * self.tile_size) - 360 + (self.tile_size // 2)

        # Initial save
        self.save_game()

        logger.info("=== NEW GAME STARTED SUCCESSFULLY ===")

    def _find_good_starting_location(self):
        """Find a good starting location (temperate forest or grassland)."""
        good_biomes = [BiomeType.TEMPERATE_FOREST, BiomeType.GRASSLAND, BiomeType.BOREAL_FOREST]

        # Find all tiles with good biomes
        candidates = [
            tile for row in self.world_tiles for tile in row
            if tile.biome in good_biomes and 0.3 <= tile.elevation <= 0.6
        ]

        if candidates:
            return random.choice(candidates)

        # Fallback: center of map
        return self.world_tiles[75][75]

    def _create_starting_citizens(self, count: int = 5):
        """Create starting citizens."""
        spawn_x = len(self.local_tiles[0]) // 2
        spawn_y = len(self.local_tiles) // 2

        for i in range(count):
            citizen = Citizen(
                id=self.next_citizen_id,
                name=generate_citizen_name(),
                x=spawn_x + random.randint(-3, 3),
                y=spawn_y + random.randint(-3, 3),
            )
            self.citizens.append(citizen)
            self.next_citizen_id += 1

            logger.info(f"Created citizen: {citizen.name} (ID: {citizen.id})")

    def _collect_resource_nodes(self):
        """Collect all resource nodes from tiles into the resource_nodes list."""
        self.resource_nodes = []
        for row in self.local_tiles:
            for tile in row:
                if tile.resource is not None:
                    self.resource_nodes.append(tile.resource)
        logger.info(f"Collected {len(self.resource_nodes)} resource nodes from world")

    def _spawn_starting_wagon(self):
        """Spawn the initial wagon stockpile at the starting location."""
        spawn_x = len(self.local_tiles[0]) // 2
        spawn_y = len(self.local_tiles) // 2

        # Place wagon at spawn location
        wagon = Building(
            id=self.next_building_id,
            building_type=BuildingType.WAGON,
            x=spawn_x,
            y=spawn_y,
        )
        # Wagon is instantly complete and active
        wagon.state = BuildingState.COMPLETE
        wagon.is_active = True
        self.buildings.append(wagon)
        self.next_building_id += 1

        logger.info(f"Spawned wagon stockpile at ({spawn_x}, {spawn_y})")

    def place_building(self, building_type: BuildingType, tile_x: int, tile_y: int) -> bool:
        """
        Place a building at the specified location.
        Buildings can ONLY be placed in local view.

        Args:
            building_type: Type of building to place
            tile_x, tile_y: Top-left corner coordinates

        Returns:
            True if placed successfully
        """
        # IMPORTANT: Only allow building in local view
        if self.current_view != "local":
            logger.warning(f"Cannot place buildings in {self.current_view} view - switch to local view first!")
            return False

        definition = BUILDING_DEFINITIONS[building_type]

        # Check if can place
        if not self._can_place_building(building_type, tile_x, tile_y):
            logger.warning(f"Cannot place {building_type.value} at ({tile_x}, {tile_y})")
            return False

        # Create building
        building = Building(
            id=self.next_building_id,
            building_type=building_type,
            x=tile_x,
            y=tile_y,
        )
        self.buildings.append(building)
        self.next_building_id += 1

        logger.info(f"Placed {building_type.value} at ({tile_x}, {tile_y}), ID: {building.id}")

        # Auto-save after building placement
        if self.current_save_name:
            self.save_system.auto_save(self._serialize_world())
            self.save_system.clean_old_auto_saves()

        return True

    def _can_place_building(self, building_type: BuildingType, tile_x: int, tile_y: int) -> bool:
        """Check if a building can be placed at the location."""
        definition = BUILDING_DEFINITIONS[building_type]

        height = len(self.local_tiles)
        width = len(self.local_tiles[0]) if height > 0 else 0

        # Check bounds
        if (tile_x < 0 or tile_y < 0 or
            tile_x + definition.width > width or
            tile_y + definition.height > height):
            return False

        # Check all tiles
        for dy in range(definition.height):
            for dx in range(definition.width):
                x, y = tile_x + dx, tile_y + dy

                # Check terrain is buildable
                tile = self.local_tiles[y][x]
                if tile.terrain_type not in [TerrainType.GRASS, TerrainType.DIRT, TerrainType.SAND]:
                    return False

                # Check no other building
                for building in self.buildings:
                    if building.occupies_tile(x, y):
                        return False

        return True

    def update(self, delta_time: float):
        """Update game state."""
        from src.core.logger import logger

        if self.paused:
            logger.warning("Game is PAUSED - skipping update")
            return

        # Apply game speed
        delta_time *= self.game_speed

        # Update game time
        self.game_time += delta_time

        # Update job manager (this updates citizens and their work)
        self.job_manager.update(
            self.citizens,
            self.buildings,
            self.local_tiles,
            delta_time,
            self.resources,
            self.resource_nodes,
            storage_capacity_check=self.can_add_resources
        )

        # Auto-save every 5 minutes of game time
        if int(self.game_time) % 300 == 0 and int(self.game_time) > 0:
            if self.current_save_name:
                self.save_system.auto_save(self._serialize_world())
                self.save_system.clean_old_auto_saves()

    def save_game(self) -> bool:
        """
        Save the current game state.

        Returns:
            True if save successful
        """
        if not self.current_save_name:
            logger.error("Cannot save: no save name set")
            return False

        world_data = self._serialize_world()
        success = self.save_system.save_game(self.current_save_name, world_data, compress=True)

        if success:
            logger.info(f"Game saved: {self.current_save_name}")

        return success

    def load_game(self, save_name: str) -> bool:
        """
        Load a saved game.

        Args:
            save_name: Name of save to load

        Returns:
            True if load successful
        """
        world_data = self.save_system.load_game(save_name)

        if world_data is None:
            return False

        self._deserialize_world(world_data)
        self.current_save_name = save_name

        logger.info(f"Game loaded: {save_name}")
        return True

    def _serialize_world(self) -> dict:
        """Serialize complete world state to dictionary."""
        # Serialize local tiles (just terrain types for now)
        tiles_data = [
            [tile.terrain_type.value for tile in row]
            for row in self.local_tiles
        ]

        # Serialize world tiles (for world view)
        world_tiles_data = []
        if self.world_tiles:
            world_tiles_data = [
                [{'biome': tile.biome.value, 'elevation': tile.elevation,
                  'temperature': tile.temperature, 'rainfall': tile.rainfall} for tile in row]
                for row in self.world_tiles
            ]

        # Serialize region tiles (for region view)
        region_tiles_data = []
        if self.region_tiles:
            region_tiles_data = [
                [{'biome': tile.biome.value, 'elevation': tile.elevation} for tile in row]
                for row in self.region_tiles
            ]

        return {
            'world_seed': self.world_seed,
            'current_biome': self.current_biome.value,
            'local_width': len(self.local_tiles[0]) if self.local_tiles else 0,
            'local_height': len(self.local_tiles),
            'tiles': tiles_data,
            'world_tiles': world_tiles_data,
            'region_tiles': region_tiles_data,
            'current_region_x': self.current_region_x,
            'current_region_y': self.current_region_y,
            'current_local_x': self.current_local_x,
            'current_local_y': self.current_local_y,
            'citizens': [c.to_dict() for c in self.citizens],
            'buildings': [b.to_dict() for b in self.buildings],
            'resource_nodes': [r.to_dict() for r in self.resource_nodes],
            'resources': self.resources,
            'camera_x': self.camera_x,
            'camera_y': self.camera_y,
            'current_view': self.current_view,
            'world_camera_x': self.world_camera_x,
            'world_camera_y': self.world_camera_y,
            'region_camera_x': self.region_camera_x,
            'region_camera_y': self.region_camera_y,
            'local_camera_x': self.local_camera_x,
            'local_camera_y': self.local_camera_y,
            'game_time': self.game_time,
            'next_citizen_id': self.next_citizen_id,
            'next_building_id': self.next_building_id,
        }

    def _deserialize_world(self, world_data: dict):
        """Deserialize world state from dictionary."""
        from src.world.terrain import Tile, TerrainType
        from src.world.world_generator_advanced import WorldTile, RegionTile

        # Restore world seed and biome
        self.world_seed = world_data['world_seed']
        self.current_biome = BiomeType(world_data['current_biome'])
        self.renderer.set_biome(self.current_biome)

        # Restore local tiles
        width = world_data['local_width']
        height = world_data['local_height']
        tiles_data = world_data['tiles']

        self.local_tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                terrain_type = TerrainType(tiles_data[y][x])
                tile = Tile(x, y, terrain_type)
                row.append(tile)
            self.local_tiles.append(row)

        # Restore world tiles if they exist
        if 'world_tiles' in world_data and world_data['world_tiles']:
            self.world_tiles = []
            for y, row in enumerate(world_data['world_tiles']):
                world_row = []
                for x, tile_data in enumerate(row):
                    world_tile = WorldTile(
                        x=x,
                        y=y,
                        biome=BiomeType(tile_data['biome']),
                        elevation=tile_data['elevation'],
                        temperature=tile_data.get('temperature', 0.0),  # Default for old saves
                        rainfall=tile_data.get('rainfall', 0.5)  # Default for old saves
                    )
                    world_row.append(world_tile)
                self.world_tiles.append(world_row)
            logger.info(f"Restored world map: {len(self.world_tiles)}x{len(self.world_tiles[0])}")

        # Restore region tiles if they exist
        if 'region_tiles' in world_data and world_data['region_tiles']:
            self.region_tiles = []
            for y, row in enumerate(world_data['region_tiles']):
                region_row = []
                for x, tile_data in enumerate(row):
                    # Handle backward compatibility - old saves may not have moisture and terrain_type
                    moisture = tile_data.get('moisture', 0.5)  # Default to moderate moisture
                    terrain_type = tile_data.get('terrain_type', 'grass')  # Default to grass

                    region_tile = RegionTile(
                        x=x,
                        y=y,
                        biome=BiomeType(tile_data['biome']),
                        elevation=tile_data['elevation'],
                        moisture=moisture,
                        terrain_type=TerrainType(terrain_type) if isinstance(terrain_type, str) else terrain_type
                    )
                    region_row.append(region_tile)
                self.region_tiles.append(region_row)
            logger.info(f"Restored region map: {len(self.region_tiles)}x{len(self.region_tiles[0])}")

        # Restore position data
        if 'current_region_x' in world_data:
            self.current_region_x = world_data['current_region_x']
            self.current_region_y = world_data['current_region_y']
            self.current_local_x = world_data['current_local_x']
            self.current_local_y = world_data['current_local_y']

        # Restore citizens
        self.citizens = [Citizen.from_dict(data) for data in world_data['citizens']]

        # Restore buildings
        self.buildings = [Building.from_dict(data) for data in world_data['buildings']]

        # Restore resource nodes
        if 'resource_nodes' in world_data:
            self.resource_nodes = [Resource.from_dict(data) for data in world_data['resource_nodes']]
        else:
            self.resource_nodes = []

        # Restore resources
        self.resources = world_data['resources']

        # Restore camera positions
        self.camera_x = world_data.get('camera_x', 0)
        self.camera_y = world_data.get('camera_y', 0)

        if 'current_view' in world_data:
            self.current_view = world_data['current_view']
            self.world_camera_x = world_data.get('world_camera_x', 0)
            self.world_camera_y = world_data.get('world_camera_y', 0)
            self.region_camera_x = world_data.get('region_camera_x', 0)
            self.region_camera_y = world_data.get('region_camera_y', 0)
            self.local_camera_x = world_data.get('local_camera_x', 0)
            self.local_camera_y = world_data.get('local_camera_y', 0)

        # Restore game state
        self.game_time = world_data['game_time']
        self.next_citizen_id = world_data['next_citizen_id']
        self.next_building_id = world_data['next_building_id']

        logger.info(f"World state deserialized: {len(self.citizens)} citizens, {len(self.buildings)} buildings")

    def get_total_storage_capacity(self) -> int:
        """
        Calculate total storage capacity based on wagon and warehouses.
        Base wagon provides 200 capacity.
        Each warehouse adds 500 capacity.
        """
        # Base capacity from wagon
        total_capacity = self.max_storage_capacity

        # Add capacity from warehouses
        warehouse_count = sum(
            1 for building in self.buildings
            if building.building_type == BuildingType.WAREHOUSE and building.state == BuildingState.COMPLETE
        )
        total_capacity += warehouse_count * self.storage_capacity_per_warehouse

        return total_capacity

    def get_current_storage_used(self) -> int:
        """Get the total amount of resources currently stored."""
        return sum(self.resources.values())

    def get_storage_remaining(self) -> int:
        """Get the amount of storage space remaining."""
        return self.get_total_storage_capacity() - self.get_current_storage_used()

    def is_storage_full(self) -> bool:
        """Check if storage is full."""
        return self.get_storage_remaining() <= 0

    def can_add_resources(self, amount: int) -> bool:
        """Check if we can add a certain amount of resources to storage."""
        return self.get_storage_remaining() >= amount

    def switch_to_world_view(self):
        """Switch to world map view (150x150)."""
        if self.current_view == "local":
            self.local_camera_x = self.camera_x
            self.local_camera_y = self.camera_y
        elif self.current_view == "region":
            self.region_camera_x = self.camera_x
            self.region_camera_y = self.camera_y

        self.current_view = "world"
        self.camera_x = self.world_camera_x
        self.camera_y = self.world_camera_y
        logger.info("Switched to WORLD view")

    def switch_to_region_view(self):
        """Switch to region view (80x80)."""
        if self.current_view == "world":
            self.world_camera_x = self.camera_x
            self.world_camera_y = self.camera_y
        elif self.current_view == "local":
            self.local_camera_x = self.camera_x
            self.local_camera_y = self.camera_y

        self.current_view = "region"
        self.camera_x = self.region_camera_x
        self.camera_y = self.region_camera_y
        logger.info("Switched to REGION view")

    def switch_to_local_view(self):
        """Switch to local view (100x100) - where building happens."""
        if self.current_view == "world":
            self.world_camera_x = self.camera_x
            self.world_camera_y = self.camera_y
        elif self.current_view == "region":
            self.region_camera_x = self.camera_x
            self.region_camera_y = self.camera_y

        self.current_view = "local"
        self.camera_x = self.local_camera_x
        self.camera_y = self.local_camera_y
        logger.info("Switched to LOCAL view - building enabled")

    def can_build_here(self) -> bool:
        """Check if building is allowed in current view."""
        return self.current_view == "local"
