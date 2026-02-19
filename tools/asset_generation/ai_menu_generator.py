"""
Generate professional main menu graphics using AI image generation.
Uses free AI APIs to create beautiful pixel art / game art.
"""

import requests
import urllib.parse
from pathlib import Path
from PIL import Image
import io


def generate_ai_image(prompt, width=1280, height=720, style="pixel-art"):
    """
    Generate an image using Pollinations.ai (free, unlimited, no API key needed).

    Args:
        prompt: Description of what to generate
        width: Image width
        height: Image height
        style: Art style modifier
    """

    # Add style to prompt
    full_prompt = f"{prompt}, {style} style, high quality, detailed"

    # URL encode the prompt
    encoded_prompt = urllib.parse.quote(full_prompt)

    # Pollinations.ai API endpoint (completely free!)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&enhance=true"

    print(f"Generating AI image with prompt: {prompt}")
    print(f"Using Pollinations.ai API...")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Convert to PIL Image
        img = Image.open(io.BytesIO(response.content))
        return img

    except Exception as e:
        print(f"Error generating image: {e}")
        return None


def generate_menu_assets_with_ai():
    """Generate all menu assets using AI."""

    print("=" * 70)
    print("AI-POWERED MENU ASSET GENERATOR")
    print("Using free Pollinations.ai API (powered by Stable Diffusion)")
    print("=" * 70)

    assets_dir = Path(__file__).parent.parent.parent / "assets" / "images" / "menu"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Define what we want to generate
    assets_to_generate = [
        {
            "name": "castle_background.png",
            "prompt": "Medieval fantasy castle background, distant mountains, blue sky, grass foreground, peaceful atmosphere, game art",
            "width": 1280,
            "height": 720,
            "style": "pixel art, 16-bit game graphics"
        },
        {
            "name": "oak_tree.png",
            "prompt": "Large oak tree with thick trunk and lush green canopy, detailed bark texture, side view with transparent background",
            "width": 800,
            "height": 720,
            "style": "pixel art, game sprite, transparent background"
        },
        {
            "name": "knight_resting.png",
            "prompt": "Medieval knight in full plate armor sitting and leaning back, holding sword, kite shield nearby, relaxed pose, red surcoat with gold cross, transparent background",
            "width": 300,
            "height": 350,
            "style": "pixel art, RPG character sprite, detailed armor"
        },
        {
            "name": "campfire.png",
            "prompt": "Campfire with orange flames, glowing embers, stone ring, burning logs, warm light, transparent background",
            "width": 200,
            "height": 250,
            "style": "pixel art, game sprite, animated fire effect"
        },
    ]

    print(f"\nGenerating {len(assets_to_generate)} assets...\n")

    for i, asset in enumerate(assets_to_generate, 1):
        print(f"[{i}/{len(assets_to_generate)}] Generating {asset['name']}...")
        print(f"    Prompt: {asset['prompt']}")

        img = generate_ai_image(
            prompt=asset['prompt'],
            width=asset['width'],
            height=asset['height'],
            style=asset['style']
        )

        if img:
            output_path = assets_dir / asset['name']

            # Convert RGBA if needed (for transparency)
            if img.mode != 'RGBA' and 'transparent' in asset['prompt']:
                img = img.convert('RGBA')

            img.save(output_path)
            print(f"    ✓ Saved to {output_path}")
        else:
            print(f"    ✗ Failed to generate {asset['name']}")

        print()

    print("=" * 70)
    print("AI asset generation complete!")
    print(f"Assets saved to: {assets_dir}")
    print("=" * 70)


def generate_complete_menu_scene():
    """Generate a complete menu scene in one image."""

    print("=" * 70)
    print("GENERATING COMPLETE MENU SCENE WITH AI")
    print("=" * 70)

    assets_dir = Path(__file__).parent.parent.parent / "assets" / "images" / "menu"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Create a comprehensive prompt for the entire scene
    prompt = """
    Medieval fantasy game main menu screen artwork, pixel art style:
    - Large oak tree on the left side with thick brown trunk and lush green canopy
    - Knight in shiny plate armor leaning against the tree, sitting down relaxing
    - Small campfire with orange flames nearby
    - Distant medieval castle in the background with towers
    - Blue sky and green grass
    - Peaceful, cozy atmosphere
    - Professional game art quality
    - 16-bit RPG style
    """

    print(f"\nPrompt: {prompt}\n")
    print("Generating complete scene...")

    img = generate_ai_image(
        prompt=prompt,
        width=1280,
        height=720,
        style="pixel art, retro game, stardew valley style, professional"
    )

    if img:
        output_path = assets_dir / "complete_menu_scene.png"
        img.save(output_path)
        print(f"\n✓ Complete scene saved to: {output_path}")
        print("\nYou can use this as a single background image for your menu!")
    else:
        print("\n✗ Failed to generate complete scene")


if __name__ == "__main__":
    import sys

    print("\nWhat would you like to generate?")
    print("1. Individual assets (tree, knight, campfire, castle)")
    print("2. Complete menu scene (single image)")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        generate_menu_assets_with_ai()
    elif choice == "2":
        generate_complete_menu_scene()
    elif choice == "3":
        generate_complete_menu_scene()
        print("\n")
        generate_menu_assets_with_ai()
    else:
        print("Invalid choice. Generating complete scene by default...")
        generate_complete_menu_scene()
