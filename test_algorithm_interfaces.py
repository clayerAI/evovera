#!/usr/bin/env python3
"""
Test all TSP algorithm interfaces for consistency.
Checks that all algorithms have solve_tsp(points) function returning (tour, length).
"""

import sys
import os
import importlib.util
import numpy as np

# List of all algorithm files
ALGORITHM_FILES = [
    "tsp_v1_nearest_neighbor.py",
    "tsp_v2_christofides_improved.py", 
    "tsp_v4_nn_ils_hybrid.py",
    "tsp_v5_christofides_ils_hybrid.py",  # Use complete version instead of simple
    "tsp_v6_multi_start_adaptive_2opt.py",
    "tsp_v7_christofides_tabu_hybrid.py",
    "tsp_v8_christofides_ils_hybrid_fixed.py",
    "tsp_v9_nn_ga_christofides_crossover.py",
    "tsp_v10_christofides_mst_ils_memory.py",
    "tsp_v11_nn_ils_adaptive_memory.py",
    "tsp_v12_nn_fast_ils.py",
    "tsp_v13_nn_efficient_ils.py",
    "tsp_v14_christofides_adaptive_matching.py",
    "tsp_v15_algorithmic_ecology.py",
    "tsp_v16_christofides_path_centrality.py",
    "tsp_v17_christofides_learning_matching.py",
    "tsp_v18_christofides_community_detection.py",
    "tsp_v19_christofides_hybrid_structural.py",
]

def test_algorithm_interface(filename):
    """Test if an algorithm has the correct solve_tsp interface."""
    print(f"\nTesting {filename}...")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"  ❌ File not found: {filename}")
        return False
    
    # Read file to check for solve_tsp function
    with open(filename, 'r') as f:
        content = f.read()
    
    # Check for solve_tsp function
    if "def solve_tsp" not in content:
        print(f"  ❌ No solve_tsp function found")
        
        # Check if it's a class-based implementation
        if "class " in content and "def solve(" in content:
            print(f"  ⚠️  Has class with solve() method, needs wrapper")
        return False
    
    # Try to import and test the function
    try:
        # Create a module spec
        spec = importlib.util.spec_from_file_location("module", filename)
        module = importlib.util.module_from_spec(spec)
        
        # Execute the module
        spec.loader.exec_module(module)
        
        # Check if solve_tsp exists in module
        if not hasattr(module, 'solve_tsp'):
            print(f"  ❌ solve_tsp not found in module namespace")
            return False
        
        # Test with small dataset
        n = 10
        points = np.random.rand(n, 2)
        
        # Call solve_tsp
        result = module.solve_tsp(points)
        
        # Check return type
        if not isinstance(result, tuple) or len(result) != 2:
            print(f"  ❌ solve_tsp should return (tour, length) tuple, got {type(result)}")
            return False
        
        tour, length = result
        
        # Check tour
        if not isinstance(tour, list):
            print(f"  ❌ tour should be list, got {type(tour)}")
            return False
        
        # TSP tours can be length n (distinct vertices) or n+1 (returns to start)
        if len(tour) not in [n, n + 1]:
            print(f"  ❌ tour length should be {n} or {n+1}, got {len(tour)}")
            return False
        
        # Check that tour contains all vertices (handle n+1 case where last vertex repeats first)
        tour_vertices = set(tour[:n])  # Take first n vertices
        if tour_vertices != set(range(n)):
            print(f"  ❌ tour doesn't contain all vertices: {tour_vertices} vs {set(range(n))}")
            return False
        
        # Check length is numeric
        if not isinstance(length, (int, float)):
            print(f"  ❌ length should be numeric, got {type(length)}")
            return False
        
        print(f"  ✅ Interface correct: solve_tsp(points) -> (tour, length)")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing interface: {e}")
        return False

def main():
    print("Testing TSP algorithm interfaces for consistency")
    print("=" * 60)
    
    # Change to solutions directory
    os.chdir("/workspace/evovera/solutions")
    
    results = {}
    for filename in ALGORITHM_FILES:
        success = test_algorithm_interface(filename)
        results[filename] = success
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total algorithms: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\nFailed algorithms:")
        for filename, success in results.items():
            if not success:
                print(f"  - {filename}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())