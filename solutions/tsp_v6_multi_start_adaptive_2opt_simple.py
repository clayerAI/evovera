"""
Multi-start 2-opt with Adaptive Neighborhood - SIMPLE VERSION

Simplified implementation to ensure correctness.
"""

import numpy as np
import random
import time
from typing import List, Tuple

class SimpleAdaptive2opt:
    """Simplified multi-start 2-opt with adaptive neighborhood."""
    
    def __init__(self, max_iterations: int = 50, num_starts: int = 5):
        self.max_iterations = max_iterations
        self.num_starts = num_starts
    
    def solve_tsp(self, points: np.ndarray) -> Tuple[List[int], float]:
        """Solve TSP using simple adaptive 2-opt."""
        n = len(points)
        dist_matrix = self._calculate_distance_matrix(points)
        
        best_tour = None
        best_length = float('inf')
        
        for start in range(self.num_starts):
            # Random initial tour
            tour = list(range(n))
            random.shuffle(tour)
            length = self._tour_length(tour, dist_matrix)
            
            # Adaptive neighborhood: start with small, expand if no improvement
            neighborhood = min(10, n // 4)
            improved = True
            iteration = 0
            
            while improved and iteration < self.max_iterations:
                improved = False
                best_improvement = 0
                best_i = best_j = -1
                
                # Search for best 2-opt move within current neighborhood
                for i in range(n):
                    for delta in range(2, neighborhood + 1):
                        j = (i + delta) % n
                        if j == i:
                            continue
                            
                        improvement = self._calculate_2opt_improvement(
                            tour, i, j, dist_matrix
                        )
                        
                        if improvement > best_improvement:
                            best_improvement = improvement
                            best_i, best_j = i, j
                
                # Apply best move if found
                if best_improvement > 0:
                    tour = self._apply_2opt(tour, best_i, best_j)
                    length -= best_improvement
                    improved = True
                    
                    # If good improvement, keep neighborhood small
                    if best_improvement > length * 0.01:  # >1% improvement
                        neighborhood = max(5, neighborhood - 1)
                    else:
                        # Small improvement, expand neighborhood to escape local optimum
                        neighborhood = min(n // 2, neighborhood + 2)
                
                iteration += 1
            
            # Update best solution
            if length < best_length:
                best_tour = tour.copy()
                best_length = length
        
        return best_tour, best_length
    
    def _calculate_distance_matrix(self, points: np.ndarray) -> np.ndarray:
        """Calculate Euclidean distance matrix."""
        n = len(points)
        dist = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                dx = points[i, 0] - points[j, 0]
                dy = points[i, 1] - points[j, 1]
                d = np.sqrt(dx*dx + dy*dy)
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def _tour_length(self, tour: List[int], dist_matrix: np.ndarray) -> float:
        """Calculate tour length."""
        length = 0.0
        n = len(tour)
        for k in range(n):
            i = tour[k]
            j = tour[(k + 1) % n]
            length += dist_matrix[i, j]
        return length
    
    def _calculate_2opt_improvement(self, tour: List[int], i: int, j: int,
                                   dist_matrix: np.ndarray) -> float:
        """Calculate improvement from 2-opt move between positions i and j in tour."""
        n = len(tour)
        
        # Ensure i comes before j
        if j < i:
            i, j = j, i
        
        # Get city indices
        a = tour[i]
        b = tour[(i + 1) % n]
        c = tour[j]
        d = tour[(j + 1) % n]
        
        # Current edges: (a,b) and (c,d)
        current = dist_matrix[a, b] + dist_matrix[c, d]
        # New edges: (a,c) and (b,d)
        new = dist_matrix[a, c] + dist_matrix[b, d]
        
        return current - new
    
    def _apply_2opt(self, tour: List[int], i: int, j: int) -> List[int]:
        """Apply 2-opt move to tour at positions i and j."""
        n = len(tour)
        
        # Ensure i comes before j
        if j < i:
            i, j = j, i
        
        # Reverse segment between i+1 and j
        new_tour = tour.copy()
        segment = new_tour[i+1:j+1]
        new_tour[i+1:j+1] = segment[::-1]
        
        return new_tour

def solve_tsp(points: np.ndarray) -> Tuple[List[int], float]:
    """Wrapper function."""
    solver = SimpleAdaptive2opt(max_iterations=30, num_starts=3)
    return solver.solve_tsp(points)

def test_simple():
    """Test the simple adaptive 2-opt."""
    np.random.seed(42)
    
    # Small test
    n = 20
    points = np.random.rand(n, 2) * 100
    
    solver = SimpleAdaptive2opt(max_iterations=20, num_starts=3)
    tour, length = solver.solve_tsp(points)
    
    print(f"Test n={n}:")
    print(f"  Tour length: {length:.2f}")
    print(f"  Tour valid: {len(set(tour)) == n}")
    
    # Compare to random tours
    random_lengths = []
    for _ in range(100):
        random_tour = list(range(n))
        random.shuffle(random_tour)
        random_length = solver._tour_length(random_tour, solver._calculate_distance_matrix(points))
        random_lengths.append(random_length)
    
    print(f"  Random avg: {np.mean(random_lengths):.2f}")
    print(f"  Random min: {np.min(random_lengths):.2f}")
    print(f"  Improvement vs random min: {(np.min(random_lengths) - length) / np.min(random_lengths) * 100:.1f}%")

if __name__ == "__main__":
    test_simple()