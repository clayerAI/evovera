#!/usr/bin/env python3
"""
Test v16 with n=100 using Evo's seeds.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
import numpy as np
import random
import time

def generate_random_points(n: int = 100, seed: int = 42) -> list:
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
    print("Testing v16 with n=100 using Evo's seeds")
    print("Seeds: 42, 123, 456, 789, 999")
    print("=" * 60)
    
    n = 100
    seeds = [42, 123, 456, 789, 999]
    
    nn2opt_results = []
    v16_results = []
    
    for seed in seeds:
        print(f"\n=== Seed {seed} ===")
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Test NN+2opt
        nn2opt_len, nn2opt_time = test_algorithm(points_array, "NN+2opt", nn2opt_solve)
        nn2opt_results.append(nn2opt_len)
        print(f"NN+2opt: {nn2opt_len:.4f} (time: {nn2opt_time:.2f}s)")
        
        # Test v16
        v16_len, v16_time = test_algorithm(points_array, "v16", v16_solve)
        v16_results.append(v16_len)
        print(f"v16: {v16_len:.4f} (time: {v16_time:.2f}s)")
        
        # Calculate improvement
        improvement = ((nn2opt_len - v16_len) / nn2opt_len) * 100
        print(f"Improvement: {improvement:.2f}%")
        
        if improvement > 0.1:
            print(f"✅ v16 BEATS 0.1% novelty threshold!")
        else:
            print(f"❌ v16 does NOT beat 0.1% novelty threshold")
    
    # Calculate averages
    avg_nn2opt = np.mean(nn2opt_results)
    avg_v16 = np.mean(v16_results)
    avg_improvement = ((avg_nn2opt - avg_v16) / avg_nn2opt) * 100
    
    print("\n" + "=" * 60)
    print("SUMMARY (n=100):")
    print(f"Average NN+2opt: {avg_nn2opt:.4f}")
    print(f"Average v16: {avg_v16:.4f}")
    print(f"Average Improvement: {avg_improvement:.2f}%")
    
    # Check consistency
    positive_count = sum(1 for i in range(len(seeds)) if ((nn2opt_results[i] - v16_results[i]) / nn2opt_results[i]) * 100 > 0.1)
    print(f"\nSeeds beating 0.1% threshold: {positive_count}/{len(seeds)}")
    
    if avg_improvement > 0.1:
        print("✅ v16 CONSISTENTLY BEATS 0.1% novelty threshold!")
    else:
        print("❌ v16 does NOT consistently beat 0.1% novelty threshold")

if __name__ == "__main__":
    main()