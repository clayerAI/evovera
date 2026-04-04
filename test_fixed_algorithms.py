#!/usr/bin/env python3
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test importing fixed algorithms
try:
    from tsp_algorithms_fixed import algorithms
    print("✓ Successfully imported fixed algorithms")
    print(f"Available algorithms: {list(algorithms.keys())}")
    
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
            print(f"  ✓ Generated tour of length {len(tour)}")
            
            # Calculate tour length using distance matrix
            tour_length = 0
            n = len(tour)
            for i in range(n):
                tour_length += test_dist_matrix[tour[i], tour[(i + 1) % n]]
            print(f"  Tour length: {tour_length:.2f}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
except Exception as e:
    print(f"✗ Failed to import fixed algorithms: {e}")
    import traceback
    traceback.print_exc()
