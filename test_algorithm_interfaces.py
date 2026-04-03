#!/usr/bin/env python3
"""
Test all TSP algorithm interfaces to ensure they have standard solve_tsp function.
"""

import sys
import os
sys.path.append('.')

import numpy as np

# List of main algorithm files to test (based on strategy document)
algorithms_to_test = [
    ('v1_nearest_neighbor', 'tsp_v1_nearest_neighbor'),
    ('v2_christofides', 'tsp_v2_christofides'),
    ('v3_iterative_local_search', 'tsp_v3_iterative_local_search'),
    ('v4_nn_ils_hybrid', 'tsp_v4_nn_ils_hybrid'),
    ('v5_christofides_ils_hybrid', 'tsp_v5_christofides_ils_hybrid'),
    ('v6_multi_start_adaptive_2opt', 'tsp_v6_multi_start_adaptive_2opt'),
    ('v7_christofides_tabu_hybrid', 'tsp_v7_christofides_tabu_hybrid'),
    ('v8_christofides_ils_hybrid_fixed', 'tsp_v8_christofides_ils_hybrid_fixed'),
    ('v9_nn_ga_christofides_crossover', 'tsp_v9_nn_ga_christofides_crossover'),
    ('v10_christofides_mst_ils_memory', 'tsp_v10_christofides_mst_ils_memory'),
    ('v11_nn_ils_adaptive_memory', 'tsp_v11_nn_ils_adaptive_memory'),
    ('v12_nn_fast_ils', 'tsp_v12_nn_fast_ils'),
    ('v13_nn_efficient_ils', 'tsp_v13_nn_efficient_ils'),
    ('v14_christofides_adaptive_matching', 'tsp_v14_christofides_adaptive_matching'),
    ('v15_algorithmic_ecology', 'tsp_v15_algorithmic_ecology'),
]

print("Testing algorithm interfaces...")
print("=" * 80)

# Create test instance
np.random.seed(42)
points = np.random.rand(10, 2)

working_algorithms = []
broken_algorithms = []

for name, module_name in algorithms_to_test:
    try:
        module = __import__(f'solutions.{module_name}', fromlist=['solve_tsp'])
        
        if hasattr(module, 'solve_tsp'):
            func = module.solve_tsp
            
            # Test the function
            try:
                result = func(points)
                
                if isinstance(result, tuple) and len(result) == 2:
                    tour, length = result
                    
                    # Basic validation
                    if len(tour) == len(points) + 1 or len(tour) == len(points):
                        if isinstance(length, (int, float)) and length > 0:
                            working_algorithms.append((name, module_name))
                            print(f"✅ {name}: OK - returns (tour, length) with length={length:.4f}")
                        else:
                            broken_algorithms.append((name, module_name, f"Invalid length: {length}"))
                            print(f"❌ {name}: ERROR - invalid length: {length}")
                    else:
                        broken_algorithms.append((name, module_name, f"Invalid tour length: {len(tour)}"))
                        print(f"❌ {name}: ERROR - invalid tour length: {len(tour)}")
                else:
                    broken_algorithms.append((name, module_name, f"Returns {type(result)} instead of tuple"))
                    print(f"❌ {name}: ERROR - returns {type(result)} instead of (tour, length)")
                    
            except Exception as e:
                broken_algorithms.append((name, module_name, f"Runtime error: {e}"))
                print(f"❌ {name}: ERROR - runtime error: {e}")
        else:
            broken_algorithms.append((name, module_name, "No solve_tsp function"))
            print(f"❌ {name}: ERROR - no solve_tsp function found")
            
    except ImportError as e:
        broken_algorithms.append((name, module_name, f"Import error: {e}"))
        print(f"❌ {name}: ERROR - import failed: {e}")
    except Exception as e:
        broken_algorithms.append((name, module_name, f"Unexpected error: {e}"))
        print(f"❌ {name}: ERROR - unexpected: {e}")

print("\n" + "=" * 80)
print(f"Summary: {len(working_algorithms)}/{len(algorithms_to_test)} algorithms working")
print(f"Broken: {len(broken_algorithms)}/{len(algorithms_to_test)} algorithms need fixing")

if broken_algorithms:
    print("\nAlgorithms needing fixes:")
    for name, module_name, error in broken_algorithms:
        print(f"  - {name} ({module_name}.py): {error}")

# Save results for reference
with open('algorithm_interface_test_results.txt', 'w') as f:
    f.write(f"Test completed: {len(working_algorithms)}/{len(algorithms_to_test)} algorithms working\n")
    f.write(f"Broken algorithms: {len(broken_algorithms)}\n\n")
    
    if broken_algorithms:
        f.write("Algorithms needing fixes:\n")
        for name, module_name, error in broken_algorithms:
            f.write(f"  - {name} ({module_name}.py): {error}\n")