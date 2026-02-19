"""
Create simple placeholder tiles for testing the world system.
These are basic colored squares - you can replace them with AI-generated tiles later.
"""

from PIL import Image, ImageDraw
from pathlib import Path

def create_placeholder_tile(name, color, size=32):
    """Create a simple colored tile with border."""
    # Create image
    img = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(img)

    # Add border
    draw.rectangle([0, 0, size-1, size-1], outline=(0, 0, 0), width=1)

    # Save
    output_dir = Path("assets/images/world")
    output_dir.mkdir(parents=True, exist_ok=True)
    img.save(output_dir / f"{name}.png")
    print(f"Created: {name}.png")

def create_all_placeholders():
    """Create all placeholder tiles."""
    print("Creating placeholder tiles...")
    print("=" * 60)

    # Terrain tiles
    create_placeholder_tile("grass", (34, 139, 34))  # Green
    create_placeholder_tile("grass_flowers", (50, 155, 50))  # Lighter green
    create_placeholder_tile("dirt", (139, 69, 19))  # Brown
    create_placeholder_tile("desert_sand", (238, 214, 175))  # Sand
    create_placeholder_tile("stone_gray", (128, 128, 128))  # Gray
    create_placeholder_tile("water_shallow", (100, 150, 255))  # Light blue
    create_placeholder_tile("water_deep", (30, 90, 200))  # Dark blue
    create_placeholder_tile("forest_floor", (45, 25, 0))  # Dark brown

    # Objects (larger)
    create_placeholder_tile("tree_oak", (0, 100, 0), size=64)  # Dark green
    create_placeholder_tile("tree_pine", (0, 80, 0), size=64)  # Darker green
    create_placeholder_tile("rock_large", (100, 100, 100), size=64)  # Gray
    create_placeholder_tile("bush_green", (50, 120, 50), size=64)  # Green
    create_placeholder_tile("house_small", (150, 100, 50), size=64)  # Brown
    create_placeholder_tile("well", (120, 120, 120), size=64)  # Light gray

    print("=" * 60)
    print("Done! Placeholder tiles created in assets/images/world/")
    print("\nThese are simple colored squares for testing.")
    print("You can generate proper AI tiles later when you add")
    print("credits to your OpenAI account.")

if __name__ == "__main__":
    create_all_placeholders()
