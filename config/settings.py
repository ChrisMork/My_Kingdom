"""
Game configuration settings for My Kingdom.
"""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "My Kingdom"
FPS = 60

# Colors - Medieval and relaxing palette (UI)
COLOR_BACKGROUND = (245, 240, 230)  # Warm parchment
COLOR_TEXT = (60, 40, 30)  # Dark brown
COLOR_MENU_BG = (205, 190, 165)  # Light tan
COLOR_BUTTON = (160, 140, 110)  # Medium brown
COLOR_BUTTON_HOVER = (180, 160, 130)  # Lighter brown
COLOR_BUTTON_TEXT = (255, 255, 245)  # Off-white
COLOR_ACCENT = (140, 100, 80)  # Rustic brown

# Enhanced terrain colors - uniform biomes with minimal variation
COLOR_GRASS_BASE = (88, 164, 76)  # Rich grass green
COLOR_GRASS_VARIANTS = [
    (86, 162, 74),   # Very slightly darker
    (90, 166, 78),   # Very slightly lighter
    (88, 164, 76),   # Same as base
]

COLOR_WATER_BASE = (65, 140, 200)  # Beautiful blue water
COLOR_WATER_DEEP = (60, 135, 195)  # Slightly deeper (minimal variation)
COLOR_WATER_SHALLOW = (70, 145, 205)  # Slightly shallow (minimal variation)
COLOR_WATER_SHINE = (120, 200, 255)  # Water highlights

COLOR_SAND_BASE = (230, 210, 150)  # Beach sand
COLOR_SAND_VARIANTS = [
    (228, 208, 148),  # Very subtle variation
    (232, 212, 152),  # Very subtle variation
]

COLOR_FOREST_BASE = (52, 110, 52)  # Deep forest green
COLOR_FOREST_DARK = (50, 108, 50)   # Slightly darker
COLOR_FOREST_LIGHT = (54, 112, 54)  # Slightly lighter
COLOR_TREE_TRUNK = (101, 67, 33)   # Tree trunk brown

COLOR_DIRT_BASE = (139, 115, 85)   # Rich soil
COLOR_DIRT_VARIANTS = [
    (137, 113, 83),  # Very subtle variation
    (141, 117, 87),  # Very subtle variation
]

COLOR_STONE_BASE = (130, 130, 130)  # Stone gray
COLOR_STONE_VARIANTS = [
    (128, 128, 128),  # Very subtle variation
    (132, 132, 132),  # Very subtle variation
    (130, 130, 130),  # Same as base
]

# Font settings
FONT_TITLE_SIZE = 72
FONT_BUTTON_SIZE = 36
FONT_NORMAL_SIZE = 24

# World generation settings
WORLD_WIDTH = 500  # Huge world!
WORLD_HEIGHT = 500
TILE_SIZE = 32

# Zoom settings
MIN_ZOOM = 0.25  # Can zoom out to 25% (see more)
MAX_ZOOM = 2.0   # Can zoom in to 200% (see details)
DEFAULT_ZOOM = 1.0
ZOOM_SPEED = 0.1

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
