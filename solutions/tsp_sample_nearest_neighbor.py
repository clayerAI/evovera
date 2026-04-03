"""
Sample TSP Nearest Neighbor Implementation
This is a simple implementation for testing the adversarial framework.
"""

import math
import random
from typing import List, Tuple

def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def nearest_neighbor_tsp(coordinates: List[Tuple[float, float]], start_city: int = 0) -> List[int]:
    """
    Solve TSP using nearest neighbor heuristic.
    
    Args:
        coordinates: List of (x, y) coordinates for each city
        start_city: Index of city to start from (default: 0)
    
    Returns:
        List of city indices in visitation order
    """
    n = len(coordinates)
    if n == 0:
        return []
    if n == 1:
        return [0]
    
    # Initialize
    unvisited = set(range(n))
    tour = []
    current = start_city
    
    # Start with the starting city
    tour.append(current)
    unvisited.remove(current)
    
    # Greedily select nearest neighbor
    while unvisited:
        nearest = None
        nearest_dist = float('inf')
        
        for city in unvisited:
            dist = euclidean_distance(coordinates[current], coordinates[city])
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = city
        
        if nearest is not None:
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        else:
            # Should not happen if unvisited is not empty
            break
    
    return tour

def solve_tsp(coordinates: List[Tuple[float, float]]) -> List[int]:
    """
    Main solve function for the adversarial test runner.
    Uses nearest neighbor with random start to avoid getting stuck on bad starting city.
    """
    # Try multiple random starts and pick the best
    best_tour = None
    best_length = float('inf')
    
    n = len(coordinates)
    if n <= 3:
        # For very small n, just use nearest neighbor from city 0
        return nearest_neighbor_tsp(coordinates, 0)
    
    # Try up to min(10, n) different starting cities
    num_starts = min(10, n)
    start_indices = random.sample(range(n), num_starts)
    
    for start in start_indices:
        tour = nearest_neighbor_tsp(coordinates, start)
        
        # Calculate tour length
        length = 0.0
        for i in range(len(tour)):
            city1 = tour[i]
            city2 = tour[(i + 1) % len(tour)]
            length += euclidean_distance(coordinates[city1], coordinates[city2])
        
        if length < best_length:
            best_length = length
            best_tour = tour
    
    return best_tour

# Alternative function name for compatibility
def solve(coordinates: List[Tuple[float, float]]) -> List[int]:
    """Alias for solve_tsp."""
    return solve_tsp(coordinates)

if __name__ == "__main__":
    # Simple test
    test_coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
    tour = solve_tsp(test_coords)
    print(f"Test coordinates: {test_coords}")
    print(f"Tour: {tour}")
    
    # Calculate length
    length = 0.0
    for i in range(len(tour)):
        city1 = tour[i]
        city2 = tour[(i + 1) % len(tour)]
        length += euclidean_distance(test_coords[city1], test_coords[city2])
    print(f"Tour length: {length}")