# Standard Operating Procedure (SOP) - Project Organization

**My Kingdom - Development Standards**
**Version:** 1.0
**Last Updated:** 2026-02-07
**Purpose:** Maintain consistent, professional project organization across all development sessions

---

## 📋 Quick Reference

**READ THIS AT THE START OF EVERY SESSION:**

1. All **production code** goes in `src/`
2. All **development tools** go in `tools/`
3. All **documentation** goes in `docs/`
4. All **examples/demos** go in `examples/`
5. **Never** put utility scripts in the root directory
6. **Always** use comprehensive docstrings (see standards below)
7. **Always** update imports when moving files

---

## 📁 Directory Structure Standards

### Root Directory - KEEP CLEAN

**Allowed in root:**
```
My-KingdomVersion 3/
├── main.py                    ✅ (Entry point only)
├── README.md                  ✅ (Project overview only)
├── requirements.txt           ✅ (Dependencies)
├── .gitignore                 ✅ (Git config)
├── LICENSE                    ✅ (If needed)
└── [directories only]         ✅
```

**NOT allowed in root:**
- ❌ Utility scripts (`.py` files except `main.py`)
- ❌ Documentation files (`.md` files except `README.md`)
- ❌ Generated files (`.png`, `.json`, etc.)
- ❌ Test files
- ❌ Demo files

### Production Code - `src/`

**Structure:**
```
src/
├── __init__.py
├── core/           # Core game systems
├── entities/       # Game entities (citizens, buildings, resources)
├── systems/        # Game systems (pathfinding, jobs, saves)
├── world/          # World generation and rendering
├── ui/             # User interface (menus, HUD)
└── audio/          # Audio systems
```

**Rules:**
1. **Only production code** - Code that runs during actual gameplay
2. **No dev tools** - No generators, converters, or utilities
3. **No demos** - No standalone test/demo scripts
4. **Proper __init__.py** - Every subdirectory must have one
5. **Comprehensive docstrings** - Every module, class, and function

**What belongs in `src/`:**
- ✅ Game state management
- ✅ Entity classes (Citizen, Building, Resource)
- ✅ Game systems (JobManager, Pathfinding, SaveSystem)
- ✅ Renderers (CozyRenderer, BuildingRenderer)
- ✅ World generation (used at runtime)
- ✅ UI components (MainMenu, PauseMenu)
- ✅ Audio managers

**What does NOT belong in `src/`:**
- ❌ Asset generators (pixel art, tile generators)
- ❌ Demo scripts (world_demo.py)
- ❌ Setup utilities (create_settings.py)
- ❌ External API tools (chatgpt_tile_generator.py)
- ❌ Preview tools

### Development Tools - `tools/`

**Structure:**
```
tools/
├── __init__.py
├── setup/                      # Initial setup scripts
│   ├── __init__.py
│   ├── create_settings.py
│   └── README.md
├── tile_generation/            # Tile/terrain asset tools
│   ├── __init__.py
│   ├── generate_tiles_now.py
│   ├── create_placeholder_tiles.py
│   ├── tile_generator.py
│   ├── chatgpt_tile_generator.py
│   └── README.md
└── asset_generation/           # Asset generation tools
    ├── __init__.py
    ├── pixel_art_generator.py
    ├── advanced_pixel_art.py
    ├── ai_menu_generator.py
    ├── preview_menu.py
    └── README.md
```

**What belongs in `tools/`:**
- ✅ Asset generators (tiles, sprites, backgrounds)
- ✅ Setup/configuration scripts
- ✅ External API integrations (OpenAI, etc.)
- ✅ Conversion utilities
- ✅ Development helpers

**Rules:**
1. **Never import from production code** - Tools should be standalone
2. **Each subdirectory has README.md** - Document what tools do
3. **Add __init__.py to each directory**
4. **Include usage examples** in README files

### Documentation - `docs/`

**Structure:**
```
docs/
├── README.md                   # Documentation index
├── setup/                      # Installation & setup guides
│   ├── INSTALLATION.md
│   ├── REQUIREMENTS.md
│   └── SETUP_TOOLS.md
├── guides/                     # User & developer guides
│   ├── WORLD_GENERATION_GUIDE.md
│   ├── BUILDING_SYSTEM_GUIDE.md
│   ├── VIEW_SYSTEM_GUIDE.md
│   └── SESSION_RECOVERY.md
├── development/                # Development documentation
│   ├── SOP_PROJECT_ORGANIZATION.md  # THIS FILE
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── INTEGRATION_COMPLETE.md
│   ├── TILE_GENERATION_PROMPTS.md
│   ├── ARCHITECTURE.md
│   └── CODING_STANDARDS.md
└── api/                        # API documentation (future)
    └── [Auto-generated API docs]
```

**Rules:**
1. **No docs in root** (except README.md)
2. **Organize by purpose:**
   - `setup/` - Getting started
   - `guides/` - How to use features
   - `development/` - Internal dev docs
   - `api/` - Code reference
3. **Keep docs updated** - Update when code changes
4. **Use consistent formatting** - Markdown with clear headers

### Examples & Demos - `examples/`

**Structure:**
```
examples/
├── __init__.py
├── world_demo.py              # World generation demo
├── pathfinding_demo.py        # Pathfinding visualization
├── citizen_behavior_demo.py   # Citizen AI demo
└── README.md
```

**Rules:**
1. **Self-contained** - Each example should run independently
2. **Educational purpose** - Show how to use systems
3. **Well-documented** - Explain what the example demonstrates
4. **Not part of main game** - Optional files for learning

### Assets - `assets/`

**Structure:**
```
assets/
├── images/
│   ├── menu/                   # Menu backgrounds, UI elements
│   │   └── backgrounds/
│   ├── world/                  # Terrain tiles, world assets
│   │   ├── terrain/
│   │   └── objects/
│   ├── entities/               # Citizens, buildings sprites
│   └── effects/                # Visual effects
├── audio/
│   ├── music/                  # Background music
│   ├── sfx/                    # Sound effects
│   └── ambience/               # Ambient sounds
└── previews/                   # Generated previews (gitignored)
    └── menu_preview.png
```

**Rules:**
1. **Organize by type** - Images, audio, fonts, etc.
2. **Subdirectories by category** - Menu, world, entities
3. **Generated assets in previews/** - Don't commit to git
4. **Use consistent naming** - lowercase_with_underscores.png

### Configuration - `config/`

**Structure:**
```
config/
├── __init__.py
└── settings.py                # Game constants & configuration
```

**Rules:**
1. **Constants only** - No game logic
2. **ALL_CAPS for constants** - `WINDOW_WIDTH = 1280`
3. **Group related settings** - Windows, colors, gameplay
4. **Document each setting** - Comment explaining purpose

### Other Directories

**`Logs/`** - Auto-generated logs (gitignored)
```
Logs/
├── game_YYYYMMDD_HHMMSS.log
└── sessions/
    ├── session_YYYYMMDD_HHMMSS.log
    └── session_YYYYMMDD_HHMMSS.json
```

**`saves/`** - Player save files (gitignored)
```
saves/
└── [player_save_name].sav.gz
```

**`Game_Research/`** - Research documents (well-organized, keep as-is)
```
Game_Research/
├── README.md
├── COMPARATIVE_ANALYSIS.md
├── Dwarf_Fortress/
├── RimWorld/
└── Songs_of_Syx/
```

---

## 🐍 Python Code Standards

### Docstring Standards

**Every Python file must have:**
```python
"""
Module name and purpose.

More detailed description of what this module does, its main
responsibilities, and how it fits into the larger system.

Classes:
    ClassName: Brief description
    AnotherClass: Brief description

Functions:
    function_name: Brief description

Example:
    from src.module import ClassName
    obj = ClassName()
    obj.method()

Notes:
    Any important notes, caveats, or warnings.

References:
    Links to related documentation or external resources.
"""
```

**Every class must have:**
```python
class MyClass:
    """
    Brief one-line description.

    Longer description explaining the purpose, design decisions,
    and usage patterns of this class.

    Attributes:
        attribute_name (type): Description of attribute
        another_attr (type): Description

    Methods:
        method_name: Brief description
        another_method: Brief description

    Example:
        >>> obj = MyClass(param=value)
        >>> obj.method()
        result

    Notes:
        Important implementation details or design decisions.
    """
```

**Every function/method must have:**
```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief one-line description of what function does.

    More detailed explanation of the function's purpose,
    behavior, and any important details.

    Args:
        param1 (type): Description of parameter
        param2 (type): Description of parameter

    Returns:
        return_type: Description of return value

    Raises:
        ExceptionType: When and why this exception is raised

    Example:
        >>> result = function_name(value1, value2)
        >>> print(result)
        expected_output

    Notes:
        Any important implementation details or edge cases.
    """
```

### Import Organization

**Order of imports:**
```python
"""Module docstring here."""

# 1. Standard library imports
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# 2. Third-party imports
import pygame
import numpy as np

# 3. Local application imports
from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.logger import logger
from src.entities.citizen import Citizen
from src.systems.pathfinding import AStar
```

**Import rules:**
1. Separate groups with blank line
2. Sort alphabetically within groups
3. Use absolute imports (not relative)
4. Import specific items when possible

### Type Hints

**Use type hints everywhere:**
```python
from typing import List, Dict, Optional, Tuple

def process_citizens(
    citizens: List[Citizen],
    buildings: Dict[int, Building]
) -> Tuple[int, int]:
    """Process citizens and return statistics."""
    pass

class GameState:
    """Game state manager."""

    def __init__(self, tile_size: int = 32):
        self.tile_size: int = tile_size
        self.citizens: List[Citizen] = []
        self.resources: Dict[str, int] = {}
```

### Code Organization Within Files

**Standard file structure:**
```python
"""Module docstring."""

# Imports
import standard_lib
import third_party
from src.local import module

# Constants
CONSTANT_NAME = value

# Type definitions
class CustomType(Enum):
    """Custom type definition."""
    pass

# Helper functions (if needed)
def _private_helper():
    """Private helper function."""
    pass

# Main classes
class MainClass:
    """Primary class of this module."""
    pass

# Module-level functions
def public_function():
    """Public API function."""
    pass
```

---

## 🔄 File Movement Checklist

**When moving a file to a new location:**

### 1. Before Moving
- [ ] Identify all files that import the file being moved
- [ ] Note the old import path
- [ ] Determine the new import path

### 2. Move the File
- [ ] Move file to new location
- [ ] Ensure parent directory has `__init__.py`
- [ ] Update file's internal docstring (if location is mentioned)

### 3. Update Imports
- [ ] Search entire codebase for old import path
- [ ] Update all import statements
- [ ] Update any string references to file path
- [ ] Check for dynamic imports (importlib, __import__)

### 4. Test
- [ ] Run the game to ensure no import errors
- [ ] Check that moved file still functions
- [ ] Verify all dependent files work

### 5. Update Documentation
- [ ] Update README if file location is documented
- [ ] Update any architecture diagrams
- [ ] Update this SOP if needed

**Search command for finding imports:**
```bash
# Find all imports of a module
grep -r "from src.ui.pixel_art" .
grep -r "import pixel_art_generator" .
```

---

## 📝 Creating New Files

### New Production Code File

**Template:**
```python
"""
Module name - Brief one-line description.

Detailed description of this module's purpose and responsibilities.
Explain how it fits into the overall architecture.

Classes:
    ClassName: Brief description

Functions:
    function_name: Brief description

Example:
    Basic usage example here.

Notes:
    Important information about this module.

Author: [Your Name]
Created: YYYY-MM-DD
"""

# Standard library imports
import os
from typing import List, Optional

# Third-party imports
import pygame

# Local imports
from config.settings import CONSTANT
from src.core.logger import logger


# Constants
MODULE_CONSTANT = value


class ClassName:
    """
    Brief description.

    Detailed description of class purpose and usage.

    Attributes:
        attr (type): Description

    Example:
        >>> obj = ClassName()
        >>> obj.method()
    """

    def __init__(self, param: type):
        """
        Initialize ClassName.

        Args:
            param (type): Description
        """
        self.attr = param
        logger.info(f"ClassName initialized with {param}")

    def method(self) -> return_type:
        """
        Brief method description.

        Returns:
            return_type: Description
        """
        pass


def function_name(param: type) -> return_type:
    """
    Brief function description.

    Args:
        param (type): Description

    Returns:
        return_type: Description
    """
    pass
```

### New Tool Script

**Template:**
```python
"""
Tool Name - Brief description.

This development tool is used for [purpose].
It is not part of the main game and should only be run manually.

Usage:
    python tools/category/script_name.py [args]

Example:
    python tools/tile_generation/generate_tiles.py --count 100

Requirements:
    - List any special requirements
    - Dependencies beyond requirements.txt

Author: [Your Name]
Created: YYYY-MM-DD
"""

import argparse
import sys
from pathlib import Path

# Add project root to path (for imports)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main entry point for tool."""
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("--arg", help="Argument help")
    args = parser.parse_args()

    print(f"Running tool with args: {args}")
    # Tool logic here


if __name__ == "__main__":
    main()
```

### New Documentation File

**Template:**
```markdown
# Document Title

**Purpose:** Brief description of what this document covers
**Audience:** Who should read this (developers, users, etc.)
**Last Updated:** YYYY-MM-DD

---

## Overview

Brief overview of the topic.

## [Main Section]

Content here...

### Subsection

More specific content...

## Examples

Concrete examples demonstrating concepts.

## References

- Link to related docs
- External resources
```

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T Do These

1. **Don't put utility scripts in root**
   ```
   ❌ My-KingdomVersion 3/generate_something.py
   ✅ My-KingdomVersion 3/tools/category/generate_something.py
   ```

2. **Don't put docs in root**
   ```
   ❌ My-KingdomVersion 3/FEATURE_GUIDE.md
   ✅ My-KingdomVersion 3/docs/guides/FEATURE_GUIDE.md
   ```

3. **Don't mix dev tools with production code**
   ```
   ❌ src/ui/pixel_art_generator.py
   ✅ tools/asset_generation/pixel_art_generator.py
   ```

4. **Don't forget __init__.py**
   ```
   ❌ src/new_module/code.py (no __init__.py)
   ✅ src/new_module/__init__.py + code.py
   ```

5. **Don't use relative imports**
   ```python
   ❌ from ..core.logger import logger
   ✅ from src.core.logger import logger
   ```

6. **Don't skip docstrings**
   ```python
   ❌ def my_function(x):
          return x * 2

   ✅ def my_function(x: int) -> int:
          """Multiply input by 2.

          Args:
              x (int): Input value

          Returns:
              int: Input multiplied by 2
          """
          return x * 2
   ```

7. **Don't commit generated files**
   ```
   ❌ Committed: Logs/game_20260207.log
   ❌ Committed: assets/previews/menu_preview.png
   ✅ Add to .gitignore
   ```

---

## ✅ Decision Tree: Where Does This File Go?

```
New file to add?
│
├─ Is it the main entry point?
│  └─ YES → main.py (root)
│
├─ Does it run during gameplay?
│  ├─ YES → src/[appropriate_module]/
│  │  ├─ Core game logic? → src/core/
│  │  ├─ Entity (Citizen, Building)? → src/entities/
│  │  ├─ System (Pathfinding, Jobs)? → src/systems/
│  │  ├─ World generation? → src/world/
│  │  ├─ UI component? → src/ui/
│  │  └─ Audio? → src/audio/
│  │
│  └─ NO → Continue...
│
├─ Is it a development/utility tool?
│  ├─ YES → tools/[category]/
│  │  ├─ Asset generation? → tools/asset_generation/
│  │  ├─ Tile generation? → tools/tile_generation/
│  │  └─ Setup script? → tools/setup/
│  │
│  └─ NO → Continue...
│
├─ Is it documentation?
│  ├─ YES → docs/[category]/
│  │  ├─ User guide? → docs/guides/
│  │  ├─ Setup instructions? → docs/setup/
│  │  ├─ Dev documentation? → docs/development/
│  │  └─ API reference? → docs/api/
│  │
│  └─ NO → Continue...
│
├─ Is it a demo/example?
│  └─ YES → examples/
│
├─ Is it an asset (image, audio)?
│  └─ YES → assets/[type]/[category]/
│
├─ Is it a config file?
│  └─ YES → config/
│
└─ Is it a test?
   └─ YES → tests/[type]/
```

---

## 🔍 Code Review Checklist

**Before committing any code:**

### Structure
- [ ] File is in the correct directory
- [ ] `__init__.py` exists in parent directory
- [ ] No utility scripts in root
- [ ] No docs in root (except README.md)

### Documentation
- [ ] Module docstring present and complete
- [ ] All classes have docstrings
- [ ] All functions have docstrings
- [ ] Type hints used throughout
- [ ] Examples provided in docstrings

### Code Quality
- [ ] Imports organized (stdlib, third-party, local)
- [ ] No unused imports
- [ ] Constants are ALL_CAPS
- [ ] No magic numbers (use named constants)
- [ ] Logging added for important operations
- [ ] Error handling present

### Testing
- [ ] Game runs without errors
- [ ] New feature works as expected
- [ ] No broken imports
- [ ] Related systems still work

---

## 📚 Quick Reference Commands

### Find Import Statements
```bash
# Find all imports of a specific module
grep -r "from src.module" .
grep -r "import module_name" .
```

### Find TODO Comments
```bash
grep -r "TODO" src/
grep -r "FIXME" src/
```

### Check for Missing Docstrings
```bash
# Find classes without docstrings
grep -A 1 "^class " src/ | grep -v '"""'

# Find functions without docstrings
grep -A 1 "def " src/ | grep -v '"""'
```

### Count Lines of Code
```bash
find src/ -name "*.py" | xargs wc -l
```

### List All Python Files
```bash
find . -name "*.py" -type f
```

---

## 📖 Additional Resources

### Internal Documentation
- `docs/development/ARCHITECTURE.md` - System architecture
- `docs/development/CODING_STANDARDS.md` - Coding guidelines
- `docs/guides/` - Feature-specific guides

### External References
- [PEP 8 - Python Style Guide](https://pep8.org/)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Real Python - Documenting Code](https://realpython.com/documenting-python-code/)

---

## 🔄 SOP Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-07 | Initial SOP creation after project reorganization |

---

## 📞 Questions?

If you're unsure where a file should go:
1. Check the decision tree above
2. Look for similar existing files
3. Consult `docs/development/ARCHITECTURE.md`
4. Ask in this document via comments

---

**Remember:** This SOP exists to maintain consistency and professionalism. Following these standards makes the codebase easier to navigate, maintain, and expand. When in doubt, refer to this document!
