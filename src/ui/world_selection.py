"""
Multi-stage world selection screen - choose where to start your settlement.
Inspired by Dwarf Fortress's embark screen.

Flow:
1. World View: Select a world tile (150x150)
2. Region View: Preview the region, see terrain detail
3. Local View: Preview the exact starting area
4. Confirm or go back
"""

import pygame
from typing import Optional, Tuple, Dict
from src.world.world_generator_advanced import TieredWorldGenerator, WorldTile
from src.world.biomes import BIOME_DEFINITIONS, BiomeType
from src.core.logger import logger


class WorldSelectionScreen:
    """
    Multi-stage selection screen for choosing starting location.

    Stages:
    - WORLD: Pick a world tile from 150x150 map
    - REGION: Preview the 80x80 region, see terrain
    - LOCAL: Preview the 100x100 local area where building happens
    - Each stage can go forward (ENTER) or back (ESC)
    """

    def __init__(self, screen, generator, world_tiles):
        self.screen = screen
        self.generator = generator
        self.world_tiles = world_tiles

        # Selection stage
        self.stage = "WORLD"  # WORLD → REGION → LOCAL → CONFIRMED

        # World selection
        self.world_selected_x = len(world_tiles[0]) // 2
        self.world_selected_y = len(world_tiles) // 2
        self.world_camera_x = 0
        self.world_camera_y = 0

        # Generated preview data
        self.region_tiles = None
        self.local_tiles = None
        self.region_camera_x = 0
        self.region_camera_y = 0
        self.local_camera_x = 0
        self.local_camera_y = 0

        # Region selection cursor
        self.region_selected_x = 40  # Center of 80x80 region
        self.region_selected_y = 40

        # Local selection cursor (not used for now, but could be)
        self.local_selected_x = 50
        self.local_selected_y = 50

        # UI
        self.title_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        self.running = True
        self.confirmed = False

        logger.info("Multi-stage world selection screen initialized")

    def handle_events(self):
        """Handle input based on current stage."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.confirmed = False
                return

            elif event.type == pygame.KEYDOWN:
                # TAB to quickly cycle forward through stages
                if event.key == pygame.K_TAB:
                    if self.stage == "WORLD":
                        self._generate_region_preview()
                        self.stage = "REGION"
                        logger.info("TAB: Advanced to REGION view")
                    elif self.stage == "REGION":
                        self._generate_local_preview()
                        self.stage = "LOCAL"
                        logger.info("TAB: Advanced to LOCAL view")
                    # Note: TAB doesn't confirm from LOCAL, only ENTER does

                elif event.key == pygame.K_RETURN:
                    # Progress to next stage
                    if self.stage == "WORLD":
                        self._generate_region_preview()
                        self.stage = "REGION"
                        logger.info(f"Advanced to REGION view for world tile ({self.world_selected_x}, {self.world_selected_y})")
                    elif self.stage == "REGION":
                        self._generate_local_preview()
                        self.stage = "LOCAL"
                        logger.info("Advanced to LOCAL view")
                    elif self.stage == "LOCAL":
                        # Final confirmation
                        self.confirmed = True
                        self.running = False
                        logger.info("Location confirmed!")

                elif event.key == pygame.K_ESCAPE:
                    # Go back or cancel
                    if self.stage == "LOCAL":
                        self.stage = "REGION"
                        logger.info("Returned to REGION view")
                    elif self.stage == "REGION":
                        self.stage = "WORLD"
                        logger.info("Returned to WORLD view")
                    else:  # WORLD
                        self.running = False
                        self.confirmed = False
                        logger.info("Selection cancelled")

                # Navigation (arrow keys work in all stages)
                elif event.key == pygame.K_LEFT:
                    if self.stage == "WORLD":
                        self.world_selected_x = max(0, self.world_selected_x - 1)
                    elif self.stage == "REGION" and self.region_tiles:
                        self.region_selected_x = max(0, self.region_selected_x - 1)
                elif event.key == pygame.K_RIGHT:
                    if self.stage == "WORLD":
                        self.world_selected_x = min(len(self.world_tiles[0]) - 1, self.world_selected_x + 1)
                    elif self.stage == "REGION" and self.region_tiles:
                        self.region_selected_x = min(len(self.region_tiles[0]) - 1, self.region_selected_x + 1)
                elif event.key == pygame.K_UP:
                    if self.stage == "WORLD":
                        self.world_selected_y = max(0, self.world_selected_y - 1)
                    elif self.stage == "REGION" and self.region_tiles:
                        self.region_selected_y = max(0, self.region_selected_y - 1)
                elif event.key == pygame.K_DOWN:
                    if self.stage == "WORLD":
                        self.world_selected_y = min(len(self.world_tiles) - 1, self.world_selected_y + 1)
                    elif self.stage == "REGION" and self.region_tiles:
                        self.region_selected_y = min(len(self.region_tiles) - 1, self.region_selected_y + 1)

        # Camera panning with WASD (works in all stages)
        keys = pygame.key.get_pressed()
        camera_speed = 10

        if self.stage == "WORLD":
            if keys[pygame.K_a]:
                self.world_camera_x = max(0, self.world_camera_x - camera_speed)
            if keys[pygame.K_d]:
                max_x = max(0, len(self.world_tiles[0]) * 8 - self.screen.get_width())
                self.world_camera_x = min(max_x, self.world_camera_x + camera_speed)
            if keys[pygame.K_w]:
                self.world_camera_y = max(0, self.world_camera_y - camera_speed)
            if keys[pygame.K_s]:
                max_y = max(0, len(self.world_tiles) * 8 - self.screen.get_height())
                self.world_camera_y = min(max_y, self.world_camera_y + camera_speed)

        elif self.stage == "REGION" and self.region_tiles:
            if keys[pygame.K_a]:
                self.region_camera_x = max(0, self.region_camera_x - camera_speed)
            if keys[pygame.K_d]:
                max_x = max(0, len(self.region_tiles[0]) * 32 - self.screen.get_width())
                self.region_camera_x = min(max_x, self.region_camera_x + camera_speed)
            if keys[pygame.K_w]:
                self.region_camera_y = max(0, self.region_camera_y - camera_speed)
            if keys[pygame.K_s]:
                max_y = max(0, len(self.region_tiles) * 32 - self.screen.get_height())
                self.region_camera_y = min(max_y, self.region_camera_y + camera_speed)

        elif self.stage == "LOCAL" and self.local_tiles:
            if keys[pygame.K_a]:
                self.local_camera_x = max(0, self.local_camera_x - camera_speed)
            if keys[pygame.K_d]:
                max_x = max(0, len(self.local_tiles[0]) * 32 - self.screen.get_width())
                self.local_camera_x = min(max_x, self.local_camera_x + camera_speed)
            if keys[pygame.K_w]:
                self.local_camera_y = max(0, self.local_camera_y - camera_speed)
            if keys[pygame.K_s]:
                max_y = max(0, len(self.local_tiles) * 32 - self.screen.get_height())
                self.local_camera_y = min(max_y, self.local_camera_y + camera_speed)

    def _generate_region_preview(self):
        """Generate region tiles for the selected world tile."""
        world_tile = self.world_tiles[self.world_selected_y][self.world_selected_x]
        logger.info(f"Generating region preview for world tile {world_tile.biome.value}...")

        self.region_tiles = self.generator.generate_region_from_world_tile(
            world_tile,
            region_width=80,
            region_height=80
        )

        # Center camera on region
        self.region_camera_x = (80 * 32) // 2 - self.screen.get_width() // 2
        self.region_camera_y = (80 * 32) // 2 - self.screen.get_height() // 2

    def _generate_local_preview(self):
        """Generate local map preview from selected region tile."""
        if not self.region_tiles:
            return

        logger.info(f"Generating local preview from region tile ({self.region_selected_x}, {self.region_selected_y})...")

        # Use the selected region coordinates
        self.local_tiles = self.generator.generate_local_map(
            self.region_tiles,
            chunk_x=self.region_selected_x,
            chunk_y=self.region_selected_y,
            chunk_width=1,  # Single region tile
            chunk_height=1,
            local_width=100,
            local_height=100
        )

        # Center camera on local
        self.local_camera_x = (100 * 32) // 2 - self.screen.get_width() // 2
        self.local_camera_y = (100 * 32) // 2 - self.screen.get_height() // 2

    def draw(self):
        """Draw current stage."""
        self.screen.fill((20, 20, 30))

        if self.stage == "WORLD":
            self._draw_world_stage()
        elif self.stage == "REGION":
            self._draw_region_stage()
        elif self.stage == "LOCAL":
            self._draw_local_stage()

    def _draw_world_stage(self):
        """Draw world selection (stage 1)."""
        TILE_SIZE = 8  # Small tiles for world view

        # Calculate visible range
        start_x = max(0, int(self.world_camera_x // TILE_SIZE))
        end_x = min(len(self.world_tiles[0]), int((self.world_camera_x + self.screen.get_width()) // TILE_SIZE) + 1)
        start_y = max(0, int(self.world_camera_y // TILE_SIZE))
        end_y = min(len(self.world_tiles), int((self.world_camera_y + self.screen.get_height()) // TILE_SIZE) + 1)

        # Draw world tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.world_tiles[y][x]
                screen_x = int(x * TILE_SIZE - self.world_camera_x)
                screen_y = int(y * TILE_SIZE - self.world_camera_y)

                biome_def = BIOME_DEFINITIONS[tile.biome]
                color = biome_def.base_grass_color

                pygame.draw.rect(self.screen, color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Draw selection cursor
        cursor_x = int(self.world_selected_x * TILE_SIZE - self.world_camera_x)
        cursor_y = int(self.world_selected_y * TILE_SIZE - self.world_camera_y)

        pygame.draw.rect(self.screen, (255, 255, 0),
                       (cursor_x - 2, cursor_y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 2)

        # UI
        self._draw_stage_ui("STAGE 1: SELECT WORLD TILE",
                           "Arrow Keys: Move | WASD: Pan | TAB/ENTER: Next | ESC: Cancel")

    def _draw_region_stage(self):
        """Draw region preview (stage 2)."""
        if not self.region_tiles:
            return

        TILE_SIZE = 32

        # Calculate visible range
        start_x = max(0, int(self.region_camera_x // TILE_SIZE))
        end_x = min(len(self.region_tiles[0]), int((self.region_camera_x + self.screen.get_width()) // TILE_SIZE) + 1)
        start_y = max(0, int(self.region_camera_y // TILE_SIZE))
        end_y = min(len(self.region_tiles), int((self.region_camera_y + self.screen.get_height()) // TILE_SIZE) + 1)

        # Draw region tiles with elevation detail
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.region_tiles[y][x]
                screen_x = int(x * TILE_SIZE - self.region_camera_x)
                screen_y = int(y * TILE_SIZE - self.region_camera_y)

                biome_def = BIOME_DEFINITIONS[tile.biome]
                r, g, b = biome_def.base_grass_color

                # Elevation-based shading
                elevation = tile.elevation
                if elevation > 0.7:
                    r = min(255, int(r * 0.6 + 100))
                    g = min(255, int(g * 0.6 + 100))
                    b = min(255, int(b * 0.6 + 100))
                elif elevation > 0.55:
                    r = int(r * 0.85)
                    g = int(g * 0.85)
                    b = int(b * 0.85)
                elif elevation < 0.35:
                    r = int(r * 0.7)
                    g = int(g * 0.8)
                    b = min(255, int(b * 1.1))

                pygame.draw.rect(self.screen, (r, g, b), (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

        # Draw selection cursor on region
        cursor_x = int(self.region_selected_x * TILE_SIZE - self.region_camera_x)
        cursor_y = int(self.region_selected_y * TILE_SIZE - self.region_camera_y)

        # Yellow selection box
        pygame.draw.rect(self.screen, (255, 255, 0),
                       (cursor_x - 2, cursor_y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 3)
        pygame.draw.rect(self.screen, (255, 200, 0),
                       (cursor_x, cursor_y, TILE_SIZE, TILE_SIZE), 2)

        # UI
        selected_tile = self.world_tiles[self.world_selected_y][self.world_selected_x]
        biome_name = selected_tile.biome.value.replace('_', ' ').title()
        self._draw_stage_ui(f"STAGE 2: REGION PREVIEW - {biome_name}",
                           "Arrow Keys: Move | WASD: Pan | TAB/ENTER: Next | ESC: Back")

    def _draw_local_stage(self):
        """Draw local preview (stage 3) - with actual game rendering."""
        if not self.local_tiles:
            return

        TILE_SIZE = 32

        # Calculate visible range
        start_x = max(0, int(self.local_camera_x // TILE_SIZE))
        end_x = min(len(self.local_tiles[0]), int((self.local_camera_x + self.screen.get_width()) // TILE_SIZE) + 1)
        start_y = max(0, int(self.local_camera_y // TILE_SIZE))
        end_y = min(len(self.local_tiles), int((self.local_camera_y + self.screen.get_height()) // TILE_SIZE) + 1)

        # Use the CozyRenderer to draw tiles exactly as they'll appear in-game
        from src.world.cozy_renderer import CozyRenderer
        from src.world.biomes import BiomeType

        # Create a temporary renderer with the appropriate biome
        # Get biome from the selected world tile
        selected_world_tile = self.world_tiles[self.world_selected_y][self.world_selected_x]
        renderer = CozyRenderer(tile_size=TILE_SIZE)
        renderer.set_biome(selected_world_tile.biome)

        # Draw tiles using the cozy renderer
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.local_tiles[y][x]
                screen_x = int(x * TILE_SIZE - self.local_camera_x)
                screen_y = int(y * TILE_SIZE - self.local_camera_y)

                # Render tile with the actual game renderer
                renderer.render_tile(self.screen, tile, screen_x, screen_y)

        # Draw starting location indicator (center)
        center_x = int(50 * TILE_SIZE - self.local_camera_x)
        center_y = int(50 * TILE_SIZE - self.local_camera_y)

        pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), 20, 3)
        label = self.small_font.render("START", True, (255, 255, 0))
        self.screen.blit(label, (center_x - 20, center_y - 30))

        # UI
        self._draw_stage_ui("STAGE 3: LOCAL PREVIEW - Your Starting Area",
                           "WASD: Pan | ENTER: Confirm | ESC: Back")

    def _draw_stage_ui(self, title, instructions):
        """Draw stage UI overlay."""
        # Top panel
        panel = pygame.Surface((self.screen.get_width(), 100))
        panel.set_alpha(220)
        panel.fill((30, 25, 20))
        self.screen.blit(panel, (0, 0))

        # Title
        title_text = self.title_font.render(title, True, (255, 240, 200))
        self.screen.blit(title_text, (10, 10))

        # Instructions
        inst_text = self.info_font.render(instructions, True, (200, 190, 170))
        self.screen.blit(inst_text, (10, 60))

    def run(self) -> Optional[Dict]:
        """
        Run the selection screen, return selection data if confirmed.

        Returns:
            Dictionary with:
                - 'world_coords': (x, y) of selected world tile
                - 'region_coords': (x, y) of selected region tile
                - 'region_tiles': The generated region tiles
                - 'local_tiles': The generated local tiles
            Or None if cancelled
        """
        clock = pygame.time.Clock()

        # Center camera on selected world tile
        self.world_camera_x = self.world_selected_x * 8 - self.screen.get_width() // 2
        self.world_camera_y = self.world_selected_y * 8 - self.screen.get_height() // 2

        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        if self.confirmed:
            return {
                'world_coords': (self.world_selected_x, self.world_selected_y),
                'region_coords': (self.region_selected_x, self.region_selected_y),
                'region_tiles': self.region_tiles,
                'local_tiles': self.local_tiles
            }
        else:
            return None
