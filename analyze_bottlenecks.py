#!/usr/bin/env python3
"""Analyze bottlenecks in optimized v19 algorithm."""

import sys
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized
import random
import time
import cProfile
import pstats
from io import StringIO

def create_random_points(n=100, seed=42):
    random.seed(seed)
    points = []
    for i in range(n):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        points.append((x, y))
    return points

def profile_algorithm(n=100):
    print(f"Profiling optimized v19 algorithm with n={n}...")
    points = create_random_points(n, seed=42)
    
    # Create profiler
    pr = cProfile.Profile()
    pr.enable()
    
    # Run algorithm
    solver = ChristofidesHybridStructuralOptimized(points, seed=42)
    result = solver.solve(apply_2opt=False)  # Disable 2-opt to focus on core algorithm
    
    pr.disable()
    
    # Print profiling results
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)
    
    print("Top 20 functions by cumulative time:")
    print(s.getvalue())
    
    print(f"\nAlgorithm results:")
    print(f"  Tour length: {result[1]:.2f}")
    print(f"  Runtime: {result[2]:.4f} seconds")
    
    return result

if __name__ == "__main__":
    # Test with increasing sizes
    for n in [50, 100, 150]:
        print(f"\n{'='*60}")
        profile_algorithm(n)
