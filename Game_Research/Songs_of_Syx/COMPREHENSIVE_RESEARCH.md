# Songs of Syx - Comprehensive Development Research

## Overview
Songs of Syx is a fantasy city-state simulator developed by Jake de Laval (known as "Jake the Dondorian"), running a 1-man indie studio called Gamatron AB. The game has been in development since 2015 and was released on Steam in 2020.

---

## Programming & Technical Stack

### Core Technology
- **Programming Language**: Java 1.8 (runs on Java 21)
- **Game Engine**: Custom-built engine called "Snake2D"
- **Graphics Library**: LWJGL 3.x (Lightweight Java Gaming Library)
- **Graphics API**: OpenGL
- **Build System**: Maven

### Why Java?
According to the developer, Java was chosen because it "boils down how easy it is to set up and deploy." The developer stated: "I have also learnt how to write java as efficient as assembler, well more or less," demonstrating a focus on optimization despite Java's reputation for performance concerns in game development.

### Engine Philosophy
The Snake2D engine is NOT a general-purpose city builder engine, but rather a Songs of Syx engine specifically tinkered for its purpose. It was built from scratch rather than using popular game engines like Unity or Unreal.

---

## Architecture & Design Patterns

### Modding Architecture

**Two-Tier Mod System**:
1. **Content Mods**: Add or change races, rooms, music, maps, technology by extending game data
2. **Feature Mods**: Add or modify gameplay mechanics through source code extension/replacement

**Modular Design**: The game separates game data from code, allowing modders to work with the game through Maven-based build pipelines and JAR file extensions.

**Dependency Management**: The framework installs the game's `SongsOfSyx.jar` and `SongsOfSyx-sources.jar` as local Maven dependencies, enabling developers to access the source code for reference and extension.

**Testing Infrastructure**: Modders have access to JUnit 5, AssertJ, and Mockito 4 for unit testing.

### Source Code Access
The source code is available in the game installation directory, allowing modders and researchers to study the implementation directly.

---

## Procedural Generation Systems

### City Map Generation
- **Algorithm**: Semi-random generation using a 3x3 tile chunk from the world-map as reference
- **Challenge**: According to the developer, this approach is harder than going fully random, since you need to control the randomness to:
  - Resemble the world-map
  - Ensure entrance points aren't blocked
  - Make results functional and playable
- **Development Note**: The developer has re-written this code several times
- **Result**: Creates more interesting maps where different areas have distinct characteristics with recognizable landmarks
- **Features**: Includes caves and rivers that branch and create islands

### World Generation
- **Dynamic Systems**:
  - Day/night cycles
  - Climate and weather changes
  - Migrations of animals and people
- **Climate Types**: Three climate zones - warm, temperate, and cold
- **Resource Distribution**: Vast areas with multiple settlements, regions, natural resources, and huntable wildlife
- **Uniqueness**: All content, background stories, and easter-eggs are generated uniquely each iteration while maintaining consistency with the game's lore

---

## Simulation & Performance

### Population Simulation at Scale
- **Capability**: Simulates tens of thousands of citizens and soldiers
- **Individual Simulation**: Each character has their own:
  - Species
  - Religion
  - Needs
  - Routines
  - Life and death
- **Real NPCs**: Unlike some games with "fake" visual-only NPCs, Songs of Syx's people actually move around the map, perform tasks, and fulfill needs
- **Example**: Individual citizens assigned to nobility actually travel to forges and inspect them - one citizen out of thousands genuinely matters in the simulation

### Performance Optimization
- **Multithreading**: The game is multithreaded to handle large populations
- **Optimization Focus**: The developer made "major optimisations" yielding 20-50% more performance improvements over development
- **Pathfinding**: Improved pathing performance through various updates
- **Day-Length Adjustment**: The developer "prolonged the day-length" to make distances less important as an optimization
- **Known Issue**: Some players report the game "saturating a single core, with about 5% use on other cores"
- **Decoupled Systems**: Render frames and game ticks are decoupled (standard for games with speed control)

### Battle Scale
- Players can gather allies and vassals
- Conscript traveling mercenaries and local peasants
- Battles support up to 50,000 individual units
- Real-time simulation with thousands on each side

---

## Development Process & Philosophy

### Timeline
- **Started**: 2015
- **Steam Release**: 2020
- **Development Pace**: Updates occur every 1.5-3 months (according to Trello roadmap)
- **Status**: Full-time development by solo developer

### Development Approach
- **Solo Development**: Entire game built by one developer
- **Custom Engine**: Built from scratch using LWJGL rather than commercial engines
- **Iterative Process**: Key systems like city map generation have been rewritten multiple times
- **Source Available**: Code is accessible in installation directory for study

### Design Philosophy
- **Ambitious Scope**: Bridges detailed base-building with large-scale city simulation
- **Layered Systems**:
  1. Individual settlement management (detailed, player-focused)
  2. Grand Strategy overlay with world map and region management
  3. Autonomous systems allowing cities to run without constant micromanagement
- **Management Delegation**: Uses nobility systems to prevent tedium of managing massive populations
- **Trade System**: Emphasized as crucial for realism, requiring interdependency between settlements rather than self-sufficiency

---

## Technical Challenges & Solutions

### GPU Selection (Multi-GPU Systems)
- **Common Problem**: Java applications on systems with multiple GPUs default to the weaker integrated GPU
- **Solution**: Must be configured in graphics settings to use dedicated GPU

### Map Generation Complexity
According to the developer, the semi-random approach to city generation that references the world map is particularly challenging because:
1. Must maintain visual consistency with world map reference
2. Must ensure functional entrance points
3. Must create playable layouts
4. Still needs to feel organic and varied

### Scalability
The game successfully handles:
- Tens of thousands of individually simulated characters
- Real-time pathfinding for massive populations
- Complex AI behaviors for each character
- Dynamic world systems running simultaneously

---

## Modding & Extensibility

### Build Pipeline
- **Primary Tool**: Maven with automated build pipeline
- **Mod Structure**: Standardized directory layout (e.g., `V70/script/` structure)
- **Source Files**: Copied to `_src` subdirectories during packaging
- **Build Lifecycle**: Standard phases - compile → test → package → verify → install
- **Platform Support**: Custom profiles for Windows/Linux installation paths

### API Design
The game exposes both data and code extension points:
- Content can be added through data files
- Features can be added through source code extension
- Modders can reference the full source code
- Testing frameworks available for quality assurance

---

## Key Takeaways for Game Developers

### What Makes Songs of Syx Unique

1. **Java for Large-Scale Simulation**: Proves Java can handle massive real-time simulations when optimized properly
2. **Custom Engine Benefits**: Building a custom engine allowed perfect tailoring to the game's specific needs
3. **Procedural Everything**: Extensive use of procedural generation creates unique experiences while maintaining consistency
4. **Scale Achievement**: Successfully simulates tens of thousands of individual entities with unique AI
5. **Solo Development**: Demonstrates what a single dedicated developer can achieve over sustained development

### Technical Lessons

1. **Semi-Random > Pure Random**: Constrained procedural generation (using world map reference) creates better results than pure randomness
2. **Iteration is Essential**: Key systems were rewritten multiple times to achieve the desired result
3. **Multithreading Necessary**: Required for handling large populations in real-time
4. **Modding Architecture**: Separating data from code enables extensive modding
5. **Performance-First Java**: Careful optimization can make Java perform at near-native levels

### Development Insights

1. **Solo Can Scale**: One developer can build massive, complex systems over time
2. **Custom > Off-the-shelf**: For specific visions, custom engines may be better than general-purpose ones
3. **Accessibility Matters**: Choosing Java for "easy setup and deploy" paid off
4. **Source Transparency**: Making source code available enables community learning and modding
5. **Sustained Development**: 5+ years of dedicated work (2015-2020+) enabled the ambitious scope

---

## Resources & References

- **Official Site**: https://songsofsyx.com/
- **Steam Page**: https://store.steampowered.com/app/1162750/Songs_of_Syx/
- **Itch.io Devlog**: https://songsofsyx.itch.io/songs-of-syx/devlog
- **Wiki**: https://songsofsyx.com/wiki/
- **Mod Example**: https://github.com/4rg0n/songs-of-syx-mod-example
- **Developer**: Jake de Laval (Gamatron AB)

---

## Technical Specifications Summary

| Aspect | Details |
|--------|---------|
| Language | Java 1.8 (runs on Java 21) |
| Engine | Snake2D (custom, LWJGL-based) |
| Graphics | LWJGL 3.x + OpenGL |
| Build System | Maven |
| Threading | Multithreaded |
| Population Scale | Tens of thousands of NPCs |
| Battle Scale | Up to 50,000 units |
| Development Time | 2015 - Present (8+ years) |
| Team Size | 1 developer |
| Code Availability | Source in installation directory |
| Modding Support | Full (content + code) |

---

*Last Updated: 2026-01-01*
*Research compiled from developer interviews, technical documentation, community discussions, and official sources*
