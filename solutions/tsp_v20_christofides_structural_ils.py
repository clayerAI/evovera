#!/usr/bin/env python3
"""
Christofides Structural-ILS Hybrid (v20)
Combines v19's structural hybridization with v8's iterative local search.

Key Innovation:
1. Use v19's structural analysis (community detection + path centrality) for initial solution
2. Apply v8's iterative local search framework for refinement
3. Adaptive perturbation based on structural properties

This creates a two-phase approach:
- Phase 1: Structural Christofides (v19) for high-quality initial solution
- Phase 2: ILS refinement (v8) with perturbations informed by community structure

Author: Evo
Date: 2026-04-04
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set, Optional
import heapq
import numpy as np
import sys
import os

# Import v19 structural Christofides
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural

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
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix

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
    Fast 2-opt local search implementation.
    
    Args:
        tour: Current tour (list of vertex indices)
        dist_matrix: Distance matrix
        max_iterations: Maximum iterations to run
        
    Returns:
        (improved_tour, improved_length)
    """
    n = len(tour)
    current_tour = tour[:]
    current_length = 0.0
    
    # Calculate initial tour length
    for i in range(n):
        j = (i + 1) % n
        current_length += dist_matrix[current_tour[i]][current_tour[j]]
    
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(n - 1):
            for k in range(i + 1, n):
                # Calculate delta for 2-opt swap
                j = (i + 1) % n
                l = (k + 1) % n
                
                # Current edges: (i, j) and (k, l)
                # New edges: (i, k) and (j, l)
                old_cost = (dist_matrix[current_tour[i]][current_tour[j]] +
                           dist_matrix[current_tour[k]][current_tour[l]])
                new_cost = (dist_matrix[current_tour[i]][current_tour[k]] +
                           dist_matrix[current_tour[j]][current_tour[l]])
                
                delta = new_cost - old_cost
                
                if delta < -1e-9:  # Significant improvement
                    # Perform swap
                    current_tour[i+1:k+1] = current_tour[i+1:k+1][::-1]
                    current_length += delta
                    improved = True
                    break  # Restart search after improvement
            
            if improved:
                break
    
    return current_tour, current_length

def strategic_perturbation(
    tour: List[int],
    communities: Dict[int, int],
    perturbation_strength: int = 3
) -> List[int]:
    """
    Strategic perturbation informed by community structure.
    
    Args:
        tour: Current tour
        communities: Mapping from vertex to community ID
        perturbation_strength: Number of swaps to perform
        
    Returns:
        Perturbed tour
    """
    n = len(tour)
    perturbed_tour = tour[:]
    
    for _ in range(perturbation_strength):
        # Select two vertices from different communities if possible
        attempts = 0
        while attempts < 10:
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            
            if i == j:
                continue
                
            # Ensure i < j for swap
            if i > j:
                i, j = j, i
                
            # Prefer swaps between different communities
            if communities.get(tour[i], -1) != communities.get(tour[j], -1):
                # Perform swap
                perturbed_tour[i], perturbed_tour[j] = perturbed_tour[j], perturbed_tour[i]
                break
                
            attempts += 1
        
        # If couldn't find cross-community swap, do random swap
        if attempts >= 10:
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            if i != j:
                if i > j:
                    i, j = j, i
                perturbed_tour[i], perturbed_tour[j] = perturbed_tour[j], perturbed_tour[i]
    
    return perturbed_tour

def christofides_structural_ils_hybrid(
    points: np.ndarray,
    time_limit: float = 30.0,
    initial_perturbation_strength: int = 3,
    stagnation_threshold: int = 10,
    percentile_threshold: float = 70.0,
    within_community_weight: float = 0.8,
    between_community_weight: float = 0.3
) -> Tuple[List[int], float, dict]:
    """
    Christofides Structural-ILS hybrid algorithm.
    
    Args:
        points: Array of (x, y) coordinates
        time_limit: Maximum time in seconds
        initial_perturbation_strength: Initial perturbation size
        stagnation_threshold: Number of iterations without improvement before perturbation
        percentile_threshold: Percentile for community detection (0-100)
        within_community_weight: Centrality weight for within-community edges (0-1)
        between_community_weight: Centrality weight for between-community edges (0-1)
        
    Returns:
        (best_tour, best_length, statistics)
    """
    dist_matrix = create_distance_matrix(points)
    n = len(points)
    
    # Convert points to list of tuples for v19 solver
    points_list = [(float(p[0]), float(p[1])) for p in points]
    
    # Phase 1: Use v19 structural Christofides for initial solution
    print(f"Phase 1: Generating initial solution with structural Christofides...")
    v19_solver = ChristofidesHybridStructural(points_list, seed=42)
    
    # Get initial solution AND community structure
    initial_tour, initial_length, runtime = v19_solver.solve(
        percentile_threshold=percentile_threshold,
        within_community_weight=within_community_weight,
        between_community_weight=between_community_weight,
        apply_2opt=True
    )
    
    # Extract community information for strategic perturbations
    # We need to run community detection separately to get the mapping
    mst_adj, parent = v19_solver._compute_mst()
    community_labels = v19_solver._detect_communities(mst_adj, percentile_threshold)
    
    # Create vertex-to-community mapping
    vertex_community = {}
    for v in range(n):
        vertex_community[v] = community_labels[v]
    
    # Count unique communities
    unique_communities = len(set(community_labels))
    
    print(f"Initial solution length: {initial_length:.4f}")
    print(f"Detected {unique_communities} communities")
    
    # Phase 2: ILS refinement
    current_tour = initial_tour[:]
    current_length = initial_length
    best_tour = current_tour[:]
    best_length = current_length
    
    perturbation_strength = initial_perturbation_strength
    no_improvement_count = 0
    iteration = 0
    start_time = time.time()
    
    stats = {
        'initial_length': initial_length,
        'iterations': 0,
        'improvements': 0,
        'perturbations': 0,
        'best_length_history': [],
        'communities_detected': unique_communities
    }
    
    print(f"Phase 2: Starting ILS refinement with time limit {time_limit}s...")
    
    while time.time() - start_time < time_limit and no_improvement_count < stagnation_threshold:
        # Local search improvement
        improved_tour, improved_length = two_opt_improvement_fast(
            current_tour, dist_matrix, max_iterations=500
        )
        
        # Check for improvement
        if improved_length < current_length - 1e-9:
            current_tour = improved_tour
            current_length = improved_length
            no_improvement_count = 0
            stats['improvements'] += 1
            
            # Update best solution
            if current_length < best_length - 1e-9:
                best_tour = current_tour[:]
                best_length = current_length
                print(f"Iteration {iteration}: New best length = {best_length:.4f}")
        else:
            no_improvement_count += 1
        
        # Apply strategic perturbation if stagnating
        if no_improvement_count >= stagnation_threshold:
            current_tour = strategic_perturbation(
                current_tour, vertex_community, perturbation_strength
            )
            
            # Recalculate tour length
            current_length = 0.0
            for i in range(n):
                j = (i + 1) % n
                current_length += dist_matrix[current_tour[i]][current_tour[j]]
            
            no_improvement_count = 0
            perturbation_strength = min(perturbation_strength + 1, n // 10)
            stats['perturbations'] += 1
            
            print(f"Applied strategic perturbation (strength={perturbation_strength})")
        
        stats['iterations'] += 1
        stats['best_length_history'].append(best_length)
        iteration += 1
    
    total_time = time.time() - start_time
    stats['total_time'] = total_time
    stats['final_length'] = best_length
    stats['improvement_from_initial'] = (initial_length - best_length) / initial_length * 100
    
    print(f"ILS completed: {stats['iterations']} iterations, {stats['improvements']} improvements")
    print(f"Final length: {best_length:.4f} (improvement: {stats['improvement_from_initial']:.2f}%)")
    
    return best_tour, best_length, stats

def solve_tsp(
    points: np.ndarray,
    time_limit: float = 30.0
) -> Tuple[List[int], float]:
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        time_limit: Maximum time in seconds
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    tour, length, _ = christofides_structural_ils_hybrid(
        points, 
        time_limit=time_limit,
        percentile_threshold=70.0,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length

def benchmark_structural_ils_hybrid(
    n: int = 100,
    num_instances: int = 5,
    time_limit: float = 30.0
) -> dict:
    """
    Benchmark Christofides Structural-ILS hybrid algorithm.
    
    Args:
        n: Number of nodes
        num_instances: Number of random instances to test
        time_limit: Time limit per instance
        
    Returns:
        Dictionary with benchmark results
    """
    results = []
    total_time = 0.0
    
    for i in range(num_instances):
        np.random.seed(i)
        points = np.random.rand(n, 2)
        
        print(f"\n{'='*60}")
        print(f"Instance {i+1}/{num_instances} (n={n}, seed={i}):")
        print(f"{'='*60}")
        
        start_time = time.time()
        tour, length, stats = christofides_structural_ils_hybrid(
            points, 
            time_limit=time_limit,
            percentile_threshold=70.0,
            within_community_weight=0.8,
            between_community_weight=0.3
        )
        instance_time = time.time() - start_time
        total_time += instance_time
        
        results.append({
            'instance': i,
            'seed': i,
            'tour_length': length,
            'time': instance_time,
            'initial_length': stats['initial_length'],
            'improvement_percentage': stats['improvement_from_initial'],
            'iterations': stats['iterations'],
            'improvements': stats['improvements'],
            'perturbations': stats['perturbations'],
            'communities_detected': stats['communities_detected']
        })
        
        print(f"Instance {i+1} complete: length={length:.4f}, time={instance_time:.2f}s")
        print(f"Improvement from initial: {stats['improvement_from_initial']:.2f}%")
    
    # Calculate statistics
    tour_lengths = [r['tour_length'] for r in results]
    times = [r['time'] for r in results]
    improvements = [r['improvement_percentage'] for r in results]
    
    benchmark_results = {
        'algorithm': 'christofides_structural_ils_hybrid',
        'n': n,
        'num_instances': num_instances,
        'average_tour_length': np.mean(tour_lengths),
        'std_tour_length': np.std(tour_lengths),
        'average_time': np.mean(times),
        'std_time': np.std(times),
        'average_improvement': np.mean(improvements),
        'std_improvement': np.std(improvements),
        'results': results
    }
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK SUMMARY (n={n}, {num_instances} instances):")
    print(f"{'='*60}")
    print(f"Average tour length: {benchmark_results['average_tour_length']:.4f}")
    print(f"Average time: {benchmark_results['average_time']:.2f}s")
    print(f"Average improvement from initial: {benchmark_results['average_improvement']:.2f}%")
    print(f"Total benchmark time: {total_time:.2f}s")
    
    return benchmark_results

if __name__ == "__main__":
    # Quick test with small instance
    print("Testing Christofides Structural-ILS Hybrid (v20)...")
    
    # Generate test points
    n = 50
    np.random.seed(42)
    points = np.random.rand(n, 2)
    
    # Run hybrid algorithm
    tour, length, stats = christofides_structural_ils_hybrid(
        points, 
        time_limit=10.0,
        percentile_threshold=70.0,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    
    print(f"\nTest completed:")
    print(f"Tour length: {length:.4f}")
    print(f"Initial length: {stats['initial_length']:.4f}")
    print(f"Improvement: {stats['improvement_from_initial']:.2f}%")
    print(f"Iterations: {stats['iterations']}")
    print(f"Improvements: {stats['improvements']}")
    print(f"Perturbations: {stats['perturbations']}")
    print(f"Communities detected: {stats['communities_detected']}")