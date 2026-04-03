"""
TSP v1: Nearest Neighbor Implementation (Evo's solution)
Wrapper to adapt Evo's implementation for adversarial testing framework.
"""

import random
import math
from typing import List, Tuple
import numpy as np

def solve_tsp(coordinates: List[Tuple[float, float]]) -> List[int]:
    """
    Solve TSP using nearest neighbor heuristic (Evo's algorithm).
    
    Args:
        coordinates: List of (x, y) coordinates for each city
    
    Returns:
        List of city indices in visitation order (0-based)
    """
    n = len(coordinates)
    
    # Convert coordinates to numpy array
    points = np.array(coordinates)
    
    # Create a custom TSP instance with these points
    class CustomTSP:
        def __init__(self, points):
            self.n = len(points)
            self.points = points
            self.dist_matrix = self._compute_distance_matrix()
        
        def _compute_distance_matrix(self):
            import math
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
        
        def distance(self, i, j):
            return self.dist_matrix[i, j]
        
        def nearest_neighbor(self, start_city=None):
            import random
            if start_city is None:
                start_city = random.randint(0, self.n - 1)
            
            unvisited = set(range(self.n))
            tour = [start_city]
            unvisited.remove(start_city)
            
            current = start_city
            total_distance = 0.0
            
            while unvisited:
                # Find nearest unvisited city
                nearest = min(unvisited, key=lambda city: self.distance(current, city))
                total_distance += self.distance(current, nearest)
                
                tour.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Return to starting city
            total_distance += self.distance(current, start_city)
            tour.append(start_city)
            
            return tour, total_distance
        
        def nearest_neighbor_multistart(self, num_starts=10):
            best_tour = None
            best_distance = float('inf')
            
            # Try random starting cities
            starts = random.sample(range(self.n), min(num_starts, self.n))
            
            for start in starts:
                tour, distance = self.nearest_neighbor(start)
                if distance < best_distance:
                    best_tour = tour
                    best_distance = distance
            
            return best_tour, best_distance
    
    # Create instance and solve
    tsp = CustomTSP(points)
    tour, _ = tsp.nearest_neighbor_multistart(num_starts=min(10, n))
    
    # Remove the duplicate starting city at the end for our test framework
    if tour and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour

# Alias for compatibility
def solve(coordinates: List[Tuple[float, float]]) -> List[int]:
    return solve_tsp(coordinates)

if __name__ == "__main__":
    # Test with simple square
    test_coords = [(0, 0), (10, 0), (10, 10), (0, 10)]
    tour = solve_tsp(test_coords)
    print(f"Test coordinates: {test_coords}")
    print(f"Tour: {tour}")
    
    # Calculate length
    import math
    length = 0.0
    for i in range(len(tour)):
        city1 = tour[i]
        city2 = tour[(i + 1) % len(tour)]
        x1, y1 = test_coords[city1]
        x2, y2 = test_coords[city2]
        length += math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    print(f"Tour length: {length}")
    print(f"Expected optimal: 40.0 (square perimeter)")
    print(f"Ratio: {length/40.0:.3f}")