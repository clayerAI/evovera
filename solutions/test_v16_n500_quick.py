#!/usr/bin/env python3
"""
Quick test v16 with n=500 (standard benchmark size).
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
import numpy as np
import random
import time

def generate_random_points(n: int = 500, seed: int = 42) -> list:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_algorithm(points, algorithm_name, solve_func):
    """Test a single algorithm."""
    points_array = np.array(points)
    
    start_time = time.time()
    tour, length = solve_func(points_array)
    runtime = time.time() - start_time
    
    return length, runtime

def main():
    print("Quick test v16 with n=500 (standard benchmark size)")
    print("Using seed 42 only (n=500 is computationally expensive)")
    print("=" * 60)
    
    n = 500
    seed = 42
    
    points = generate_random_points(n=n, seed=seed)
    points_array = np.array(points)
    
    # Test NN+2opt
    print("Testing NN+2opt...")
    nn2opt_len, nn2opt_time = test_algorithm(points_array, "NN+2opt", nn2opt_solve)
    print(f"NN+2opt: {nn2opt_len:.4f} (time: {nn2opt_time:.2f}s)")
    
    # Test v16
    print("Testing v16...")
    v16_len, v16_time = test_algorithm(points_array, "v16", v16_solve)
    print(f"v16: {v16_len:.4f} (time: {v16_time:.2f}s)")
    
    # Calculate improvement
    improvement = ((nn2opt_len - v16_len) / nn2opt_len) * 100
    print(f"\nImprovement: {improvement:.2f}%")
    
    if improvement > 0.1:
        print(f"✅ v16 BEATS 0.1% novelty threshold at n=500!")
    else:
        print(f"❌ v16 does NOT beat 0.1% novelty threshold at n=500")
    
    # Compare to benchmark standard (17.69)
    print(f"\nBenchmark standard (NN+2opt n=500): 17.69")
    print(f"This test result (NN+2opt n=500): {nn2opt_len:.4f}")
    print(f"Note: Random seed affects absolute values, improvement % is what matters")

if __name__ == "__main__":
    main()