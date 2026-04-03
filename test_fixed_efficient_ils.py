#!/usr/bin/env python3
"""
Test the fixed efficient ILS algorithm
"""

import numpy as np
import time
import sys
sys.path.append('/workspace/evovera/solutions')

from tsp_v13_nn_efficient_ils import solve_tsp_nn_efficient_ils
from tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn
from tsp_v1_nearest_neighbor import TSP_Solver

def solve_tsp_nn_2opt(points):
    """NN+2opt baseline"""
    solver = TSP_Solver(points)
    tour, distance = solver.nearest_neighbor_with_2opt(num_starts=10, two_opt_iterations=500)
    return tour, distance

def generate_random_points(n: int, seed: int = 42) -> np.ndarray:
    """Generate random 2D points"""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def benchmark_algorithm(points: np.ndarray, algorithm_name: str, algorithm_func):
    """Benchmark a single algorithm"""
    print(f"\nBenchmarking {algorithm_name} on {len(points)} cities...")
    start_time = time.time()
    
    if algorithm_name == "NN":
        tour, length = algorithm_func(points)
        stats = {'initial_length': length, 'final_length': length, 'overall_improvement': 0.0}
    elif algorithm_name == "NN+2opt":
        tour, length = algorithm_func(points)
        stats = {'initial_length': length, 'final_length': length, 'overall_improvement': 0.0}
    else:
        tour, length, stats = algorithm_func(points, max_iterations=100)
    
    end_time = time.time()
    
    print(f"  Tour length: {length:.4f}")
    print(f"  Initial length: {stats.get('initial_length', length):.4f}")
    print(f"  Improvement: {stats.get('overall_improvement', 0.0)*100:.2f}%")
    print(f"  Time: {end_time - start_time:.3f}s")
    
    return length, stats

def main():
    print("Testing Fixed Efficient ILS Algorithm")
    print("=" * 60)
    
    # Test on different sizes
    sizes = [20, 50, 100]
    
    for n in sizes:
        print(f"\n{'='*60}")
        print(f"Testing with n = {n}")
        print(f"{'='*60}")
        
        points = generate_random_points(n)
        
        # Benchmark NN baseline
        nn_length, _ = benchmark_algorithm(points, "NN", solve_tsp_nn)
        
        # Benchmark NN+2opt baseline
        nn_2opt_length, _ = benchmark_algorithm(points, "NN+2opt", solve_tsp_nn_2opt)
        
        # Benchmark Efficient ILS
        ils_length, stats = benchmark_algorithm(points, "NN+Efficient ILS", solve_tsp_nn_efficient_ils)
        
        # Calculate improvement over NN+2opt
        improvement_over_nn_2opt = (nn_2opt_length - ils_length) / nn_2opt_length * 100
        
        print(f"\n  Improvement over NN+2opt: {improvement_over_nn_2opt:.2f}%")
        
        # Check if improvement meets threshold
        if improvement_over_nn_2opt >= 0.1:
            print(f"  ✅ SUCCESS: Meets 0.1% improvement threshold!")
        else:
            print(f"  ⚠️  Needs improvement: Below 0.1% threshold")

if __name__ == "__main__":
    main()