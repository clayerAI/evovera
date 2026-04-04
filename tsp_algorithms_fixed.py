#!/usr/bin/env python3
"""
TSP Algorithm Importer for TSPLIB Evaluation - FIXED VERSION
Imports TSP algorithms with distance matrix support for TSPLIB compatibility.
"""

import sys
import os
import importlib.util
import numpy as np

# Add solutions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))

# List of FIXED algorithm files to import
ALGORITHM_FILES = [
    "tsp_v1_nearest_neighbor_fixed.py",          # Baseline: NN + 2-opt (FIXED)
    "tsp_v2_christofides_improved_fixed.py",     # Christofides baseline (FIXED)
    "tsp_v19_christofides_hybrid_structural_fixed.py",  # Latest version (FIXED)
]

# Dictionary to store algorithm functions
algorithms = {}

def import_algorithm(filename):
    """Import a single algorithm from solutions directory."""
    try:
        filepath = os.path.join('solutions', filename)
        
        # Create module spec
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        
        # Execute the module
        spec.loader.exec_module(module)
        
        # Get the solve_tsp function
        if hasattr(module, 'solve_tsp'):
            algorithm_name = filename[:-3]  # Remove .py extension
            algorithms[algorithm_name] = module.solve_tsp
            print(f"✓ Imported {algorithm_name}")
            return True
        else:
            print(f"✗ No solve_tsp function in {filename}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to import {filename}: {e}")
        return False

# Import all algorithms
print("=" * 80)
print("IMPORTING FIXED TSP ALGORITHMS FOR TSPLIB COMPATIBILITY")
print("=" * 80)

for filename in ALGORITHM_FILES:
    import_algorithm(filename)

print(f"\n✅ Successfully imported {len(algorithms)} algorithms:")
for name in algorithms.keys():
    print(f"  - {name}")

# Test function to verify algorithms work with distance matrices
def test_algorithms_with_distance_matrix():
    """Test that algorithms accept distance matrix parameter."""
    print("\n" + "=" * 80)
    print("TESTING ALGORITHMS WITH DISTANCE MATRIX SUPPORT")
    print("=" * 80)
    
    # Create simple test points
    points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    
    # Create custom distance matrix (not Euclidean)
    n = len(points)
    custom_dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            custom_dist[i, j] = abs(i - j) * 10  # Simple linear distance
    
    for name, solve_func in algorithms.items():
        print(f"\n🔍 Testing {name}:")
        
        # Test with points only (Euclidean)
        try:
            tour1, length1 = solve_func(points)
            print(f"  ✓ Works with points: length={length1:.2f}")
        except Exception as e:
            print(f"  ✗ Failed with points: {e}")
        
        # Test with distance matrix
        try:
            tour2, length2 = solve_func(points, distance_matrix=custom_dist)
            print(f"  ✓ Works with distance matrix: length={length2:.2f}")
            
            # Verify different results (should be different due to custom distances)
            if abs(length1 - length2) > 0.1:
                print(f"  ✓ Correctly uses distance matrix (different lengths)")
            else:
                print(f"  ⚠️ Same length - may not be using distance matrix")
                
        except TypeError as e:
            if "distance_matrix" in str(e):
                print(f"  ✗ Does not accept distance_matrix parameter")
            else:
                print(f"  ✗ Error: {e}")
        except Exception as e:
            print(f"  ✗ Failed with distance matrix: {e}")

if __name__ == "__main__":
    test_algorithms_with_distance_matrix()