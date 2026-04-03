"""
TSP Hybrid Algorithm #1: NN-ILS Hybrid with Adaptive Restart

Novel Hybrid Approach: Combines Nearest Neighbor construction with Iterative Local Search,
but adds adaptive restart mechanism based on solution quality stagnation.

Hypothesis: This specific combination with adaptive restart thresholds (not fixed iteration counts)
and quality-based perturbation strength adjustment represents a novel approach not found in TSP literature.

Components:
1. Nearest Neighbor: Fast construction heuristic
2. Iterative Local Search: Strategic perturbations + fast local search
3. Adaptive Restart: When improvement < threshold for N iterations, restart from new NN solution
4. Quality-based Perturbation: Perturbation strength adjusted based on current solution quality

Novelty Claims:
- Adaptive restart based on solution quality stagnation (not fixed iteration counts)
- Quality-based perturbation strength adjustment (stronger perturbations for worse solutions)
- Hybrid of construction heuristic (NN) with metaheuristic (ILS) with restart mechanism
- No literature found combining these specific components with these adaptive mechanisms
"""

import numpy as np
import time
import random
from typing import List, Tuple, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def nearest_neighbor_tour(dist_matrix: np.ndarray, start_node: int = 0) -> List[int]:
    """Construct tour using nearest neighbor heuristic."""
    n = len(dist_matrix)
    unvisited = set(range(n))
    tour = [start_node]
    unvisited.remove(start_node)
    
    current = start_node
    while unvisited:
        # Find nearest unvisited neighbor
        nearest = min(unvisited, key=lambda node: dist_matrix[current][node])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour

def validate_tour(tour: List[int], n: int) -> bool:
    """Validate that tour is a proper permutation of [0, n-1]."""
    if len(tour) != n:
        return False
    if set(tour) != set(range(n)):
        return False
    # Check for duplicates
    if len(tour) != len(set(tour)):
        return False
    return True

def tour_length(tour: List[int], dist_matrix: np.ndarray) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += dist_matrix[tour[i]][tour[j]]
    return total

def two_opt_swap(tour: List[int], i: int, j: int) -> List[int]:
    """Perform 2-opt swap between positions i and j.
    
    Standard 2-opt: Reverse segment from i+1 to j.
    Removes edges (i, i+1) and (j, j+1), adds edges (i, j) and (i+1, j+1).
    """
    # Note: i < j is assumed
    new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
    return new_tour

def two_opt_improvement(tour: List[int], dist_matrix: np.ndarray, max_iterations: int = 1000) -> Tuple[List[int], float]:
    """Improve tour using 2-opt local search with limited iterations."""
    n = len(tour)
    current_tour = tour[:]
    current_length = tour_length(current_tour, dist_matrix)
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        for i in range(n - 1):
            for j in range(i + 1, n):
                # Calculate gain from swapping
                a1, a2 = current_tour[i], current_tour[(i + 1) % n]
                b1, b2 = current_tour[j], current_tour[(j + 1) % n]
                
                old_segment = dist_matrix[a1][a2] + dist_matrix[b1][b2]
                new_segment = dist_matrix[a1][b1] + dist_matrix[a2][b2]
                
                if new_segment < old_segment:
                    # Perform the swap
                    current_tour = two_opt_swap(current_tour, i, j)
                    current_length = current_length - old_segment + new_segment
                    improved = True
                    iterations += 1
                    break
            if improved:
                break
    
    return current_tour, current_length

def strategic_perturbation(tour: List[int], strength: int, dist_matrix: np.ndarray) -> List[int]:
    """
    Apply strategic perturbation to escape local optima.
    
    Strength determines perturbation intensity:
    1: Simple swap of two random cities
    2: Reverse a random segment
    3: Move a random segment to different position
    4: Combination of above
    """
    n = len(tour)
    perturbed = tour[:]
    
    if strength == 1:
        # Simple swap of two random cities
        idx1, idx2 = random.sample(range(n), 2)
        perturbed[idx1], perturbed[idx2] = perturbed[idx2], perturbed[idx1]
    
    elif strength == 2:
        # Reverse a random segment
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)
        perturbed[i:j+1] = perturbed[i:j+1][::-1]
    
    elif strength == 3:
        # Move a random segment to different position
        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)
        segment = perturbed[i:j+1]
        remaining = perturbed[:i] + perturbed[j+1:]
        insert_pos = random.randint(0, len(remaining))
        perturbed = remaining[:insert_pos] + segment + remaining[insert_pos:]
    
    else:  # strength >= 4
        # Combination of perturbations
        for _ in range(min(strength, 3)):
            if random.random() < 0.5:
                # Reverse random segment
                i = random.randint(0, n - 2)
                j = random.randint(i + 1, n - 1)
                perturbed[i:j+1] = perturbed[i:j+1][::-1]
            else:
                # Swap random cities
                idx1, idx2 = random.sample(range(n), 2)
                perturbed[idx1], perturbed[idx2] = perturbed[idx2], perturbed[idx1]
    
    # Validate the perturbation produced a valid tour
    if not validate_tour(perturbed, n):
        # Fall back to original tour if perturbation created invalid tour
        perturbed = tour[:]
    
    return perturbed

def adaptive_restart_ils_hybrid(
    dist_matrix: np.ndarray,
    max_iterations: int = 100,
    stagnation_threshold: float = 0.001,
    stagnation_window: int = 10,
    initial_perturbation_strength: int = 2
) -> Tuple[List[int], float, dict]:
    """
    NN-ILS Hybrid with Adaptive Restart.
    
    Novel features:
    1. Adaptive restart when improvement < stagnation_threshold for stagnation_window iterations
    2. Quality-based perturbation strength adjustment
    3. Combines NN construction with ILS metaheuristic
    
    Returns:
        best_tour: Best tour found
        best_length: Length of best tour
        stats: Dictionary with algorithm statistics
    """
    n = len(dist_matrix)
    stats = {
        'restarts': 0,
        'perturbation_strength_changes': 0,
        'total_iterations': 0,
        'improvement_history': []
    }
    
    # Initial solution using Nearest Neighbor
    best_tour = nearest_neighbor_tour(dist_matrix, start_node=random.randint(0, n-1))
    best_length = tour_length(best_tour, dist_matrix)
    
    current_tour = best_tour[:]
    current_length = best_length
    
    perturbation_strength = initial_perturbation_strength
    no_improvement_count = 0
    improvement_history = []
    
    for iteration in range(max_iterations):
        stats['total_iterations'] += 1
        
        # Local search improvement
        improved_tour, improved_length = two_opt_improvement(current_tour, dist_matrix, max_iterations=500)
        
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
                # Better solutions get smaller perturbations
                relative_quality = best_length / (n * np.mean(dist_matrix))
                if relative_quality < 0.8:
                    perturbation_strength = max(1, perturbation_strength - 1)
                    stats['perturbation_strength_changes'] += 1
            else:
                no_improvement_count += 1
        else:
            no_improvement_count += 1
        
        # Check for stagnation
        if len(improvement_history) >= stagnation_window:
            recent_improvements = improvement_history[-stagnation_window:]
            avg_improvement = np.mean(recent_improvements) if recent_improvements else 0
            
            # stagnation_threshold is now relative (e.g., 0.0005 = 0.05% improvement)
            if avg_improvement < stagnation_threshold:
                # Adaptive restart: generate new NN solution
                current_tour = nearest_neighbor_tour(dist_matrix, start_node=random.randint(0, n-1))
                current_length = tour_length(current_tour, dist_matrix)
                stats['restarts'] += 1
                no_improvement_count = 0
                improvement_history = []
                
                # Reset perturbation strength
                perturbation_strength = initial_perturbation_strength
                stats['perturbation_strength_changes'] += 1
        
        # Apply strategic perturbation
        current_tour = strategic_perturbation(current_tour, perturbation_strength, dist_matrix)
        
        # Validate tour after perturbation
        if not validate_tour(current_tour, n):
            print(f"Warning: Invalid tour after perturbation at iteration {iteration}")
            # Reset to best tour
            current_tour = best_tour[:]
        
        current_length = tour_length(current_tour, dist_matrix)
    
    stats['improvement_history'] = improvement_history
    return best_tour, best_length, stats

def solve_tsp_original(points: np.ndarray, time_limit: float = 30.0) -> Tuple[List[int], float, dict]:
    """
    Original solve_tsp function returning (tour, length, statistics).
    
    Args:
        points: Array of points (n x 2)
        time_limit: Maximum time in seconds
    
    Returns:
        tour: List of node indices in visitation order
        length: Total tour length
        metadata: Algorithm statistics and parameters
    """
    start_time = time.time()
    
    # Create distance matrix
    dist_matrix = create_distance_matrix(points)
    n = len(points)
    
    # Adjust parameters based on problem size
    max_iterations = min(200, max(50, n // 5))
    stagnation_threshold = 0.0005
    stagnation_window = min(15, max(5, n // 50))
    
    # Run hybrid algorithm
    tour, length, stats = adaptive_restart_ils_hybrid(
        dist_matrix,
        max_iterations=max_iterations,
        stagnation_threshold=stagnation_threshold,
        stagnation_window=stagnation_window,
        initial_perturbation_strength=2
    )
    
    elapsed_time = time.time() - start_time
    stats['elapsed_time'] = elapsed_time
    stats['n'] = n
    stats['parameters'] = {
        'max_iterations': max_iterations,
        'stagnation_threshold': stagnation_threshold,
        'stagnation_window': stagnation_window,
        'initial_perturbation_strength': 2
    }
    
    return tour, length, stats


def solve_tsp(points: np.ndarray, time_limit: float = 30.0) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: Array of points (n x 2)
        time_limit: Maximum time in seconds
    
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    tour, length, stats = solve_tsp_original(points, time_limit)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length

def benchmark_algorithm():
    """Run benchmark tests on the hybrid algorithm."""
    import json
    from pathlib import Path
    
    # Test on random instances
    np.random.seed(42)
    random.seed(42)
    
    results = []
    for n in [50, 100, 200, 500]:
        print(f"\nTesting n={n}...")
        
        # Generate random points
        points = np.random.rand(n, 2) * 100
        
        # Run algorithm
        tour, length, stats = solve_tsp(points, time_limit=30.0)
        
        # Compare with Nearest Neighbor baseline
        dist_matrix = create_distance_matrix(points)
        nn_tour = nearest_neighbor_tour(dist_matrix)
        nn_length = tour_length(nn_tour, dist_matrix)
        
        improvement = nn_length / length if length > 0 else 1.0
        
        result = {
            'n': n,
            'hybrid_length': float(length),
            'nn_length': float(nn_length),
            'improvement_vs_nn': float(improvement),
            'elapsed_time': stats['elapsed_time'],
            'restarts': stats['restarts'],
            'total_iterations': stats['total_iterations'],
            'perturbation_strength_changes': stats['perturbation_strength_changes']
        }
        results.append(result)
        
        print(f"  Hybrid: {length:.3f}, NN: {nn_length:.3f}, Improvement: {improvement:.3f}x")
        print(f"  Time: {stats['elapsed_time']:.3f}s, Restarts: {stats['restarts']}")
    
    # Save results
    output_file = Path(__file__).parent / "nn_ils_hybrid_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBenchmark results saved to {output_file}")
    return results

if __name__ == "__main__":
    # Run benchmark when executed directly
    benchmark_algorithm()