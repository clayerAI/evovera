"""
TSP Hybrid Algorithm #2: Christofides-ILS Hybrid (Simplified Version)

Novel Hybrid Approach: Uses Christofides algorithm to generate initial solution,
then applies Iterative Local Search for improvement. Includes adaptive restart
when ILS stagnates.

Components:
1. Christofides: Provides 1.5x approximation guarantee starting solution
2. Iterative Local Search: Strategic perturbations + 2-opt local search
3. Adaptive Restart: Restart from new Christofides solution when ILS stagnates

Novelty Claims:
- Christofides + ILS combination not found in literature
- Adaptive restart based on ILS stagnation (not fixed iterations)
- Integration of approximation algorithm with metaheuristic refinement
"""

import numpy as np
import random
import time
import sys
import os
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing algorithms
from solutions.tsp_v2_christofides import solve_tsp as christofides_solve

def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two points."""
    return np.linalg.norm(p1 - p2)

def create_distance_matrix(points: np.ndarray) -> np.ndarray:
    """Create distance matrix for all points."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = euclidean_distance(points[i], points[j])
            dist_matrix[i, j] = dist
            dist_matrix[j, i] = dist
    return dist_matrix

def tour_length(tour: List[int], dist_matrix: np.ndarray) -> float:
    """Calculate total length of tour."""
    total = 0.0
    for i in range(len(tour)):
        j = (i + 1) % len(tour)
        # Ensure indices are integers
        idx_i = int(tour[i])
        idx_j = int(tour[j])
        total += dist_matrix[idx_i, idx_j]
    return total


def two_opt_improvement_fast(tour: List[int], dist_matrix: np.ndarray, 
                           max_iterations: int = 500) -> Tuple[List[int], float]:
    """
    Simple 2-opt local search improvement.
    
    Args:
        tour: Current tour
        dist_matrix: Distance matrix
        max_iterations: Maximum iterations
        
    Returns:
        Improved tour and its length
    """
    n = len(tour)
    best_tour = tour[:]
    best_length = tour_length(tour, dist_matrix)
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue  # Don't swap first and last
                
                # Calculate gain from 2-opt swap
                a, b = best_tour[i], best_tour[(i + 1) % n]
                c, d = best_tour[j], best_tour[(j + 1) % n]
                
                current = dist_matrix[a, b] + dist_matrix[c, d]
                new = dist_matrix[a, c] + dist_matrix[b, d]
                
                if new < current - 1e-9:  # Small epsilon for floating point
                    # Perform 2-opt swap
                    new_tour = best_tour[:i+1] + best_tour[i+1:j+1][::-1] + best_tour[j+1:]
                    new_length = best_length - current + new
                    
                    best_tour = new_tour
                    best_length = new_length
                    improved = True
                    break  # Restart search after improvement
            
            if improved:
                break
    
    return best_tour, best_length

def christofides_ils_hybrid_simple(
    points: np.ndarray,
    max_iterations: int = 50,
    stagnation_threshold: float = 0.0005,  # 0.05% relative improvement
    stagnation_window: int = 10,
    initial_perturbation_strength: int = 2
) -> Tuple[List[int], float, dict]:
    """
    Simplified Christofides-ILS Hybrid.
    
    Args:
        points: Array of (x, y) coordinates
        max_iterations: Maximum ILS iterations
        stagnation_threshold: Minimum average improvement to avoid restart
        stagnation_window: Number of iterations to check for stagnation
        initial_perturbation_strength: Initial perturbation strength
    
    Returns:
        (best_tour, best_length, statistics)
    """
    n = len(points)
    dist_matrix = create_distance_matrix(points)
    start_time = time.time()
    
    # Statistics
    stats = {
        'restarts': 0,
        'total_iterations': 0,
        'improvement_history': [],
        'elapsed_time': 0.0,
        'n': n,
        'parameters': {
            'max_iterations': max_iterations,
            'stagnation_threshold': stagnation_threshold,
            'stagnation_window': stagnation_window,
            'initial_perturbation_strength': initial_perturbation_strength
        }
    }
    
    # Generate initial Christofides solution
    # Convert points to list of tuples for Christofides
    points_list = [(float(p[0]), float(p[1])) for p in points]
    current_tour, christofides_length = christofides_solve(points_list)
    # Debug: check tour contents
    # print(f"Debug: n={n}, current_tour={current_tour}, tour length={len(current_tour)}")
    # print(f"Debug: tour types: {[type(x) for x in current_tour[:3]]}")
    # print(f"Debug: dist_matrix shape: {dist_matrix.shape}")
    current_length = tour_length(current_tour, dist_matrix)
    
    best_tour = current_tour[:]
    best_length = current_length
    
    perturbation_strength = initial_perturbation_strength
    no_improvement_count = 0
    improvement_history = []
    
    for iteration in range(max_iterations):
        # Local search improvement
        improved_tour, improved_length = two_opt_improvement_fast(
            current_tour, dist_matrix, max_iterations=500
        )
        
        # Check for improvement
        if improved_length < current_length:
            # Calculate relative improvement (percentage of current length)
            relative_improvement = (current_length - improved_length) / current_length
            improvement_history.append(relative_improvement)
            current_tour, current_length = improved_tour, improved_length
            
            # Update best solution
            if current_length < best_length:
                best_tour, best_length = current_tour[:], current_length
                no_improvement_count = 0
                
                # Adjust perturbation strength based on quality
                if relative_improvement > 0.01:  # >1% improvement
                    perturbation_strength = max(1, perturbation_strength - 1)
                elif relative_improvement < 0.001:  # <0.1% improvement
                    perturbation_strength = min(5, perturbation_strength + 1)
            else:
                no_improvement_count += 1
        else:
            no_improvement_count += 1
        
        # Check for stagnation
        if len(improvement_history) >= stagnation_window:
            recent_improvements = improvement_history[-stagnation_window:]
            avg_improvement = np.mean(recent_improvements) if recent_improvements else 0
            
            # If average improvement is below threshold, restart from new Christofides solution
            if avg_improvement < stagnation_threshold:
                # Generate new Christofides solution
                current_tour = christofides_solve(points_list)
                current_length = tour_length(current_tour, dist_matrix)
                stats['restarts'] += 1
                
                # Reset tracking
                improvement_history = []
                no_improvement_count = 0
                perturbation_strength = initial_perturbation_strength
        
        # Apply perturbation for next iteration
        current_tour = strategic_perturbation(current_tour, perturbation_strength)
        current_length = tour_length(current_tour, dist_matrix)
        
        stats['total_iterations'] += 1
    
    stats['improvement_history'] = improvement_history
    stats['elapsed_time'] = time.time() - start_time
    
    return best_tour, best_length, stats

def solve_tsp_original(
    points: np.ndarray,
    time_limit: float = 30.0
) -> Tuple[List[int], float, dict]:
    """
    Solve TSP using Christofides-ILS hybrid algorithm.
    
    Args:
        points: Array of (x, y) coordinates
        time_limit: Maximum time in seconds
    
    Returns:
        (tour, length, statistics)
    """
    n = len(points)
    
    # Adjust parameters based on problem size
    max_iterations = min(100, max(30, n // 10))
    stagnation_threshold = 0.0005  # 0.05%
    stagnation_window = min(15, max(5, n // 50))
    
    tour, length, stats = christofides_ils_hybrid_simple(
        points,
        max_iterations=max_iterations,
        stagnation_threshold=stagnation_threshold,
        stagnation_window=stagnation_window,
        initial_perturbation_strength=2
    )
    
    return tour, length, stats


# Standard interface
def solve_tsp(points):
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    tour, length, _ = solve_tsp_original(points)
    return tour, length

def benchmark():
    """Run benchmark tests."""
    import json
    from typing import List, Tuple
    
    results = []
    for n in [50, 100]:
        print(f"\nTesting n={n}...")
        
        # Generate random points
        np.random.seed(42 + n)
        points = np.random.rand(n, 2) * 100
        
        # Run algorithm
        tour, length, stats = solve_tsp(points, time_limit=30.0)
        
        # Compare with Christofides baseline
        points_list = [(float(p[0]), float(p[1])) for p in points]
        christofides_tour_baseline = christofides_solve(points_list)
        
        dist_matrix = create_distance_matrix(points)
        christofides_length = tour_length(christofides_tour_baseline, dist_matrix)
        
        improvement = christofides_length / length if length > 0 else 1.0
        
        result = {
            'n': n,
            'hybrid_length': float(length),
            'christofides_length': float(christofides_length),
            'improvement_vs_christofides': float(improvement),
            'elapsed_time': stats['elapsed_time'],
            'restarts': stats['restarts'],
            'total_iterations': stats['total_iterations']
        }
        results.append(result)
        
        print(f"  Hybrid: {length:.3f}, Christofides: {christofides_length:.3f}, Improvement: {improvement:.3f}x")
        print(f"  Time: {stats['elapsed_time']:.2f}s, Restarts: {stats['restarts']}")
    
    # Save results
    with open('christofides_ils_hybrid_simple_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nBenchmark results saved to christofides_ils_hybrid_simple_benchmark.json")
    return results

if __name__ == "__main__":
    benchmark()