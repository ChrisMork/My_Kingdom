"""
Citizen entity system for My Kingdom.
Implements lessons from RimWorld (needs, skills) and Songs of Syx (work assignment).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
import random


class JobType(Enum):
    """Types of jobs citizens can perform."""
    IDLE = "idle"
    CONSTRUCTION = "construction"
    GATHERING = "gathering"
    HAULING = "hauling"
    FARMING = "farming"
    CRAFTING = "crafting"


class CitizenState(Enum):
    """Current state of a citizen."""
    IDLE = "idle"
    WALKING = "walking"
    WORKING = "working"
    CARRYING = "carrying"


@dataclass
class Citizen:
    """
    A citizen in your kingdom.

    Design inspired by:
    - RimWorld: Individual skills, needs
    - Songs of Syx: Work assignment, efficiency
    - Dwarf Fortress: Job designation system
    """

    # Identity
    id: int
    name: str
    x: float
    y: float

    # State
    state: CitizenState = CitizenState.IDLE
    current_job: Optional[JobType] = None
    target_x: Optional[float] = None
    target_y: Optional[float] = None

    # Skills (0-20, RimWorld-style)
    construction_skill: int = field(default_factory=lambda: random.randint(0, 10))
    gathering_skill: int = field(default_factory=lambda: random.randint(0, 10))
    hauling_skill: int = field(default_factory=lambda: random.randint(0, 10))

    # Work preferences (Songs of Syx approach: not everyone builds)
    can_construct: bool = True
    can_gather: bool = True
    can_haul: bool = True

    # Carrying
    carrying_resource: Optional[str] = None
    carrying_amount: int = 0

    # Movement speed
    move_speed: float = 5.0  # tiles per second (faster so you can see them move)

    # Current task target
    current_task: Optional[object] = None  # Reference to Building or Resource

    # Pathfinding
    current_path: Optional[list] = None  # List of (x, y) waypoints
    path_index: int = 0  # Current waypoint in path

    def assign_task(self, task, job_type: JobType):
        """Assign a task to this citizen."""
        self.current_task = task
        self.current_job = job_type
        self.state = CitizenState.WALKING

    def clear_task(self):
        """Clear current task."""
        self.current_task = None
        self.current_job = None
        self.state = CitizenState.IDLE
        self.target_x = None
        self.target_y = None
        self.current_path = None
        self.path_index = 0

    def set_target(self, x: float, y: float, path: list = None):
        """
        Set movement target.

        Args:
            x, y: Target coordinates
            path: Optional pre-calculated path (list of (x,y) tuples)
        """
        self.target_x = x
        self.target_y = y
        self.state = CitizenState.WALKING
        self.current_path = path
        self.path_index = 0 if path else 0

    def has_reached_target(self, threshold: float = 0.5) -> bool:
        """Check if citizen has reached target."""
        if self.target_x is None or self.target_y is None:
            return True

        distance = ((self.x - self.target_x) ** 2 + (self.y - self.target_y) ** 2) ** 0.5
        return distance < threshold

    def update(self, delta_time: float):
        """Update citizen state."""
        # Move toward target
        if self.state == CitizenState.WALKING and self.target_x is not None:
            # If we have a path, follow it waypoint by waypoint
            if self.current_path and self.path_index < len(self.current_path):
                # Get current waypoint
                waypoint_x, waypoint_y = self.current_path[self.path_index]

                # Move toward waypoint
                dx = waypoint_x - self.x
                dy = waypoint_y - self.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < 0.3:
                    # Reached waypoint, move to next
                    self.path_index += 1
                    if self.path_index >= len(self.current_path):
                        # Reached end of path
                        self.x = self.target_x
                        self.y = self.target_y
                else:
                    # Move toward waypoint
                    move_dist = self.move_speed * delta_time
                    if move_dist >= distance:
                        self.x = waypoint_x
                        self.y = waypoint_y
                    else:
                        self.x += (dx / distance) * move_dist
                        self.y += (dy / distance) * move_dist
            else:
                # No path - simple direct movement toward target
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance > 0.1:
                    # Normalize and apply speed
                    move_dist = self.move_speed * delta_time
                    if move_dist >= distance:
                        self.x = self.target_x
                        self.y = self.target_y
                    else:
                        self.x += (dx / distance) * move_dist
                        self.y += (dy / distance) * move_dist
                else:
                    self.x = self.target_x
                    self.y = self.target_y

    def get_skill_for_job(self, job_type: JobType) -> int:
        """Get skill level for a specific job type."""
        if job_type == JobType.CONSTRUCTION:
            return self.construction_skill
        elif job_type == JobType.GATHERING:
            return self.gathering_skill
        elif job_type == JobType.HAULING:
            return self.hauling_skill
        return 5  # Default

    def can_do_job(self, job_type: JobType) -> bool:
        """Check if citizen can perform a job type."""
        if job_type == JobType.CONSTRUCTION:
            return self.can_construct
        elif job_type == JobType.GATHERING:
            return self.can_gather
        elif job_type == JobType.HAULING:
            return self.can_haul
        return True

    def to_dict(self) -> dict:
        """Serialize to dictionary for saving."""
        return {
            'id': self.id,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'state': self.state.value,
            'current_job': self.current_job.value if self.current_job else None,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'construction_skill': self.construction_skill,
            'gathering_skill': self.gathering_skill,
            'hauling_skill': self.hauling_skill,
            'can_construct': self.can_construct,
            'can_gather': self.can_gather,
            'can_haul': self.can_haul,
            'carrying_resource': self.carrying_resource,
            'carrying_amount': self.carrying_amount,
            'move_speed': self.move_speed,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Citizen':
        """Deserialize from dictionary."""
        citizen = Citizen(
            id=data['id'],
            name=data['name'],
            x=data['x'],
            y=data['y'],
        )
        citizen.state = CitizenState(data['state'])
        citizen.current_job = JobType(data['current_job']) if data['current_job'] else None
        citizen.target_x = data['target_x']
        citizen.target_y = data['target_y']
        citizen.construction_skill = data['construction_skill']
        citizen.gathering_skill = data['gathering_skill']
        citizen.hauling_skill = data['hauling_skill']
        citizen.can_construct = data['can_construct']
        citizen.can_gather = data['can_gather']
        citizen.can_haul = data['can_haul']
        citizen.carrying_resource = data['carrying_resource']
        citizen.carrying_amount = data['carrying_amount']
        citizen.move_speed = data['move_speed']
        return citizen


# Name generator for citizens
FIRST_NAMES = [
    "Aelric", "Bran", "Cedric", "Doran", "Elara", "Finn", "Greta", "Hilda",
    "Isla", "Jorah", "Kael", "Lysa", "Mira", "Nolan", "Olwen", "Piper",
    "Quinn", "Rolan", "Sasha", "Thora", "Una", "Vale", "Wren", "Xander",
    "Yara", "Zara"
]

LAST_NAMES = [
    "Ashwood", "Blackthorn", "Clearwater", "Dawnbringer", "Evergreen", "Fairwind",
    "Goldleaf", "Highvale", "Ironforge", "Jadebrook", "Kindler", "Lightfoot",
    "Meadowbrook", "Nightshade", "Oakenshield", "Proudhorn", "Quickstep", "Ravenwood",
    "Silverstream", "Thornberry", "Underhill", "Valorheart", "Windwhisper", "Youngblood"
]


def generate_citizen_name() -> str:
    """Generate a random citizen name."""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
