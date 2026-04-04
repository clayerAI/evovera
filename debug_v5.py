#!/usr/bin/env python3
import numpy as np
import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v5_christofides_ils_hybrid_simple import christofides_ils_hybrid_simple

# Very small test
np.random.seed(42)
points = np.random.rand(5, 2)

print("Testing christofides_ils_hybrid_simple with n=5")
print(f"Points shape: {points.shape}")

try:
    tour, length, stats = christofides_ils_hybrid_simple(
        points, 
        max_iterations=2,  # Very small
        stagnation_threshold=0.0005,
        stagnation_window=2,
        initial_perturbation_strength=1
    )
    print(f"Success! Tour length: {len(tour)}, Total length: {length}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Let's debug step by step
    print("\n=== Step-by-step debug ===")
    
    # Import the functions we need
    from tsp_v5_christofides_ils_hybrid_simple import (
        create_distance_matrix, 
        tour_length,
        euclidean_distance
    )
    from tsp_v2_christofides import solve_tsp as christofides_solve
    
    # Create distance matrix
    dist_matrix = create_distance_matrix(points)
    print(f"Distance matrix shape: {dist_matrix.shape}")
    
    # Convert points to list
    points_list = [(float(p[0]), float(p[1])) for p in points]
    print(f"Points list length: {len(points_list)}")
    
    # Get Christofides tour
    christofides_tour, christofides_length = christofides_solve(points_list)
    print(f"Christofides tour: {christofides_tour}")
    print(f"Christofides tour length (vertices): {len(christofides_tour)}")
    print(f"Christofides total length: {christofides_length}")
    
    # Try to compute tour length
    print(f"\nTrying tour_length function...")
    print(f"Tour[0]: {christofides_tour[0]}, type: {type(christofides_tour[0])}")
    print(f"Tour[1]: {christofides_tour[1]}, type: {type(christofides_tour[1])}")
    
    # Try direct access
    try:
        val = dist_matrix[christofides_tour[0], christofides_tour[1]]
        print(f"dist_matrix[{christofides_tour[0]}, {christofides_tour[1]}] = {val}")
    except Exception as e2:
        print(f"Direct access error: {e2}")
        
    # Check if all indices are valid
    print(f"\nChecking all tour indices...")
    for i, vertex in enumerate(christofides_tour):
        if vertex < 0 or vertex >= len(points):
            print(f"  Invalid vertex at position {i}: {vertex} (n={len(points)})")
        else:
            print(f"  Position {i}: vertex {vertex} OK")