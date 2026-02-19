# RimWorld - Comprehensive Development Research

## Overview
RimWorld is a sci-fi colony simulation game developed by Ludeon Studios, founded and led by Tynan Sylvester. The game was started in 2013 with no outside funding, entered Early Access, and became one of the most successful indie games, known for its AI storyteller system and emergent narratives.

---

## Programming & Technical Stack

### Core Technology
- **Programming Language**: C#
- **Game Engine**: Unity (version 5.6 initially, now Unity 2022.3.35)
- **IDE**: Visual Studio Code
- **Graphics**: Unity's built-in rendering
- **Audio**: Unity's audio system

### Additional Tools
- **Art/Graphics**: Photoshop, Illustrator, Flash 8
- **Audio**: Audition
- **Compiler**: Visual Studio

### Why Unity + C#?
Unity was chosen as the game engine, but with significant custom modifications. The choice of C# provides:
- Strong typing and modern language features
- Excellent IDE support
- Unity integration
- Good modding support through .NET runtime

---

## Architecture & Design Patterns

### Custom Systems Over Unity Defaults

**Critical Architectural Decision**: RimWorld implements custom object and time handling systems because:
- RimWorld is a tile-based 2D game with thousands of objects
- Unity is optimized for smooth-space 3D games with hundreds of objects
- This architectural modification was necessary to work around Unity's limitations for this specific use case

### Data-Driven Design: The Def System

**Core Architecture**: XML Definitions (Defs) are the primary content definition and configuration source

**What are Defs?**
- Packages containing most game content
- Stored in human-readable XML files
- Located in `Mods/Core/Defs` folder in installation directory
- Define everything from items, plants, and animals to faction types and ideology options

**XML Structure**:
- `Defs` is the root node (enforced uniformity)
- Each Def must have a specific name matching a Type in C#
- Uses inheritance system with `Name` and `ParentName` attributes
- Supports `Abstract` attribute for template-only definitions

**XML Inheritance System**:
```xml
<!-- Example pattern -->
<ThingDef Name="BaseBook" Abstract="true">
    <!-- Common properties -->
</ThingDef>

<ThingDef ParentName="BaseBook">
    <!-- Inherits from BaseBook -->
</ThingDef>
```

### Object-Oriented Integration

**Linking XML to C# Code**:
- RimWorld heavily uses Object-Oriented Programming
- Exposes specific classes to XML through naming conventions
- Common class references: `workerClass`, `thingClass`
- Allows XML data to instantiate specific C# implementations

### Modding Architecture: Harmony Patching

**Harmony Library**: The primary modding framework for RimWorld
- **Purpose**: Monkey-patch C# methods at runtime without modifying DLL files
- **Developer**: Andreas Pardeike
- **Approach**: Elegant, high-level runtime alterations

**Three Patch Types**:

1. **Prefixes**:
   - Run before the original method
   - Can skip original method by returning false
   - Used for interception and conditional execution

2. **Postfixes**:
   - Run after the original method
   - Guaranteed to execute
   - Recommended for greatest mod compatibility
   - Can modify return values and side effects

3. **Transpilers**:
   - Modify the IL code of methods
   - Low-level alterations using System.Reflection and System.Reflection.Emit
   - Allows changing method internals without replacing entire method
   - Most powerful but most complex

**Mod Architecture Post-1.x**:
- Harmony cannot be included in every mod (changed from earlier versions)
- Harmony must be loaded before any other mod
- Placed at top of mod list
- All mods use the same Harmony version
- Central update system for Harmony library

**Mod Folder Structure**:
- `Assemblies/` folder contains compiled DLL files
- DLLs are automatically loaded by RimWorld
- Mods separate content (XML Defs) from code (C# assemblies)

---

## AI Storyteller System

### Core Concept
RimWorld is defined not as a game, but as a **story generator**. This fundamental framing drove all design decisions.

### Storyteller Architecture

**Not True AI**: Storytellers have no intelligence regarding how you play and make no decisions based on actions taken. They function as scheduled series of dice rolls that run endlessly.

**Algorithm Input Parameters**:
- Colony wealth
- Building wealth
- Colonist count
- Animal count
- Recent colonist deaths or severe wounds
- Time since last major event

**Configuration**:
- Curves defined in `Storytellers.xml`
- Determine event probabilities and timing
- Modifiable through modding

**Population Calculations**:
- Searches entire map for pawns of colony (includes caravans)
- Includes prisoners (each counts as half a colonist)
- Used for scaling event difficulty

### Three Storyteller Implementations

**1. Cassandra Classic**:
- **Algorithm**: Steadily rising difficulty over time
- **Inspiration**: Aristotelian dramatic arc (exposition → rising action → climax → catastrophe)
- **Recovery System**: After successful raid repulsion, schedules "recovery period" for healing and rebuilding
- **Experience**: Structured, predictable difficulty curve

**2. Phoebe Chillax**:
- **Algorithm**: Fewer events, generally less severe
- **Experience**: Relaxed, lower-stress gameplay
- **Purpose**: For players who want to build without constant pressure

**3. Randy Random**:
- **Algorithm**: Pseudo-random event triggers
- **Timing**: Any time, any difficulty
- **Extremes**: Can launch several dangerous threats simultaneously or consecutively
- **Experience**: Chaotic, unpredictable, high variance

### Difficulty Scaling Mechanics

**Storyteller Wealth System**:
1. Player succeeds (mines gold, recruits colonists)
2. Colony's "Storyteller Wealth" increases
3. Wealth converts to "Raid Points"
4. Raid Points determine attack strength and composition

**Result**: Natural difficulty progression based on player success rather than arbitrary timers

### Design Philosophy: Strategic Omission

From Tynan's GDC talk "Contrarian, Ridiculous, and Impossible Game Design Methods":
- Features are strategically left OUT to enhance engagement
- Players engage with story elements that "aren't actually there"
- Forcing definition as "story generator" opened new design mechanisms
- Prioritized features providing actual player value over assumed necessities
- No extensive planning - decision-making was agile and responsive

---

## Performance & Optimization

### Threading Model (as of Version 1.6)

**Major Improvements**:
- **Pathfinding**: Now fully multithreaded and batched
- **Lighting System**: Multithreaded
- **Technology**: Uses Unity's Burst compiler for performance

**Limitations**:
- Pawn AI/pathfinding/ticking NOT threaded for colonists or animals (as of 1.4-1.5)
- Only pawn rendering was threaded in version 1.5
- Helps FPS (frames per second) not TPS (ticks per second)

### Variable Tick Rate System (Version 1.6)

**Concept**: Update frequency varies based on importance and visibility

**Implementation**:
- Pawns/Things tick less often in certain circumstances
- Distance-based: Pawns off-camera update less frequently
- Variable Tick Rate (VTR) system
- Things can run as slow as 4Hz (vs. standard 60Hz)
- Delta-based logic for lower-frequency updates

**Performance Impact**: Significant improvement for large colonies

### Tick System

**Speed Settings**:
- 1x: Targets 60 ticks per second (TPS)
- 2x: Targets 180 TPS
- 3x: Targets 360 TPS
- 4x: Targets 900 TPS

**Performance Considerations**:
- Pawn Tick handles all pawn-specific updates
- Includes job finding and pathfinding
- Can become bottleneck with many pawns

**Profiling Tools**:
- Dubs Performance Analyzer: Community tool for identifying bottlenecks
- Shows where performance issues occur
- Essential for mod development and optimization

### Performance Tips

**Known Issue**: Animals can account for almost 70% of load in large colonies, even with optimizations

**Optimization Strategies**:
- Reduce pawn count (especially animals)
- Use performance mods (Slower Pawn Tick Rate, etc.)
- Monitor with profiling tools
- Understand TPS vs FPS difference

---

## Procedural Generation

### World Map Generation

**Scale & Uniqueness**:
- Worlds generated from random or user-provided seeds
- Completely new experience every time
- Multiple biomes per world
- Each tile has unique characteristics

**World Parameters**:
- **Temperature Slider**: Controls overall planet temperature
- **Rainfall Slider**: Controls precipitation
- **Time Zones**: Modeled physically - world actually exists spatially
- **Latitude Effects**: Hotter biomes near equator, colder near poles

**Biome System**:
- Nine biomes on normally generated world
- Each biome affects world appearance and behavior
- Determined by temperature, rainfall, and location

### Map Tile Generation

**Tile Structure**:
- World made of mostly hexagons with some pentagons
- Each tile has specific characteristics

**Tile Parameters**:
1. **Elevation**: Distance above sea level
   - Higher elevation = colder weather
   - Affects available resources and difficulty

2. **Terrain Types**:
   - Flat
   - Small Hills
   - Large Hills
   - Mountains
   - Determines mountain generation in actual play map

3. **Climate Data**: Temperature, rainfall, growing season

**Generation Algorithms**:
- Noise algorithms commonly used for terrain
- Complex mathematics for natural-looking results
- Layered generation (base terrain → features → resources)

### Modding World Generation

**Geological Landforms Mod Example**:
- Demonstrates advanced generation techniques
- Separate layer applied to any biome
- Shows extensibility of generation system
- Community can add sophisticated new generation methods

---

## Development Process & Philosophy

### Creator Background
**Tynan Sylvester**:
- Previously worked at Irrational Games on BioShock Infinite
- Became independent developer in 2012
- Founded Ludeon Studios
- Built first version of RimWorld by himself in 2013
- No outside funding initially

### Design Influences
- **Primary Inspiration**: Dwarf Fortress
- **Thematic Inspiration**: Firefly (TV show)
- **Art Style Influence**: Prison Architect

### Development Philosophy

**"Story Generator, Not Game"**:
- Fundamental framing that drove all decisions
- Focus on emergent narratives over scripted content
- Systems designed to create memorable stories
- Player agency in interpreting events

**Contrarian Design Methods**:
- Don't follow standard game design conventions
- Question "obvious" features
- Strip away unnecessary elements
- Focus on what creates actual player value

**Solo Development Advantages**:
- No team bureaucracy
- Immediate implementation of changes
- Direct vision-to-implementation
- Consistent design philosophy

---

## Technical Challenges & Solutions

### Unity Adaptation

**Problem**: Unity optimized for 3D games with hundreds of objects
**RimWorld Needs**: 2D tile-based game with thousands of objects

**Solution**: Custom object and time handling systems built on top of Unity
- Bypassed Unity's standard object management
- Created tile-based spatial system
- Implemented custom update/tick system
- Maintained Unity's rendering and tools while replacing core simulation

### Performance at Scale

**Challenge**: Simulating hundreds of pawns with complex AI, needs, and pathfinding

**Solutions**:
1. Variable tick rate system
2. Multithreaded pathfinding and lighting
3. Efficient data structures
4. Delta-based updates for off-screen entities
5. Profiling tools for optimization

### Modding Support

**Challenge**: Allow deep modding without game instability

**Solution**: Harmony patching system
- Runtime method modification
- Multiple mod compatibility
- Three patch types for different use cases
- Centralized Harmony version management
- Clear mod load order requirements

---

## Data Structures & Systems

### The Def System

**Purpose**: Separate data from code for easy modding and maintenance

**Benefits**:
1. Modders can add content without programming
2. Human-readable XML format
3. Inheritance reduces duplication
4. Version control friendly
5. Easy to inspect and modify

**Integration**:
- XML Defs instantiate C# classes at runtime
- Strong typing through C# backing
- Validation at load time
- Hot-reload support for modding

### Save System

**Approach**: Full state serialization
- All game state stored in save files
- Deterministic behavior
- Mod compatibility considerations
- Version migration support

---

## Key Takeaways for Game Developers

### What Makes RimWorld Unique

1. **Story Generator Focus**: Defining the game as a story generator, not a game, drove innovative design
2. **AI Storyteller**: Procedural event generation that creates narrative arcs
3. **Emergent Narratives**: Systems create stories rather than scripted content
4. **Deep Simulation**: Individual needs, psychology, social relationships
5. **Modding Ecosystem**: Harmony patching enables extensive modification
6. **Unity Customization**: Shows Unity can be adapted far beyond its default use case

### Technical Lessons

1. **Engine Flexibility**: Commercial engines can be customized extensively
2. **Data-Driven Design**: XML Defs enable modding and rapid iteration
3. **Custom > Default**: Sometimes replacing engine systems is necessary
4. **Performance Matters**: Variable tick rates and multithreading crucial for scale
5. **Modding Architecture**: Runtime patching more powerful than simple data mods

### Design Insights

1. **Constraints Drive Innovation**: Unity's limitations led to better solutions
2. **Strategic Omission**: Leaving things out can improve engagement
3. **Systems Over Content**: Deep systems create more value than scripted content
4. **Emergent > Scripted**: Player stories more memorable than authored ones
5. **Clear Vision**: "Story generator" framing guided all decisions

### Development Insights

1. **Solo Can Ship**: One developer can create a commercially successful, complex game
2. **No Funding Needed**: Can start without external funding
3. **Early Access Works**: Community involvement during development valuable
4. **Iteration Matters**: Years of refinement created the polished result
5. **Community Creation**: Modding turns players into co-creators

---

## Advanced Technical Details

### Pawn (Character) System

**Components**:
- Needs system (hunger, rest, recreation, etc.)
- Skills with experience and decay
- Traits affecting behavior
- Health system with body parts
- Social relationships and opinions
- Work priorities and job assignment
- Inventory management
- Psychological state

**AI Behavior**:
- Job assignment system
- Pathfinding (A* based, multithreaded)
- Need satisfaction prioritization
- Social interaction decisions
- Combat tactics

### Event System

**Structure**:
- Event definitions in XML
- Probability curves
- Storyteller-specific modifiers
- Cooldown and pacing systems
- Wealth-based scaling

**Event Types**:
- Threats (raids, mechanoid attacks, infestations)
- Opportunities (traders, wanderers, quests)
- Environmental (weather, eclipse, solar flare)
- Random (mad animals, disease, etc.)

---

## Resources & References

### Official
- **Steam Page**: https://store.steampowered.com/app/294100/RimWorld/
- **Official Site**: https://rimworldgame.com/
- **Ludeon Studios**: https://ludeon.com/
- **Official Wiki**: https://rimworldwiki.com/

### Development
- **Tynan Sylvester**: https://tynansylvester.com/
- **GDC Talk**: "RimWorld: Contrarian, Ridiculous, and Impossible Game Design Methods"
- **Book**: "Designing Games" by Tynan Sylvester

### Modding
- **RimWorld Wiki Modding Section**: https://rimworldwiki.com/wiki/Modding_Tutorials
- **Harmony Library**: https://harmony.pardeike.net/
- **RimWorld Modding Resources**: https://spdskatr.github.io/RWModdingResources/

---

## Technical Specifications Summary

| Aspect | Details |
|--------|---------|
| Language | C# |
| Engine | Unity (2022.3.35 current) |
| IDE | Visual Studio Code |
| Initial Engine Version | Unity 5.6 |
| Threading | Partial (pathfinding, lighting, rendering) |
| Tick System | Variable (4Hz - 60Hz) |
| Target TPS | 60 (1x speed) |
| Development Start | 2013 |
| Early Access | 2013-2018 |
| Full Release | 2018 |
| Team Size | Started solo, now small team |
| Modding System | Harmony (runtime patching) |
| Data Format | XML (Defs) |
| Code Format | C# (compiled DLLs) |

---

*Last Updated: 2026-01-01*
*Research compiled from developer interviews, GDC talks, technical documentation, modding wikis, and official sources*
