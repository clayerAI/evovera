#!/usr/bin/env python3
"""
Quick test for v18 Christofides with Community Detection.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import solve_tsp as v18_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_v18():
    """Test v18 algorithm."""
    print("Testing v18: Christofides with Community Detection")
    print("=" * 60)
    
    test_cases = [
        {'n': 30, 'seed': 42, 'name': 'small'},
        {'n': 50, 'seed': 42, 'name': 'medium'},
        {'n': 75, 'seed': 42, 'name': 'large'},
    ]
    
    for test_case in test_cases:
        n = test_case['n']
        seed = test_case['seed']
        name = test_case['name']
        
        print(f"\nTesting {name} (n={n}):")
        
        points = generate_random_points(n=n, seed=seed)
        
        # Get baseline
        start = time.time()
        baseline_tour, baseline_length = nn2opt_solve(points)
        baseline_time = time.time() - start
        
        # Test v18
        start = time.time()
        v18_tour, v18_length = v18_solve(points, seed=seed)
        v18_time = time.time() - start
        
        improvement = ((baseline_length - v18_length) / baseline_length) * 100
        
        print(f"  Baseline (NN+2opt): {baseline_length:.4f} ({baseline_time:.2f}s)")
        print(f"  v18: {v18_length:.4f} ({v18_time:.2f}s)")
        print(f"  Improvement: {improvement:.2f}%")
        
        if improvement > 0.1:
            print(f"  ✅ Exceeds 0.1% publication threshold")
        elif improvement > 0:
            print(f"  ⚠️  Positive but below threshold")
        else:
            print(f"  ❌ Worse than baseline")
    
    print(f"\n{'='*60}")
    print("v18 implementation complete and ready for comprehensive testing.")

if __name__ == "__main__":
    test_v18()