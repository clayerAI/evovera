#!/usr/bin/env python3
"""Quick test of optimized v19 benchmark at n=100 to verify everything works."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
import time
from typing import List, Tuple

from solutions.tsp_v19_christofides_hybrid_structural_optimized import ChristofidesHybridStructuralOptimized

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def compute_nn_2opt_tour(points: List[Tuple[float, float]]) -> Tuple[List[int], float]:
    """Compute Nearest Neighbor + 2-opt baseline tour."""
    n = len(points)
    
    # Compute distance matrix
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
            dist[i][j] = d
            dist[j][i] = d
    
    # Nearest Neighbor
    start = random.randint(0, n-1)
    tour = [start]
    unvisited = set(range(n))
    unvisited.remove(start)
    
    current = start
    while unvisited:
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist[current][city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Compute tour length
    def tour_length(tour):
        length = 0.0
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            length += dist[tour[i]][tour[j]]
        return length
    
    # 2-opt improvement
    best_tour = tour[:]
    best_length = tour_length(tour)
    improved = True
    
    while improved:
        improved = False
        for i in range(len(best_tour)):
            for j in range(i + 2, len(best_tour) + (i > 0)):
                if j == len(best_tour):
                    k = 0
                else:
                    k = j
                
                # Try 2-opt swap
                new_tour = best_tour[:i+1] + best_tour[i+1:k+1][::-1] + best_tour[k+1:]
                new_length = tour_length(new_tour)
                
                if new_length < best_length:
                    best_tour = new_tour
                    best_length = new_length
                    improved = True
                    break
            if improved:
                break
    
    return best_tour, best_length

# Test at n=100 first
n = 100
seed = 42
points = generate_random_points(n, seed=seed)

print(f"Testing optimized v19 at n={n}...")

# Compute baseline
start = time.time()
nn_tour, nn_length = compute_nn_2opt_tour(points)
nn_time = time.time() - start
print(f"NN+2opt baseline: {nn_length:.2f} (took {nn_time:.2f}s)")

# Test optimized v19
try:
    start = time.time()
    solver_v19 = ChristofidesHybridStructuralOptimized(points, seed=seed)
    tour_v19, length_v19, time_v19 = solver_v19.solve(
        percentile_threshold=70,
        within_community_weight=0.8,
        between_community_weight=0.3,
        apply_2opt=True
    )
    v19_time = time.time() - start
    v19_improvement = (nn_length - length_v19) / nn_length * 100 if nn_length > 0 else 0
    
    print(f"v19 (OPTIMIZED): {length_v19:.2f} ({v19_improvement:+.2f}%) (took {v19_time:.2f}s)")
    
    # Verify correctness (compare with original v19 if available)
    try:
        from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural
        solver_original = ChristofidesHybridStructural(points, seed=seed)
        tour_orig, length_orig, time_orig = solver_original.solve(
            percentile_threshold=70,
            within_community_weight=0.8,
            between_community_weight=0.3,
            apply_2opt=True
        )
        print(f"Original v19: {length_orig:.2f} (took {time_orig:.2f}s)")
        
        if abs(length_v19 - length_orig) < 0.01:
            print(f"✓ OPTIMIZED VERSION MATCHES ORIGINAL (difference: {abs(length_v19 - length_orig):.6f})")
        else:
            print(f"✗ OPTIMIZED VERSION DIFFERS FROM ORIGINAL (difference: {abs(length_v19 - length_orig):.6f})")
    except Exception as e:
        print(f"Note: Could not compare with original v19: {e}")
        
except Exception as e:
    print(f"Error testing optimized v19: {e}")
    import traceback
    traceback.print_exc()