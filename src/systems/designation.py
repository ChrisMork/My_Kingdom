"""
Designation System for My Kingdom
Based on research from Dwarf Fortress, RimWorld, and Songs of Syx
Allows players to designate areas for resource gathering
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import time
import logging

logger = logging.getLogger(__name__)


class DesignationType(Enum):
    """Types of designations players can make"""
    CHOP_TREES = "chop_trees"
    MINE_STONE = "mine_stone"
    GATHER_BERRIES = "gather_berries"


@dataclass
class Designation:
    """Represents a player-created designation for work"""
    designation_type: DesignationType
    objects: List  # List of designated objects (trees, stones, etc.)
    created_time: float = field(default_factory=time.time)
    completed: bool = False

    def cancel(self):
        """Cancel this designation and unmark all objects"""
        for obj in self.objects:
            obj.designated = False
        self.completed = True
        logger.info(f"Cancelled designation of type {self.designation_type.value} with {len(self.objects)} objects")

    def is_complete(self) -> bool:
        """Check if all objects in this designation are depleted"""
        if not self.objects:
            return True
        return all(hasattr(obj, 'is_depleted') and obj.is_depleted for obj in self.objects)


class DesignationManager:
    """Manages all active designations in the game"""

    def __init__(self):
        self.designations: List[Designation] = []
        logger.info("DesignationManager initialized")

    def add_designation(self, designation_type: DesignationType, objects: List) -> Designation:
        """Create a new designation and mark all objects as designated"""
        if not objects:
            logger.warning(f"Attempted to create empty designation of type {designation_type.value}")
            return None

        designation = Designation(
            designation_type=designation_type,
            objects=objects
        )

        # Mark all objects as designated
        for obj in objects:
            obj.designated = True

        self.designations.append(designation)
        logger.info(f"Created {designation_type.value} designation with {len(objects)} objects")
        return designation

    def update(self):
        """Update all designations, removing completed ones"""
        initial_count = len(self.designations)

        # Mark completed designations
        for designation in self.designations:
            if designation.is_complete() and not designation.completed:
                designation.completed = True
                logger.info(f"Designation {designation.designation_type.value} auto-completed")

        # Remove completed designations
        self.designations = [d for d in self.designations if not d.completed]

        removed_count = initial_count - len(self.designations)
        if removed_count > 0:
            logger.debug(f"Removed {removed_count} completed designations")

    def get_active_designations(self, designation_type: Optional[DesignationType] = None) -> List[Designation]:
        """Get all active designations, optionally filtered by type"""
        result = [d for d in self.designations if not d.completed]

        if designation_type:
            result = [d for d in result if d.designation_type == designation_type]

        return result

    def cancel_all(self, designation_type: Optional[DesignationType] = None):
        """Cancel all designations, optionally filtered by type"""
        to_cancel = self.get_active_designations(designation_type)
        for designation in to_cancel:
            designation.cancel()
        logger.info(f"Cancelled {len(to_cancel)} designations")

    def get_designated_objects(self, designation_type: DesignationType) -> List:
        """Get all objects that are designated for a specific type"""
        objects = []
        for designation in self.get_active_designations(designation_type):
            objects.extend([obj for obj in designation.objects if hasattr(obj, 'designated') and obj.designated])
        return objects


class AreaSelector:
    """Handles rectangle selection for area designation"""

    def __init__(self):
        self.is_selecting = False
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.current_x: Optional[int] = None
        self.current_y: Optional[int] = None
        self.designation_type: Optional[DesignationType] = None
        logger.info("AreaSelector initialized")

    def start_selection(self, screen_x: int, screen_y: int, designation_type: DesignationType):
        """Begin area selection at screen coordinates"""
        self.is_selecting = True
        self.start_x = screen_x
        self.start_y = screen_y
        self.current_x = screen_x
        self.current_y = screen_y
        self.designation_type = designation_type
        logger.debug(f"Started selection at ({screen_x}, {screen_y}) for {designation_type.value}")

    def update_selection(self, screen_x: int, screen_y: int):
        """Update current selection endpoint"""
        if self.is_selecting:
            self.current_x = screen_x
            self.current_y = screen_y

    def finish_selection(self) -> Optional[Tuple[int, int, int, int]]:
        """End selection and return rectangle bounds (min_x, min_y, max_x, max_y)"""
        if not self.is_selecting:
            return None

        self.is_selecting = False

        if self.start_x is None or self.current_x is None:
            return None

        min_x = min(self.start_x, self.current_x)
        min_y = min(self.start_y, self.current_y)
        max_x = max(self.start_x, self.current_x)
        max_y = max(self.start_y, self.current_y)

        logger.debug(f"Finished selection: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        return (min_x, min_y, max_x, max_y)

    def cancel_selection(self):
        """Cancel the current selection"""
        self.is_selecting = False
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.designation_type = None
        logger.debug("Selection cancelled")

    def get_rect_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """Get current rectangle bounds without finishing selection"""
        if not self.is_selecting or self.start_x is None or self.current_x is None:
            return None

        min_x = min(self.start_x, self.current_x)
        min_y = min(self.start_y, self.current_y)
        max_x = max(self.start_x, self.current_x)
        max_y = max(self.start_y, self.current_y)

        return (min_x, min_y, max_x, max_y)
