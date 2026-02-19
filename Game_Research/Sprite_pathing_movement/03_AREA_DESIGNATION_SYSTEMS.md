# Area Designation Systems

## Research Date: 2026-01-02

---

## Dwarf Fortress Designation System

### Core Mechanic: Rectangle Selection

**How Players Designate Areas:**

1. **Access designation menu** (press `d`)
2. **Select designation type**:
   - Mine (`d` for mining)
   - Chop Down Trees (`t` for logging)
   - Gather Plants
   - Channel
   - Etc.
3. **Mark first corner** (move cursor, press Enter)
4. **Mark second corner** (move cursor again, press Enter)
5. **Result**: All tiles in rectangle are designated

### 3D Designation (Cuboid)

- Works **across Z-levels**
- Select top-left-front corner
- Select bottom-right-back corner
- Creates a **3-dimensional cuboid** designation
- Extremely powerful for multi-level mining

---

## Tree Chopping Mechanics (Dwarf Fortress)

### Designation Details

**Marking Trees:**
- Select "Chop Down Trees" (`t` when outside/above ground)
- Drag rectangle over forest area
- All trees turn **brown** (designated for chopping)

**Important Rule:**
> Only ONE trunk tile needs designation - any trunk tile will do
> The whole tree will be marked for cutting

**Visual Feedback:**
- Designated trees highlighted in brown
- Clear indication of what will be chopped

### Labor Requirements

**Wood Cutting Labor:**
- Mutually exclusive with mining
- Requires a tool (axe) to be equipped
- Dwarves with wood cutting enabled will automatically chop designated trees

---

## Mining Mechanics (Dwarf Fortress)

### How It Works

**Designation:**
- Select "Mine" (`d` twice for mine)
- Mark rectangular area
- Removes stone/soil walls
- Leaves stone/soil floors
- May leave stone/ore/gems

**Worker Behavior:**
- Miners automatically work on designated tiles
- Work order persists until complete
- Designations can be cancelled

---

## RimWorld Hauling & Work System

### Automatic vs Manual Designation

**Automatic Hauling:**
- Colonists with "Haul" enabled auto-haul items
- Items moved to appropriate stockpiles
- No player designation needed for most hauling

**Manual Priority:**
1. Select colonist
2. Right-click on item
3. Choose "Prioritize hauling"
4. Colonist immediately performs that haul

### Priority System Interaction

**Key Rule:**
> Priority 1 work will complete ALL available tasks before moving to Priority 2

**Example Problem:**
```
Colonist has:
- Hauling: Priority 1
- Building: Priority 2

Result:
- Hauls every single item on the map
- Only then starts building
- Can cause inefficiency
```

**Better Approach:**
```
Multi-role colonist:
- Main job (mining/farming): Priority 1
- Hauling: Priority 2

Result:
- Complete main job → Haul results → Next main job
```

---

## Songs of Syx Work Assignment

### Employment System

**Building-Based Assignment:**
- Construct buildings (farm, workshop, etc.)
- **Assign employees** to buildings
- Workers continuously perform jobs at that building
- Only stop for needs/wants

### Odd Jobbers (Unassigned Workers)

**What they do:**
- Idle until given a command
- **Construct** things when designated
- **Haul** things to stockpiles
- **Hunt** designated targets

**Behavior:**
- Wander around settlement
- Look for odd jobs
- Don't have permanent workplace

### Work Priority System

**Customizable Priorities:**
- Set priority by **race/species**
- 4 major categories:
  - Agriculture
  - Crafting
  - Services
  - Administration
- Slide bars for detailed preferences

**Race-Based Optimization:**
- Assign races to jobs matching their strengths
- Some races better at farming
- Some races better at crafting
- Maximize efficiency through specialization

---

## Area Selection Implementation (Generic)

### Basic Rectangle Selection Algorithm

```
1. Mouse Down Event:
   - Record starting position (start_x, start_y)
   - Begin selection mode

2. Mouse Drag Event:
   - Update current position (current_x, current_y)
   - Calculate rectangle bounds:
     * min_x = min(start_x, current_x)
     * min_y = min(start_y, current_y)
     * max_x = max(start_x, current_x)
     * max_y = max(start_y, current_y)
   - Draw selection rectangle on screen

3. Mouse Up Event:
   - Finalize selection
   - Find all objects within rectangle
   - Apply designation to selected objects
   - Clear selection visual
```

### Coordinate Space Conversion

**Challenge:**
- Selection rectangle is in **screen space** (pixels)
- Game objects are in **world space** (tiles/coordinates)

**Solution:**
```python
def screen_to_world(screen_x, screen_y, camera_x, camera_y, tile_size):
    world_x = (screen_x + camera_x) // tile_size
    world_y = (screen_y + camera_y) // tile_size
    return (world_x, world_y)
```

### Contains Check

**Detect objects in rectangle:**
```python
def rect_contains(rect_min_x, rect_min_y, rect_max_x, rect_max_y, obj_x, obj_y):
    return (rect_min_x <= obj_x <= rect_max_x and
            rect_min_y <= obj_y <= rect_max_y)
```

---

## Visual Feedback Best Practices

### During Selection
- **Draw rectangle outline** (usually white or yellow)
- **Semi-transparent fill** (low opacity)
- **Real-time update** as mouse moves

### After Selection
- **Highlight selected objects** (change color)
- **Show count** ("15 trees selected for chopping")
- **Confirmation feedback** (sound effect, animation)

### Cancelled Selection
- **Clear visuals** immediately
- **Reset selection state**
- **No changes to game state**

---

## Implementation for My Kingdom

### Recommended Approach

**Phase 1: Basic Rectangle Selection**
```python
class AreaSelector:
    def __init__(self):
        self.selecting = False
        self.start_pos = None
        self.current_pos = None

    def on_mouse_down(self, x, y):
        self.selecting = True
        self.start_pos = (x, y)

    def on_mouse_drag(self, x, y):
        if self.selecting:
            self.current_pos = (x, y)

    def on_mouse_up(self, x, y):
        if self.selecting:
            self.current_pos = (x, y)
            selected_objects = self.get_objects_in_rect()
            self.apply_designation(selected_objects)
            self.selecting = False

    def get_rect_bounds(self):
        if not self.start_pos or not self.current_pos:
            return None

        x1, y1 = self.start_pos
        x2, y2 = self.current_pos

        return {
            'min_x': min(x1, x2),
            'min_y': min(y1, y2),
            'max_x': max(x1, x2),
            'max_y': max(y1, y2)
        }
```

**Phase 2: Designation Types**
```python
class DesignationType(Enum):
    CHOP_TREES = "chop_trees"
    MINE_STONE = "mine_stone"
    GATHER_BERRIES = "gather_berries"
    BUILD_ZONE = "build_zone"

class Designation:
    def __init__(self, type, objects):
        self.type = type
        self.objects = objects
        self.completed = False

    def cancel(self):
        for obj in self.objects:
            obj.undesignate()
```

**Phase 3: Worker Assignment**
```python
# Citizens automatically work on designated tasks
def find_task_for_citizen(citizen):
    # Find nearest designation matching citizen's skills
    for designation in active_designations:
        if designation.type == DesignationType.CHOP_TREES:
            if citizen.can_chop_trees:
                nearest_tree = get_nearest_designated_tree(citizen, designation)
                return ChopTreeTask(nearest_tree)

    return None
```

---

## UI Mockup for My Kingdom

```
┌─────────────────────────────────────┐
│  [D] Designation Mode               │
│  ┌─────────────────────────────┐    │
│  │ [1] Chop Trees              │    │
│  │ [2] Mine Stone              │    │
│  │ [3] Gather Berries          │    │
│  │ [4] Build Zone              │    │
│  └─────────────────────────────┘    │
│                                     │
│  Instructions:                      │
│  - Click designation type           │
│  - Click and drag on map            │
│  - Release to confirm               │
│  - ESC to cancel                    │
└─────────────────────────────────────┘
```

---

## Comparison Table

| Feature | Dwarf Fortress | RimWorld | Songs of Syx | My Kingdom (Proposed) |
|---------|---------------|-----------|--------------|----------------------|
| **Area Selection** | Rectangle drag | Manual click | Auto-assign | Rectangle drag |
| **Designation Types** | Many (mine, chop, gather, etc.) | Zones + manual | Building assignment | Start with chop/gather |
| **Worker Assignment** | Automatic by labor | Automatic by priority | Building-based | Automatic (nearest) |
| **Visual Feedback** | Color highlight | Overlay zones | UI indicators | Color highlight |
| **Cancellation** | Click designation, cancel | Delete zone | Un-assign | ESC or right-click |

---

## Sources
- Dwarf Fortress Wiki - Designations Menu
- RimWorld Wiki - Work System
- Songs of Syx Wiki - Workforce
- Game development tutorials on area selection
- Unity/Unreal community discussions
