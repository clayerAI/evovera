#!/usr/bin/env python3
"""
Simple test to verify algorithms work correctly.
"""

import sys
import os
import time
import random
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as christofides_ils_solve
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as christofides_structural_solve

def generate_random_points(n, seed=None):
    """Generate random points in unit square."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def calculate_tour_length(points, tour):
    """Calculate total tour length."""
    total = 0
    n = len(points)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total

def test_algorithm(algorithm_func, name, points, timeout=30):
    """Test a single algorithm."""
    print(f"\nTesting {name}...")
    
    try:
        start_time = time.time()
        tour, distance = algorithm_func(points)
        end_time = time.time()
        
        # Verify tour
        # TSP tours can be represented as cycles (starting and ending at same vertex)
        # or as paths (visiting each vertex exactly once)
        
        # Check if it's a cycle representation (n+1 vertices with first=last)
        is_cycle = len(tour) == len(points) + 1 and tour[0] == tour[-1]
        
        # Check if it's a path representation (n vertices, all unique)
        is_path = len(tour) == len(points) and len(set(tour)) == len(points)
        
        if not (is_cycle or is_path):
            print(f"  ERROR: Invalid tour format")
            print(f"    Length: {len(tour)} (expected {len(points)} or {len(points)+1})")
            print(f"    Unique vertices: {len(set(tour))}")
            if len(tour) > 0:
                print(f"    First vertex: {tour[0]}, Last vertex: {tour[-1]}")
            return None
        
        if is_cycle:
            # Remove duplicate start/end vertex for validation
            tour_for_validation = tour[:-1]
        else:
            tour_for_validation = tour
        
        # Verify all vertices are present
        if set(tour_for_validation) != set(range(len(points))):
            print(f"  ERROR: Tour doesn't visit all vertices")
            missing = set(range(len(points))) - set(tour_for_validation)
            extra = set(tour_for_validation) - set(range(len(points)))
            if missing:
                print(f"    Missing vertices: {missing}")
            if extra:
                print(f"    Extra vertices: {extra}")
            return None
        
        # Verify distance
        calculated = calculate_tour_length(points, tour)
        if abs(calculated - distance) > 0.001:
            print(f"  WARNING: Distance mismatch {distance:.3f} vs {calculated:.3f}")
        
        print(f"  Success: distance={distance:.3f}, runtime={end_time-start_time:.2f}s")
        return distance
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def main():
    """Main test function."""
    print("=" * 60)
    print("SIMPLE ALGORITHM TEST")
    print("=" * 60)
    
    # Test small problem first
    n = 30
    seed = 42
    points = generate_random_points(n, seed)
    
    print(f"\nTesting with n={n}, seed={seed}")
    
    # Test each algorithm
    results = {}
    
    results['v1_nn'] = test_algorithm(nn_solve, "Nearest Neighbor + 2-opt", points)
    results['v8_christofides_ils'] = test_algorithm(christofides_ils_solve, "Christofides-ILS Hybrid", points, timeout=60)
    results['v19_christofides_structural'] = test_algorithm(christofides_structural_solve, "Christofides Structural Hybrid", points, timeout=60)
    
    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    baseline = results['v1_nn']
    if baseline is not None:
        print(f"\nBaseline (NN+2opt): {baseline:.3f}")
        
        for algo_name in ['v8_christofides_ils', 'v19_christofides_structural']:
            if results[algo_name] is not None:
                improvement = ((baseline - results[algo_name]) / baseline) * 100
                print(f"{algo_name}: {results[algo_name]:.3f} ({improvement:+.2f}%)")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()