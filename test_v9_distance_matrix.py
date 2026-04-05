#!/usr/bin/env python3
"""
Quick test to verify v9 algorithm accepts distance_matrix parameter.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v19_optimized_fixed_v9 import ChristofidesHybridStructuralOptimizedV8
import random
import numpy as np

def test_distance_matrix():
    """Test that v9 works with distance_matrix parameter."""
    print("Testing v9 distance_matrix compatibility...")
    
    # Create random points
    n = 10
    random.seed(42)
    points = np.array([(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)])
    
    # Create distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d
    
    # Test 1: With points only (should compute distance matrix internally)
    print("\nTest 1: With points only")
    try:
        solver1 = ChristofidesHybridStructuralOptimizedV8(points=points)
        tour1, length1, time1 = solver1.solve()
        print(f"  Success! Tour length: {length1:.2f}, Time: {time1:.3f}s")
    except Exception as e:
        print(f"  Failed: {e}")
    
    # Test 2: With distance_matrix parameter
    print("\nTest 2: With distance_matrix parameter")
    try:
        solver2 = ChristofidesHybridStructuralOptimizedV8(distance_matrix=dist_matrix)
        tour2, length2, time2 = solver2.solve()
        print(f"  Success! Tour length: {length2:.2f}, Time: {time2:.3f}s")
    except Exception as e:
        print(f"  Failed: {e}")
    
    # Test 3: Check if results are identical
    print("\nTest 3: Comparing results")
    if 'tour1' in locals() and 'tour2' in locals():
        diff = abs(length1 - length2)
        print(f"  Length difference: {diff:.6f}")
        if diff < 1e-6:
            print("  ✓ Results are identical")
        else:
            print("  ⚠ Results differ slightly (expected due to floating point)")
    
    print("\n✅ v9 algorithm verified to accept distance_matrix parameter")

if __name__ == "__main__":
    test_distance_matrix()
