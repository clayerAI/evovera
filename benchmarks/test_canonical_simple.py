#!/usr/bin/env python3
"""Simple test of canonical benchmark with random instances only."""

import sys
import os
sys.path.append('.')

import numpy as np
import time
import math
import json
from typing import List

# Import key algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt
from solutions.tsp_v2_christofides import solve_tsp as solve_tsp_christofides
from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as solve_tsp_christofides_ils_fixed
from solutions.tsp_v16_christofides_path_centrality import solve_tsp as solve_tsp_christofides_path_centrality
from solutions.tsp_v18_christofides_community_detection import solve_tsp as solve_tsp_christofides_community_detection
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as solve_tsp_christofides_hybrid_structural

def generate_random_instance(n: int, seed: int = 42):
    """Generate random Euclidean TSP instance in [0, 1] scale."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

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

def run_algorithm(algorithm_name: str, solve_func, points: np.ndarray, seed: int = 42):
    """Run a single algorithm and measure performance."""
    np.random.seed(seed)
    start_time = time.time()
    
    try:
        # Convert points to list of tuples for algorithms expecting that format
        points_list = [(float(p[0]), float(p[1])) for p in points]
        
        # Special handling for v8 which expects numpy arrays
        if algorithm_name == "v8_christofides_ils_hybrid":
            result = solve_func(points)
        else:
            result = solve_func(points_list)
        
        # Handle different return types
        if isinstance(result, tuple):
            # Most algorithms return (tour, length)
            tour = result[0]
            returned_length = result[1] if len(result) > 1 else None
        else:
            # Some algorithms return just the tour
            tour = result
            returned_length = None
        
        # Ensure tour is a list of integers
        if isinstance(tour, np.ndarray):
            tour = tour.tolist()
        
        # Convert numpy ints to Python ints
        tour = [int(x) for x in tour]
        
        length = calculate_tour_length(points, tour)
        
        # Verify returned length if available
        if returned_length and abs(returned_length - length) > 0.001:
            print(f"    Warning: length mismatch: returned {returned_length:.3f}, calculated {length:.3f}")
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "tour_length": length,
            "runtime": elapsed,
            "tour": tour[:10] if len(tour) > 10 else tour
        }
    
    except Exception as e:
        print(f"  Error running {algorithm_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "runtime": time.time() - start_time
        }

def main():
    """Test with small random instance."""
    print("Testing canonical benchmark with n=20 random instance...")
    
    # Generate small instance
    points = generate_random_instance(20, seed=42)
    print(f"Generated instance with {len(points)} points in [0, 1] scale")
    
    # Test NN+2opt
    print("\nTesting NN+2opt...")
    result = run_algorithm("nn_2opt", solve_tsp_nn_2opt, points, seed=42)
    if result["success"]:
        print(f"  Success! Length: {result['tour_length']:.3f}, Time: {result['runtime']:.3f}s")
    else:
        print(f"  Failed: {result.get('error')}")
    
    # Test v19
    print("\nTesting v19...")
    result = run_algorithm("v19", solve_tsp_christofides_hybrid_structural, points, seed=42)
    if result["success"]:
        print(f"  Success! Length: {result['tour_length']:.3f}, Time: {result['runtime']:.3f}s")
    else:
        print(f"  Failed: {result.get('error')}")

if __name__ == "__main__":
    main()