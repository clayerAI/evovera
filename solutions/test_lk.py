#!/usr/bin/env python3
"""Test Iterative Local Search implementation"""

import numpy as np
import math
import random
from typing import List
import sys
sys.path.append('.')

from tsp_v3_iterative_local_search import EuclideanTSPIterativeLocalSearch

def test_aggressive_two_opt():
    """Test if aggressive 2-opt finds improvements."""
    solver = EuclideanTSPIterativeLocalSearch(n=20, seed=42)
    
    # Create a simple tour
    tour = list(range(20))
    random.shuffle(tour)
    
    print("Initial tour length:", solver.tour_length(tour))
    
    # Apply aggressive 2-opt
    improved_tour = solver._aggressive_two_opt(tour, neighborhood_size=10)
    improved_length = solver.tour_length(improved_tour)
    
    print("After aggressive 2-opt:", improved_length)
    
    # Apply regular 2-opt
    regular_improved = solver.two_opt_improvement(tour, max_iterations=1000)
    regular_length = solver.tour_length(regular_improved)
    
    print("After regular 2-opt:", regular_length)
    
    return improved_length < solver.tour_length(tour)

def test_double_bridge():
    """Test double-bridge kick."""
    solver = EuclideanTSPIterativeLocalSearch(n=20, seed=42)
    
    tour = list(range(20))
    print("Original tour:", tour[:10], "...")
    
    kicked = solver._double_bridge_kick(tour)
    print("After double-bridge:", kicked[:10], "...")
    
    # Check that it's a valid permutation
    assert sorted(kicked) == list(range(20)), "Double-bridge produced invalid tour"
    print("✓ Double-bridge produces valid tour")

def test_iterative_local_search():
    """Test full Lin-Kernighan."""
    solver = EuclideanTSPLinKernighan(n=50, seed=42)
    
    # Get nearest neighbor tour
    nn_tour = solver.nearest_neighbor_tour()
    nn_length = solver.tour_length(nn_tour)
    print("Nearest neighbor length:", nn_length)
    
    # Apply 2-opt
    two_opt_tour = solver.two_opt_improvement(nn_tour, max_iterations=1000)
    two_opt_length = solver.tour_length(two_opt_tour)
    print("2-opt length:", two_opt_length)
    
    # Apply Iterative Local Search
    ils_tour = solver.iterative_local_search(two_opt_tour, max_iterations=20)
    ils_length = solver.tour_length(ils_tour)
    print("Iterative Local Search length:", ils_length)
    
    if ils_length < two_opt_length:
        improvement = (two_opt_length - ils_length) / two_opt_length * 100
        print(f"✓ Iterative Local Search improved by {improvement:.2f}%")
        return True
    else:
        print("✗ Iterative Local Search did not improve")
        return False

if __name__ == "__main__":
    print("=== Testing Lin-Kernighan Implementation ===\n")
    
    print("1. Testing aggressive 2-opt...")
    test_aggressive_two_opt()
    print()
    
    print("2. Testing double-bridge kick...")
    test_double_bridge()
    print()
    
    print("3. Testing full Iterative Local Search...")
    success = test_iterative_local_search()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Lin-Kernighan needs improvement")