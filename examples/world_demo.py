"""
Demo/Test for the new tiered world generation system.
Shows how the World → Region → Local generation works.
"""

import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.world.world_generator_advanced import TieredWorldGenerator
from src.world.cozy_renderer import CozyRenderer
from src.world.biomes import BiomeType
from src.core.logger import logger


class WorldGenerationDemo:
    """Interactive demo of the tiered world generation system."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("My Kingdom - World Generation Demo")

        self.clock = pygame.time.Clock()
        self.running = True

        # Generation system
        self.generator = TieredWorldGenerator(seed=12345)
        self.renderer = CozyRenderer(tile_size=32)

        # Current view state
        self.view_level = "world"  # "world", "region", or "local"

        # Generated data
        self.world_tiles = None
        self.region_tiles = None
        self.local_tiles = None

        # Selected tiles
        self.selected_world_tile = None
        self.selected_region_chunk = None

        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 10

        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        logger.info("World Generation Demo initialized")

    def run(self):
        """Main demo loop."""
        # Generate world on start
        self.generate_world()

        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Go back up a level
                    if self.view_level == "local":
                        self.view_level = "region"
                    elif self.view_level == "region":
                        self.view_level = "world"
                    elif self.view_level == "world":
                        self.running = False

                elif event.key == pygame.K_r:
                    # Regenerate current level
                    if self.view_level == "world":
                        self.generate_world()
                    elif self.view_level == "region" and self.selected_world_tile:
                        self.generate_region()
                    elif self.view_level == "local" and self.region_tiles:
                        self.generate_local()

                elif event.key == pygame.K_SPACE:
                    # Auto-generate down to local level for testing
                    self.auto_generate_to_local()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_tile_click(event.pos)

        # Handle continuous camera movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera_x -= self.camera_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x += self.camera_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera_y -= self.camera_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y += self.camera_speed

        # Clamp camera
        self.camera_x = max(0, self.camera_x)
        self.camera_y = max(0, self.camera_y)

    def handle_tile_click(self, pos):
        """Handle clicking on a tile to drill down."""
        mouse_x, mouse_y = pos

        if self.view_level == "world" and self.world_tiles:
            # Click on world tile to see region
            tile_x = (mouse_x + self.camera_x) // self.renderer.tile_size
            tile_y = (mouse_y + self.camera_y) // self.renderer.tile_size

            if 0 <= tile_y < len(self.world_tiles) and 0 <= tile_x < len(self.world_tiles[0]):
                self.selected_world_tile = self.world_tiles[tile_y][tile_x]
                self.generate_region()
                self.view_level = "region"
                self.camera_x = 0
                self.camera_y = 0

        elif self.view_level == "region" and self.region_tiles:
            # Click on region to see local map
            tile_x = (mouse_x + self.camera_x) // self.renderer.tile_size
            tile_y = (mouse_y + self.camera_y) // self.renderer.tile_size

            # Store chunk position (we'll use 3x3 around click)
            self.selected_region_chunk = (tile_x, tile_y)
            self.generate_local()
            self.view_level = "local"
            self.camera_x = 0
            self.camera_y = 0

    def generate_world(self):
        """Generate Tier 1: World map."""
        logger.info("=== GENERATING WORLD MAP ===")
        self.world_tiles = self.generator.generate_world_map(width=100, height=100)
        self.camera_x = 0
        self.camera_y = 0
        logger.info("World map generation complete!")

    def generate_region(self):
        """Generate Tier 2: Region map from selected world tile."""
        if not self.selected_world_tile:
            logger.error("No world tile selected!")
            return

        logger.info("=== GENERATING REGION MAP ===")
        self.region_tiles = self.generator.generate_region_from_world_tile(
            self.selected_world_tile,
            region_width=50,
            region_height=50
        )
        # Set renderer biome
        self.renderer.set_biome(self.selected_world_tile.biome)
        logger.info("Region map generation complete!")

    def generate_local(self):
        """Generate Tier 3: Local playable map from region chunk."""
        if not self.region_tiles or not self.selected_region_chunk:
            logger.error("No region or chunk selected!")
            return

        chunk_x, chunk_y = self.selected_region_chunk

        logger.info("=== GENERATING LOCAL MAP ===")
        self.local_tiles = self.generator.generate_local_map(
            self.region_tiles,
            chunk_x=chunk_x,
            chunk_y=chunk_y,
            chunk_width=3,
            chunk_height=3,
            local_width=60,
            local_height=60
        )
        logger.info("Local map generation complete!")

    def auto_generate_to_local(self):
        """Auto-generate all the way to local level for quick testing."""
        logger.info("=== AUTO-GENERATING TO LOCAL LEVEL ===")

        # Generate world if not exists
        if not self.world_tiles:
            self.generate_world()

        # Select center world tile
        world_height = len(self.world_tiles)
        world_width = len(self.world_tiles[0])
        self.selected_world_tile = self.world_tiles[world_height // 2][world_width // 2]

        # Generate region
        self.generate_region()

        # Select center of region
        self.selected_region_chunk = (25, 25)

        # Generate local
        self.generate_local()

        # Switch to local view
        self.view_level = "local"
        self.camera_x = 0
        self.camera_y = 0

        logger.info("=== AUTO-GENERATION COMPLETE ===")

    def update(self):
        """Update game state."""
        pass

    def render(self):
        """Render current view."""
        self.screen.fill((15, 20, 25))  # Dark background

        if self.view_level == "world" and self.world_tiles:
            self.render_world_map()

        elif self.view_level == "region" and self.region_tiles:
            self.render_region_map()

        elif self.view_level == "local" and self.local_tiles:
            self.render_local_map()

        # UI overlay
        self.render_ui()

        pygame.display.flip()

    def render_world_map(self):
        """Render the world map (Tier 1)."""
        # Render world tiles with color-coded biomes
        height = len(self.world_tiles)
        width = len(self.world_tiles[0])

        tile_size = self.renderer.tile_size

        start_x = max(0, self.camera_x // tile_size)
        start_y = max(0, self.camera_y // tile_size)
        end_x = min(width, (self.camera_x + 1280) // tile_size + 1)
        end_y = min(height, (self.camera_y + 720) // tile_size + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                world_tile = self.world_tiles[y][x]

                screen_x = x * tile_size - self.camera_x
                screen_y = y * tile_size - self.camera_y

                # Color based on biome
                from src.world.biomes import get_biome_properties
                props = get_biome_properties(world_tile.biome)
                color = props.base_grass_color

                # Draw tile
                rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
                pygame.draw.rect(self.screen, color, rect)

                # Border
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

    def render_region_map(self):
        """Render the region map (Tier 2)."""
        # Convert region tiles to regular tiles for rendering
        from src.world.terrain import Tile

        display_tiles = []
        for row in self.region_tiles:
            display_row = []
            for region_tile in row:
                tile = Tile(region_tile.x, region_tile.y, region_tile.terrain_type)
                display_row.append(tile)
            display_tiles.append(display_row)

        # Use cozy renderer
        self.renderer.render_tile_batch(
            self.screen,
            display_tiles,
            self.camera_x,
            self.camera_y,
            1280,
            720,
            self.selected_world_tile.biome if self.selected_world_tile else None
        )

    def render_local_map(self):
        """Render the local playable map (Tier 3)."""
        # Use cozy renderer with full details
        self.renderer.render_tile_batch(
            self.screen,
            self.local_tiles,
            self.camera_x,
            self.camera_y,
            1280,
            720,
            self.selected_world_tile.biome if self.selected_world_tile else None
        )

        # Optional: Draw minimap
        if self.local_tiles:
            self.renderer.render_minimap(
                self.screen,
                self.local_tiles,
                minimap_x=1280 - 210,
                minimap_y=10,
                minimap_width=200,
                minimap_height=200,
                camera_x=self.camera_x,
                camera_y=self.camera_y,
                screen_width=1280,
                screen_height=720
            )

    def render_ui(self):
        """Render UI overlay with information."""
        # Title showing current level
        if self.view_level == "world":
            title = "TIER 1: WORLD MAP (Click a tile to see region)"
            color = (100, 200, 255)
        elif self.view_level == "region":
            title = "TIER 2: REGION MAP (Click to see local map)"
            color = (100, 255, 150)
        elif self.view_level == "local":
            title = "TIER 3: LOCAL MAP (Playable area)"
            color = (255, 200, 100)
        else:
            title = "UNKNOWN"
            color = (255, 255, 255)

        title_surf = self.font.render(title, True, color)
        title_rect = title_surf.get_rect(centerx=640, top=10)

        # Dark background for title
        bg_rect = title_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (20, 20, 30), bg_rect)
        pygame.draw.rect(self.screen, color, bg_rect, 2)

        self.screen.blit(title_surf, title_rect)

        # Info panel
        info_y = 50
        info_lines = []

        if self.view_level == "world":
            info_lines.append("World seed: " + str(self.generator.seed))
            info_lines.append("World size: 100x100 tiles")
            if self.world_tiles:
                info_lines.append(f"Tiles generated: {len(self.world_tiles) * len(self.world_tiles[0])}")

        elif self.view_level == "region" and self.selected_world_tile:
            info_lines.append(f"Biome: {self.selected_world_tile.biome.value}")
            info_lines.append(f"Temperature: {self.selected_world_tile.temperature:.2f}")
            info_lines.append(f"Rainfall: {self.selected_world_tile.rainfall:.2f}")
            info_lines.append(f"Elevation: {self.selected_world_tile.elevation:.2f}")

        elif self.view_level == "local" and self.local_tiles:
            info_lines.append(f"Local map size: {len(self.local_tiles[0])}x{len(self.local_tiles)}")
            if self.selected_world_tile:
                info_lines.append(f"Biome: {self.selected_world_tile.biome.value}")

        # Render info
        for i, line in enumerate(info_lines):
            text_surf = self.small_font.render(line, True, (200, 220, 255))
            self.screen.blit(text_surf, (10, info_y + i * 20))

        # Controls at bottom
        controls = [
            "SPACE: Auto-generate to local map",
            "CLICK: Drill down to next level",
            "ESC: Go back up a level",
            "R: Regenerate current level",
            "WASD/Arrows: Move camera"
        ]

        controls_y = 720 - 20 - len(controls) * 18
        for i, control in enumerate(controls):
            text_surf = self.small_font.render(control, True, (150, 150, 170))
            self.screen.blit(text_surf, (10, controls_y + i * 18))


if __name__ == "__main__":
    try:
        demo = WorldGenerationDemo()
        demo.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        pygame.quit()
        sys.exit(1)
