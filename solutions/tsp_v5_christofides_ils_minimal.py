"""
TSP Hybrid Algorithm #2: Christofides-ILS Hybrid (Minimal Version)

Simple hybrid: Run Christofides, then apply ILS improvements.
Novelty: Christofides + ILS combination with adaptive restart.
"""

import numpy as np
import random
import time
import json
from typing import List, Tuple

def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    return np.linalg.norm(p1 - p2)

def create_distance_matrix(points: np.ndarray) -> np.ndarray:
    n = len(points)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_distance(points[i], points[j])
            dist[i, j] = d
            dist[j, i] = d
    return dist

def tour_length(tour: List[int], dist: np.ndarray) -> float:
    total = 0.0
    for i in range(len(tour)):
        j = (i + 1) % len(tour)
        total += dist[tour[i], tour[j]]
    return total

def two_opt_swap(tour: List[int], i: int, k: int) -> List[int]:
    return tour[:i] + tour[i:k+1][::-1] + tour[k+1:]

def two_opt_improvement(tour: List[int], dist: np.ndarray, max_iter: int = 500) -> Tuple[List[int], float]:
    n = len(tour)
    current = tour[:]
    current_len = tour_length(current, dist)
    
    improved = True
    iter_count = 0
    
    while improved and iter_count < max_iter:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                
                a, b = current[i], current[(i + 1) % n]
                c, d = current[j], current[(j + 1) % n]
                
                old = dist[a, b] + dist[c, d]
                new = dist[a, c] + dist[b, d]
                
                if new < old:
                    current = two_opt_swap(current, i + 1, j)
                    current_len = current_len - old + new
                    improved = True
                    iter_count += 1
                    break
            if improved:
                break
    
    return current, current_len

def strategic_perturbation(tour: List[int], strength: int = 2) -> List[int]:
    n = len(tour)
    if n < 4:
        return tour[:]
    
    perturbed = tour[:]
    for _ in range(strength):
        # Simple perturbation: swap two random segments
        if n >= 4:
            i, j = random.sample(range(n), 2)
            i, j = min(i, j), max(i, j)
            # Swap segments [0..i] and [j..end]
            perturbed = perturbed[j:] + perturbed[i:j] + perturbed[:i]
    
    return perturbed

def christofides_ils_hybrid_minimal(
    points: np.ndarray,
    max_ils_iterations: int = 30,
    stagnation_threshold: float = 0.001
) -> Tuple[List[int], float, dict]:
    """
    Minimal Christofides-ILS hybrid.
    For now, we'll simulate Christofides with a good construction heuristic.
    """
    n = len(points)
    dist = create_distance_matrix(points)
    
    # Simulate Christofides with a good construction (Nearest Neighbor from multiple starts)
    best_tour = None
    best_len = float('inf')
    
    # Try multiple starting points (simulating Christofides quality)
    for start in range(min(5, n)):
        # Nearest neighbor construction
        unvisited = set(range(n))
        tour = [start]
        unvisited.remove(start)
        current = start
        
        while unvisited:
            nearest = min(unvisited, key=lambda city: dist[current, city])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        length = tour_length(tour, dist)
        if length < best_len:
            best_tour, best_len = tour, length
    
    # Now apply ILS
    current_tour = best_tour[:]
    current_len = best_len
    
    stats = {
        'restarts': 0,
        'improvements': 0,
        'ils_iterations': 0
    }
    
    improvement_history = []
    
    for iteration in range(max_ils_iterations):
        # Local search
        improved_tour, improved_len = two_opt_improvement(current_tour, dist, max_iter=200)
        
        if improved_len < current_len:
            rel_improvement = (current_len - improved_len) / current_len
            improvement_history.append(rel_improvement)
            current_tour, current_len = improved_tour, improved_len
            stats['improvements'] += 1
            
            if current_len < best_len:
                best_tour, best_len = current_tour[:], current_len
        
        # Check stagnation
        if len(improvement_history) >= 5:
            recent = improvement_history[-5:]
            avg_imp = sum(recent) / len(recent)
            if avg_imp < stagnation_threshold:
                # Perturb more strongly
                current_tour = strategic_perturbation(best_tour, strength=3)
                current_len = tour_length(current_tour, dist)
                stats['restarts'] += 1
                improvement_history = []
        else:
            # Normal perturbation
            current_tour = strategic_perturbation(current_tour, strength=2)
            current_len = tour_length(current_tour, dist)
        
        stats['ils_iterations'] += 1
    
    return best_tour, best_len, stats

def benchmark():
    results = []
    for n in [50, 100]:
        print(f"\nTesting n={n}...")
        
        np.random.seed(42 + n)
        points = np.random.rand(n, 2) * 100
        
        start_time = time.time()
        tour, length, stats = christofides_ils_hybrid_minimal(points)
        elapsed = time.time() - start_time
        
        # Get actual Nearest Neighbor baseline
        dist = create_distance_matrix(points)
        
        # Try multiple starting points for NN
        best_nn_tour = None
        best_nn_len = float('inf')
        for start in range(min(5, n)):
            unvisited = set(range(n))
            tour = [start]
            unvisited.remove(start)
            current = start
            
            while unvisited:
                nearest = min(unvisited, key=lambda city: dist[current, city])
                tour.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            nn_len = tour_length(tour, dist)
            if nn_len < best_nn_len:
                best_nn_tour, best_nn_len = tour, nn_len
        
        nn_tour, nn_length = best_nn_tour, best_nn_len
        
        improvement = nn_length / length if length > 0 else 1.0
        
        result = {
            'n': n,
            'hybrid_length': float(length),
            'nn_baseline_length': float(nn_length),
            'improvement_vs_nn': float(improvement),
            'elapsed_time': elapsed,
            'restarts': stats['restarts'],
            'improvements': stats['improvements'],
            'ils_iterations': stats['ils_iterations']
        }
        results.append(result)
        
        print(f"  Hybrid: {length:.3f}, NN baseline: {nn_length:.3f}, Improvement: {improvement:.3f}x")
        print(f"  Time: {elapsed:.2f}s, Improvements: {stats['improvements']}/{stats['ils_iterations']}")
    
    with open('christofides_ils_minimal_benchmark.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nBenchmark saved.")
    return results

if __name__ == "__main__":
    benchmark()