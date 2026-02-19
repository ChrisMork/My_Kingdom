"""
Building system for My Kingdom.
Implements lessons from all three games:
- RimWorld: Construction queue, material requirements
- Dwarf Fortress: Designation system, hauling materials
- Songs of Syx: Worker assignment, auto-employ
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple
import random


class BuildingType(Enum):
    """Types of buildings (placeholder for now)."""
    HOUSE = "house"
    STORAGE = "storage"
    WAREHOUSE = "warehouse"
    WORKSHOP = "workshop"
    FARM = "farm"
    MINE = "mine"
    LUMBER_CAMP = "lumber_camp"
    WELL = "well"
    MARKET = "market"
    WAGON = "wagon"


class BuildingState(Enum):
    """State of building construction."""
    PLANNED = "planned"          # Designated but not started (DF approach)
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETE = "complete"


@dataclass
class BuildingDefinition:
    """
    Definition of a building type.
    Similar to RimWorld's Def system - separates data from code.
    """
    building_type: BuildingType
    name: str
    width: int  # in tiles
    height: int  # in tiles

    # Resource requirements (RimWorld/DF approach)
    required_resources: Dict[str, int]  # {"wood": 10, "stone": 5}

    # Construction parameters
    construction_work: float  # Amount of work needed (DF approach)

    # Employment (Songs of Syx approach)
    max_workers: int = 0  # 0 = not a workplace

    # Visual (placeholder color for now)
    color: Tuple[int, int, int] = (100, 100, 100)

    description: str = ""


# Building definitions (data-driven approach like RimWorld)
BUILDING_DEFINITIONS = {
    BuildingType.HOUSE: BuildingDefinition(
        building_type=BuildingType.HOUSE,
        name="House",
        width=3,
        height=3,
        required_resources={"wood": 20, "stone": 10},
        construction_work=100.0,
        max_workers=0,
        color=(139, 69, 19),
        description="A cozy home for your citizens"
    ),

    BuildingType.STORAGE: BuildingDefinition(
        building_type=BuildingType.STORAGE,
        name="Storage",
        width=4,
        height=4,
        required_resources={"wood": 30},
        construction_work=80.0,
        max_workers=0,
        color=(101, 67, 33),
        description="Stores resources and goods"
    ),

    BuildingType.WAREHOUSE: BuildingDefinition(
        building_type=BuildingType.WAREHOUSE,
        name="Warehouse",
        width=5,
        height=5,
        required_resources={"wood": 50, "stone": 30},
        construction_work=150.0,
        max_workers=0,
        color=(85, 55, 28),
        description="Large storage building. Adds 2000 storage capacity."
    ),

    BuildingType.WORKSHOP: BuildingDefinition(
        building_type=BuildingType.WORKSHOP,
        name="Workshop",
        width=3,
        height=3,
        required_resources={"wood": 25, "stone": 15},
        construction_work=120.0,
        max_workers=4,
        color=(70, 70, 90),
        description="A place for crafting and production"
    ),

    BuildingType.FARM: BuildingDefinition(
        building_type=BuildingType.FARM,
        name="Farm",
        width=5,
        height=5,
        required_resources={"wood": 10},
        construction_work=60.0,
        max_workers=3,
        color=(139, 117, 67),
        description="Grows crops for food"
    ),

    BuildingType.MINE: BuildingDefinition(
        building_type=BuildingType.MINE,
        name="Mine",
        width=2,
        height=2,
        required_resources={"wood": 15, "stone": 5},
        construction_work=150.0,
        max_workers=5,
        color=(60, 60, 60),
        description="Extracts stone and ore"
    ),

    BuildingType.LUMBER_CAMP: BuildingDefinition(
        building_type=BuildingType.LUMBER_CAMP,
        name="Lumber Camp",
        width=3,
        height=2,
        required_resources={"wood": 15},
        construction_work=70.0,
        max_workers=4,
        color=(101, 67, 33),
        description="Harvests wood from forests"
    ),

    BuildingType.WELL: BuildingDefinition(
        building_type=BuildingType.WELL,
        name="Well",
        width=1,
        height=1,
        required_resources={"stone": 20},
        construction_work=100.0,
        max_workers=0,
        color=(100, 150, 200),
        description="Provides fresh water"
    ),

    BuildingType.MARKET: BuildingDefinition(
        building_type=BuildingType.MARKET,
        name="Market",
        width=4,
        height=3,
        required_resources={"wood": 40, "stone": 20},
        construction_work=140.0,
        max_workers=6,
        color=(200, 150, 50),
        description="Facilitates trade and commerce"
    ),

    BuildingType.WAGON: BuildingDefinition(
        building_type=BuildingType.WAGON,
        name="Wagon Stockpile",
        width=2,
        height=2,
        required_resources={},  # Free, placed at start
        construction_work=0.0,  # Instant
        max_workers=0,
        color=(139, 90, 43),
        description="Initial stockpile where citizens bring gathered resources"
    ),
}


@dataclass
class Building:
    """
    A building instance in the game world.

    Design approach:
    - Dwarf Fortress: Designation → Material hauling → Construction
    - RimWorld: Construction queue, skill-based speed
    - Songs of Syx: Worker assignment for workplaces
    """

    id: int
    building_type: BuildingType
    x: int  # Top-left corner
    y: int

    # Construction state (Dwarf Fortress approach)
    state: BuildingState = BuildingState.PLANNED
    construction_progress: float = 0.0  # 0 to definition.construction_work

    # Materials (Dwarf Fortress: materials must be hauled first)
    materials_delivered: Dict[str, int] = field(default_factory=dict)

    # Workers (Songs of Syx approach)
    assigned_workers: list = field(default_factory=list)  # List of citizen IDs
    auto_employ: bool = True

    # For workplaces: production/gathering
    is_active: bool = False
    production_progress: float = 0.0

    def get_definition(self) -> BuildingDefinition:
        """Get the building definition."""
        return BUILDING_DEFINITIONS[self.building_type]

    def get_required_materials(self) -> Dict[str, int]:
        """Get materials still needed."""
        definition = self.get_definition()
        needed = {}
        for resource, amount in definition.required_resources.items():
            delivered = self.materials_delivered.get(resource, 0)
            if delivered < amount:
                needed[resource] = amount - delivered
        return needed

    def has_all_materials(self) -> bool:
        """Check if all materials have been delivered."""
        return len(self.get_required_materials()) == 0

    def deliver_material(self, resource_type: str, amount: int):
        """Deliver construction materials."""
        current = self.materials_delivered.get(resource_type, 0)
        self.materials_delivered[resource_type] = current + amount

    def can_start_construction(self) -> bool:
        """Can construction begin? (DF: need materials first)"""
        return self.state == BuildingState.PLANNED and self.has_all_materials()

    def add_construction_progress(self, amount: float):
        """Add construction work (RimWorld: skill affects speed)."""
        if self.state == BuildingState.UNDER_CONSTRUCTION:
            self.construction_progress += amount

            # Check if complete
            if self.construction_progress >= self.get_definition().construction_work:
                self.state = BuildingState.COMPLETE
                self.construction_progress = self.get_definition().construction_work
                self.is_active = True

    def occupies_tile(self, tile_x: int, tile_y: int) -> bool:
        """Check if this building occupies a specific tile."""
        definition = self.get_definition()
        return (self.x <= tile_x < self.x + definition.width and
                self.y <= tile_y < self.y + definition.height)

    def get_center(self) -> Tuple[float, float]:
        """Get center position of building."""
        definition = self.get_definition()
        return (self.x + definition.width / 2, self.y + definition.height / 2)

    def needs_workers(self) -> bool:
        """Check if building needs more workers (Songs of Syx)."""
        definition = self.get_definition()
        if definition.max_workers == 0 or not self.is_active:
            return False
        return len(self.assigned_workers) < definition.max_workers

    def assign_worker(self, citizen_id: int):
        """Assign a worker to this building."""
        if citizen_id not in self.assigned_workers:
            self.assigned_workers.append(citizen_id)

    def remove_worker(self, citizen_id: int):
        """Remove a worker from this building."""
        if citizen_id in self.assigned_workers:
            self.assigned_workers.remove(citizen_id)

    def to_dict(self) -> dict:
        """Serialize to dictionary for saving."""
        return {
            'id': self.id,
            'building_type': self.building_type.value,
            'x': self.x,
            'y': self.y,
            'state': self.state.value,
            'construction_progress': self.construction_progress,
            'materials_delivered': self.materials_delivered,
            'assigned_workers': self.assigned_workers,
            'auto_employ': self.auto_employ,
            'is_active': self.is_active,
            'production_progress': self.production_progress,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Building':
        """Deserialize from dictionary."""
        building = Building(
            id=data['id'],
            building_type=BuildingType(data['building_type']),
            x=data['x'],
            y=data['y'],
        )
        building.state = BuildingState(data['state'])
        building.construction_progress = data['construction_progress']
        building.materials_delivered = data['materials_delivered']
        building.assigned_workers = data['assigned_workers']
        building.auto_employ = data['auto_employ']
        building.is_active = data['is_active']
        building.production_progress = data['production_progress']
        return building
