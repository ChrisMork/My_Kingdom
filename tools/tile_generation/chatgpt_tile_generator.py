"""
ChatGPT/DALL-E based tile generator for My Kingdom.
Uses OpenAI API to generate game tiles.
"""

import os
from pathlib import Path
from openai import OpenAI
import requests
from PIL import Image
import io


class ChatGPTTileGenerator:
    """Generate game tiles using OpenAI's DALL-E."""

    def __init__(self, api_key=None):
        """
        Initialize the generator.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment variable OPENAI_API_KEY
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment variable
            self.client = OpenAI()  # Will automatically use OPENAI_API_KEY env var

        self.assets_dir = Path("assets/images/world")
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        self.base_style = "pixel art, medieval fantasy, warm colors, detailed, game asset, top-down view"

    def generate_tile(self, tile_name, description, size="1024x1024"):
        """
        Generate a single tile using DALL-E.

        Args:
            tile_name: Name for the output file (without extension)
            description: Description of what to generate
            size: Image size (256x256, 512x512, or 1024x1024)
        """
        prompt = f"{description}, {self.base_style}"

        print(f"\nGenerating: {tile_name}")
        print(f"Prompt: {prompt}")

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download the image
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Open and save the image
            img = Image.open(io.BytesIO(image_response.content))

            output_path = self.assets_dir / f"{tile_name}.png"
            img.save(output_path)

            print(f"[OK] Saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"[ERROR] Error generating {tile_name}: {e}")
            return None

    def generate_terrain_tiles(self):
        """Generate basic terrain tiles."""
        print("\n" + "="*60)
        print("GENERATING TERRAIN TILES")
        print("="*60)

        terrain = {
            "grass": "seamless repeating tileable pattern of lush vibrant green grass texture, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "grass_flowers": "seamless repeating tileable pattern of green grass with small scattered wildflowers, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "dirt": "seamless repeating tileable pattern of brown dirt ground texture, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "desert_sand": "seamless repeating tileable pattern of golden sand desert texture, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "stone_gray": "seamless repeating tileable pattern of gray cobblestone ground, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "water_shallow": "seamless repeating tileable pattern of clear shallow water with light ripples, light blue, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "water_deep": "seamless repeating tileable pattern of deep blue water, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
            "forest_floor": "seamless repeating tileable pattern of dark soil with fallen leaves and moss, must tile perfectly edge-to-edge with no visible seams, 32x32 pixels",
        }

        for tile_name, description in terrain.items():
            self.generate_tile(tile_name, description)

    def generate_objects(self):
        """Generate object sprites."""
        print("\n" + "="*60)
        print("GENERATING OBJECT SPRITES")
        print("="*60)

        # Objects use 2.5D isometric/angled view for depth
        objects = {
            "tree_oak": "large oak tree with green leaves and brown trunk, 2.5D isometric view, 3/4 perspective, transparent background, 64x64 pixels",
            "tree_pine": "pine tree, conical shape, dark green, 2.5D isometric view, 3/4 perspective, transparent background, 64x64 pixels",
            "rock_large": "large gray boulder, rough texture, 2.5D isometric view, 3/4 perspective, transparent background, 64x64 pixels",
            "bush_green": "round green leafy bush, 2.5D isometric view, 3/4 perspective, transparent background, 64x64 pixels",
            "house_small": "small medieval house with thatched roof and stone walls, 2.5D isometric view, 3/4 perspective showing front and side, transparent background, 64x64 pixels",
            "well": "stone well with wooden roof, 2.5D isometric view, 3/4 perspective showing depth, transparent background, 64x64 pixels",
        }

        for obj_name, description in objects.items():
            self.generate_tile(obj_name, description)

    def generate_all(self):
        """Generate complete asset pack."""
        print("\n" + "="*80)
        print("MY KINGDOM - CHATGPT TILE GENERATION")
        print("="*80)

        self.generate_terrain_tiles()
        self.generate_objects()

        print("\n" + "="*80)
        print("GENERATION COMPLETE!")
        print(f"Assets saved to: {self.assets_dir}")
        print("="*80 + "\n")


def main():
    """Main function to run the generator."""
    print("ChatGPT Tile Generator")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("\nNo OpenAI API key found!")
        print("\nPlease set your API key in one of these ways:")
        print("1. Set environment variable: OPENAI_API_KEY=your-key-here")
        print("2. Or enter it now:")
        api_key = input("Enter your OpenAI API key: ").strip()

        if not api_key:
            print("No API key provided. Exiting.")
            return

    # Create generator
    generator = ChatGPTTileGenerator(api_key=api_key)

    # Generate all assets
    generator.generate_all()


if __name__ == "__main__":
    main()
