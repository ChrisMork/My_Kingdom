"""
A* Pathfinding system for My Kingdom.
Allows citizens to navigate around obstacles.
"""

import heapq
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass, field

from src.world.terrain import Tile, TerrainType
from src.entities.building import Building


@dataclass(order=True)
class Node:
    """A node in the A* pathfinding algorithm."""
    f_cost: float
    g_cost: float = field(compare=False)
    h_cost: float = field(compare=False)
    x: int = field(compare=False)
    y: int = field(compare=False)
    parent: Optional['Node'] = field(default=None, compare=False)


class Pathfinder:
    """
    A* pathfinding for citizens to navigate the world.

    Considers:
    - Terrain walkability (water is not walkable)
    - Building obstacles
    - Efficient path to target
    """

    def __init__(self):
        pass

    def find_path(
        self,
        start_x: int,
        start_y: int,
        goal_x: int,
        goal_y: int,
        tiles: List[List[Tile]],
        buildings: List[Building] = None,
        max_iterations: int = 1000
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find a path from start to goal using A*.

        Args:
            start_x, start_y: Starting position
            goal_x, goal_y: Goal position
            tiles: 2D array of terrain tiles
            buildings: List of buildings (obstacles)
            max_iterations: Maximum search iterations to prevent infinite loops

        Returns:
            List of (x, y) coordinates from start to goal, or None if no path
        """
        # Validate inputs
        if not tiles or len(tiles) == 0 or len(tiles[0]) == 0:
            return None

        height = len(tiles)
        width = len(tiles[0])

        # Check bounds
        if not (0 <= start_x < width and 0 <= start_y < height):
            return None
        if not (0 <= goal_x < width and 0 <= goal_y < height):
            return None

        # If already at goal
        if start_x == goal_x and start_y == goal_y:
            return [(start_x, start_y)]

        # Create building obstacle map
        building_obstacles = set()
        if buildings:
            for building in buildings:
                definition = building.get_definition()
                for by in range(building.y, building.y + definition.height):
                    for bx in range(building.x, building.x + definition.width):
                        if 0 <= bx < width and 0 <= by < height:
                            building_obstacles.add((bx, by))

        # Allow walking on goal tile even if it has a building
        if (goal_x, goal_y) in building_obstacles:
            building_obstacles.remove((goal_x, goal_y))

        # A* algorithm
        open_list = []
        closed_set: Set[Tuple[int, int]] = set()

        # Start node
        start_node = Node(
            f_cost=0,
            g_cost=0,
            h_cost=self._heuristic(start_x, start_y, goal_x, goal_y),
            x=start_x,
            y=start_y,
            parent=None
        )
        start_node.f_cost = start_node.g_cost + start_node.h_cost

        heapq.heappush(open_list, start_node)

        iterations = 0
        while open_list and iterations < max_iterations:
            iterations += 1

            # Get node with lowest f_cost
            current = heapq.heappop(open_list)

            # Check if reached goal
            if current.x == goal_x and current.y == goal_y:
                return self._reconstruct_path(current)

            # Add to closed set
            closed_set.add((current.x, current.y))

            # Check neighbors (8 directions)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nx, ny = current.x + dx, current.y + dy

                # Check bounds
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                # Skip if in closed set
                if (nx, ny) in closed_set:
                    continue

                # Check walkability
                if not self._is_walkable(nx, ny, tiles, building_obstacles):
                    continue

                # Calculate costs
                # Diagonal movement costs more (1.414 vs 1.0)
                move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                g_cost = current.g_cost + move_cost
                h_cost = self._heuristic(nx, ny, goal_x, goal_y)
                f_cost = g_cost + h_cost

                # Create neighbor node
                neighbor = Node(
                    f_cost=f_cost,
                    g_cost=g_cost,
                    h_cost=h_cost,
                    x=nx,
                    y=ny,
                    parent=current
                )

                # Add to open list
                heapq.heappush(open_list, neighbor)

        # No path found
        return None

    def _heuristic(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """
        Calculate heuristic (estimated distance to goal).
        Uses Euclidean distance.
        """
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def _is_walkable(
        self,
        x: int,
        y: int,
        tiles: List[List[Tile]],
        building_obstacles: Set[Tuple[int, int]]
    ) -> bool:
        """Check if a tile is walkable."""
        # Check building obstacle
        if (x, y) in building_obstacles:
            return False

        # Check terrain
        tile = tiles[y][x]

        # Water is not walkable
        if tile.terrain_type == TerrainType.WATER:
            return False

        # Stone/mountains might not be walkable (optional - you can adjust)
        # For now, let's allow walking on stone

        return True

    def _reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node back to start."""
        path = []
        current = node

        while current is not None:
            path.append((current.x, current.y))
            current = current.parent

        path.reverse()
        return path


# Global pathfinder instance
_pathfinder = None


def get_pathfinder() -> Pathfinder:
    """Get or create the global pathfinder."""
    global _pathfinder
    if _pathfinder is None:
        _pathfinder = Pathfinder()
    return _pathfinder
