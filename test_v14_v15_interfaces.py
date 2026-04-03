#!/usr/bin/env python3
"""Test v14 and v15 interfaces for benchmarking."""

import sys
sys.path.append('.')

import random
import math
from typing import List, Tuple

# Import the algorithms
from solutions.tsp_v14_christofides_adaptive_matching import solve_tsp as solve_v14
from solutions.tsp_v15_algorithmic_ecology import solve_tsp as solve_v15

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def calculate_tour_length(points: List[Tuple[float, float]], tour: List[int]) -> float:
    """Calculate total length of a TSP tour."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return total

def main():
    print("Testing v14 and v15 interfaces")
    print("=" * 50)
    
    # Generate test points
    n = 20
    points = generate_random_points(n, seed=42)
    
    print(f"Testing on n={n} random points")
    
    # Test v14
    print("\nTesting v14 (Christofides with Adaptive Matching)...")
    try:
        tour_v14 = solve_v14(points, seed=42)
        length_v14 = calculate_tour_length(points, tour_v14)
        print(f"  Success! Tour length: {length_v14:.4f}")
        print(f"  Tour: {tour_v14[:5]}... (first 5 nodes)")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Test v15
    print("\nTesting v15 (Algorithmic Ecology)...")
    try:
        tour_v15 = solve_v15(points, seed=42)
        length_v15 = calculate_tour_length(points, tour_v15)
        print(f"  Success! Tour length: {length_v15:.4f}")
        print(f"  Tour: {tour_v15[:5]}... (first 5 nodes)")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nInterface test complete!")

if __name__ == "__main__":
    main()