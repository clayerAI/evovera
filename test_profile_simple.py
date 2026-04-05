#!/usr/bin/env python3
"""
Simple profiling of v19 corrected algorithm.
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
    try:
        tour, length = solve_tsp(points, timeout=300)
        elapsed = time.time() - start
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Tour length: {length:.2f}")
        print(f"  Valid tour: {len(set(tour)) == len(points)}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Timeout or error after {elapsed:.3f}s: {e}")
    
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
        try:
            tour, length = solve_tsp(points, timeout=60)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Time: {elapsed:.3f}s")
        except Exception as e:
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Stopped after {elapsed:.3f}s: {e}")
            break
    
    # Print scaling analysis
    print("\n=== Scaling Summary ===")
    for i, n in enumerate(sizes[:len(times)]):
        print(f"n={n}: {times[i]:.3f}s")
    
    if len(times) >= 2:
        print("\n=== Projected Times ===")
        last_n = sizes[len(times)-1]
        last_time = times[-1]
        
        # Quadratic scaling projection
        for n in [280, 400, 532]:
            projected = last_time * (n**2) / (last_n**2)
            print(f"n={n}: projected {projected:.1f}s (quadratic scaling)")

if __name__ == "__main__":
    print("=== V19 Corrected Algorithm Performance Test ===")
    test_n_100()
    test_n_200()
    test_n_300()
    analyze_scaling()
