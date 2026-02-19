"""
Job management system for My Kingdom.
Implements work assignment from all three games:
- RimWorld: Priority-based work system
- Dwarf Fortress: Designation and hauling
- Songs of Syx: Unemployed build, workers at workplaces
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import random

from src.entities.citizen import Citizen, JobType, CitizenState
from src.entities.building import Building, BuildingState, BuildingType
from src.entities.resource import Resource
from src.world.terrain import TerrainType
from src.systems.pathfinding import get_pathfinder


@dataclass
class GatherTask:
    """A resource gathering task."""
    x: int
    y: int
    resource_type: str  # "wood", "stone", etc.
    amount: int
    assigned_to: Optional[int] = None  # Citizen ID


class JobManager:
    """
    Manages all citizen jobs and work assignments.

    Philosophy (from research):
    - Unemployed citizens build (Songs of Syx)
    - Employed citizens work at their workplace (Songs of Syx)
    - Priority system for tasks (RimWorld)
    - Designation system (Dwarf Fortress)
    """

    def __init__(self):
        self.gather_tasks: List[GatherTask] = []
        # Track gathering time for each citizen
        self.citizen_gather_time: Dict[int, float] = {}
        # Pathfinder
        self.pathfinder = get_pathfinder()

    def update(
        self,
        citizens: List[Citizen],
        buildings: List[Building],
        tiles: List[List],
        delta_time: float,
        resources: Dict[str, int],
        resource_nodes: List[Resource] = None,
        storage_capacity_check=None
    ):
        """
        Update all job assignments and work.

        Args:
            citizens: List of all citizens
            buildings: List of all buildings
            tiles: 2D array of terrain tiles
            delta_time: Time since last update
            resources: Resource stockpile
            resource_nodes: List of resource nodes
            storage_capacity_check: Callable to check if storage can accept resources
        """
        self.storage_capacity_check = storage_capacity_check
        from src.core.logger import logger

        # Update each citizen
        for citizen in citizens:
            citizen.update(delta_time)

            # Assign work to idle citizens
            if citizen.state == CitizenState.IDLE and citizen.current_task is None:
                self._assign_work(citizen, buildings, tiles, resources, resource_nodes)

            # If working on a task
            elif citizen.current_task is not None:
                self._update_citizen_task(citizen, buildings, tiles, delta_time, resources, resource_nodes)

    def _assign_work(
        self,
        citizen: Citizen,
        buildings: List[Building],
        tiles: List[List],
        resources: Dict[str, int],
        resource_nodes: List[Resource] = None
    ):
        """
        Assign work to an idle citizen.

        Priority (from research):
        1. Haul materials to buildings (Dwarf Fortress)
        2. Construct buildings (highest priority)
        3. Gather resources
        4. Work at assigned workplace (Songs of Syx)
        """
        # Priority 1: Haul materials to buildings under construction
        material_task = self._find_material_hauling_task(citizen, buildings, resources)
        if material_task:
            citizen.assign_task(material_task, JobType.HAULING)
            return

        # Priority 2: Construction work
        construction_task = self._find_construction_task(citizen, buildings)
        if construction_task:
            citizen.assign_task(construction_task, JobType.CONSTRUCTION)
            return

        # Priority 3: Resource gathering
        gather_task = self._find_gathering_task(citizen, tiles, resources, resource_nodes)
        if gather_task:
            citizen.assign_task(gather_task, JobType.GATHERING)
            return
        # Priority 4: Work at workplace (if assigned)
        # TODO: Implement when we have production buildings

    def _find_material_hauling_task(
        self,
        citizen: Citizen,
        buildings: List[Building],
        resources: Dict[str, int]
    ) -> Optional[Building]:
        """
        Find a building that needs materials hauled.
        Dwarf Fortress approach: Materials must be delivered before construction.
        """
        if not citizen.can_haul:
            return None

        for building in buildings:
            if building.state == BuildingState.PLANNED:
                needed = building.get_required_materials()
                if needed:
                    # Check if we have any of the needed resources in stockpile
                    for resource_type, needed_amount in needed.items():
                        if resources.get(resource_type, 0) > 0:
                            return building

        return None

    def _find_construction_task(
        self,
        citizen: Citizen,
        buildings: List[Building]
    ) -> Optional[Building]:
        """
        Find a building that needs construction work.
        RimWorld approach: Skill affects construction speed.
        """
        if not citizen.can_construct:
            return None

        # Find buildings ready for construction
        ready_buildings = [
            b for b in buildings
            if b.can_start_construction() or b.state == BuildingState.UNDER_CONSTRUCTION
        ]

        if not ready_buildings:
            return None

        # Return closest (simple for now)
        return min(
            ready_buildings,
            key=lambda b: (citizen.x - b.x)**2 + (citizen.y - b.y)**2
        )

    def _find_gathering_task(
        self,
        citizen: Citizen,
        tiles: List[List],
        resources: Dict[str, int],
        resource_nodes: List[Resource] = None
    ) -> Optional[Resource]:
        """
        Find resource nodes to gather from.
        Returns the nearest ungathered TREE node (wood gathering only for now).
        """
        if not citizen.can_gather:
            return None

        if resource_nodes is None:
            return None

        # Find nearest DESIGNATED ungathered resource node (trees, stone, berries)
        from src.entities.resource import ResourceType

        available_nodes = [
            node for node in resource_nodes
            if (node.designated and  # Only gather designated resources
                not node.is_depleted and
                not node.currently_being_gathered)  # Any designated resource type
        ]

        if not available_nodes:
            return None

        # Find closest resource node
        def distance(node):
            return (citizen.x - node.x) ** 2 + (citizen.y - node.y) ** 2

        nearest = min(available_nodes, key=distance)

        # Assign citizen to this resource
        nearest.assign_citizen(citizen.id)

        return nearest

    def _update_citizen_task(
        self,
        citizen: Citizen,
        buildings: List[Building],
        tiles: List[List],
        delta_time: float,
        resources: Dict[str, int],
        resource_nodes: List[Resource] = None
    ):
        """Update a citizen currently working on a task."""

        # Material hauling
        if citizen.current_job == JobType.HAULING:
            self._update_hauling(citizen, buildings, resources, delta_time, tiles)

        # Construction
        elif citizen.current_job == JobType.CONSTRUCTION:
            self._update_construction(citizen, buildings, delta_time, tiles)

        # Gathering
        elif citizen.current_job == JobType.GATHERING:
            self._update_gathering(citizen, tiles, resources, delta_time, buildings)

    def _update_hauling(
        self,
        citizen: Citizen,
        buildings: List[Building],
        resources: Dict[str, int],
        delta_time: float,
        tiles: List[List]
    ):
        """
        Update material hauling task.
        Dwarf Fortress approach: Fetch from stockpile → Haul to building
        """
        building = citizen.current_task

        if not isinstance(building, Building):
            citizen.clear_task()
            return

        # State machine for hauling
        if citizen.carrying_resource is None:
            # Not carrying anything - go to stockpile (wagon)
            stockpile_x, stockpile_y = self._get_stockpile_location(buildings)

            if not citizen.has_reached_target():
                self._move_citizen_to(citizen, stockpile_x, stockpile_y, tiles, buildings)
            else:
                # At stockpile - pick up materials
                needed = building.get_required_materials()
                for resource_type, needed_amount in needed.items():
                    if resources.get(resource_type, 0) > 0:
                        # Pick up resource
                        amount_to_take = min(5, resources[resource_type], needed_amount)
                        citizen.carrying_resource = resource_type
                        citizen.carrying_amount = amount_to_take
                        resources[resource_type] -= amount_to_take
                        citizen.state = CitizenState.CARRYING
                        break

        else:
            # Carrying materials - go to building
            building_x, building_y = building.get_center()

            if not citizen.has_reached_target():
                self._move_citizen_to(citizen, building_x, building_y, tiles, buildings)
            else:
                # At building - deliver materials
                building.deliver_material(citizen.carrying_resource, citizen.carrying_amount)
                citizen.carrying_resource = None
                citizen.carrying_amount = 0

                # Check if building still needs materials
                if not building.get_required_materials():
                    # Done hauling for this building
                    citizen.clear_task()
                # Otherwise continue hauling

    def _update_construction(
        self,
        citizen: Citizen,
        buildings: List[Building],
        delta_time: float,
        tiles: List[List]
    ):
        """
        Update construction task.
        RimWorld approach: Skill affects speed.
        """
        building = citizen.current_task

        if not isinstance(building, Building):
            citizen.clear_task()
            return

        # Check if building can be constructed
        if building.state == BuildingState.PLANNED and building.has_all_materials():
            building.state = BuildingState.UNDER_CONSTRUCTION

        if building.state == BuildingState.UNDER_CONSTRUCTION:
            # Move to building if not there
            building_x, building_y = building.get_center()

            if not citizen.has_reached_target():
                # Note: We don't pass buildings here to allow walking to the building site
                citizen.set_target(building_x, building_y)
            else:
                # At building - do construction work
                citizen.state = CitizenState.WORKING

                # Work speed based on skill (RimWorld)
                skill_multiplier = 1.0 + (citizen.construction_skill / 20.0)
                work_done = 10.0 * skill_multiplier * delta_time

                building.add_construction_progress(work_done)

                # Check if complete
                if building.state == BuildingState.COMPLETE:
                    citizen.clear_task()

        elif building.state == BuildingState.COMPLETE:
            # Building is done
            citizen.clear_task()

    def _update_gathering(
        self,
        citizen: Citizen,
        tiles: List[List],
        resources: Dict[str, int],
        delta_time: float,
        buildings: List[Building] = None
    ):
        """
        Update resource gathering task.
        Simple: Go to location → Gather → Return to stockpile
        """
        resource_node = citizen.current_task

        # Check if task is a Resource node
        if not isinstance(resource_node, Resource):
            citizen.clear_task()
            return

        # State machine for gathering
        if citizen.carrying_resource is None:
            # Not carrying - go to resource location
            # Always try to move (this will set target if not set, and move if not at target)
            self._move_citizen_to(citizen, float(resource_node.x), float(resource_node.y), tiles, buildings)

            # Check if we've reached the resource
            if citizen.has_reached_target():
                # At resource - start or continue gathering
                citizen.state = CitizenState.WORKING

                # Track gathering time (5 seconds to harvest a tree)
                GATHER_TIME = 5.0  # seconds

                if citizen.id not in self.citizen_gather_time:
                    # Start gathering timer
                    self.citizen_gather_time[citizen.id] = 0.0

                # Accumulate gathering time
                self.citizen_gather_time[citizen.id] += delta_time

                # Check if gathering is complete
                if self.citizen_gather_time[citizen.id] >= GATHER_TIME:
                    # Gathering complete - harvest the resource
                    resource_type, amount = resource_node.gather()

                    # Unassign citizen from resource
                    resource_node.unassign_citizen()

                    # Reset gathering timer
                    del self.citizen_gather_time[citizen.id]

                    if resource_type and amount > 0:
                        # Pick up the gathered resource
                        citizen.carrying_resource = resource_type
                        citizen.carrying_amount = amount
                        citizen.state = CitizenState.CARRYING
                        # Clear target so they need to move to stockpile
                        citizen.target_x = None
                        citizen.target_y = None

                        from src.core.logger import logger
                        logger.info(f"Citizen {citizen.id} ({citizen.name}) harvested {amount} {resource_type} - returning to wagon")
                    else:
                        # Resource was depleted or couldn't gather
                        citizen.clear_task()

        else:
            # Carrying resources - return to stockpile (wagon)
            stockpile_x, stockpile_y = self._get_stockpile_location(buildings)

            # Always try to move to stockpile (this will set target if not set)
            self._move_citizen_to(citizen, stockpile_x, stockpile_y, tiles, buildings)

            # Check if we've reached the stockpile
            if citizen.has_reached_target():
                # At stockpile - check storage capacity before depositing
                from src.core.logger import logger

                # Check if storage has room
                can_deposit = True
                if self.storage_capacity_check:
                    can_deposit = self.storage_capacity_check(citizen.carrying_amount)

                if can_deposit:
                    # Deposit resources
                    deposited_resource = citizen.carrying_resource
                    deposited_amount = citizen.carrying_amount

                    resources[citizen.carrying_resource] = (
                        resources.get(citizen.carrying_resource, 0) + citizen.carrying_amount
                    )

                    logger.info(f"Citizen {citizen.id} ({citizen.name}) deposited {deposited_amount} {deposited_resource} at wagon - Total: {resources[deposited_resource]}")

                    citizen.carrying_resource = None
                    citizen.carrying_amount = 0
                    citizen.clear_task()
                else:
                    # Storage full - drop resources and cancel task
                    logger.warning(f"Citizen {citizen.id} ({citizen.name}) cannot deposit {citizen.carrying_amount} {citizen.carrying_resource} - storage full!")
                    citizen.carrying_resource = None
                    citizen.carrying_amount = 0
                    citizen.clear_task()

    def _get_stockpile_location(self, buildings: List[Building]) -> Tuple[float, float]:
        """
        Get the location of the main stockpile (wagon).
        Returns center position of the wagon, or default location if no wagon exists.
        """
        if buildings:
            for building in buildings:
                if building.building_type == BuildingType.WAGON:
                    return building.get_center()

        # Fallback to default location
        return (5.0, 5.0)

    def _move_citizen_to(
        self,
        citizen: Citizen,
        target_x: float,
        target_y: float,
        tiles: List[List],
        buildings: List[Building]
    ):
        """
        Move a citizen to a target location using pathfinding.

        Args:
            citizen: The citizen to move
            target_x, target_y: Target location
            tiles: Terrain tiles
            buildings: List of buildings (for obstacle avoidance)
        """
        # Calculate path if citizen doesn't have one or target changed
        if not citizen.current_path or citizen.target_x != target_x or citizen.target_y != target_y:
            # Find path from current position to target
            start_x = int(citizen.x)
            start_y = int(citizen.y)
            goal_x = int(target_x)
            goal_y = int(target_y)

            path = self.pathfinder.find_path(
                start_x, start_y,
                goal_x, goal_y,
                tiles,
                buildings
            )

            # Set target with path
            citizen.set_target(target_x, target_y, path)

    def cancel_building_tasks(self, building: Building):
        """Cancel all tasks related to a building."""
        # Remove from citizen tasks
        # (Citizens will auto-reassign next update)
        pass
