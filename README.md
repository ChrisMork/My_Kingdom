# My Kingdom

A peaceful medieval city-building game with a relaxing, positive vibe.

## Features

- **Huge Procedural World**: Each game creates a massive 500x500 tile world (250,000 tiles!) with varied terrain including grass, forests, water, sand, and stone
- **Beautiful Graphics**: Stunning top-down visuals inspired by modern hero games
  - Rich, vibrant color palette with color variation per tile
  - Animated water with shimmer and wave effects
  - Detailed forest rendering with visible trees (zoom dependent)
  - Textured terrain with shadows, highlights, and depth
  - Dynamic lighting effects and smooth gradients
- **Zoom Controls**: Smoothly zoom in and out from 25% to 200% to see your entire kingdom or focus on details
- **Medieval Theme**: Warm, inviting color palette with a parchment-style aesthetic
- **Relaxing Gameplay**: Build your kingdom at your own pace with peaceful animations
- **Full Logging**: All game events are logged to the Logs folder for debugging and tracking

## Getting Started

### Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

Simply double-click `main.py` or run:
```bash
python main.py
```

## Controls

- **Arrow Keys** or **WASD**: Move camera around the world (speed adjusts with zoom level)
- **Mouse Wheel**: Zoom in (scroll up) and zoom out (scroll down)
- **B Key**: Toggle Building Mode (shows grid overlay for precise building placement)
- **ESC**: Return to main menu
- **Mouse**: Click menu buttons

### Zoom Levels
- **Zoom Out (25%)**: See the entire world at once - perfect for planning your kingdom
- **Normal (100%)**: Default view with clear tile details
- **Zoom In (200%)**: Close-up view for detailed work

### Building Mode
Press **B** to toggle Building Mode, which overlays a subtle grid on the world. This helps you:
- See exact tile boundaries
- Plan building placement precisely
- Align structures perfectly
- The grid automatically hides when you toggle Building Mode off for a seamless landscape view

## Project Structure

```
My-KingdomVersion 3/
├── main.py                 # Game entry point - double-click to start!
├── requirements.txt        # Python dependencies
├── Logs/                   # Game logs (auto-generated)
├── config/
│   └── settings.py        # Game configuration
├── src/
│   ├── core/
│   │   ├── logger.py      # Logging system
│   │   └── game.py        # Main game state
│   ├── ui/
│   │   └── menu.py        # Main menu
│   └── world/
│       ├── terrain.py     # Terrain types and tiles
│       ├── generator.py   # Procedural world generation
│       └── renderer.py    # Advanced tile rendering with effects
└── assets/                # Future: images, fonts, sounds
```

## Development Roadmap

- [x] Main menu system
- [x] Huge procedural world generation (500x500 tiles)
- [x] Camera controls with zoom functionality
- [x] Beautiful top-down graphics with effects
- [x] Advanced tile rendering system
- [x] Animated water and environmental effects
- [x] Logging system
- [ ] Building placement
- [ ] Resource management
- [ ] Population system
- [ ] Save/Load functionality
- [ ] Custom art assets
- [ ] Sound and music

## Visual Features

The game now features a gorgeous top-down aesthetic similar to popular mobile hero games with **seamless terrain blending**:

- **Grass**: Multiple shades of rich green with subtle texture patches that blend smoothly into neighboring terrains
- **Water**: Animated with gentle waves, sparkling shimmer effects, and smooth shorelines that transition naturally to land
- **Forests**: Dense tree coverage with visible tree crowns and trunks when zoomed in, edges blend naturally into surrounding grassland
- **Sand**: Beach-like texture with grainy detail that creates soft transitions to water and grass
- **Stone**: Rocky mountainous terrain with cracks and 3D depth
- **Dirt**: Rich soil with visible clumps and variation

### Clean Biome-Based Rendering
The game features **clean, uniform biomes** with minimal color variation:
- **Uniform terrain regions**: Grasslands appear as one solid green area, forests as dark green blocks, water as blue regions
- **No visible tiles**: Each terrain type looks like one continuous painted region
- **Minimal variation**: Only 2-4 RGB values difference within same terrain types for subtle texture
- **Clean boundaries**: Sharp, clear edges between different terrain types (no blending)
- **Painted map aesthetic**: The world looks like a professional game map with distinct terrain regions
- **Slower water**: Peaceful, gentle water animation (70% slower) for a relaxing vibe

## Logs

All game events are automatically logged to timestamped files in the `Logs/` folder. Check these logs for debugging or to see detailed game statistics like terrain distribution.

---

Built with love and Python!
