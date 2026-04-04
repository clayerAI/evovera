#!/usr/bin/env python3
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing fixed algorithms
try:
    from tsp_algorithms_fixed import algorithms
    print("✓ Successfully imported fixed algorithms")
    
    # Test with a simple distance matrix
    test_points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    test_dist_matrix = np.array([
        [0, 1, 1, np.sqrt(2)],
        [1, 0, np.sqrt(2), 1],
        [1, np.sqrt(2), 0, 1],
        [np.sqrt(2), 1, 1, 0]
    ])
    
    for name, func in algorithms.items():
        print(f"\nTesting {name}...")
        try:
            # Test with distance matrix
            tour = func(test_points, distance_matrix=test_dist_matrix)
            print(f"  Tour type: {type(tour)}")
            print(f"  Tour value: {tour}")
            print(f"  Tour length: {len(tour)}")
            
            if isinstance(tour, (list, np.ndarray)):
                # Try to calculate tour length
                try:
                    tour_length = 0
                    n = len(tour)
                    for i in range(n):
                        tour_length += test_dist_matrix[int(tour[i]), int(tour[(i + 1) % n])]
                    print(f"  Tour length: {tour_length:.2f}")
                except Exception as e:
                    print(f"  Error calculating length: {e}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"✗ Failed to import fixed algorithms: {e}")
