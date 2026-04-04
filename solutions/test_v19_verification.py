#!/usr/bin/env python3
"""
Quick verification test for v19 performance claims.
"""

import sys
sys.path.append('.')
from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_2opt
import random
import math
import time

def test_v19_performance(n=50, seed=42, num_tests=3):
    """Test v19 performance against NN+2opt baseline."""
    
    results = []
    
    for test_idx in range(num_tests):
        test_seed = seed + test_idx * 100
        random.seed(test_seed)
        
        # Generate random points
        points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
        
        # Run v19
        v19_start = time.time()
        v19 = ChristofidesHybridStructural(points, seed=test_seed)
        v19_tour, v19_length, v19_runtime = v19.solve()
        v19_time = time.time() - v19_start
        
        # Run NN+2opt
        nn_start = time.time()
        nn_tour, nn_length = nn_2opt(points)
        nn_time = time.time() - nn_start
        
        # Calculate improvement
        improvement = ((nn_length - v19_length) / nn_length) * 100
        
        results.append({
            'seed': test_seed,
            'n': n,
            'v19_length': v19_length,
            'nn_length': nn_length,
            'improvement': improvement,
            'v19_time': v19_time,
            'nn_time': nn_time,
            'exceeds_threshold': improvement > 0.1
        })
        
        print(f"Test {test_idx+1} (seed={test_seed}):")
        print(f"  NN+2opt: {nn_length:.2f} ({nn_time:.3f}s)")
        print(f"  v19:     {v19_length:.2f} ({v19_time:.3f}s)")
        print(f"  Improvement: {improvement:.2f}%")
        print(f"  Exceeds 0.1% threshold: {improvement > 0.1}")
        print()
    
    # Calculate averages
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    avg_exceeds = sum(1 for r in results if r['exceeds_threshold']) / len(results) * 100
    
    print(f"Summary (n={n}, {num_tests} tests):")
    print(f"  Average improvement: {avg_improvement:.2f}%")
    print(f"  Tests exceeding 0.1% threshold: {avg_exceeds:.1f}%")
    
    return results

if __name__ == "__main__":
    print("Testing v19 performance claims...")
    print("=" * 50)
    
    # Test n=50 as claimed in analysis
    results_50 = test_v19_performance(n=50, seed=42, num_tests=3)
    
    print("\n" + "=" * 50)
    print("Testing n=100...")
    
    # Test n=100
    results_100 = test_v19_performance(n=100, seed=42, num_tests=2)