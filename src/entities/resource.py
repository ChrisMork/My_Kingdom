"""
Resource nodes that can be gathered by citizens.
"""

from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    """Types of resources that can be gathered."""
    TREE = "tree"
    STONE = "stone"
    BERRY_BUSH = "berry_bush"
    IRON_ORE = "iron_ore"


@dataclass
class Resource:
    """A gatherable resource node on a tile."""

    resource_type: ResourceType
    x: int
    y: int
    amount_remaining: int = 100
    max_amount: int = 100
    gather_time: float = 3.0  # Seconds to gather one unit

    # What resource it provides when gathered
    provides_resource: str = "wood"  # "wood", "stone", "food", "iron"
    provides_amount: int = 10  # Amount per gather action

    # Visual state
    is_depleted: bool = False
    currently_being_gathered: bool = False
    assigned_citizen_id: int = None

    # Designation state (for player-controlled gathering)
    designated: bool = False

    def __post_init__(self):
        """Set up resource type-specific properties."""
        if self.resource_type == ResourceType.TREE:
            self.provides_resource = "wood"
            self.provides_amount = 4  # Each tree gives exactly 4 wood
            self.gather_time = 3.0  # Faster gathering
            self.max_amount = 4  # Tree has exactly one harvest worth
            self.amount_remaining = self.max_amount
        elif self.resource_type == ResourceType.STONE:
            self.provides_resource = "stone"
            self.provides_amount = 8  # Amount per harvest
            self.gather_time = 5.0
            self.max_amount = 24  # 3 harvests (8 stone × 3 = 24 total)
            self.amount_remaining = self.max_amount
        elif self.resource_type == ResourceType.BERRY_BUSH:
            self.provides_resource = "food"
            self.provides_amount = 5  # Amount per harvest
            self.gather_time = 2.0
            self.max_amount = 25  # 5 harvests (5 food × 5 = 25 total)
            self.amount_remaining = self.max_amount
        elif self.resource_type == ResourceType.IRON_ORE:
            self.provides_resource = "iron"
            self.provides_amount = 5
            self.gather_time = 6.0
            self.max_amount = 60
            self.amount_remaining = self.max_amount

    def gather(self) -> tuple[str, int]:
        """
        Gather from this resource.
        Returns (resource_type, amount) or (None, 0) if depleted.
        """
        if self.is_depleted or self.amount_remaining <= 0:
            self.is_depleted = True
            return (None, 0)

        # Calculate how much to gather
        gather_amount = min(self.provides_amount, self.amount_remaining)
        self.amount_remaining -= gather_amount

        if self.amount_remaining <= 0:
            self.is_depleted = True

        return (self.provides_resource, gather_amount)

    def get_gather_progress_percent(self) -> float:
        """Get how much of this resource has been gathered (0-1)."""
        return 1.0 - (self.amount_remaining / self.max_amount)

    def assign_citizen(self, citizen_id: int):
        """Assign a citizen to gather from this resource."""
        self.currently_being_gathered = True
        self.assigned_citizen_id = citizen_id

    def unassign_citizen(self):
        """Remove citizen assignment."""
        self.currently_being_gathered = False
        self.assigned_citizen_id = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for saving."""
        return {
            'resource_type': self.resource_type.value,
            'x': self.x,
            'y': self.y,
            'amount_remaining': self.amount_remaining,
            'max_amount': self.max_amount,
            'gather_time': self.gather_time,
            'provides_resource': self.provides_resource,
            'provides_amount': self.provides_amount,
            'is_depleted': self.is_depleted,
        }

    @staticmethod
    def from_dict(data: dict) -> 'Resource':
        """Deserialize from dictionary."""
        resource = Resource(
            resource_type=ResourceType(data['resource_type']),
            x=data['x'],
            y=data['y'],
            amount_remaining=data['amount_remaining'],
            max_amount=data['max_amount'],
            gather_time=data['gather_time'],
        )
        resource.provides_resource = data['provides_resource']
        resource.provides_amount = data['provides_amount']
        resource.is_depleted = data['is_depleted']
        return resource
