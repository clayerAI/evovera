#!/usr/bin/env python3
"""
Reproduce Evo's v16 test with n=50 against Standard Christofides.
Using Evo's exact seeds: 42, 123, 456, 789, 999
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v2_christofides import solve_tsp as christofides_solve
from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
import numpy as np
import random
import time

def generate_random_points(n: int = 50, seed: int = 42) -> list:
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
    print("Reproducing Evo's v16 test: n=50 vs Standard Christofides")
    print("Using Evo's exact seeds: 42, 123, 456, 789, 999")
    print("=" * 70)
    
    n = 50
    seeds = [42, 123, 456, 789, 999]
    
    results = []
    
    for seed in seeds:
        print(f"\n=== Seed {seed} ===")
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Test Standard Christofides
        christofides_len, christofides_time = test_algorithm(points_array, "Christofides", christofides_solve)
        
        # Test v16
        v16_len, v16_time = test_algorithm(points_array, "v16", v16_solve)
        
        # Calculate improvement
        improvement = ((christofides_len - v16_len) / christofides_len) * 100
        
        results.append({
            'seed': seed,
            'christofides': christofides_len,
            'v16': v16_len,
            'improvement': improvement,
            'christofides_time': christofides_time,
            'v16_time': v16_time
        })
        
        print(f"Christofides: {christofides_len:.4f} (time: {christofides_time:.2f}s)")
        print(f"v16: {v16_len:.4f} (time: {v16_time:.2f}s)")
        print(f"Improvement: {improvement:.2f}%")
        
        if improvement > 0:
            print(f"✅ v16 BEATS Christofides")
        else:
            print(f"❌ v16 does NOT beat Christofides")
    
    # Calculate averages
    avg_christofides = sum(r['christofides'] for r in results) / len(results)
    avg_v16 = sum(r['v16'] for r in results) / len(results)
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    
    print("\n" + "=" * 70)
    print("SUMMARY (n=50 vs Standard Christofides):")
    print(f"Average Christofides: {avg_christofides:.4f}")
    print(f"Average v16: {avg_v16:.4f}")
    print(f"Average Improvement: {avg_improvement:.2f}%")
    
    # Check consistency
    positive_count = sum(1 for r in results if r['improvement'] > 0)
    print(f"\nPositive improvements: {positive_count}/{len(seeds)}")
    
    if positive_count == len(seeds):
        print("✅ v16 CONSISTENTLY BEATS Standard Christofides (n=50)")
    else:
        print(f"❌ v16 does NOT consistently beat Standard Christofides")
    
    # Also test against NN+2opt for comparison
    print("\n" + "=" * 70)
    print("ADDITIONAL TEST: v16 vs NN+2opt (n=50)")
    print("=" * 70)
    
    from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
    
    nn2opt_results = []
    
    for seed in seeds:
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Test NN+2opt
        nn2opt_len, nn2opt_time = test_algorithm(points_array, "NN+2opt", nn2opt_solve)
        
        # Test v16 (already computed)
        v16_len = next(r['v16'] for r in results if r['seed'] == seed)
        
        # Calculate improvement vs NN+2opt
        improvement_vs_nn2opt = ((nn2opt_len - v16_len) / nn2opt_len) * 100
        
        nn2opt_results.append({
            'seed': seed,
            'nn2opt': nn2opt_len,
            'v16': v16_len,
            'improvement': improvement_vs_nn2opt
        })
        
        print(f"Seed {seed}: NN+2opt={nn2opt_len:.4f}, v16={v16_len:.4f}, Improvement={improvement_vs_nn2opt:.2f}%")
    
    # Calculate averages vs NN+2opt
    avg_nn2opt = sum(r['nn2opt'] for r in nn2opt_results) / len(nn2opt_results)
    avg_v16_vs_nn2opt = sum(r['v16'] for r in nn2opt_results) / len(nn2opt_results)
    avg_improvement_vs_nn2opt = sum(r['improvement'] for r in nn2opt_results) / len(nn2opt_results)
    
    print(f"\nAverage NN+2opt: {avg_nn2opt:.4f}")
    print(f"Average v16: {avg_v16_vs_nn2opt:.4f}")
    print(f"Average Improvement vs NN+2opt: {avg_improvement_vs_nn2opt:.2f}%")
    
    # Check 0.1% novelty threshold
    if avg_improvement_vs_nn2opt > 0.1:
        print(f"✅ v16 BEATS 0.1% novelty threshold vs NN+2opt (n=50)")
    else:
        print(f"❌ v16 does NOT beat 0.1% novelty threshold vs NN+2opt (n=50)")

if __name__ == "__main__":
    main()