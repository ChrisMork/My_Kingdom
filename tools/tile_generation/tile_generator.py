"""
AI-powered tile and asset generator for My Kingdom.
Generates terrain tiles, objects, and props using AI image generation.
"""

import requests
import urllib.parse
from pathlib import Path
from PIL import Image
import io


class TileGenerator:
    """Generate game tiles and assets using AI."""

    def __init__(self):
        self.assets_dir = Path("assets/images/world")
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Art style to match the menu
        self.base_style = "pixel art, medieval fantasy, warm colors, detailed, game asset, top-down view, 32x32 pixels"

    def generate_tile(self, tile_type, description, size=32):
        """Generate a single tile using AI."""
        prompt = f"{description}, {self.base_style}"

        print(f"Generating {tile_type} tile...")
        print(f"Prompt: {prompt}")

        try:
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={size}&height={size}&nologo=true&enhance=true&seed=42"

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            img = Image.open(io.BytesIO(response.content))

            # Save the tile
            output_path = self.assets_dir / f"{tile_type}.png"
            img.save(output_path)
            print(f"SUCCESS: Saved to {output_path}")

            return output_path
        except Exception as e:
            print(f"ERROR generating {tile_type}: {e}")
            return None

    def generate_terrain_tileset(self):
        """Generate all basic terrain tiles."""
        print("\n" + "="*60)
        print("GENERATING TERRAIN TILESET")
        print("="*60 + "\n")

        terrain_tiles = {
            # Grass variants
            "grass": "lush green grass texture, vibrant",
            "grass_flowers": "green grass with small wildflowers scattered",
            "grass_dark": "dark green grass, shaded area",

            # Dirt/Path
            "dirt": "brown dirt ground, earth texture",
            "dirt_path": "worn dirt path, footprints visible",

            # Desert/Sand
            "desert_sand": "golden sand desert texture",
            "desert_dune": "sand dune with ripples",

            # Stone/Rock
            "stone_gray": "gray stone ground, cobblestone texture",
            "stone_path": "cobblestone medieval path",

            # Water
            "water_shallow": "clear shallow water, light blue, reflective",
            "water_deep": "deep blue water, darker",

            # Forest floor
            "forest_floor": "dark soil with fallen leaves and moss",

            # Snow (for variety)
            "snow": "white snow ground texture, pristine",
        }

        for tile_name, description in terrain_tiles.items():
            self.generate_tile(tile_name, description, size=32)

    def generate_objects(self):
        """Generate objects and props for the world."""
        print("\n" + "="*60)
        print("GENERATING WORLD OBJECTS")
        print("="*60 + "\n")

        objects = {
            # Trees
            "tree_oak": "large oak tree, green leaves, brown trunk, top-down view",
            "tree_pine": "pine tree, conical shape, dark green, top-down view",
            "tree_small": "small bush or young tree, green, top-down view",
            "tree_dead": "dead tree, bare branches, gray wood, top-down view",

            # Rocks
            "rock_large": "large gray boulder, rough texture, top-down view",
            "rock_small": "small stone, gray, top-down view",
            "rock_cluster": "cluster of rocks, varied sizes, top-down view",

            # Plants
            "bush_green": "round green bush, leafy, top-down view",
            "flowers_red": "patch of red flowers, colorful, top-down view",
            "flowers_yellow": "patch of yellow flowers, bright, top-down view",

            # Resources
            "iron_ore": "iron ore deposit, metallic gray with brown rock, top-down view",
            "gold_ore": "gold ore deposit, shiny yellow in rock, top-down view",
            "wood_pile": "stack of cut logs, brown wood, top-down view",
            "stone_pile": "pile of stone blocks, gray, top-down view",

            # Structures (simple)
            "house_small": "small medieval house, thatched roof, stone walls, top-down view",
            "house_wood": "wooden cottage, brown wood, top-down view",
            "well": "stone well with wooden roof, top-down view",
            "fence_wood": "wooden fence section, brown planks, top-down view",
        }

        for obj_name, description in objects.items():
            self.generate_tile(obj_name, description, size=64)  # Objects are larger

    def generate_transition_tiles(self):
        """Generate tiles that blend between terrain types."""
        print("\n" + "="*60)
        print("GENERATING TRANSITION TILES")
        print("="*60 + "\n")

        transitions = {
            "grass_to_sand_n": "top half grass, bottom half sand, smooth transition, seamless blend",
            "grass_to_sand_e": "left half grass, right half sand, smooth transition, seamless blend",
            "grass_to_water_n": "top half grass, bottom half water edge, smooth transition",
            "grass_to_water_e": "left half grass, right half water edge, smooth transition",
            "grass_to_stone_n": "top half grass, bottom half stone, smooth transition",
            "sand_to_water_n": "top half sand beach, bottom half water, smooth transition",
        }

        for tile_name, description in transitions.items():
            self.generate_tile(tile_name, description, size=32)

    def generate_all(self):
        """Generate complete asset pack."""
        print("\n" + "="*80)
        print("MY KINGDOM - WORLD ASSET GENERATION")
        print("="*80 + "\n")

        self.generate_terrain_tileset()
        self.generate_objects()
        self.generate_transition_tiles()

        print("\n" + "="*80)
        print("ASSET GENERATION COMPLETE!")
        print(f"Assets saved to: {self.assets_dir}")
        print("="*80 + "\n")


if __name__ == "__main__":
    generator = TileGenerator()
    generator.generate_all()
