# Sprite Pathfinding & Movement - Research Summary

## Research Date: 2026-01-02
## For: My Kingdom Game Development

---

## Executive Summary

This research analyzes how three successful colony simulation games handle sprite movement, pathfinding, and resource gathering:

1. **Dwarf Fortress**: Perfect pathfinding, traffic system, designation-based tasks
2. **RimWorld**: Performance-optimized pathfinding, priority-based work system
3. **Songs of Syx**: Building-based employment, odd jobbers for construction

---

## Key Findings

### Pathfinding Approaches

| Game | Algorithm | Philosophy | Pros | Cons |
|------|-----------|-----------|------|------|
| **Dwarf Fortress** | A* (perfect) | "Always find optimal path" | Perfect paths, predictable | Can lag with many units |
| **RimWorld** | A* (waypoint-based) | "Good enough, fast enough" | Better FPS, scales well | Suboptimal long paths |
| **My Kingdom** | A* (current) | Simple implementation | Works for small maps | May need optimization |

---

## Resource Gathering Workflows

### Dwarf Fortress
```
1. Player designates area (rectangle drag)
2. Designation persists (trees marked brown)
3. Workers with correct labor auto-work on designations
4. Materials hauled to stockpiles
5. Designation completes when all work done
```

**Strengths:**
- ✅ Clear visual feedback
- ✅ Persistent designations
- ✅ No micromanagement after designation

**Weaknesses:**
- ❌ Requires player designation
- ❌ Can't "set and forget" gathering

---

### RimWorld
```
1. System auto-assigns work based on priorities
2. Colonists with high hauling priority auto-haul
3. Player can manually prioritize specific items
4. Work completes all Priority 1 before Priority 2
```

**Strengths:**
- ✅ Minimal micromanagement
- ✅ Flexible priority system
- ✅ Manual override available

**Weaknesses:**
- ❌ Priority system can be confusing
- ❌ "All-or-nothing" priority behavior
- ❌ Less direct control

---

### Songs of Syx
```
1. Construct buildings (farm, workshop, etc.)
2. Assign workers to buildings
3. Workers continuously work at building
4. "Odd jobbers" (unassigned) build & haul when needed
```

**Strengths:**
- ✅ Clear worker roles
- ✅ Automatic continuous work
- ✅ Building-centric design

**Weaknesses:**
- ❌ Requires building infrastructure
- ❌ Less flexible for open-world gathering

---

## Recommended Implementation for My Kingdom

### Phase 1: Current System (DONE ✅)

**What you have:**
- A* pathfinding
- Auto-gathering from nearest trees
- Walk to tree → gather → return to wagon → repeat

**Pros:** Simple, works, easy to understand

**Cons:** No player control, citizens wander

---

### Phase 2: Area Designation System (RECOMMENDED)

**Implement rectangle-drag designation:**

```python
# 1. Add Designation Mode
class DesignationMode(Enum):
    NONE = 0
    CHOP_TREES = 1
    MINE_STONE = 2
    GATHER_BERRIES = 3

# 2. Rectangle Selection
class DesignationTool:
    def on_key_press(self, key):
        if key == 'D':  # Enter designation mode
            self.mode = DesignationMode.CHOP_TREES

    def on_mouse_drag(self, start, end):
        # Draw rectangle
        # Convert screen coords to world coords
        # Find all trees in rectangle

    def on_mouse_release(self):
        # Mark all selected trees as "designated"
        for tree in selected_trees:
            tree.designated_for_chopping = True
```

**Result:**
- Player clicks 'D' for designation mode
- Selects "Chop Trees"
- Drags rectangle over forest
- Citizens automatically chop designated trees
- Clear visual feedback (trees turn brown/highlighted)

---

### Phase 3: Work Priority System (FUTURE)

**Add RimWorld-style priorities:**

```python
class WorkPriority(Enum):
    CRITICAL = 1    # Do immediately
    HIGH = 2        # Do when no critical work
    NORMAL = 3      # Do when idle
    LOW = 4         # Do only if nothing else

class Citizen:
    work_priorities = {
        'construction': WorkPriority.CRITICAL,
        'hauling': WorkPriority.HIGH,
        'gathering': WorkPriority.NORMAL,
        'crafting': WorkPriority.LOW
    }

    def find_next_task(self):
        for priority in [CRITICAL, HIGH, NORMAL, LOW]:
            task = self.find_task_with_priority(priority)
            if task:
                return task
```

---

## Area Designation Implementation Guide

### Step-by-Step Implementation

**1. Add Mouse Selection State**
```python
# In game.py or input_handler.py
class AreaSelector:
    def __init__(self):
        self.is_selecting = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.designation_type = None

    def start_selection(self, x, y, designation_type):
        self.is_selecting = True
        self.start_x = x
        self.start_y = y
        self.designation_type = designation_type

    def update_selection(self, x, y):
        if self.is_selecting:
            self.end_x = x
            self.end_y = y

    def finish_selection(self):
        if self.is_selecting:
            objects = self.get_objects_in_rect()
            self.apply_designation(objects)
            self.is_selecting = False
```

**2. Convert Screen to World Coordinates**
```python
def screen_to_world(self, screen_x, screen_y):
    # Account for camera offset and tile size
    world_x = int((screen_x + self.camera_x) // TILE_SIZE)
    world_y = int((screen_y + self.camera_y) // TILE_SIZE)
    return (world_x, world_y)
```

**3. Find Objects in Rectangle**
```python
def get_trees_in_rect(self, min_x, min_y, max_x, max_y):
    selected_trees = []

    for resource_node in self.resource_nodes:
        if resource_node.resource_type == ResourceType.TREE:
            if (min_x <= resource_node.x <= max_x and
                min_y <= resource_node.y <= max_y):
                selected_trees.append(resource_node)

    return selected_trees
```

**4. Mark Trees as Designated**
```python
class Resource:
    def __init__(self):
        # ... existing code ...
        self.designated = False  # NEW: Track if designated for gathering

# In job_manager.py
def _find_gathering_task(self, citizen, ...):
    # Find nearest DESIGNATED tree
    available_nodes = [
        node for node in resource_nodes
        if (node.designated and              # NEW: Only designated trees
            not node.is_depleted and
            not node.currently_being_gathered and
            node.resource_type == ResourceType.TREE)
    ]
```

**5. Draw Selection Rectangle**
```python
def draw_selection_rectangle(self, screen):
    if self.area_selector.is_selecting:
        start_screen_x = self.area_selector.start_x
        start_screen_y = self.area_selector.start_y
        end_screen_x = self.area_selector.end_x
        end_screen_y = self.area_selector.end_y

        width = end_screen_x - start_screen_x
        height = end_screen_y - start_screen_y

        # Draw rectangle outline
        pygame.draw.rect(screen, (255, 255, 0),
                        (start_screen_x, start_screen_y, width, height), 2)

        # Draw semi-transparent fill
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(50)
        overlay.fill((255, 255, 0))
        screen.blit(overlay, (start_screen_x, start_screen_y))
```

**6. Add Keyboard Shortcut**
```python
# In game.py handle_events()
elif event.key == pygame.K_d:
    # Enter designation mode
    self.designation_mode = True
    self.selected_designation = DesignationType.CHOP_TREES
    logger.info("Designation mode: Chop Trees")
```

---

## UI Design Mockup

```
┌──────────────────────────────────────────┐
│ My Kingdom                               │
│ [ESC] Menu  [B] Build  [D] Designate     │
├──────────────────────────────────────────┤
│                                          │
│   ┌─────────────────────────┐           │
│   │ Designation Mode        │           │
│   │                         │           │
│   │ [1] Chop Trees          │           │
│   │ [2] Mine Stone (later)  │           │
│   │ [3] Harvest (later)     │           │
│   │                         │           │
│   │ Click and drag to       │           │
│   │ select area.            │           │
│   │                         │           │
│   │ [ESC] Cancel            │           │
│   └─────────────────────────┘           │
│                                          │
│  Game Map Here                           │
│  (Trees turn brown when designated)      │
│  (Selection rectangle shows while drag)  │
│                                          │
└──────────────────────────────────────────┘
```

---

## Performance Optimization Strategies

### From Research

**Dwarf Fortress Lessons:**
- Use traffic costs to guide pathfinding
- Limit search space where possible
- Cache frequently-used paths

**RimWorld Lessons:**
- Use waypoint system for long distances
- Simplify pathfinding for distant targets
- Limit number of paths considered
- Don't recalculate paths every frame

**Recommended for My Kingdom:**

```python
# Path caching
class PathCache:
    def __init__(self, max_age=5.0):  # 5 seconds
        self.cache = {}
        self.max_age = max_age

    def get_path(self, start, goal):
        key = (start, goal)
        if key in self.cache:
            path, timestamp = self.cache[key]
            if time.time() - timestamp < self.max_age:
                return path
        return None

    def store_path(self, start, goal, path):
        key = (start, goal)
        self.cache[key] = (path, time.time())

# Waypoint system for long distances
def find_path_with_waypoints(start, goal):
    distance = calculate_distance(start, goal)

    if distance < 30:
        # Short distance: use accurate A*
        return astar(start, goal)
    else:
        # Long distance: use waypoints
        waypoints = []
        current = start

        while distance_to_goal(current, goal) > 30:
            waypoint = move_toward(current, goal, distance=25)
            waypoints.append(waypoint)
            current = waypoint

        waypoints.append(goal)
        return waypoints
```

---

## Code Examples for Implementation

### Complete Designation System Example

```python
# designation.py
from enum import Enum
from dataclasses import dataclass
from typing import List

class DesignationType(Enum):
    CHOP_TREES = "chop_trees"
    MINE_STONE = "mine_stone"
    HARVEST_PLANTS = "harvest_plants"

@dataclass
class Designation:
    designation_type: DesignationType
    objects: List  # List of designated objects (trees, stones, etc.)
    created_time: float
    completed: bool = False

    def cancel(self):
        """Cancel this designation and unmark all objects."""
        for obj in self.objects:
            obj.designated = False
        self.completed = True

class DesignationManager:
    def __init__(self):
        self.designations: List[Designation] = []

    def add_designation(self, designation_type, objects):
        """Create a new designation."""
        designation = Designation(
            designation_type=designation_type,
            objects=objects,
            created_time=time.time()
        )

        # Mark all objects as designated
        for obj in objects:
            obj.designated = True

        self.designations.append(designation)
        return designation

    def update(self):
        """Remove completed designations."""
        self.designations = [
            d for d in self.designations
            if not d.completed and any(not obj.is_depleted for obj in d.objects)
        ]

        # Auto-complete if all objects depleted
        for designation in self.designations:
            if all(obj.is_depleted for obj in designation.objects):
                designation.completed = True

    def get_active_designations(self, designation_type=None):
        """Get all active designations of a specific type."""
        result = [d for d in self.designations if not d.completed]

        if designation_type:
            result = [d for d in result if d.designation_type == designation_type]

        return result
```

---

## Visual Feedback Guidelines

### Designated Objects
- **Trees**: Brown/orange tint overlay
- **Stones**: Gray tint overlay
- **Plants**: Green tint overlay

### Selection Rectangle
- **Outline**: Bright yellow, 2px thick
- **Fill**: Semi-transparent yellow (alpha=50)
- **Corners**: Small corner indicators

### Citizen Status
- **Walking to resource**: White circle
- **Gathering/Working**: Yellow circle
- **Carrying resource**: Blue circle
- **Walking to wagon**: Blue circle

### Counter Display
```
Wood: 24 (+4)  ← Shows current + what's being carried
Stone: 12
Food: 8
```

---

## Testing Checklist

### Area Designation
- [ ] Can enter designation mode (D key)
- [ ] Can drag rectangle on screen
- [ ] Rectangle shows during drag
- [ ] Trees turn brown when designated
- [ ] Can designate multiple areas
- [ ] Can cancel designation (ESC)

### Citizen Behavior
- [ ] Citizens move to designated trees
- [ ] Citizens ignore non-designated trees
- [ ] Citizens use pathfinding to reach trees
- [ ] Citizens carry wood back to wagon
- [ ] Wood counter increases by 4 per tree
- [ ] Citizens find next designated tree automatically

### Performance
- [ ] No lag with 5 citizens
- [ ] No lag with 10+ designated trees
- [ ] Pathfinding works smoothly
- [ ] No infinite loops

---

## Next Steps Roadmap

### Immediate (Phase 2)
1. ✅ Implement rectangle selection
2. ✅ Add tree designation
3. ✅ Update job_manager to use designated trees
4. ✅ Add visual feedback (brown trees)

### Short Term
5. Add "cancel designation" feature
6. Add designation counter UI
7. Add keyboard shortcuts (1-9 for different designations)

### Medium Term
8. Add stone designation
9. Add berry gathering designation
10. Improve pathfinding performance

### Long Term
11. Add work priority system
12. Add citizen work preferences
13. Add designation templates (save/load common patterns)

---

## Sources & References

- **Dwarf Fortress Wiki**: Path, Traffic, Designations
- **RimWorld Wiki**: Work system, Hauling
- **Songs of Syx Wiki**: Workforce, Citizens
- **Game Dev Forums**: Unity, Unreal pathfinding discussions
- **My Kingdom Codebase**: Current implementation analysis

---

## Conclusion

The research shows three successful but different approaches:

**Dwarf Fortress**: Player-controlled designations, perfect pathfinding
**RimWorld**: Automated priorities, performance-focused pathfinding
**Songs of Syx**: Building-centric, role-based workers

**For My Kingdom, I recommend:**
- Start with **Dwarf Fortress-style designations** (clear, intuitive)
- Use **RimWorld-style optimization** (performance over perfection)
- Keep **Songs of Syx simplicity** (easy to understand)

This hybrid approach will give you:
- ✅ Player control over what gets gathered
- ✅ Visual feedback of designations
- ✅ Automatic worker assignment
- ✅ Good performance
- ✅ Modular system (easy to add stone, berries, etc.)
