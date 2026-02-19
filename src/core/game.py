"""
Main game state - handles the playing mode with world rendering.
Updated to use the new GameState system with building and gathering.
"""

import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import *
from src.core.logger import logger
from src.core.game_state import GameState
from src.entities.building import BuildingType, BuildingState, BUILDING_DEFINITIONS
from src.audio.music_manager import get_music_manager
from src.systems.designation import DesignationManager, AreaSelector, DesignationType
from src.entities.resource import ResourceType


class Game:
    """Main game state for playing using the new GameState system."""

    def __init__(self, screen, save_name=None, action="new"):
        self.screen = screen
        self.running = True
        self.next_state = None

        # Camera speed
        self.camera_speed = 10

        # Game modes
        self.building_mode = False
        self.selected_building_type = None

        # Designation mode
        self.designation_mode = False
        self.current_designation_type = DesignationType.CHOP_TREES  # Default to trees
        self.designation_manager = DesignationManager()
        self.area_selector = AreaSelector()

        # Font for UI
        pygame.font.init()
        self.ui_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Initialize game state
        logger.info("Initializing new GameState system...")
        self.game_state = GameState(tile_size=TILE_SIZE)

        if action == "new" and save_name:
            # Start new game with world selection
            selection_data = self._show_world_selection()
            if selection_data is None:
                # User cancelled - return to menu
                self.running = False
                self.next_state = STATE_MENU
                return

            self.game_state.new_game(
                save_name=save_name,
                selected_tile_coords=selection_data['world_coords'],
                region_coords=selection_data['region_coords']
            )
        elif action == "load" and save_name:
            # Load existing game
            if not self.game_state.load_game(save_name):
                logger.error(f"Failed to load game: {save_name}")
                # Fallback to new game
                selection_data = self._show_world_selection()
                if selection_data is None:
                    self.running = False
                    self.next_state = STATE_MENU
                    return
                self.game_state.new_game(
                    save_name=save_name,
                    selected_tile_coords=selection_data['world_coords'],
                    region_coords=selection_data['region_coords']
                )
        else:
            # Demo mode (no save name)
            selection_data = self._show_world_selection()
            if selection_data is None:
                self.running = False
                self.next_state = STATE_MENU
                return
            self.game_state.new_game(
                save_name="Demo Game",
                selected_tile_coords=selection_data['world_coords'],
                region_coords=selection_data['region_coords']
            )

        logger.info("Game initialized successfully")

        # Start gameplay music
        music_manager = get_music_manager()
        music_manager.play('gameplay')

    def _show_world_selection(self):
        """
        Show the world selection screen.
        Returns selected (x, y) coordinates or None if cancelled.
        """
        from src.ui.world_selection import WorldSelectionScreen
        from src.world.world_generator_advanced import TieredWorldGenerator
        import random

        # Generate a temporary world for selection
        seed = random.randint(0, 999999)
        generator = TieredWorldGenerator(seed=seed)
        world_tiles = generator.generate_world_map(width=150, height=150)

        # Show multi-stage selection screen (World → Region → Local)
        selection_screen = WorldSelectionScreen(self.screen, generator, world_tiles)
        selection_data = selection_screen.run()

        # Store the seed, world tiles, and generated preview tiles in game_state
        if selection_data:
            self.game_state.world_seed = seed
            self.game_state.world_tiles = world_tiles
            self.game_state.generator = generator
            # Store the pre-generated region and local tiles from preview
            self.game_state._preview_region_tiles = selection_data['region_tiles']
            self.game_state._preview_local_tiles = selection_data['local_tiles']

        return selection_data

    def handle_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received from game")
                self.running = False
                self.next_state = "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.selected_building_type:
                        # Cancel building selection
                        self.selected_building_type = None
                        logger.info("Cancelled building placement")
                    else:
                        # Show pause menu
                        logger.info("Escape pressed - showing pause menu")
                        from src.ui.pause_menu import PauseMenu
                        pause_menu = PauseMenu(self.screen)
                        result = pause_menu.run()

                        if result == "resume":
                            # Continue playing
                            logger.info("Resuming game")
                        elif result == "save":
                            # Save the game
                            self.game_state.save_game()
                            logger.info("Game saved from pause menu")
                        elif result == "main_menu":
                            # Save and return to menu
                            logger.info("Returning to main menu")
                            self.game_state.save_game()
                            # Switch back to menu music
                            music_manager = get_music_manager()
                            music_manager.play('menu')
                            self.running = False
                            self.next_state = STATE_MENU
                        elif result == "quit":
                            # Quit game
                            self.running = False
                            self.next_state = "quit"
                elif event.key == pygame.K_b:
                    # Toggle building mode
                    self.building_mode = not self.building_mode
                    if not self.building_mode:
                        self.selected_building_type = None
                    mode_text = "ON" if self.building_mode else "OFF"
                    logger.info(f"Building mode toggled: {mode_text}")
                elif event.key == pygame.K_d:
                    # Toggle designation mode for TREES (only in local view)
                    if self.game_state.current_view == "local":
                        if not self.designation_mode or self.current_designation_type != DesignationType.CHOP_TREES:
                            self.designation_mode = True
                            self.current_designation_type = DesignationType.CHOP_TREES
                            # Cancel building mode if active
                            self.building_mode = False
                            self.selected_building_type = None
                            logger.info("Designation mode: ON (Chop Trees)")
                        else:
                            self.designation_mode = False
                            self.area_selector.cancel_selection()
                            logger.info("Designation mode: OFF")
                    else:
                        logger.warning("Designation mode only available in local view")
                elif event.key == pygame.K_m:
                    # Toggle designation mode for STONE (Mine) (only in local view)
                    if self.game_state.current_view == "local":
                        if not self.designation_mode or self.current_designation_type != DesignationType.MINE_STONE:
                            self.designation_mode = True
                            self.current_designation_type = DesignationType.MINE_STONE
                            # Cancel building mode if active
                            self.building_mode = False
                            self.selected_building_type = None
                            logger.info("Designation mode: ON (Mine Stone)")
                        else:
                            self.designation_mode = False
                            self.area_selector.cancel_selection()
                            logger.info("Designation mode: OFF")
                    else:
                        logger.warning("Designation mode only available in local view")
                elif event.key == pygame.K_f:
                    # Toggle designation mode for BERRIES (only in local view)
                    if self.game_state.current_view == "local":
                        if not self.designation_mode or self.current_designation_type != DesignationType.GATHER_BERRIES:
                            self.designation_mode = True
                            self.current_designation_type = DesignationType.GATHER_BERRIES
                            # Cancel building mode if active
                            self.building_mode = False
                            self.selected_building_type = None
                            logger.info("Designation mode: ON (Gather Berries)")
                        else:
                            self.designation_mode = False
                            self.area_selector.cancel_selection()
                            logger.info("Designation mode: OFF")
                    else:
                        logger.warning("Designation mode only available in local view")
                elif event.key == pygame.K_SPACE:
                    # Toggle pause
                    self.game_state.paused = not self.game_state.paused
                    logger.info(f"Game {'paused' if self.game_state.paused else 'unpaused'}")
                # View switching (TAB to cycle through views)
                elif event.key == pygame.K_TAB:
                    if self.game_state.current_view == "local":
                        self.game_state.switch_to_region_view()
                    elif self.game_state.current_view == "region":
                        self.game_state.switch_to_world_view()
                    elif self.game_state.current_view == "world":
                        self.game_state.switch_to_local_view()
                # Direct view switching
                elif event.key == pygame.K_F1:
                    self.game_state.switch_to_world_view()
                elif event.key == pygame.K_F2:
                    self.game_state.switch_to_region_view()
                elif event.key == pygame.K_F3:
                    self.game_state.switch_to_local_view()
                # Home key - snap back to settlement location
                elif event.key == pygame.K_h:
                    self._snap_camera_to_home()
                    logger.info(f"Snapped camera to home in {self.game_state.current_view} view")
                # Building selection hotkeys
                elif event.key == pygame.K_1 and self.building_mode:
                    self.selected_building_type = BuildingType.HOUSE
                    logger.info("Selected: House")
                elif event.key == pygame.K_2 and self.building_mode:
                    self.selected_building_type = BuildingType.STORAGE
                    logger.info("Selected: Storage")
                elif event.key == pygame.K_3 and self.building_mode:
                    self.selected_building_type = BuildingType.WORKSHOP
                    logger.info("Selected: Workshop")
                elif event.key == pygame.K_4 and self.building_mode:
                    self.selected_building_type = BuildingType.FARM
                    logger.info("Selected: Farm")
                elif event.key == pygame.K_5 and self.building_mode:
                    self.selected_building_type = BuildingType.MINE
                    logger.info("Selected: Mine")
                elif event.key == pygame.K_6 and self.building_mode:
                    self.selected_building_type = BuildingType.LUMBER_CAMP
                    logger.info("Selected: Lumber Camp")
                elif event.key == pygame.K_7 and self.building_mode:
                    self.selected_building_type = BuildingType.WELL
                    logger.info("Selected: Well")
                elif event.key == pygame.K_8 and self.building_mode:
                    self.selected_building_type = BuildingType.MARKET
                    logger.info("Selected: Market")
                elif event.key == pygame.K_9 and self.building_mode:
                    self.selected_building_type = BuildingType.WAREHOUSE
                    logger.info("Selected: Warehouse")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.designation_mode and self.game_state.current_view == "local":
                        # Start designation selection with current designation type
                        mouse_x, mouse_y = event.pos
                        self.area_selector.start_selection(mouse_x, mouse_y, self.current_designation_type)
                    elif self.building_mode and self.selected_building_type:
                        # Place building at mouse position
                        mouse_x, mouse_y = event.pos
                        # Convert screen position to world tile position
                        world_x = int((mouse_x + self.game_state.camera_x) // TILE_SIZE)
                        world_y = int((mouse_y + self.game_state.camera_y) // TILE_SIZE)

                        # Try to place the building
                        placed = self.game_state.place_building(
                            self.selected_building_type,
                            world_x,
                            world_y
                        )
                        if placed:
                            logger.info(f"Placed {self.selected_building_type.value} at ({world_x}, {world_y})")
                        else:
                            logger.warning(f"Cannot place {self.selected_building_type.value} at ({world_x}, {world_y})")
            elif event.type == pygame.MOUSEMOTION:
                if self.area_selector.is_selecting:
                    # Update selection rectangle
                    mouse_x, mouse_y = event.pos
                    self.area_selector.update_selection(mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.area_selector.is_selecting:
                    # Finish designation selection
                    rect_bounds = self.area_selector.finish_selection()
                    if rect_bounds:
                        self._apply_designation(rect_bounds)

        # Handle camera movement with arrow keys
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.game_state.camera_x = max(0, self.game_state.camera_x - self.camera_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            max_x = max(0, len(self.game_state.local_tiles[0]) * TILE_SIZE - WINDOW_WIDTH)
            self.game_state.camera_x = min(max_x, self.game_state.camera_x + self.camera_speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.game_state.camera_y = max(0, self.game_state.camera_y - self.camera_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            max_y = max(0, len(self.game_state.local_tiles) * TILE_SIZE - WINDOW_HEIGHT)
            self.game_state.camera_y = min(max_y, self.game_state.camera_y + self.camera_speed)

    def draw(self):
        """Draw the game world with enhanced rendering."""
        self.screen.fill(COLOR_BACKGROUND)

        # Render based on current view
        if self.game_state.current_view == "world":
            self._draw_world_view()
        elif self.game_state.current_view == "region":
            self._draw_region_view()
        else:  # local
            self._draw_local_view()

        # Draw UI overlay
        self._draw_ui()

    def _draw_world_view(self):
        """Draw the world map (150x150 tiles) - zoomed out view."""
        # Check if world tiles exist
        if not self.game_state.world_tiles:
            return

        # World view uses smaller tiles (8x8) for zoomed out effect
        WORLD_TILE_SIZE = 8

        # Calculate visible tile range
        start_x = max(0, int(self.game_state.camera_x // WORLD_TILE_SIZE))
        end_x = min(len(self.game_state.world_tiles[0]), int((self.game_state.camera_x + WINDOW_WIDTH) // WORLD_TILE_SIZE) + 1)
        start_y = max(0, int(self.game_state.camera_y // WORLD_TILE_SIZE))
        end_y = min(len(self.game_state.world_tiles), int((self.game_state.camera_y + WINDOW_HEIGHT) // WORLD_TILE_SIZE) + 1)

        # Draw world tiles (simple biome colors)
        from src.world.biomes import BIOME_DEFINITIONS
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                world_tile = self.game_state.world_tiles[y][x]
                screen_x = int(x * WORLD_TILE_SIZE - self.game_state.camera_x)
                screen_y = int(y * WORLD_TILE_SIZE - self.game_state.camera_y)

                # Simple biome-based color
                biome_def = BIOME_DEFINITIONS[world_tile.biome]
                color = biome_def.base_grass_color

                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, WORLD_TILE_SIZE, WORLD_TILE_SIZE))

        # Draw indicator showing where the current region/local area is
        # This shows "You are here" on the world map - always visible
        if hasattr(self.game_state, 'current_region_x'):
            indicator_x = int(self.game_state.current_region_x * WORLD_TILE_SIZE - self.game_state.camera_x)
            indicator_y = int(self.game_state.current_region_y * WORLD_TILE_SIZE - self.game_state.camera_y)

            # Draw pulsing indicator (yellow square) - larger so it's always visible
            pygame.draw.rect(self.screen, (255, 255, 0),
                           (indicator_x - 2, indicator_y - 2, WORLD_TILE_SIZE + 4, WORLD_TILE_SIZE + 4), 2)
            pygame.draw.rect(self.screen, (255, 200, 0),
                           (indicator_x, indicator_y, WORLD_TILE_SIZE, WORLD_TILE_SIZE), 2)

            # Add a label so it's clear where home is
            font = pygame.font.Font(None, 16)
            label = font.render("HOME", True, (255, 255, 0))
            self.screen.blit(label, (indicator_x - 10, indicator_y - 18))

    def _draw_region_view(self):
        """Draw the region map (80x80 tiles) with terrain detail."""
        if not self.game_state.region_tiles:
            return

        # Calculate visible tile range
        start_x = max(0, int(self.game_state.camera_x // TILE_SIZE))
        end_x = min(len(self.game_state.region_tiles[0]), int((self.game_state.camera_x + WINDOW_WIDTH) // TILE_SIZE) + 1)
        start_y = max(0, int(self.game_state.camera_y // TILE_SIZE))
        end_y = min(len(self.game_state.region_tiles), int((self.game_state.camera_y + WINDOW_HEIGHT) // TILE_SIZE) + 1)

        # Draw region tiles with elevation-based detail
        from src.world.biomes import BIOME_DEFINITIONS
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                region_tile = self.game_state.region_tiles[y][x]
                screen_x = int(x * TILE_SIZE - self.game_state.camera_x)
                screen_y = int(y * TILE_SIZE - self.game_state.camera_y)

                # Get base biome color
                biome_def = BIOME_DEFINITIONS[region_tile.biome]
                color = biome_def.base_grass_color

                # Modify color based on elevation to show terrain features
                elevation = region_tile.elevation

                # Create a color tuple we can modify
                r, g, b = color

                if elevation > 0.7:
                    # Mountains - darker, grayer
                    r = min(255, int(r * 0.6 + 100))
                    g = min(255, int(g * 0.6 + 100))
                    b = min(255, int(b * 0.6 + 100))
                elif elevation > 0.55:
                    # Hills - slightly darker
                    r = int(r * 0.85)
                    g = int(g * 0.85)
                    b = int(b * 0.85)
                elif elevation < 0.35:
                    # Low areas / wetlands - bluer, darker
                    r = int(r * 0.7)
                    g = int(g * 0.8)
                    b = min(255, int(b * 1.1))

                color = (r, g, b)

                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

                # Add visual markers for high elevation
                if elevation > 0.7:
                    # Draw mountain peaks (small triangles or dots)
                    peak_color = (200, 200, 220)
                    pygame.draw.circle(self.screen, peak_color,
                                     (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2), 3)

        # Draw indicator showing where the citizens are (local area within region)
        if hasattr(self.game_state, 'current_local_x'):
            local_x = self.game_state.current_local_x
            local_y = self.game_state.current_local_y
            indicator_x = int(local_x * TILE_SIZE - self.game_state.camera_x)
            indicator_y = int(local_y * TILE_SIZE - self.game_state.camera_y)

            # Draw bright yellow highlighted tile showing citizen location
            pygame.draw.rect(self.screen, (255, 255, 0),
                           (indicator_x - 2, indicator_y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 3)
            pygame.draw.rect(self.screen, (255, 200, 0),
                           (indicator_x, indicator_y, TILE_SIZE, TILE_SIZE), 2)

            # Add label
            font = pygame.font.Font(None, 16)
            label = font.render("CITIZENS", True, (255, 255, 0))
            self.screen.blit(label, (indicator_x - 15, indicator_y - 18))

    def _draw_local_view(self):
        """Draw the local playable map (100x100 tiles) - ONLY view where building is allowed."""
        # Calculate visible tile range
        start_x = max(0, int(self.game_state.camera_x // TILE_SIZE))
        end_x = min(len(self.game_state.local_tiles[0]), int((self.game_state.camera_x + WINDOW_WIDTH) // TILE_SIZE) + 1)
        start_y = max(0, int(self.game_state.camera_y // TILE_SIZE))
        end_y = min(len(self.game_state.local_tiles), int((self.game_state.camera_y + WINDOW_HEIGHT) // TILE_SIZE) + 1)

        # Draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.game_state.local_tiles[y][x]
                screen_x = int(x * TILE_SIZE - self.game_state.camera_x)
                screen_y = int(y * TILE_SIZE - self.game_state.camera_y)

                # Use renderer from game_state
                self.game_state.renderer.render_tile(
                    self.screen, tile, screen_x, screen_y,
                    self.game_state.current_biome
                )

                # Draw grid overlay in building mode (only in local view)
                if self.building_mode and TILE_SIZE >= 8:
                    grid_color = (80, 80, 80)
                    pygame.draw.rect(self.screen, grid_color,
                                   (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

        # Draw buildings (only in local view)
        for building in self.game_state.buildings:
            self._draw_building(building)

        # Draw citizens (only in local view)
        for citizen in self.game_state.citizens:
            self._draw_citizen(citizen)

        # Draw designated resource overlays
        self._draw_designated_resources()

        # Draw selection rectangle if dragging
        self._draw_selection_rectangle()

    def _draw_building(self, building):
        """Draw a single building."""
        definition = building.get_definition()

        # Screen position
        screen_x = int(building.x * TILE_SIZE - self.game_state.camera_x)
        screen_y = int(building.y * TILE_SIZE - self.game_state.camera_y)

        # Size
        width = definition.width * TILE_SIZE
        height = definition.height * TILE_SIZE

        # Color based on state
        if building.state == BuildingState.PLANNED:
            color = (100, 100, 100)  # Gray
        elif building.state == BuildingState.UNDER_CONSTRUCTION:
            color = (200, 150, 50)   # Orange
        else:
            color = definition.color

        # Draw rectangle
        pygame.draw.rect(self.screen, color, (screen_x, screen_y, width, height))
        pygame.draw.rect(self.screen, (0, 0, 0), (screen_x, screen_y, width, height), 2)

        # Draw progress bar if under construction
        if building.state == BuildingState.UNDER_CONSTRUCTION:
            progress = building.construction_progress / definition.construction_work
            bar_width = int(width * progress)
            pygame.draw.rect(self.screen, (0, 255, 0),
                            (screen_x, screen_y + height - 5, bar_width, 5))

    def _draw_citizen(self, citizen):
        """Draw a single citizen."""
        # Screen position
        screen_x = int(citizen.x * TILE_SIZE - self.game_state.camera_x)
        screen_y = int(citizen.y * TILE_SIZE - self.game_state.camera_y)

        # Color based on state
        from src.entities.citizen import CitizenState
        if citizen.state == CitizenState.WORKING:
            color = (255, 200, 0)  # Yellow
        elif citizen.state == CitizenState.CARRYING:
            color = (150, 200, 255)  # Blue
        else:
            color = (255, 255, 255)  # White

        # Draw circle
        pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), 6)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(screen_x), int(screen_y)), 6, 1)

    def _snap_camera_to_home(self):
        """Snap camera back to settlement location in current view."""
        if self.game_state.current_view == "world":
            # In world view, center on the world tile where settlement is
            WORLD_TILE_SIZE = 8
            self.game_state.camera_x = (self.game_state.current_region_x * WORLD_TILE_SIZE) - WINDOW_WIDTH // 2
            self.game_state.camera_y = (self.game_state.current_region_y * WORLD_TILE_SIZE) - WINDOW_HEIGHT // 2
        elif self.game_state.current_view == "region":
            # In region view, center on the local area within the region
            self.game_state.camera_x = (self.game_state.current_local_x * TILE_SIZE) - WINDOW_WIDTH // 2
            self.game_state.camera_y = (self.game_state.current_local_y * TILE_SIZE) - WINDOW_HEIGHT // 2
        else:  # local view
            # In local view, center on the settlement (around tile 50, 50)
            self.game_state.camera_x = (50 * TILE_SIZE) - WINDOW_WIDTH // 2
            self.game_state.camera_y = (50 * TILE_SIZE) - WINDOW_HEIGHT // 2

    def _draw_ui(self):
        """Draw UI elements."""
        # Semi-transparent panel at top
        panel_height = 140 if self.building_mode else 100
        panel = pygame.Surface((WINDOW_WIDTH, panel_height))
        panel.set_alpha(200)
        panel.fill(COLOR_MENU_BG)
        self.screen.blit(panel, (0, 0))

        # Info text - line 1 - View and controls
        view_name = self.game_state.current_view.upper()
        view_color = (100, 255, 100) if self.game_state.current_view == "local" else (255, 200, 100)
        pause_indicator = " | PAUSED" if self.game_state.paused else ""

        info_text1 = self.ui_font.render(
            f"My Kingdom - WASD to move | TAB/F1-F3 to change view | H to snap home | ESC for pause menu{pause_indicator}",
            True,
            COLOR_TEXT
        )
        self.screen.blit(info_text1, (10, 8))

        # Info text - line 2 - Current view
        view_sizes = {
            "world": "150x150",
            "region": "80x80",
            "local": "100x100"
        }
        can_build_text = " (Building Enabled)" if self.game_state.can_build_here() else " (View Only - Press F3 for Local)"
        info_text2 = self.ui_font.render(
            f"View: {view_name} {view_sizes[self.game_state.current_view]}{can_build_text}",
            True,
            view_color
        )
        self.screen.blit(info_text2, (10, 32))

        # Info text - line 3 - Resources (only in local view)
        if self.game_state.current_view == "local":
            resources = self.game_state.resources
            storage_used = self.game_state.get_current_storage_used()
            storage_capacity = self.game_state.get_total_storage_capacity()

            # Color code storage based on fullness
            storage_percent = storage_used / storage_capacity if storage_capacity > 0 else 0
            if storage_percent >= 0.9:
                storage_color = (255, 100, 100)  # Red when nearly full
            elif storage_percent >= 0.7:
                storage_color = (255, 200, 100)  # Orange when getting full
            else:
                storage_color = COLOR_TEXT  # Normal

            info_text3 = self.ui_font.render(
                f"Resources: Wood {resources['wood']} | Stone {resources['stone']} | Food {resources['food']} | Storage: {storage_used}/{storage_capacity}",
                True,
                COLOR_TEXT
            )
            self.screen.blit(info_text3, (10, 56))

            # Save name and position (line 4 for local view, may shift down for warning)
            world_x = int(self.game_state.camera_x / TILE_SIZE)
            world_y = int(self.game_state.camera_y / TILE_SIZE)
            info_text4 = self.small_font.render(
                f"Save: {self.game_state.current_save_name} | Position: ({world_x}, {world_y}) | Citizens: {len(self.game_state.citizens)} | Buildings: {len(self.game_state.buildings)}",
                True,
                COLOR_TEXT
            )
            self.screen.blit(info_text4, (10, 78))

            # Add storage warning on line 5 if needed
            if storage_percent >= 0.9:
                warning_text = self.small_font.render(
                    "WARNING: Storage nearly full! Build a warehouse!",
                    True,
                    (255, 100, 100)
                )
                self.screen.blit(warning_text, (10, 96))
        else:
            # Show world info in other views
            info_text3 = self.ui_font.render(
                f"Seed: {self.game_state.world_seed} | Switch to LOCAL view (F3) to build",
                True,
                (200, 200, 200)
            )
            self.screen.blit(info_text3, (10, 56))

            # Info text - line 4 - Save name and position
            world_x = int(self.game_state.camera_x / TILE_SIZE)
            world_y = int(self.game_state.camera_y / TILE_SIZE)
            info_text4 = self.small_font.render(
                f"Save: {self.game_state.current_save_name} | Position: ({world_x}, {world_y})",
                True,
                COLOR_TEXT
            )
            self.screen.blit(info_text4, (10, 78))

        # Building mode UI (only effective in local view)
        if self.building_mode:
            if self.game_state.can_build_here():
                building_info = "[1]House [2]Storage [3]Workshop [4]Farm [5]Mine [6]Lumber [7]Well [8]Market [9]Warehouse | Click to place"
                if self.selected_building_type:
                    definition = BUILDING_DEFINITIONS[self.selected_building_type]
                    cost_str = ", ".join([f"{k.title()} {v}" for k, v in definition.required_resources.items()])
                    building_info = f"Selected: {self.selected_building_type.value.title()} (Cost: {cost_str})"

                building_text = self.small_font.render(building_info, True, (100, 255, 100))
            else:
                building_text = self.small_font.render(
                    "BUILDING MODE: Switch to LOCAL view (F3) to place buildings!",
                    True,
                    (255, 100, 100)
                )

            self.screen.blit(building_text, (10, 100))

        # Designation mode UI (only in local view)
        if self.designation_mode:
            # Determine designation mode name
            mode_name = "Chop Trees (D)"
            if self.current_designation_type == DesignationType.MINE_STONE:
                mode_name = "Mine Stone (M)"
            elif self.current_designation_type == DesignationType.GATHER_BERRIES:
                mode_name = "Gather Berries (F)"

            designation_text = self.small_font.render(
                f"DESIGNATION MODE: {mode_name} | Drag to select area | ESC to cancel",
                True,
                (255, 200, 100)
            )
            self.screen.blit(designation_text, (10, 120))

    def _draw_designated_resources(self):
        """Draw colored tint over designated resources"""
        for resource_node in self.game_state.resource_nodes:
            if resource_node.designated:
                screen_x = int(resource_node.x * TILE_SIZE - self.game_state.camera_x)
                screen_y = int(resource_node.y * TILE_SIZE - self.game_state.camera_y)

                # Choose color based on resource type
                if resource_node.resource_type == ResourceType.TREE:
                    overlay_color = (139, 90, 43)   # Brown for trees
                    border_color = (100, 60, 20)
                elif resource_node.resource_type == ResourceType.STONE:
                    overlay_color = (100, 100, 120)  # Gray for stone
                    border_color = (70, 70, 90)
                elif resource_node.resource_type == ResourceType.BERRY_BUSH:
                    overlay_color = (200, 50, 150)   # Pink/purple for berries
                    border_color = (150, 30, 100)
                else:
                    overlay_color = (255, 255, 0)    # Yellow fallback
                    border_color = (200, 200, 0)

                # Draw tint overlay
                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                overlay.set_alpha(80)
                overlay.fill(overlay_color)
                self.screen.blit(overlay, (screen_x, screen_y))

                # Draw border
                pygame.draw.rect(self.screen, border_color,
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 2)

    def _draw_selection_rectangle(self):
        """Draw the selection rectangle while dragging"""
        if self.area_selector.is_selecting:
            rect_bounds = self.area_selector.get_rect_bounds()
            if rect_bounds:
                min_x, min_y, max_x, max_y = rect_bounds
                width = max_x - min_x
                height = max_y - min_y

                # Draw semi-transparent fill
                overlay = pygame.Surface((width, height))
                overlay.set_alpha(50)
                overlay.fill((255, 255, 0))  # Yellow
                self.screen.blit(overlay, (min_x, min_y))

                # Draw outline
                pygame.draw.rect(self.screen, (255, 255, 0),
                               (min_x, min_y, width, height), 2)

    def _apply_designation(self, rect_bounds):
        """Apply designation to all resources of the current type in the selected rectangle"""
        min_screen_x, min_screen_y, max_screen_x, max_screen_y = rect_bounds

        # Convert screen coordinates to world coordinates
        min_world_x = int((min_screen_x + self.game_state.camera_x) // TILE_SIZE)
        min_world_y = int((min_screen_y + self.game_state.camera_y) // TILE_SIZE)
        max_world_x = int((max_screen_x + self.game_state.camera_x) // TILE_SIZE)
        max_world_y = int((max_screen_y + self.game_state.camera_y) // TILE_SIZE)

        # Determine which resource type we're designating
        target_resource_type = None
        designation_name = ""

        if self.current_designation_type == DesignationType.CHOP_TREES:
            target_resource_type = ResourceType.TREE
            designation_name = "trees for chopping"
        elif self.current_designation_type == DesignationType.MINE_STONE:
            target_resource_type = ResourceType.STONE
            designation_name = "stone for mining"
        elif self.current_designation_type == DesignationType.GATHER_BERRIES:
            target_resource_type = ResourceType.BERRY_BUSH
            designation_name = "berry bushes for gathering"

        # Find all resources of the target type in the rectangle
        selected_resources = []
        for resource_node in self.game_state.resource_nodes:
            if resource_node.resource_type == target_resource_type:
                if (min_world_x <= resource_node.x <= max_world_x and
                    min_world_y <= resource_node.y <= max_world_y):
                    selected_resources.append(resource_node)

        # Create designation
        if selected_resources:
            self.designation_manager.add_designation(self.current_designation_type, selected_resources)
            logger.info(f"Designated {len(selected_resources)} {designation_name}")
        else:
            logger.info(f"No {designation_name.split()[0]} found in selected area")

    def run(self):
        """Run the game loop."""
        clock = pygame.time.Clock()

        while self.running:
            # Calculate delta time
            delta_time = clock.get_time() / 1000.0  # Convert to seconds

            # Handle events
            self.handle_events()

            # Update game state (citizens work, buildings construct, etc.)
            self.game_state.update(delta_time)

            # Update designation manager (remove completed designations)
            self.designation_manager.update()

            # Draw everything
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

        return self.next_state
