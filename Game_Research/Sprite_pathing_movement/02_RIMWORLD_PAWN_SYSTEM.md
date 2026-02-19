# RimWorld - Pawn Movement & Job System

## Research Date: 2026-01-02

---

## Pathfinding System

### Performance-Optimized Approach

RimWorld uses **less accurate pathfinding** compared to Dwarf Fortress, prioritizing **game performance** over perfect paths.

### Waypoint-Based Navigation

**How it works:**
- Pawns path to an **imaginary waypoint** ~20 tiles away in the direction of their target
- When they reach the waypoint, they **repath** to the next waypoint
- This continues until they reach the final destination

**Why this approach:**
- Reduces calculation time
- Prevents FPS drops
- Good enough for most situations

---

## Simplified Long-Distance Pathfinding

### Distance-Based Heuristics

**For paths >30 tiles:**
- Uses an **alternate heuristic** that's faster but less accurate
- Results in "zig-zag" diversions around corners and doorways
- **Ignores terrain movement penalties** (except water)
- Faster calculation = better performance

**For paths <30 tiles:**
- More accurate pathfinding
- Considers terrain costs
- Better path quality for nearby destinations

---

## Path Calculation Strategy

### Selection Algorithm

Instead of finding the **perfect** path:
1. Pawn considers **a few possible paths**
2. Picks the **fastest one from the selection**
3. Doesn't exhaustively search all possibilities

### Weight-Based System
- Each tile has a **movement cost weight**
- Algorithm applies weight to squares
- Uses "least-squares" approach to find path
- Balances speed vs accuracy

---

## Environmental Factors

### Light & Weather Effects

**Important Implementation Detail:**
- Pawns move slower in **darkness**
- Pawns move slower in **rain**
- Vanilla algorithm uses light/weather at **starting position** for entire path
  - This is a performance optimization
  - Path calculated once, not continuously updated

### Terrain Costs
- **Roads**: Fastest movement
- **Grass/Dirt**: Normal speed
- **Mud/Marsh**: Slower movement
- **Water**: Very slow or impassable
- **Debris/Rubble**: Slower movement

---

## Work & Job System

### Work Priority Levels

**Manual Priority Mode:**
- Each work type can be prioritized **1 (highest) to 4 (lowest)**
- For same priority: **Left-to-right** task order

**Critical Rule:**
> All available work of one priority must be completed before moving to the next priority

**Example Problem:**
- If Hauling = Priority 1
- Pawn will haul **every single object** (even across the map)
- Before doing any Priority 2+ tasks

### Work Type Hierarchy

Tasks within each work-type have internal priorities:
- Higher tasks in the list = done first
- Lower tasks = done later

---

## Hauling System (Resource Gathering)

### Automatic Hauling

**How it works:**
- Largely **automatic** - no player micro-management needed
- Pawns with "Haul" enabled will periodically look for things to haul
- Items are moved to stockpiles based on stockpile rules

### Manual Prioritization

**Player can override:**
1. Select a pawn
2. Right-click target item
3. Choose "Prioritize hauling"
4. Pawn immediately goes to haul that specific item

### Animal Haulers

**Different behavior than human haulers:**
- Animals trained to haul work **occasionally**
- **Mean time**: 1.5 hours between haul tasks
- Not as reliable as human haulers

---

## Stockpile Priority System

### Important Distinction

**Common Misconception:**
> Stockpile priority does NOT affect hauling order

**How it actually works:**
- Priority determines **which stockpile** item goes to
- NOT the **order** in which items are hauled
- Critical stockpile ≠ hauled first
- Normal stockpile ≠ hauled last

**Use Case:**
- High priority stockpile near crafting bench
- Low priority stockpile at edge of map
- Items go to high priority first (when both accept the item type)

---

## Best Practices for Resource Gathering

### Work Priority Configuration

**For multi-role colonists:**
- Main job (mining/cooking/farming): Priority 1
- Hauling: Priority 2

**Result:**
- Mine all the ore → haul it all → move to next task
- Cook all meals → haul them → move to next task
- Prevents constant task-switching

---

## Job Queueing System

### Visible Job Queue

- **Inspect pane** shows queued jobs for each colonist
- Jobs process in order
- **Shift+Click** to chain multiple tasks together

### Task Chaining Example:
```
Shift+Click Task Flow:
1. Mine ore at location A
2. Haul ore to stockpile
3. Mine ore at location B
4. Haul ore to stockpile
5. Return to other duties
```

---

## Implementation Lessons for My Kingdom

### What to Adopt:

1. ✅ **Waypoint System**: Break long paths into shorter segments
2. ✅ **Distance-Based Optimization**: Use simpler pathfinding for far targets
3. ✅ **Priority System**: Implement 1-4 priority levels for tasks
4. ✅ **Manual Override**: Allow player to force-assign specific tasks
5. ✅ **Automatic Hauling**: Citizens auto-haul when idle

### What to Avoid:

1. ❌ **All-or-nothing priorities**: Don't make Priority 1 block everything
2. ❌ **Complex stockpile systems**: Keep it simple initially
3. ❌ **Perfect pathfinding**: Don't sacrifice performance for perfection

### Recommended Implementation:

```python
# Pathfinding Tiers
def find_path(start, goal):
    distance = calculate_distance(start, goal)

    if distance < 30:
        # Accurate A* pathfinding
        return accurate_astar(start, goal)
    else:
        # Waypoint-based simplified pathfinding
        waypoint = get_waypoint_toward(goal, distance=20)
        return simple_path(start, waypoint)

# Job Priority System
class Citizen:
    def get_next_task(self):
        # Priority 1: Construction
        if task := find_construction_task():
            return task

        # Priority 2: Hauling materials to buildings
        if task := find_hauling_task():
            return task

        # Priority 3: Gathering resources
        if task := find_gathering_task():
            return task

        # Priority 4: Idle / wander
        return None
```

---

## Performance Optimization Lessons

### RimWorld's Approach:
1. **Limit calculation depth** (few paths considered, not all)
2. **Use waypoints** (break long paths into segments)
3. **Cache environmental data** (light/weather at start, not continuous)
4. **Simplify distant pathfinding** (trade accuracy for speed)

### Apply to My Kingdom:
- Don't recalculate paths every frame
- Use path caching
- Limit A* search depth
- Consider FPS impact of having many citizens pathing simultaneously

---

## Sources
- RimWorld Wiki - Work System
- Steam Community discussions
- Pathfinding Framework mod documentation
- Player guides on work priorities
