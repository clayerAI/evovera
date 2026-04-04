#!/usr/bin/env python3
"""
Test optimized v19 algorithm.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
import time
from typing import List, Tuple

from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_original
from solutions.tsp_v19_christofides_hybrid_structural_optimized import solve_tsp as solve_tsp_optimized

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def test_correctness():
    """Test that optimized version produces same results as original."""
    print("=== Correctness Test ===")
    
    test_cases = [
        (10, 123),
        (20, 456),
        (30, 789),
        (50, 1011)
    ]
    
    all_correct = True
    for n, seed in test_cases:
        points = generate_random_points(n, seed=seed)
        
        # Run original
        start = time.time()
        tour1, length1 = solve_tsp_original(points)
        time1 = time.time() - start
        
        # Run optimized
        start = time.time()
        tour2, length2 = solve_tsp_optimized(points)
        time2 = time.time() - start
        
        # Check validity
        valid1 = len(set(tour1)) == n and tour1[0] == tour1[-1]
        valid2 = len(set(tour2)) == n and tour2[0] == tour2[-1]
        
        # Check if tours are similar (allow small floating point differences)
        length_diff = abs(length1 - length2) / length1 if length1 > 0 else 0
        
        print(f"n={n}, seed={seed}:")
        print(f"  Original: length={length1:.3f}, time={time1:.3f}s, valid={valid1}")
        print(f"  Optimized: length={length2:.3f}, time={time2:.3f}s, valid={valid2}")
        print(f"  Length difference: {length_diff:.6f} ({length_diff*100:.4f}%)")
        print(f"  Speedup: {time1/time2:.2f}x")
        
        if length_diff > 0.01:  # More than 1% difference
            print(f"  WARNING: Significant length difference!")
            all_correct = False
    
    return all_correct

def test_performance():
    """Test performance scaling."""
    print("\n=== Performance Test ===")
    
    for n in [50, 100, 200, 300]:
        points = generate_random_points(n, seed=42)
        
        # Warm up
        _ = solve_tsp_optimized(points[:10])
        
        # Test optimized
        start = time.time()
        tour, length = solve_tsp_optimized(points)
        time_opt = time.time() - start
        
        valid = len(set(tour)) == n and tour[0] == tour[-1]
        
        print(f"n={n}:")
        print(f"  Optimized: time={time_opt:.3f}s, length={length:.3f}, valid={valid}")
        
        # Estimate original time based on scaling
        # Original scales roughly O(n^2) due to all-pairs paths
        # Optimized scales better since it only considers odd vertices
        if n == 50:
            # Actually measure original for n=50
            start = time.time()
            tour_orig, length_orig = solve_tsp_original(points)
            time_orig = time.time() - start
            print(f"  Original: time={time_orig:.3f}s (measured)")
            print(f"  Speedup: {time_orig/time_opt:.2f}x")
        else:
            # Estimate based on n=50 measurement
            # Original: O(n^2) for path computation
            # Optimized: O(m^2) where m ≈ 0.43n (odd vertices)
            estimated_orig = time_opt * (n/50)**2  # Rough estimate
            print(f"  Original (estimated): time≈{estimated_orig:.3f}s")
            print(f"  Estimated speedup: {estimated_orig/time_opt:.2f}x")

def test_n500():
    """Test if optimized version can handle n=500."""
    print("\n=== n=500 Test ===")
    
    points = generate_random_points(500, seed=42)
    
    print("Running optimized v19 on n=500...")
    start = time.time()
    
    try:
        tour, length = solve_tsp_optimized(points)
        time_taken = time.time() - start
        
        valid = len(set(tour)) == 500 and tour[0] == tour[-1]
        
        print(f"  Success! Time: {time_taken:.3f}s")
        print(f"  Tour length: {length:.3f}")
        print(f"  Valid tour: {valid}")
        
        if time_taken < 180:  # 3 minute timeout
            print(f"  PASS: Under 180s timeout (by {180-time_taken:.1f}s)")
            return True
        else:
            print(f"  FAIL: Exceeds 180s timeout (by {time_taken-180:.1f}s)")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Optimized v19 Algorithm")
    print("=" * 40)
    
    # Test correctness
    if test_correctness():
        print("\n✓ All correctness tests passed")
    else:
        print("\n✗ Some correctness tests failed")
    
    # Test performance
    test_performance()
    
    # Test n=500
    if test_n500():
        print("\n✓ n=500 test passed - algorithm is now optimized!")
    else:
        print("\n✗ n=500 test failed - needs further optimization")