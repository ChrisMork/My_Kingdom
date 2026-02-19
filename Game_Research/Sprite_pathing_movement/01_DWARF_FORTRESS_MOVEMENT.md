# Dwarf Fortress - Movement & Pathfinding System

## Research Date: 2026-01-02

---

## Pathfinding Algorithm

### Core System: A* Search Algorithm

Dwarf Fortress uses the **A* search algorithm** for pathfinding, which is a well-established method that quickly calculates the ideal path between points.

**Key Characteristics:**
- **Heuristic**: Admissible heuristic ensures the ideal path is always found
- **Map Coverage**: Hostile creatures and dwarves can consider the entire map when making pathing choices
- **Optimal Routing**: Always takes the shortest route when multiple options exist

### How It Works
1. Dwarf receives a task (e.g., "haul stone from here to there")
2. A* algorithm calculates the shortest path considering:
   - Distance
   - Traffic designations
   - Occupied tiles
   - Terrain costs
3. Dwarf follows the calculated path tile-by-tile

---

## Traffic Cost System

Dwarves consider **traffic designations** when pathfinding. This is a weight-based system:

| Traffic Type | Path Cost | Usage |
|--------------|-----------|-------|
| **High** | 1 point | Main thoroughfares, frequently used corridors |
| **Normal** (default) | 2 points | Standard undesignated areas |
| **Low** | 5 points | Less important paths |
| **Restricted** | 25 points | Areas to avoid except as last resort |

**Performance Impact:**
- Implementing traffic designations can increase FPS by up to 10%
- Helps guide dwarves to use optimal routes
- Prevents overcrowding in narrow passages

---

## Collision & Movement Mechanics

### Tile Occupation
- **Dwarves can walk over each other** when necessary
- Moving through occupied tiles is **much slower**
- Pathfinding actively tries to avoid occupied tiles

### Design Best Practices
- **High-traffic routes**: Minimum 2 tiles wide
- **Avoid bottlenecks**: Single doors and single stairs cause pathfinding issues
- **Prevent congestion**: Wide corridors in busy areas

---

## Performance Considerations

### Edge Case Issues
- **Worst Case**: A* may search every single tile on the map
- **Impact**: Can significantly slow down the game
- **Solution**: Use traffic designations to guide pathfinding

### Optimization Strategies
1. **Limit search space** with traffic designations
2. **Create clear main routes** between important areas
3. **Use restricted areas** to prevent unnecessary path calculations
4. **Keep fortress compact** when possible

---

## Implementation Lessons for My Kingdom

### What to Adopt:
1. ✅ **A* Pathfinding**: Proven, reliable algorithm
2. ✅ **Traffic Cost System**: Could implement as "preferred paths"
3. ✅ **Tile Occupation**: Allow citizens to step around each other
4. ✅ **Performance Optimization**: Cache paths, limit search scope

### What to Avoid:
1. ❌ **Full-map searches**: Limit pathfinding to relevant areas
2. ❌ **Single-tile bottlenecks**: Design with 2+ tile paths
3. ❌ **Complex 3D pathfinding**: Keep it simple for 2D gameplay

### Recommended Approach:
```
1. Implement A* pathfinding (already done in src/systems/pathfinding.py)
2. Add path caching to avoid recalculating frequently used routes
3. Consider "road" or "path" designations that citizens prefer
4. Allow citizens to navigate around obstacles smoothly
5. Optimize by limiting search range (e.g., only search within 50 tiles radius)
```

---

## Technical Implementation Notes

### Pathfinding Flow
```
Task Assigned → Calculate Path (A*) → Follow Waypoints → Reach Destination
                    ↓
            Consider: Distance, Traffic, Occupied Tiles
```

### Movement Speed Factors
- Base movement speed
- Terrain type (grass vs mud vs stone)
- Occupation (slower through crowded areas)
- Light levels (in some versions)

---

## Sources
- Dwarf Fortress Wiki - Path articles
- Bay12 Forums - Algorithm discussions
- Steam Community discussions on pathfinding
