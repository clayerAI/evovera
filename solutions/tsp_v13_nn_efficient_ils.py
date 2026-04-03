"""
TSP Hybrid Algorithm v13: NN with Efficient ILS using incremental updates

Novel hybrid approach: Start with NN tour, apply efficient ILS with
incremental distance updates to avoid recomputing full tour length.

Key novelties:
1. Incremental distance updates for 2-opt moves (O(1) instead of O(n))
2. Fast local search with first-improvement strategy
3. Efficient perturbation and acceptance
4. Optimized for speed while maintaining quality
"""

import numpy as np
import random
import math
import time
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt(np.sum((p1 - p2) ** 2))

def compute_distance_matrix(points: np.ndarray) -> np.ndarray:
    """Precompute distance matrix for faster lookups"""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = euclidean_distance(points[i], points[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix

def nearest_neighbor_tsp(points: np.ndarray, dist_matrix: np.ndarray = None) -> List[int]:
    """Nearest neighbor algorithm for TSP"""
    n = len(points)
    if dist_matrix is None:
        dist_matrix = compute_distance_matrix(points)
    
    unvisited = set(range(n))
    tour = [0]
    unvisited.remove(0)
    
    while unvisited:
        current = tour[-1]
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist_matrix[current, city])
        tour.append(nearest)
        unvisited.remove(nearest)
    
    return tour

def fast_local_search(tour: List[int], dist_matrix: np.ndarray, 
                     max_trials: int = 100) -> Tuple[List[int], float]:
    """
    Fast local search using first-improvement 2-opt with incremental updates
    """
    n = len(tour)
    current_tour = tour.copy()
    
    # Current tour length
    current_length = 0.0
    for i in range(n):
        j = (i + 1) % n
        current_length += dist_matrix[current_tour[i], current_tour[j]]
    
    improved = True
    iterations = 0
    
    while improved and iterations < 20:  # Limit iterations for speed
        improved = False
        iterations += 1
        
        # Try random 2-opt moves
        for _ in range(max_trials):
            # Choose two random edges (i, i+1) and (j, j+1)
            i = random.randint(0, n - 2)
            j = random.randint(i + 2, n - 1) if i < n - 2 else random.randint(0, n - 3)
            if j <= i:
                j = (j + i + 2) % n
            
            # Cities at the four positions
            a = current_tour[i]
            b = current_tour[(i + 1) % n]
            c = current_tour[j]
            d = current_tour[(j + 1) % n]
            
            # Calculate gain
            current = dist_matrix[a, b] + dist_matrix[c, d]
            new = dist_matrix[a, c] + dist_matrix[b, d]
            gain = current - new
            
            if gain > 1e-10:  # Significant improvement
                # Reverse segment between i+1 and j
                if i + 1 < j:
                    current_tour[i+1:j+1] = reversed(current_tour[i+1:j+1])
                else:
                    # Handle wrap-around case (j < i)
                    # Reverse segment from i+1 to end and from start to j
                    segment = current_tour[i+1:] + current_tour[:j+1]
                    segment.reverse()
                    current_tour[i+1:] = segment[:len(current_tour[i+1:])]
                    current_tour[:j+1] = segment[len(current_tour[i+1:]):]
                
                # Update length incrementally
                current_length -= gain
                improved = True
                break  # First-improvement strategy
    
    return current_tour, current_length

def double_bridge_kick(tour: List[int]) -> List[int]:
    """Apply double-bridge perturbation"""
    n = len(tour)
    if n < 8:
        return tour.copy()
    
    # Choose 4 random cut points
    points = sorted(random.sample(range(1, n - 1), 4))
    a, b, c, d = points
    
    # Reorder segments: [0..a], [c..d], [b..c], [a..b]
    new_tour = tour[:a] + tour[c:d] + tour[b:c] + tour[a:b] + tour[d:]
    return new_tour

class EfficientILS:
    """Efficient Iterated Local Search"""
    
    def __init__(self, max_iterations: int = 200, initial_temp: float = 0.05):
        self.max_iterations = max_iterations
        self.temperature = initial_temp
        self.cooling_rate = 0.97
    
    def solve(self, initial_tour: List[int], dist_matrix: np.ndarray) -> Tuple[List[int], float, Dict]:
        """Run efficient ILS"""
        current_tour = initial_tour.copy()
        
        # Initial tour length
        n = len(current_tour)
        current_length = 0.0
        for i in range(n):
            j = (i + 1) % n
            current_length += dist_matrix[current_tour[i], current_tour[j]]
        
        best_tour = current_tour.copy()
        best_length = current_length
        initial_length = current_length
        
        stats = {
            'iterations': 0,
            'improvements': 0,
            'perturbations': 0,
            'acceptances': 0
        }
        
        for iteration in range(self.max_iterations):
            # Local search
            new_tour, new_length = fast_local_search(current_tour, dist_matrix, max_trials=30)
            
            # Acceptance criterion
            delta = new_length - current_length
            
            if delta < 0 or random.random() < math.exp(-delta / self.temperature):
                current_tour = new_tour
                current_length = new_length
                stats['acceptances'] += 1
                
                if delta < 0:
                    stats['improvements'] += 1
                    
                    # Update best solution
                    if new_length < best_length:
                        best_tour = new_tour.copy()
                        best_length = new_length
            
            # Perturbation every 5-10 iterations
            if iteration % random.randint(5, 10) == 0:
                current_tour = double_bridge_kick(current_tour)
                current_length = 0.0
                for i in range(n):
                    j = (i + 1) % n
                    current_length += dist_matrix[current_tour[i], current_tour[j]]
                stats['perturbations'] += 1
            
            # Cool temperature
            self.temperature *= self.cooling_rate
            
            # Early stopping - only if no improvements for many iterations
            if iteration > 100 and stats['improvements'] < 5:
                break
        
        stats['iterations'] = iteration + 1
        stats['final_improvement'] = (initial_length - best_length) / initial_length
        
        return best_tour, best_length, stats

def solve_tsp_nn_efficient_ils(points: np.ndarray, 
                              max_iterations: int = 200) -> Tuple[List[int], float, Dict]:
    """
    Solve TSP using NN with efficient ILS
    
    Args:
        points: numpy array of shape (n, 2) with coordinates
        max_iterations: maximum ILS iterations
    
    Returns:
        tour: list of city indices
        length: total tour length
        stats: dictionary with algorithm statistics
    """
    # Precompute distance matrix
    dist_matrix = compute_distance_matrix(points)
    
    # Start with NN tour
    initial_tour = nearest_neighbor_tsp(points, dist_matrix)
    
    # Run efficient ILS
    solver = EfficientILS(max_iterations=max_iterations)
    best_tour, best_length, stats = solver.solve(initial_tour, dist_matrix)
    
    # Update stats
    initial_length = 0.0
    n = len(initial_tour)
    for i in range(n):
        j = (i + 1) % n
        initial_length += dist_matrix[initial_tour[i], initial_tour[j]]
    
    stats['initial_length'] = initial_length
    stats['final_length'] = best_length
    stats['overall_improvement'] = (initial_length - best_length) / initial_length
    
    return best_tour, best_length, stats

# Quick test
if __name__ == "__main__":
    np.random.seed(42)
    n = 100
    points = np.random.rand(n, 2) * 100
    
    print(f"Testing NN with Efficient ILS on {n} cities")
    print("=" * 60)
    
    start_time = time.time()
    tour, length, stats = solve_tsp_nn_efficient_ils(points, max_iterations=100)
    end_time = time.time()
    
    print(f"Tour length: {length:.2f}")
    print(f"Initial length: {stats['initial_length']:.2f}")
    print(f"Overall improvement: {stats['overall_improvement']*100:.2f}%")
    print(f"Computation time: {end_time - start_time:.3f}s")
    print(f"Iterations: {stats['iterations']}")
    print(f"Improvements: {stats['improvements']}")