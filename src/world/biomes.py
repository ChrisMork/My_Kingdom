"""
Biome system for world generation.
Inspired by RimWorld's biome approach with cozy visual style.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class BiomeType(Enum):
    """Different biome types inspired by RimWorld."""
    TEMPERATE_FOREST = "temperate_forest"
    GRASSLAND = "grassland"
    BOREAL_FOREST = "boreal_forest"
    TUNDRA = "tundra"
    DESERT = "desert"
    TROPICAL_RAINFOREST = "tropical_rainforest"
    ARID_SHRUBLAND = "arid_shrubland"
    WETLAND = "wetland"


@dataclass
class BiomeProperties:
    """Properties defining a biome's characteristics."""
    name: str
    min_temperature: float  # -1 to 1 (cold to hot)
    max_temperature: float
    min_rainfall: float     # 0 to 1 (dry to wet)
    max_rainfall: float

    # Visual properties (RimWorld-inspired cozy colors)
    base_grass_color: Tuple[int, int, int]
    grass_variants: list  # List of grass color variants
    tree_density: float   # 0 to 1
    rock_density: float   # 0 to 1
    fertility: float      # 0 to 1 (affects farming)

    # Cozy atmosphere
    ambient_color: Tuple[int, int, int]  # Light tint for this biome
    description: str


# Define all biomes with cozy, RimWorld-style properties
BIOME_DEFINITIONS = {
    BiomeType.TEMPERATE_FOREST: BiomeProperties(
        name="Temperate Forest",
        min_temperature=-0.2,
        max_temperature=0.6,
        min_rainfall=0.4,
        max_rainfall=0.8,
        base_grass_color=(76, 153, 76),  # Lush green
        grass_variants=[
            (76, 153, 76),
            (70, 145, 70),
            (82, 161, 82),
            (65, 140, 65),
        ],
        tree_density=0.4,
        rock_density=0.1,
        fertility=0.8,
        ambient_color=(240, 250, 240),  # Slight green tint
        description="A pleasant, temperate region with abundant trees and fertile soil. Perfect for building a thriving settlement."
    ),

    BiomeType.GRASSLAND: BiomeProperties(
        name="Grassland",
        min_temperature=0.0,
        max_temperature=0.7,
        min_rainfall=0.3,
        max_rainfall=0.6,
        base_grass_color=(124, 186, 94),  # Vibrant grass green
        grass_variants=[
            (124, 186, 94),
            (116, 178, 88),
            (132, 194, 100),
            (140, 202, 108),
        ],
        tree_density=0.1,
        rock_density=0.05,
        fertility=0.9,
        ambient_color=(255, 255, 240),  # Warm sunlight
        description="Wide open plains with tall grass. Excellent for farming and grazing."
    ),

    BiomeType.BOREAL_FOREST: BiomeProperties(
        name="Boreal Forest",
        min_temperature=-0.6,
        max_temperature=0.2,
        min_rainfall=0.4,
        max_rainfall=0.7,
        base_grass_color=(65, 105, 75),  # Darker, cold-looking green
        grass_variants=[
            (65, 105, 75),
            (58, 98, 68),
            (72, 112, 82),
            (60, 100, 70),
        ],
        tree_density=0.5,
        rock_density=0.15,
        fertility=0.4,
        ambient_color=(230, 240, 255),  # Cool blue tint
        description="A cold forest of hardy evergreens. Challenging but beautiful."
    ),

    BiomeType.TUNDRA: BiomeProperties(
        name="Tundra",
        min_temperature=-0.8,
        max_temperature=-0.2,
        min_rainfall=0.2,
        max_rainfall=0.5,
        base_grass_color=(167, 178, 150),  # Pale, cold grass
        grass_variants=[
            (167, 178, 150),
            (160, 171, 143),
            (174, 185, 157),
            (155, 166, 138),
        ],
        tree_density=0.05,
        rock_density=0.25,
        fertility=0.2,
        ambient_color=(220, 230, 245),  # Very cold blue
        description="A harsh, frozen land with permafrost and sparse vegetation."
    ),

    BiomeType.DESERT: BiomeProperties(
        name="Desert",
        min_temperature=0.5,
        max_temperature=1.0,
        min_rainfall=0.0,
        max_rainfall=0.2,
        base_grass_color=(210, 180, 140),  # Sandy color
        grass_variants=[
            (210, 180, 140),
            (205, 175, 135),
            (215, 185, 145),
            (200, 170, 130),
        ],
        tree_density=0.02,
        rock_density=0.3,
        fertility=0.1,
        ambient_color=(255, 250, 230),  # Warm sandy light
        description="A hot, arid desert with little water. Only the hardiest survive here."
    ),

    BiomeType.TROPICAL_RAINFOREST: BiomeProperties(
        name="Tropical Rainforest",
        min_temperature=0.6,
        max_temperature=1.0,
        min_rainfall=0.7,
        max_rainfall=1.0,
        base_grass_color=(34, 139, 34),  # Deep jungle green
        grass_variants=[
            (34, 139, 34),
            (28, 133, 28),
            (40, 145, 40),
            (30, 135, 30),
        ],
        tree_density=0.7,
        rock_density=0.05,
        fertility=0.7,
        ambient_color=(235, 255, 235),  # Humid green
        description="A dense, humid jungle teeming with life. Resources are abundant but diseases lurk."
    ),

    BiomeType.ARID_SHRUBLAND: BiomeProperties(
        name="Arid Shrubland",
        min_temperature=0.3,
        max_temperature=0.8,
        min_rainfall=0.2,
        max_rainfall=0.4,
        base_grass_color=(156, 147, 108),  # Dry grass
        grass_variants=[
            (156, 147, 108),
            (150, 141, 102),
            (162, 153, 114),
            (145, 136, 97),
        ],
        tree_density=0.15,
        rock_density=0.2,
        fertility=0.4,
        ambient_color=(255, 248, 220),  # Dry, dusty
        description="A semi-arid region with scrubby vegetation. Moderate resources."
    ),

    BiomeType.WETLAND: BiomeProperties(
        name="Wetland",
        min_temperature=-0.1,
        max_temperature=0.5,
        min_rainfall=0.6,
        max_rainfall=1.0,
        base_grass_color=(85, 145, 85),  # Wet, dark green
        grass_variants=[
            (85, 145, 85),
            (79, 139, 79),
            (91, 151, 91),
            (75, 135, 75),
        ],
        tree_density=0.25,
        rock_density=0.05,
        fertility=0.6,
        ambient_color=(240, 248, 255),  # Misty blue
        description="A marshy region with abundant water. Good for fishing but challenging to build on."
    ),
}


def get_biome_from_climate(temperature: float, rainfall: float) -> BiomeType:
    """
    Determine biome type from climate parameters (RimWorld approach).

    Args:
        temperature: -1 (very cold) to 1 (very hot)
        rainfall: 0 (dry) to 1 (wet)

    Returns:
        BiomeType that matches the climate
    """
    # Score each biome based on how well it matches the climate
    best_biome = BiomeType.GRASSLAND
    best_score = float('-inf')

    for biome_type, properties in BIOME_DEFINITIONS.items():
        # Calculate how well this climate matches this biome
        temp_match = 1.0
        if temperature < properties.min_temperature:
            temp_match = 1.0 - (properties.min_temperature - temperature)
        elif temperature > properties.max_temperature:
            temp_match = 1.0 - (temperature - properties.max_temperature)

        rain_match = 1.0
        if rainfall < properties.min_rainfall:
            rain_match = 1.0 - (properties.min_rainfall - rainfall)
        elif rainfall > properties.max_rainfall:
            rain_match = 1.0 - (rainfall - properties.max_rainfall)

        # Combined score
        score = temp_match * rain_match

        if score > best_score:
            best_score = score
            best_biome = biome_type

    return best_biome


def get_biome_properties(biome_type: BiomeType) -> BiomeProperties:
    """Get the properties for a specific biome type."""
    return BIOME_DEFINITIONS[biome_type]
