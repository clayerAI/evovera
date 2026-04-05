#!/usr/bin/env python3
"""
Comprehensive test of optimized v19 algorithm.
"""

import sys
import os
sys.path.append('.')

import random
import time
import math
from solutions.tsp_v19_optimized_fixed import solve_tsp
from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp as solve_tsp_original

def generate_random_points(n: int, seed: int = 42):
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def compare_algorithms():
    """Compare original vs optimized algorithms."""
    print("=== Comparing Original vs Optimized v19 Algorithms ===")
    
    sizes = [50, 100, 150, 200]
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n, seed=n)
        
        # Test original
        print("  Original algorithm:")
        start = time.time()
        try:
            tour1, length1 = solve_tsp_original(points)
            elapsed1 = time.time() - start
            print(f"    Time: {elapsed1:.3f}s")
            print(f"    Length: {length1:.2f}")
        except Exception as e:
            elapsed1 = time.time() - start
            print(f"    Error after {elapsed1:.3f}s: {e}")
        
        # Test optimized
        print("  Optimized algorithm:")
        start = time.time()
        try:
            tour2, length2 = solve_tsp(points)
            elapsed2 = time.time() - start
            print(f"    Time: {elapsed2:.3f}s")
            print(f"    Length: {length2:.2f}")
            
            # Compare quality
            if 'tour1' in locals() and 'tour2' in locals():
                quality_diff = abs(length1 - length2) / length1 * 100
                print(f"    Quality difference: {quality_diff:.2f}%")
                speedup = elapsed1 / elapsed2 if elapsed2 > 0 else float('inf')
                print(f"    Speedup: {speedup:.1f}x")
                
        except Exception as e:
            elapsed2 = time.time() - start
            print(f"    Error after {elapsed2:.3f}s: {e}")

def test_scaling():
    """Test scaling behavior."""
    print("\n=== Scaling Analysis for Optimized Algorithm ===")
    
    sizes = [50, 100, 150, 200, 250, 300, 350, 400]
    times = []
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n, seed=n)
        
        start = time.time()
        try:
            tour, length = solve_tsp(points)
            elapsed = time.time() - start
            times.append(elapsed)
            
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Length: {length:.2f}")
            
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Error after {elapsed:.3f}s: {e}")
            break
    
    # Analyze scaling
    print("\n=== Scaling Summary ===")
    for i, n in enumerate(sizes[:len(times)]):
        print(f"n={n}: {times[i]:.3f}s")
    
    if len(times) >= 2:
        print("\n=== Projected Times for TSPLIB Instances ===")
        # Use n=300 as baseline
        baseline_n = 300
        baseline_time = times[5]  # n=300
        
        # Project using observed scaling (looks like O(n^2) or better)
        for n in [280, 400, 532]:
            # Conservative quadratic projection
            projected = baseline_time * (n**2) / (baseline_n**2)
            print(f"n={n} (TSPLIB): projected {projected:.1f}s")
            
            # Check against targets
            if n == 280:
                target = 30
                status = "✓" if projected <= target else "✗"
                print(f"  Target: {target}s {status} (projected: {projected:.1f}s)")
            elif n == 532:
                target = 120
                status = "✓" if projected <= target else "✗"
                print(f"  Target: {target}s {status} (projected: {projected:.1f}s)")

def test_correctness():
    """Test algorithm correctness on small instances."""
    print("\n=== Correctness Testing ===")
    
    # Simple test cases
    test_cases = [
        # Square
        [(0, 0), (0, 1), (1, 1), (1, 0)],
        # Triangle
        [(0, 0), (3, 0), (1.5, 2.6)],
        # Line
        [(0, 0), (1, 0), (2, 0), (3, 0)],
    ]
    
    for i, points in enumerate(test_cases):
        print(f"\nTest case {i+1} (n={len(points)}):")
        
        try:
            tour, length = solve_tsp(points)
            print(f"  Tour: {tour}")
            print(f"  Length: {length:.2f}")
            
            # Check validity
            if len(set(tour)) == len(points) and len(tour) == len(points):
                print("  ✓ Valid tour")
            else:
                print("  ✗ Invalid tour")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    compare_algorithms()
    test_scaling()
    test_correctness()
