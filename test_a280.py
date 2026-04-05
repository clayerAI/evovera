#!/usr/bin/env python3
"""Test v11 on a280 instance."""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver

def main():
    print("Testing v11 on a280...")
    
    parser = TSPLIBParser("data/tsplib/a280.tsp")
    if not parser.parse():
        print("Failed to parse a280")
        return
    
    distance_matrix = parser.get_distance_matrix()
    n = distance_matrix.shape[0]
    
    print(f"a280: n={n}, matrix shape={distance_matrix.shape}")
    print("Running solver (this may take a while)...")
    
    solver = V11Solver(distance_matrix=distance_matrix)
    
    start = time.time()
    try:
        tour, length, runtime = solver.solve()
        elapsed = time.time() - start
        
        print(f"Success! Length={length}, runtime={runtime}, elapsed={elapsed}")
        print(f"Tour length: {len(tour)}")
        
        # Quick validation
        if len(tour) == n + 1 and tour[0] == tour[-1]:
            unique = len(set(tour[:-1]))
            print(f"Validation: {unique} unique nodes (expected {n})")
            if unique == n:
                print("✅ Valid Hamiltonian cycle")
                
                # Compute gap (optimal=2579)
                optimal = 2579
                gap = ((length - optimal) / optimal) * 100
                print(f"Gap from optimal ({optimal}): {gap:.2f}%")
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
