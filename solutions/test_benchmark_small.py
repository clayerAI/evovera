#!/usr/bin/env python3
"""Quick test of the comprehensive benchmark with small instance."""
import sys
sys.path.append('.')

import numpy as np
import time
import math
from typing import List, Tuple

# Import a few algorithms for testing
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
from solutions.tsp_v14_christofides_adaptive_matching import solve_tsp as solve_tsp_christofides_adaptive_matching

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance."""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def calculate_tour_length(points: np.ndarray, tour: List[int]) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        dx = points[tour[i]][0] - points[tour[i+1]][0]
        dy = points[tour[i]][1] - points[tour[i+1]][1]
        total += math.sqrt(dx*dx + dy*dy)
    # Close the tour
    dx = points[tour[-1]][0] - points[tour[0]][0]
    dy = points[tour[-1]][1] - points[tour[0]][1]
    total += math.sqrt(dx*dx + dy*dy)
    return total

def test_algorithm(name, points, points_list, solve_func):
    """Test a single algorithm."""
    print(f"\nTesting {name}...")
    start_time = time.time()
    try:
        result = solve_func(points_list if 'nn' in name.lower() else points)
        runtime = time.time() - start_time
        
        if isinstance(result, tuple):
            tour = result[0]
            reported_length = result[1]
        else:
            tour = result
            reported_length = calculate_tour_length(points, tour)
        
        print(f"  Runtime: {runtime:.3f}s")
        print(f"  Tour length: {reported_length:.4f}")
        print(f"  Tour valid: {len(tour) == len(points)}")
        return tour, runtime, reported_length
    except Exception as e:
        print(f"  ERROR: {e}")
        return None, float('inf'), float('inf')

def main():
    print("Testing standardized TSP algorithm interfaces")
    print("=" * 50)
    
    # Generate small test instance
    n = 50  # Small for quick testing
    points = generate_random_instance(n)
    points_list = [(float(x), float(y)) for x, y in points]
    
    print(f"Generated TSP instance with {n} points")
    
    # Test a few key algorithms
    algorithms = [
        ("NN+2opt (v1)", points_list, solve_tsp_nn_2opt),
        ("Christofides (v2)", points, solve_tsp_christofides),
        ("Christofides-ILS Fixed (v8)", points, solve_tsp_christofides_ils_fixed),
        ("Christofides Adaptive Matching (v14)", points, solve_tsp_christofides_adaptive_matching),
    ]
    
    results = {}
    for name, data, func in algorithms:
        tour, runtime, length = test_algorithm(name, points, data, func)
        if tour is not None:
            results[name] = (length, runtime)
    
    # Compare results
    if results:
        print("\n" + "=" * 50)
        print("Performance Summary (n=50):")
        baseline = results.get("NN+2opt (v1)", (float('inf'), float('inf')))[0]
        
        for name, (length, runtime) in sorted(results.items(), key=lambda x: x[1][0]):
            improvement = ((baseline - length) / baseline * 100) if baseline != float('inf') else 0
            print(f"{name:35} Length: {length:8.4f}  Runtime: {runtime:6.3f}s  Improvement: {improvement:6.2f}%")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()