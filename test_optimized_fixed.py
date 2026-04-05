#!/usr/bin/env python3
"""
Test optimized v19 algorithm.
"""

import sys
import os
sys.path.append('.')

import random
import time
from solutions.tsp_v19_optimized_fixed import solve_tsp

def generate_random_points(n: int, seed: int = 42):
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def test_optimized():
    """Test optimized algorithm."""
    print("=== Testing Optimized v19 Algorithm ===")
    
    sizes = [50, 100, 150, 200, 250, 300]
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n, seed=n)
        
        start = time.time()
        try:
            tour, length = solve_tsp(points)
            elapsed = time.time() - start
            
            # Validate tour
            valid = len(set(tour)) == n and len(tour) == n
            
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Length: {length:.2f}")
            print(f"  Valid: {valid}")
            
            if n >= 200:
                print(f"  Speedup needed for n={n}: target <30s, current {elapsed:.1f}s")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"  Error after {elapsed:.3f}s: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    test_optimized()
