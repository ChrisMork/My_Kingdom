# View System Guide - My Kingdom

## Three-Tier View System

Inspired by Songs of Syx, the game now has three distinct view levels that you can switch between. **Buildings can ONLY be placed in the LOCAL view.**

### View Levels

#### 1. World View (150x150 tiles) - F1
- **Purpose**: See the entire generated world
- **What you see**: Biome-colored tiles showing the full world map
- **What you can do**:
  - Explore the entire world
  - See biome distribution
  - Plan future expansion
- **What you CANNOT do**: Build buildings (view only)

#### 2. Region View (80x80 tiles) - F2
- **Purpose**: See a mid-level regional overview
- **What you see**: The region around your starting location
- **What you can do**:
  - Explore your local region
  - See surrounding terrain
  - Plan expansion within the region
- **What you CANNOT do**: Build buildings (view only)

#### 3. Local View (100x100 tiles) - F3 ✅ **BUILDING ENABLED**
- **Purpose**: The playable area where you build your kingdom
- **What you see**: Detailed terrain with forests, grass, water, etc.
- **What you can do**:
  - **Place buildings** (ONLY in this view!)
  - See citizens working
  - See buildings being constructed
  - Manage your settlement
- **This is the ONLY view where building is allowed**

## Controls

### View Switching

| Key | Action |
|-----|--------|
| **TAB** | Cycle through views (Local → Region → World → Local) |
| **F1** | Jump directly to World View |
| **F2** | Jump directly to Region View |
| **F3** | Jump directly to Local View (building area) |

### Movement (All Views)
- **WASD** or **Arrow Keys**: Move camera
- Camera position is preserved when switching views

## UI Indicators

### View Indicator
The second line of the UI shows your current view:
- **Green text**: `View: LOCAL 100x100 (Building Enabled)` - You can build here!
- **Orange text**: `View: REGION 80x80 (View Only - Press F3 for Local)` - Cannot build
- **Orange text**: `View: WORLD 150x150 (View Only - Press F3 for Local)` - Cannot build

### Building Mode Warning
If you toggle building mode ([B]) while NOT in local view:
- **Red warning**: `BUILDING MODE: Switch to LOCAL view (F3) to place buildings!`
- You must press **F3** to switch to local view before you can place buildings

## How It Works

### Camera System
Each view has its own independent camera position:
- `world_camera_x/y` - Remembers where you were in world view
- `region_camera_x/y` - Remembers where you were in region view
- `local_camera_x/y` - Remembers where you were in local view

When you switch views, your camera position is saved and restored when you return.

### Building Restriction
The `place_building()` method now checks:
```python
if self.current_view != "local":
    logger.warning("Cannot place buildings in {view} view - switch to local view first!")
    return False
```

This ensures buildings can only be placed in the local playable area.

## Example Usage

### Exploring the World
1. Start in local view (default)
2. Press **TAB** or **F2** to see region view
3. Press **TAB** or **F1** to see the full world map
4. Move around with **WASD** to explore
5. Press **F3** to return to local view

### Building After Exploring
1. You're in world view looking at the map
2. Press **[B]** to toggle building mode
3. **UI shows red warning**: Cannot build in world view
4. Press **F3** to switch to local view
5. **UI turns green**: Building enabled!
6. Press **[1-8]** to select building
7. **Click** to place building

## Implementation Details

### View State (`game_state.py`)
```python
self.current_view = "local"  # "world", "region", or "local"
self.world_camera_x = 0
self.world_camera_y = 0
self.region_camera_x = 0
self.region_camera_y = 0
self.local_camera_x = 0
self.local_camera_y = 0
```

### View Methods
- `switch_to_world_view()` - Switch to 150x150 world map
- `switch_to_region_view()` - Switch to 80x80 region
- `switch_to_local_view()` - Switch to 100x100 playable area
- `can_build_here()` - Returns True only if in local view

### Rendering
The game automatically renders the appropriate tiles based on current view:
- **World view**: Simple biome-colored rectangles (fast rendering)
- **Region view**: Biome-colored tiles
- **Local view**: Detailed terrain with CozyRenderer, buildings, and citizens

## Benefits

### Performance
- World and region views use simple rendering (just colored rectangles)
- Detailed rendering only happens in local view
- Citizens and buildings only update/render in local view

### Organization
- Keep the playable area manageable (100x100)
- See the bigger picture with world/region views
- Plan expansion without getting lost

### Songs of Syx Inspiration
This three-tier system is directly inspired by Songs of Syx's approach:
- World map for global perspective
- Region map for mid-level planning
- Local map for detailed gameplay

## Summary

✅ **You can build ONLY in LOCAL view (F3)**
- World view (F1): See the entire 150x150 world - View only
- Region view (F2): See the 80x80 regional area - View only
- Local view (F3): The 100x100 playable area - **Building enabled!**

Press **TAB** to cycle through views, or **F1/F2/F3** to jump directly to a specific view.

---

*View System implemented: 2026-01-01*
*Building restriction: LOCAL view only*
