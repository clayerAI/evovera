#!/usr/bin/env python3
"""
Debug efficient ILS algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import random
from solutions.tsp_v13_nn_efficient_ils import (
    compute_distance_matrix,
    nearest_neighbor_tsp,
    fast_local_search,
    double_bridge_kick,
    euclidean_distance
)

def test_basic():
    """Test basic components"""
    np.random.seed(42)
    n = 10
    points = np.random.rand(n, 2) * 100
    
    print("Testing basic components")
    print("=" * 60)
    
    # Distance matrix
    dist_matrix = compute_distance_matrix(points)
    print(f"Distance matrix shape: {dist_matrix.shape}")
    print(f"Sample distance [0,1]: {dist_matrix[0,1]:.2f}")
    print(f"Sample distance [1,0]: {dist_matrix[1,0]:.2f}")
    
    # NN tour
    nn_tour = nearest_neighbor_tsp(points, dist_matrix)
    print(f"\nNN tour: {nn_tour}")
    
    # Tour length
    length1 = tour_length(nn_tour, points)
    length2 = 0.0
    for i in range(n):
        j = (i + 1) % n
        length2 += dist_matrix[nn_tour[i], nn_tour[j]]
    
    print(f"Tour length (function): {length1:.2f}")
    print(f"Tour length (manual): {length2:.2f}")
    print(f"Match: {abs(length1 - length2) < 1e-10}")
    
    # Fast local search
    print(f"\nRunning fast local search...")
    improved_tour, improved_length = fast_local_search(nn_tour, dist_matrix, max_trials=20)
    
    print(f"Original tour length: {length1:.2f}")
    print(f"Improved tour length: {improved_length:.2f}")
    print(f"Improvement: {(length1 - improved_length)/length1*100:.2f}%")
    print(f"Tour changed: {nn_tour != improved_tour}")
    
    # Verify improved length matches calculation
    calc_length = 0.0
    for i in range(n):
        j = (i + 1) % n
        calc_length += dist_matrix[improved_tour[i], improved_tour[j]]
    
    print(f"Calculated length: {calc_length:.2f}")
    print(f"Length match: {abs(improved_length - calc_length) < 1e-10}")

def test_double_bridge():
    """Test double bridge perturbation"""
    np.random.seed(42)
    n = 20
    points = np.random.rand(n, 2) * 100
    dist_matrix = compute_distance_matrix(points)
    
    print("\n\nTesting double bridge perturbation")
    print("=" * 60)
    
    # Create a simple tour
    tour = list(range(n))
    random.shuffle(tour)
    
    print(f"Original tour (first 10): {tour[:10]}")
    
    from solutions.tsp_v13_nn_efficient_ils import double_bridge_kick
    perturbed = double_bridge_kick(tour)
    
    print(f"Perturbed tour (first 10): {perturbed[:10]}")
    
    # Check if it's a valid permutation
    print(f"Valid permutation: {sorted(tour) == sorted(perturbed)}")
    
    # Check lengths
    orig_length = 0.0
    pert_length = 0.0
    for i in range(n):
        j = (i + 1) % n
        orig_length += dist_matrix[tour[i], tour[j]]
        pert_length += dist_matrix[perturbed[i], perturbed[j]]
    
    print(f"Original length: {orig_length:.2f}")
    print(f"Perturbed length: {pert_length:.2f}")
    print(f"Change: {pert_length - orig_length:.2f}")

if __name__ == "__main__":
    test_basic()
    test_double_bridge()