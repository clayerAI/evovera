#!/usr/bin/env python3
"""
TSP Algorithm Importer for Benchmarking
Imports all TSP algorithms from solutions directory for comprehensive multi-seed benchmarks.
"""

import sys
import os
import importlib.util
import numpy as np

# Add solutions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'solutions'))

# List of algorithm files to import (focus on key versions for benchmark)
ALGORITHM_FILES = [
    "tsp_v1_nearest_neighbor.py",          # Baseline: NN + 2-opt
    "tsp_v2_christofides_improved.py",     # Christofides baseline
    "tsp_v19_christofides_hybrid_structural.py",  # Latest version
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
print("Importing TSP algorithms for benchmarking...")
for alg_file in ALGORITHM_FILES:
    import_algorithm(alg_file)

print(f"\nSuccessfully imported {len(algorithms)} algorithms:")
for name in algorithms.keys():
    print(f"  - {name}")

# Convenience function to get algorithm by name
def get_algorithm(name):
    """Get algorithm function by name."""
    return algorithms.get(name)

# Test function to verify all algorithms work
def test_all_algorithms(n=10, seed=42):
    """Test all imported algorithms with a small instance."""
    print(f"\nTesting all algorithms with n={n}, seed={seed}...")
    np.random.seed(seed)
    points = np.random.rand(n, 2)
    
    results = {}
    for name, func in algorithms.items():
        try:
            tour, length = func(points)
            results[name] = {
                'length': length,
                'tour_length': len(tour),
                'success': True
            }
            print(f"  ✓ {name}: length={length:.4f}, tour_len={len(tour)}")
        except Exception as e:
            results[name] = {
                'success': False,
                'error': str(e)
            }
            print(f"  ✗ {name}: {e}")
    
    return results

if __name__ == "__main__":
    # Run test when executed directly
    test_all_algorithms()
