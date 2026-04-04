#!/usr/bin/env python3
"""
Simple test for v16 Christofides with Path-Based Centrality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
from solutions.tsp_v16_christofides_path_centrality import solve_tsp as v16_solve

def generate_random_points(n, seed=42):
    """Generate random Euclidean points"""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 1000

def calculate_tour_length(points, tour):
    """Calculate length of a tour given points"""
    length = 0.0
    n = len(tour)
    for i in range(n):
        p1 = points[tour[i]]
        p2 = points[tour[(i + 1) % n]]
        length += np.linalg.norm(p1 - p2)
    return length

def main():
    print("=== Simple v16 Test ===")
    
    # Use n=100 for faster testing
    n = 100
    print(f"Testing with n={n} nodes")
    
    # Generate points
    points = generate_random_points(n, seed=42)
    
    # Test NN+2opt
    print("\n1. Testing NN+2opt baseline...")
    start = time.time()
    nn_tour, nn_length = nn2opt_solve(points)
    nn_time = time.time() - start
    print(f"   Tour length: {nn_length:.4f}")
    print(f"   Time: {nn_time:.2f}s")
    
    # Test v16
    print("\n2. Testing v16 Christofides with Path-Based Centrality...")
    start = time.time()
    v16_tour, v16_length = v16_solve(points, seed=42)
    v16_time = time.time() - start
    print(f"   Tour length: {v16_length:.4f}")
    print(f"   Time: {v16_time:.2f}s")
    
    # Calculate improvement
    improvement = ((nn_length - v16_length) / nn_length) * 100
    print(f"\n=== Results ===")
    print(f"NN+2opt baseline: {nn_length:.4f}")
    print(f"v16 Path Centrality: {v16_length:.4f}")
    print(f"Improvement: {improvement:.2f}%")
    
    if improvement > 0.1:
        print(f"✅ EXCEEDS 0.1% publication threshold")
        return True
    else:
        print(f"❌ Below 0.1% publication threshold")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)