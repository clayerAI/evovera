#!/usr/bin/env python3
"""Test v11 on a single instance to debug performance."""

import sys
import os
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver

def main():
    print("Testing v11 on eil51...")
    
    parser = TSPLIBParser("data/tsplib/eil51.tsp")
    if not parser.parse():
        print("Failed to parse")
        return
    
    distance_matrix = parser.get_distance_matrix()
    n = distance_matrix.shape[0]
    
    print(f"n={n}, matrix shape={distance_matrix.shape}")
    
    # Test with timeout
    solver = V11Solver(distance_matrix=distance_matrix)
    
    start = time.time()
    try:
        tour, length, runtime = solver.solve()
        elapsed = time.time() - start
        
        print(f"Success! Length={length}, runtime={runtime}, elapsed={elapsed}")
        print(f"Tour length: {len(tour)}")
        print(f"First 10 nodes: {tour[:10]}")
        print(f"Last 10 nodes: {tour[-10:]}")
        
        # Validate
        if len(tour) == n + 1 and tour[0] == tour[-1]:
            unique = len(set(tour[:-1]))
            print(f"Validation: {unique} unique nodes (expected {n})")
            if unique == n:
                print("✅ Valid Hamiltonian cycle")
            else:
                print("❌ Invalid tour")
        else:
            print("❌ Invalid tour structure")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
