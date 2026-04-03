#!/usr/bin/env python3
"""Test Iterative Local Search on larger instance (formerly mislabeled as Lin-Kernighan)"""

import numpy as np
import math
import random
from typing import List
import sys
sys.path.append('.')

from tsp_v3_iterative_local_search import EuclideanTSPIterativeLocalSearch

def test_large_instance():
    """Test on 100-city instance."""
    solver = EuclideanTSPIterativeLocalSearch(n=100, seed=42)
    
    # Get nearest neighbor tour
    nn_tour = solver.nearest_neighbor_tour()
    nn_length = solver.tour_length(nn_tour)
    print(f"Nearest neighbor: {nn_length:.4f}")
    
    # Apply 2-opt
    two_opt_tour = solver.two_opt_improvement(nn_tour, max_iterations=1000)
    two_opt_length = solver.tour_length(two_opt_tour)
    print(f"2-opt: {two_opt_length:.4f}")
    print(f"  Improvement: {((nn_length - two_opt_length) / nn_length * 100):.2f}%")
    
    # Apply Iterative Local Search starting from NN (not from 2-opt)
    print("\nTrying Iterative Local Search from NN tour (not from 2-opt)...")
    ils_from_nn = solver.iterative_local_search(nn_tour, max_iterations=50)
    ils_from_nn_length = solver.tour_length(ils_from_nn)
    print(f"ILS from NN: {ils_from_nn_length:.4f}")
    
    # Apply Iterative Local Search starting from 2-opt
    print("\nTrying Iterative Local Search from 2-opt tour...")
    ils_from_2opt = solver.iterative_local_search(two_opt_tour, max_iterations=50)
    ils_from_2opt_length = solver.tour_length(ils_from_2opt)
    print(f"ILS from 2-opt: {ils_from_2opt_length:.4f}")
    
    # Try multiple random starts
    print("\nTrying multiple random starts...")
    best_length = two_opt_length
    best_tour = two_opt_tour
    
    for restart in range(5):
        # Create random tour
        random_tour = list(range(100))
        random.shuffle(random_tour)
        
        # Apply ILS
        ils_tour = solver.iterative_local_search(random_tour, max_iterations=30)
        ils_length = solver.tour_length(ils_tour)
        
        print(f"  Restart {restart+1}: {ils_length:.4f}")
        
        if ils_length < best_length:
            best_length = ils_length
            best_tour = ils_tour
    
    print(f"\nBest found: {best_length:.4f}")
    if best_length < two_opt_length:
        improvement = (two_opt_length - best_length) / two_opt_length * 100
        print(f"✓ Improvement over 2-opt: {improvement:.2f}%")
    else:
        print("✗ No improvement over 2-opt")

def test_double_bridge_effectiveness():
    """Test if double-bridge helps escape local optima."""
    solver = EuclideanTSPIterativeLocalSearch(n=100, seed=42)
    
    # Get 2-opt tour (local optimum)
    nn_tour = solver.nearest_neighbor_tour()
    two_opt_tour = solver.two_opt_improvement(nn_tour, max_iterations=1000)
    two_opt_length = solver.tour_length(two_opt_tour)
    
    print(f"2-opt local optimum: {two_opt_length:.4f}")
    
    # Apply double-bridge kick
    kicked_tour = solver._double_bridge_kick(two_opt_tour)
    kicked_length = solver.tour_length(kicked_tour)
    print(f"After double-bridge: {kicked_length:.4f}")
    print(f"  Degradation: {((kicked_length - two_opt_length) / two_opt_length * 100):.2f}%")
    
    # Try to improve kicked tour with 2-opt
    improved_kicked = solver._aggressive_two_opt(kicked_tour, neighborhood_size=50)
    improved_length = solver.tour_length(improved_kicked)
    print(f"After re-optimizing: {improved_length:.4f}")
    
    if improved_length < two_opt_length:
        improvement = (two_opt_length - improved_length) / two_opt_length * 100
        print(f"✓ Found better solution! Improvement: {improvement:.2f}%")
        return True
    else:
        print("✗ Did not find better solution")
        return False

if __name__ == "__main__":
    print("=== Testing on Larger Instance ===\n")
    
    print("1. Testing on 100-city instance...")
    test_large_instance()
    print()
    
    print("\n2. Testing double-bridge effectiveness...")
    test_double_bridge_effectiveness()