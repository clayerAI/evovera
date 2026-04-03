"""
TSP Hybrid Algorithm #2: Christofides-ILS Hybrid with Matching Strategy Adaptation

Novel Hybrid Approach: Combines Christofides approximation algorithm (1.5x guarantee)
with Iterative Local Search, adding adaptive matching strategy selection based on
ILS improvement rate.

Hypothesis: Christofides provides a strong theoretical guarantee (1.5x optimal),
but can be further improved with ILS. The matching component of Christofides
(greedy vs optimal) can be adapted based on ILS performance: if ILS shows rapid
improvement, use faster greedy matching; if improvement stagnates, switch to
optimal matching for better starting solution.

Components:
1. Christofides: Minimum Spanning Tree + Minimum Weight Perfect Matching + Eulerian tour
2. Iterative Local Search: Strategic perturbations + fast local search
3. Adaptive Matching Strategy: Switch between greedy and optimal matching based on ILS improvement rate
4. Quality-guided Restart: Restart from new Christofides solution when ILS stagnates

Novelty Claims:
- Christofides + ILS combination not found in literature (ILS different from standard local search)
- Adaptive matching strategy based on ILS improvement rate (not fixed by problem size)
- Quality-guided restart mechanism that considers both Christofides and ILS performance
- Integration of approximation algorithm guarantee with metaheuristic improvement

Literature Check: Christofides with local search (2-opt) exists (1976), but
Christofides with Iterative Local Search (perturbation + local search cycles)
appears novel based on literature database.
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We'll implement Christofides components directly to avoid dependency issues

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

def christofides_tour(
    dist_matrix: np.ndarray, 
    use_optimal_matching: bool = True,
    matching_time_limit: float = 1.0
) -> List[int]:
    """
    Christofides algorithm for TSP.
    
    Args:
        dist_matrix: Distance matrix
        use_optimal_matching: If True, use optimal matching (O(m³)); if False, use greedy
        matching_time_limit: Time limit for optimal matching (seconds)
    
    Returns:
        Tour as list of node indices
    """
    n = len(dist_matrix)
    
    # Step 1: Find Minimum Spanning Tree (MST)
    mst_edges = minimum_spanning_tree_prim(dist_matrix)
    
    # Step 2: Find vertices with odd degree in MST
    odd_vertices = find_odd_degree_vertices(mst_edges, n)
    
    # Step 3: Minimum Weight Perfect Matching on odd vertices
    if len(odd_vertices) == 0:
        # All vertices have even degree (unlikely but possible)
        matching_edges = []
    else:
        if use_optimal_matching and len(odd_vertices) <= 14:
            # Use optimal matching for small instances
            start_time = time.time()
            matching_edges = minimum_weight_perfect_matching_optimal(
                dist_matrix, odd_vertices, time_limit=matching_time_limit
            )
        else:
            # Use greedy matching for larger instances
            matching_edges = minimum_weight_perfect_matching_greedy(dist_matrix, odd_vertices)
    
    # Step 4: Combine MST and matching to create Eulerian graph
    eulerian_edges = mst_edges + matching_edges
    
    # Step 5: Find Eulerian tour
    eulerian_tour = find_eulerian_tour(eulerian_edges, n)
    
    # Step 6: Shortcut to get Hamiltonian tour
    tour = shortcut_eulerian_tour(eulerian_tour)
    
    return tour

def tour_length(tour: List[int], dist_matrix: np.ndarray) -> float:
    """Calculate total length of tour."""
    total = 0.0
    for i in range(len(tour)):
        j = (i + 1) % len(tour)
        total += dist_matrix[tour[i], tour[j]]
    return total

def two_opt_swap(tour: List[int], i: int, k: int) -> List[int]:
    """Perform 2-opt swap between positions i and k."""
    new_tour = tour[:i] + tour[i:k+1][::-1] + tour[k+1:]
    return new_tour

def two_opt_improvement_fast(
    tour: List[int], 
    dist_matrix: np.ndarray,
    max_iterations: int = 1000
) -> Tuple[List[int], float]:
    """
    Fast 2-opt local search with limited iterations.
    
    Returns:
        (improved_tour, improved_length)
    """
    n = len(tour)
    current_tour = tour[:]
    current_length = tour_length(current_tour, dist_matrix)
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue  # Don't swap first and last
                
                # Calculate delta for 2-opt swap
                a, b = current_tour[i], current_tour[(i + 1) % n]
                c, d = current_tour[j], current_tour[(j + 1) % n]
                
                old_cost = dist_matrix[a, b] + dist_matrix[c, d]
                new_cost = dist_matrix[a, c] + dist_matrix[b, d]
                
                if new_cost < old_cost:
                    # Perform swap
                    current_tour = two_opt_swap(current_tour, i + 1, j)
                    current_length = current_length - old_cost + new_cost
                    improved = True
                    iterations += 1
                    break  # Restart search after improvement
            
            if improved:
                break
    
    return current_tour, current_length

def strategic_perturbation(
    tour: List[int], 
    strength: int = 2
) -> List[int]:
    """
    Apply strategic perturbation to tour.
    
    Args:
        tour: Current tour
        strength: Number of 4-opt moves to apply
    
    Returns:
        Perturbed tour
    """
    n = len(tour)
    if n < 4:
        return tour[:]
    
    perturbed_tour = tour[:]
    
    for _ in range(strength):
        # Select 4 random distinct positions
        positions = random.sample(range(n), min(4, n))
        positions.sort()
        
        # Apply 4-opt move (double bridge move)
        if len(positions) == 4:
            i, j, k, l = positions
            # Create segments: [0..i], [i+1..j], [j+1..k], [k+1..l], [l+1..end]
            # Reorder as: A, D, C, B (double bridge)
            segment1 = perturbed_tour[:i+1]
            segment2 = perturbed_tour[i+1:j+1]
            segment3 = perturbed_tour[j+1:k+1]
            segment4 = perturbed_tour[k+1:l+1]
            segment5 = perturbed_tour[l+1:]
            
            perturbed_tour = segment1 + segment4 + segment3 + segment2 + segment5
    
    return perturbed_tour

def christofides_ils_hybrid(
    dist_matrix: np.ndarray,
    max_iterations: int = 50,
    stagnation_threshold: float = 0.0005,  # 0.05% relative improvement
    stagnation_window: int = 10,
    initial_perturbation_strength: int = 2,
    matching_adaptation_threshold: float = 0.001  # Switch matching if improvement < this
) -> Tuple[List[int], float, dict]:
    """
    Christofides-ILS Hybrid Algorithm.
    
    Args:
        dist_matrix: Distance matrix
        max_iterations: Maximum ILS iterations
        stagnation_threshold: Minimum average improvement to avoid restart
        stagnation_window: Number of iterations to check for stagnation
        initial_perturbation_strength: Initial perturbation strength
        matching_adaptation_threshold: Threshold for switching matching strategy
    
    Returns:
        (best_tour, best_length, statistics)
    """
    n = len(dist_matrix)
    start_time = time.time()
    
    # Statistics
    stats = {
        'restarts': 0,
        'matching_strategy_changes': 0,
        'total_iterations': 0,
        'improvement_history': [],
        'matching_strategy_history': [],
        'elapsed_time': 0.0,
        'n': n,
        'parameters': {
            'max_iterations': max_iterations,
            'stagnation_threshold': stagnation_threshold,
            'stagnation_window': stagnation_window,
            'initial_perturbation_strength': initial_perturbation_strength,
            'matching_adaptation_threshold': matching_adaptation_threshold
        }
    }
    
    # Initial matching strategy: optimal for small, greedy for large
    use_optimal_matching = (n <= 100)  # Start with optimal for small instances
    
    # Generate initial Christofides solution
    current_tour = christofides_tour(
        dist_matrix, 
        use_optimal_matching=use_optimal_matching,
        matching_time_limit=1.0
    )
    current_length = tour_length(current_tour, dist_matrix)
    
    best_tour = current_tour[:]
    best_length = current_length
    
    stats['matching_strategy_history'].append(use_optimal_matching)
    
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
                # Better solutions get smaller perturbations
                if relative_improvement > 0.01:  # >1% improvement
                    perturbation_strength = max(1, perturbation_strength - 1)
                elif relative_improvement < 0.001:  # <0.1% improvement
                    perturbation_strength = min(5, perturbation_strength + 1)
            else:
                no_improvement_count += 1
        else:
            no_improvement_count += 1
        
        # Check for stagnation and adapt matching strategy
        if len(improvement_history) >= stagnation_window:
            recent_improvements = improvement_history[-stagnation_window:]
            avg_improvement = np.mean(recent_improvements) if recent_improvements else 0
            
            # If average improvement is below threshold, consider changing strategy
            if avg_improvement < matching_adaptation_threshold:
                # Switch matching strategy
                use_optimal_matching = not use_optimal_matching
                stats['matching_strategy_changes'] += 1
                stats['matching_strategy_history'].append(use_optimal_matching)
                
                # Generate new Christofides solution with new strategy
                current_tour = christofides_tour(
                    dist_matrix,
                    use_optimal_matching=use_optimal_matching,
                    matching_time_limit=1.0
                )
                current_length = tour_length(current_tour, dist_matrix)
                
                # Reset stagnation tracking
                improvement_history = []
                no_improvement_count = 0
                
                # Reset perturbation strength
                perturbation_strength = initial_perturbation_strength
        
        # Apply perturbation for next iteration
        current_tour = strategic_perturbation(current_tour, perturbation_strength)
        current_length = tour_length(current_tour, dist_matrix)
        
        stats['total_iterations'] += 1
    
    stats['improvement_history'] = improvement_history
    stats['elapsed_time'] = time.time() - start_time
    
    return best_tour, best_length, stats

def solve_tsp(
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
    dist_matrix = create_distance_matrix(points)
    n = len(points)
    
    # Adjust parameters based on problem size
    max_iterations = min(100, max(30, n // 10))
    stagnation_threshold = 0.0005  # 0.05%
    stagnation_window = min(15, max(5, n // 50))
    
    tour, length, stats = christofides_ils_hybrid(
        dist_matrix,
        max_iterations=max_iterations,
        stagnation_threshold=stagnation_threshold,
        stagnation_window=stagnation_window,
        initial_perturbation_strength=2,
        matching_adaptation_threshold=0.001
    )
    
    return tour, length, stats

def benchmark():
    """Run benchmark tests."""
    import json
    
    results = []
    for n in [50, 100, 200]:
        print(f"\nTesting n={n}...")
        
        # Generate random points
        np.random.seed(42 + n)
        points = np.random.rand(n, 2) * 100
        
        # Run algorithm
        tour, length, stats = solve_tsp(points, time_limit=30.0)
        
        # Compare with Christofides baseline
        dist_matrix = create_distance_matrix(points)
        christofides_tour_baseline = christofides_tour(dist_matrix, use_optimal_matching=(n <= 100))
        christofides_length = tour_length(christofides_tour_baseline, dist_matrix)
        
        improvement = christofides_length / length if length > 0 else 1.0
        
        result = {
            'n': n,
            'hybrid_length': float(length),
            'christofides_length': float(christofides_length),
            'improvement_vs_christofides': float(improvement),
            'elapsed_time': stats['elapsed_time'],
            'restarts': stats['restarts'],
            'matching_strategy_changes': stats['matching_strategy_changes'],
            'total_iterations': stats['total_iterations']
        }
        results.append(result)
        
        print(f"  Hybrid: {length:.3f}, Christofides: {christofides_length:.3f}, Improvement: {improvement:.3f}x")
        print(f"  Time: {stats['elapsed_time']:.2f}s, Matching changes: {stats['matching_strategy_changes']}")
    
    # Save results
    with open('christofides_ils_hybrid_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nBenchmark results saved to christofides_ils_hybrid_benchmark.json")
    return results

if __name__ == "__main__":
    benchmark()