#!/usr/bin/env python3
"""
Simple test for Fast ILS algorithm
"""

import numpy as np
import time
import sys
sys.path.append('/workspace/evovera/solutions')

from tsp_v12_nn_fast_ils import solve_tsp_nn_fast_ils

def generate_random_points(n: int, seed: int = 42) -> np.ndarray:
    """Generate random 2D points"""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def compute_tour_length(tour: list, points: np.ndarray) -> float:
    """Compute tour length"""
    n = len(tour)
    total = 0.0
    for i in range(n):
        j = (i + 1) % n
        total += np.sqrt(np.sum((points[tour[i]] - points[tour[j]]) ** 2))
    return total

def main():
    print("Testing Fast ILS Algorithm")
    print("=" * 60)
    
    # Test on n=50 (where we saw 16.01% improvement)
    n = 50
    points = generate_random_points(n)
    
    # Simple NN baseline (greedy)
    print("\n1. NN Baseline (greedy):")
    start_time = time.time()
    nn_tour = []
    unvisited = set(range(n))
    current = 0
    nn_tour.append(current)
    unvisited.remove(current)
    
    while unvisited:
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: np.sqrt(np.sum((points[current] - points[city]) ** 2)))
        nn_tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    nn_length = compute_tour_length(nn_tour, points)
    nn_time = time.time() - start_time
    print(f"   Tour length: {nn_length:.4f}")
    print(f"   Time: {nn_time:.3f}s")
    
    # Fast ILS
    print("\n2. NN + Fast ILS:")
    start_time = time.time()
    fast_ils_tour, fast_ils_length, stats = solve_tsp_nn_fast_ils(points, max_iterations=100)
    fast_ils_time = time.time() - start_time
    
    print(f"   Tour length: {fast_ils_length:.4f}")
    print(f"   Initial length: {stats.get('initial_length', fast_ils_length):.4f}")
    print(f"   Improvement: {stats.get('overall_improvement', 0.0)*100:.2f}%")
    print(f"   Time: {fast_ils_time:.3f}s")
    
    # Calculate improvement
    improvement = (nn_length - fast_ils_length) / nn_length * 100
    print(f"\n   Improvement over NN: {improvement:.2f}%")
    
    if improvement >= 0.1:
        print(f"   ✅ SUCCESS: Meets 0.1% improvement threshold!")
    else:
        print(f"   ⚠️  Needs improvement: Below 0.1% threshold")

if __name__ == "__main__":
    main()