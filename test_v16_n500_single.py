#!/usr/bin/env python3
"""
Quick test of v16 on n=500 with single seed.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time

def generate_random_points(n: int = 500, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_v16_n500():
    """Test v16 on n=500 with single seed."""
    print("Testing v16 on n=500 (single seed)")
    print("=" * 60)
    
    seed = 42
    points = generate_random_points(n=500, seed=seed)
    
    # Get baseline
    print("Running baseline (NN+2opt)...")
    start = time.time()
    baseline_tour, baseline_length = nn2opt_solve(points)
    baseline_time = time.time() - start
    print(f"  Baseline length: {baseline_length:.4f}")
    print(f"  Baseline time: {baseline_time:.2f}s")
    
    # Test v16 with adaptive weight (0.7 for n>50)
    print("\nRunning v16 with adaptive weight (0.7)...")
    start = time.time()
    solver = ChristofidesPathCentrality(points, seed=seed)
    v16_tour, v16_length, _ = solver.solve(centrality_weight=0.7, apply_2opt=True)
    v16_time = time.time() - start
    
    improvement = ((baseline_length - v16_length) / baseline_length) * 100
    
    print(f"  v16 length: {v16_length:.4f}")
    print(f"  v16 time: {v16_time:.2f}s")
    print(f"  Improvement: {improvement:.2f}%")
    
    if improvement > 0.1:
        print(f"  ✅ Exceeds 0.1% publication threshold")
    elif improvement > 0:
        print(f"  ⚠️  Positive but below threshold")
    else:
        print(f"  ❌ Worse than baseline")
    
    print(f"\n{'='*60}")
    print("v16 n=500 test complete.")

if __name__ == "__main__":
    test_v16_n500()