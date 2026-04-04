#!/usr/bin/env python3
"""
Test v16 performance on smaller n to understand runtime.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
import random
import time

def test_performance(n=100, seed=42):
    """Test v16 performance on n=100."""
    random.seed(seed)
    points = [(random.random(), random.random()) for _ in range(n)]
    
    print(f"Testing v16 on n={n}, seed={seed}")
    
    start = time.time()
    solver = ChristofidesPathCentrality(points, seed=seed)
    tour, length, _ = solver.solve(centrality_weight=0.7, apply_2opt=True)
    elapsed = time.time() - start
    
    print(f"  Result: length={length:.4f}, time={elapsed:.1f}s")
    print(f"  Estimated time for n=500: {elapsed * (500/100)**3:.1f}s (cubic scaling)")
    
    return elapsed

if __name__ == "__main__":
    # Test on n=100 first
    time_100 = test_performance(n=100, seed=42)
    
    # Test on n=200 if n=100 was reasonable
    if time_100 < 10:  # If n=100 takes less than 10s
        print("\n" + "="*40)
        time_200 = test_performance(n=200, seed=42)
        
        # Estimate n=500 time
        if time_200 < 60:  # If n=200 takes less than 60s
            print("\n" + "="*40)
            print(f"Estimated scaling:")
            print(f"  n=100: {time_100:.1f}s")
            print(f"  n=200: {time_200:.1f}s")
            print(f"  Scaling factor: {time_200/time_100:.1f}x for 2x n")
            print(f"  Estimated n=500: {time_100 * (500/100)**3:.1f}s (cubic)")
            print(f"  Estimated n=500: {time_100 * (500/100)**2.5:.1f}s (n^2.5)")
            print(f"  Estimated n=500: {time_100 * (500/100)**2:.1f}s (quadratic)")