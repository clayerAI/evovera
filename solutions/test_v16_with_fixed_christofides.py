#!/usr/bin/env python3
"""
Test v16 against FIXED Christofides baseline.
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
    print("Testing v16 against FIXED Christofides baseline")
    print("=" * 60)
    
    n_values = [20, 30, 50, 100]
    seeds = [42, 43, 44, 45, 46]
    
    results = {}
    
    for n in n_values:
        print(f"\n=== Testing n={n} ===")
        n_results = []
        
        for seed in seeds:
            points = generate_random_points(n=n, seed=seed)
            points_array = np.array(points)
            
            # Test Christofides
            christofides_len, christofides_time = test_algorithm(points_array, "Christofides", christofides_solve)
            
            # Test v16
            v16_len, v16_time = test_algorithm(points_array, "v16", v16_solve)
            
            # Calculate improvement
            improvement = (christofides_len - v16_len) / christofides_len * 100
            
            n_results.append({
                'seed': seed,
                'christofides': christofides_len,
                'v16': v16_len,
                'improvement': improvement,
                'christofides_time': christofides_time,
                'v16_time': v16_time
            })
            
            print(f"Seed {seed}: Christofides={christofides_len:.4f}, v16={v16_len:.4f}, "
                  f"Improvement={improvement:.2f}%")
        
        # Calculate averages
        avg_christofides = sum(r['christofides'] for r in n_results) / len(n_results)
        avg_v16 = sum(r['v16'] for r in n_results) / len(n_results)
        avg_improvement = sum(r['improvement'] for r in n_results) / len(n_results)
        
        results[n] = {
            'avg_christofides': avg_christofides,
            'avg_v16': avg_v16,
            'avg_improvement': avg_improvement,
            'details': n_results
        }
        
        print(f"\nAverage for n={n}:")
        print(f"  Christofides: {avg_christofides:.4f}")
        print(f"  v16: {avg_v16:.4f}")
        print(f"  Improvement: {avg_improvement:.2f}%")
        
        # Check if beats 0.1% threshold
        if avg_improvement > 0.1:
            print(f"  ✅ v16 BEATS 0.1% novelty threshold!")
        else:
            print(f"  ❌ v16 does NOT beat 0.1% novelty threshold")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    for n in n_values:
        imp = results[n]['avg_improvement']
        status = "✅" if imp > 0.1 else "❌"
        print(f"n={n}: {imp:.2f}% improvement {status}")
    
    # Check if v16 is consistently better
    all_improvements = [results[n]['avg_improvement'] for n in n_values]
    positive_count = sum(1 for imp in all_improvements if imp > 0)
    
    print(f"\nPositive improvements: {positive_count}/{len(n_values)}")
    
    if positive_count >= 3:
        print("✅ v16 shows consistent improvement over Christofides")
    else:
        print("❌ v16 does not show consistent improvement")

if __name__ == "__main__":
    main()