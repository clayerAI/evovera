#!/usr/bin/env python3
"""
Debug v19 algorithm.
"""

import sys
import os
import random
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp

def generate_random_points(n, seed=None):
    """Generate random points in unit square."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

# Test with small problem
n = 30
seed = 42
points = generate_random_points(n, seed)

print(f"Testing v19 with n={n}, seed={seed}")
print(f"Points: {len(points)}")

try:
    tour, distance = solve_tsp(points)
    print(f"\nTour length: {len(tour)}")
    print(f"Tour: {tour[:10]}...")  # Show first 10 elements
    
    # Check for duplicates
    unique = set(tour)
    print(f"\nUnique vertices: {len(unique)}")
    
    if len(unique) != len(tour):
        print(f"WARNING: Duplicates found!")
        # Count occurrences
        from collections import Counter
        counts = Counter(tour)
        duplicates = {k: v for k, v in counts.items() if v > 1}
        print(f"Duplicates: {duplicates}")
    
    # Check if tour starts and ends with same vertex
    if tour[0] == tour[-1]:
        print(f"\nTour starts and ends with same vertex: {tour[0]}")
        print(f"Tour without last vertex: {len(tour)-1} vertices")
        
        # Remove last vertex and check
        tour_without_last = tour[:-1]
        unique_without_last = set(tour_without_last)
        print(f"Unique vertices without last: {len(unique_without_last)}")
        
        if len(unique_without_last) == n:
            print("SUCCESS: Tour is valid if we remove the duplicate start/end vertex")
        else:
            print("ERROR: Still not valid even after removing last vertex")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()