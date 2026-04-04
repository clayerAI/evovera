#!/usr/bin/env python3
"""
Nearest Neighbor TSP solver - FIXED VERSION for TSPLIB compatibility.
Accepts distance matrix parameter to support different TSPLIB distance metrics.
"""

import numpy as np
import random
import math
from typing import List, Tuple, Optional, Union

class NearestNeighborTSP:
    """
    Nearest Neighbor TSP solver with distance matrix support.
    
    FIXED: Accepts precomputed distance matrix for TSPLIB compatibility.
    Supports both Euclidean (via points) and TSPLIB (via distance_matrix) inputs.
    """
    
    def __init__(self, points: Optional[np.ndarray] = None, 
                 distance_matrix: Optional[np.ndarray] = None,
                 seed: Optional[int] = None):
        """
        Initialize solver.
        
        Args:
            points: Array of shape (n, 2) with city coordinates
            distance_matrix: Precomputed distance matrix of shape (n, n)
            seed: Random seed for reproducibility
        """
        if points is None and distance_matrix is None:
            raise ValueError("Must provide either points or distance_matrix")
        
        if points is not None:
            self.points = np.array(points)
            self.n = len(points)
            self.use_points = True
        else:
            self.n = distance_matrix.shape[0]
            self.use_points = False
        
        if distance_matrix is not None:
            self.dist_matrix = np.array(distance_matrix)
            self.use_distance_matrix = True
        else:
            self.dist_matrix = None
            self.use_distance_matrix = False
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute distance matrix from points (Euclidean)."""
        if not self.use_points:
            raise ValueError("Cannot compute distance matrix without points")
        
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = np.linalg.norm(self.points[i] - self.points[j])
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between cities i and j."""
        if self.use_distance_matrix and self.dist_matrix is not None:
            return self.dist_matrix[i, j]
        elif self.use_points:
            if self.dist_matrix is None:
                self.dist_matrix = self._compute_distance_matrix()
            return self.dist_matrix[i, j]
        else:
            raise ValueError("No distance information available")
    
    def solve(self, start_city: Optional[int] = None) -> Tuple[List[int], float]:
        """
        Solve TSP using nearest neighbor heuristic.
        
        Args:
            start_city: Starting city index (None for random)
            
        Returns:
            tour: List of city indices
            tour_length: Total tour length
        """
        if start_city is None:
            start_city = random.randint(0, self.n - 1)
        
        unvisited = set(range(self.n))
        tour = [start_city]
        unvisited.remove(start_city)
        
        current = start_city
        tour_length = 0.0
        
        while unvisited:
            # Find nearest unvisited city
            nearest = min(unvisited, key=lambda city: self.distance(current, city))
            tour_length += self.distance(current, nearest)
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to starting city
        tour_length += self.distance(current, start_city)
        tour.append(start_city)
        
        return tour, tour_length
    
    def solve_multiple_starts(self, num_starts: int = 10) -> Tuple[List[int], float]:
        """
        Run nearest neighbor from multiple starting cities and return best.
        
        Args:
            num_starts: Number of different starting cities to try
            
        Returns:
            best_tour: Best tour found
            best_length: Length of best tour
        """
        best_tour = None
        best_length = float('inf')
        
        # Try different starting cities
        starts = random.sample(range(self.n), min(num_starts, self.n))
        
        for start in starts:
            tour, length = self.solve(start_city=start)
            if length < best_length:
                best_length = length
                best_tour = tour
        
        return best_tour, best_length

def solve_tsp(points: np.ndarray, distance_matrix: Optional[np.ndarray] = None, 
              seed: Optional[int] = None) -> Tuple[List[int], float]:
    """
    Interface function for compatibility with existing code.
    
    Args:
        points: Array of shape (n, 2) with city coordinates
        distance_matrix: Optional precomputed distance matrix for TSPLIB
        seed: Random seed
        
    Returns:
        tour: List of city indices
        tour_length: Total tour length
    """
    solver = NearestNeighborTSP(points=points, distance_matrix=distance_matrix, seed=seed)
    return solver.solve_multiple_starts(num_starts=10)

# Test function
if __name__ == "__main__":
    # Test with simple points
    points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    
    print("Testing Nearest Neighbor with Euclidean distances:")
    tour, length = solve_tsp(points)
    print(f"Tour: {tour}")
    print(f"Length: {length:.2f}")
    
    # Test with distance matrix
    print("\nTesting with custom distance matrix:")
    n = len(points)
    custom_dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            custom_dist[i, j] = abs(i - j) * 10  # Simple linear distance
    
    tour2, length2 = solve_tsp(points, distance_matrix=custom_dist)
    print(f"Tour: {tour2}")
    print(f"Length: {length2:.2f}")
    
    print("\n✅ Fixed version ready for TSPLIB evaluation")