#!/usr/bin/env python3
"""
Test algorithm complexity by measuring runtime vs instance size.
"""

import time
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11

def generate_random_points(n):
    """Generate n random points in unit square."""
    return np.random.rand(n, 2).tolist()

def test_runtime_scaling():
    """Test runtime scaling with instance size."""
    sizes = [50, 100, 150, 200, 250, 300]
    results = []
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n)
        
        start_time = time.time()
        try:
            solver = ChristofidesHybridStructuralOptimizedV11(points=points)
            tour, length, runtime = solver.solve(timeout=60)
            success = True
        except Exception as e:
            print(f"  Error: {e}")
            success = False
        
        elapsed = time.time() - start_time
        
        if success:
            results.append((n, elapsed))
            print(f"  Success: {elapsed:.2f}s")
        else:
            results.append((n, None))
            print(f"  Failed or timed out")
    
    print("\n=== Runtime Scaling Results ===")
    for n, t in results:
        if t is not None:
            print(f"n={n}: {t:.2f}s")
        else:
            print(f"n={n}: Failed")

if __name__ == "__main__":
    test_runtime_scaling()
