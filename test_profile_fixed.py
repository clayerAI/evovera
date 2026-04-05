#!/usr/bin/env python3
"""
Fixed profiling of v19 corrected algorithm.
"""

import sys
import os
sys.path.append('.')

import random
import time
from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp, ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def test_n_100():
    """Test with n=100."""
    print("Testing n=100...")
    points = generate_random_points(100, seed=123)
    
    start = time.time()
    tour, length = solve_tsp(points)
    elapsed = time.time() - start
    
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Tour length: {length:.2f}")
    print(f"  Valid tour: {len(set(tour)) == len(points)}")
    return elapsed

def test_n_200():
    """Test with n=200."""
    print("\nTesting n=200...")
    points = generate_random_points(200, seed=456)
    
    start = time.time()
    tour, length = solve_tsp(points)
    elapsed = time.time() - start
    
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Tour length: {length:.2f}")
    print(f"  Valid tour: {len(set(tour)) == len(points)}")
    return elapsed

def test_n_300():
    """Test with n=300."""
    print("\nTesting n=300...")
    points = generate_random_points(300, seed=789)
    
    start = time.time()
    tour, length = solve_tsp(points)
    elapsed = time.time() - start
    
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Tour length: {length:.2f}")
    print(f"  Valid tour: {len(set(tour)) == len(points)}")
    return elapsed

def analyze_scaling():
    """Analyze scaling behavior."""
    print("\n=== Scaling Analysis ===")
    
    sizes = [50, 100, 150, 200, 250]
    times = []
    
    for n in sizes:
        print(f"\nTesting n={n}...")
        points = generate_random_points(n, seed=n)
        
        start = time.time()
        tour, length = solve_tsp(points)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Time: {elapsed:.3f}s")
    
    # Print scaling analysis
    print("\n=== Scaling Summary ===")
    for i, n in enumerate(sizes):
        print(f"n={n}: {times[i]:.3f}s")
    
    print("\n=== Projected Times (Quadratic Scaling) ===")
    # Use n=200 as baseline for quadratic projection
    baseline_n = 200
    baseline_time = times[3]  # n=200
    
    for n in [280, 400, 532]:
        projected = baseline_time * (n**2) / (baseline_n**2)
        print(f"n={n}: projected {projected:.1f}s")
    
    print("\n=== Projected Times (Observed Scaling) ===")
    # Use observed scaling from n=100 to n=200
    n1, t1 = 100, times[1]
    n2, t2 = 200, times[3]
    
    # Compute scaling exponent
    exponent = math.log(t2/t1) / math.log(n2/n1)
    print(f"Observed scaling exponent: {exponent:.2f}")
    
    for n in [280, 400, 532]:
        projected = t1 * (n/n1)**exponent
        print(f"n={n}: projected {projected:.1f}s")

if __name__ == "__main__":
    import math
    print("=== V19 Corrected Algorithm Performance Test ===")
    t100 = test_n_100()
    t200 = test_n_200()
    t300 = test_n_300()
    analyze_scaling()
