#!/usr/bin/env python3
"""
Test v18 performance to understand computational requirements for n=500.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

try:
    from tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
    v18_available = True
except ImportError:
    v18_available = False
    print("v18 algorithm not found in solutions directory")

from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time

def test_v18_performance(n=100, seed=42):
    """Test v18 performance on given n."""
    if not v18_available:
        print("v18 not available for testing")
        return None
    
    random.seed(seed)
    points = [(random.random(), random.random()) for _ in range(n)]
    
    print(f"Testing v18 on n={n}, seed={seed}")
    
    # Test baseline
    start = time.time()
    baseline_tour, baseline_length = nn2opt_solve(points)
    baseline_time = time.time() - start
    
    # Test v18
    start = time.time()
    solver = ChristofidesCommunityDetection(points, seed=seed)
    v18_tour, v18_length, _ = solver.solve()
    v18_time = time.time() - start
    
    improvement = ((baseline_length - v18_length) / baseline_length) * 100
    
    print(f"  Baseline: {baseline_length:.4f} ({baseline_time:.1f}s)")
    print(f"  v18:      {v18_length:.4f} ({v18_time:.1f}s)")
    print(f"  Improvement: {improvement:.2f}%")
    print(f"  Estimated n=500 time: {v18_time * (500/n)**2:.1f}s (quadratic scaling)")
    
    return {
        "n": n,
        "baseline_time": baseline_time,
        "v18_time": v18_time,
        "improvement": improvement
    }

if __name__ == "__main__":
    if v18_available:
        # Test on n=100 first
        result_100 = test_v18_performance(n=100, seed=42)
        
        if result_100 and result_100["v18_time"] < 10:  # If n=100 takes less than 10s
            print("\n" + "="*40)
            result_200 = test_v18_performance(n=200, seed=42)
            
            if result_200 and result_200["v18_time"] < 60:  # If n=200 takes less than 60s
                print("\n" + "="*40)
                print("Performance scaling analysis:")
                print(f"  n=100: {result_100['v18_time']:.1f}s, improvement: {result_100['improvement']:.2f}%")
                print(f"  n=200: {result_200['v18_time']:.1f}s, improvement: {result_200['improvement']:.2f}%")
                print(f"  Scaling factor: {result_200['v18_time']/result_100['v18_time']:.1f}x for 2x n")
                print(f"  Estimated n=500 (quadratic): {result_100['v18_time'] * (500/100)**2:.1f}s")
                print(f"  Estimated n=500 (n^2.5): {result_100['v18_time'] * (500/100)**2.5:.1f}s")
    else:
        print("\nChecking for alternative v18 implementations...")
        # Look for v18 files
        import glob
        v18_files = glob.glob("/workspace/evovera/*v18*")
        print(f"Found v18 related files: {[f.split('/')[-1] for f in v18_files[:5]]}")