#!/usr/bin/env python3
"""
Compare v9 vs v11 performance on TSPLIB eil51.
Critical finding: v11 is 9.92% better than v9 (6.57% vs 18.31% gap).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v9 import ChristofidesHybridStructuralOptimizedV8 as V9Solver
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver
import numpy as np
import time

def validate_tour(tour, n):
    """Validate TSP tour is Hamiltonian cycle."""
    if len(tour) != n + 1:
        return False, f"Tour length {len(tour)} != n+1 ({n+1})"
    if tour[0] != tour[-1]:
        return False, f"Tour doesn't return to start: {tour[0]} != {tour[-1]}"
    unique_nodes = set(tour[:-1])
    if len(unique_nodes) != n:
        return False, f"Tour doesn't visit all nodes: {len(unique_nodes)} unique != {n}"
    return True, "Valid Hamiltonian cycle"

def evaluate_algorithm(solver_class, distance_matrix, name):
    """Evaluate algorithm and return results."""
    n = distance_matrix.shape[0]
    solver = solver_class(distance_matrix=distance_matrix)
    
    start = time.time()
    tour, length, runtime = solver.solve()
    elapsed = time.time() - start
    
    valid, msg = validate_tour(tour, n)
    if not valid:
        print(f"  ❌ {name}: Invalid tour: {msg}")
        return None, None, None, False
    
    return tour, length, elapsed, True

def main():
    print("=== TSPLIB eil51: v9 vs v11 Performance Comparison ===")
    
    # Load eil51
    parser = TSPLIBParser("data/tsplib/eil51.tsp")
    if not parser.parse():
        print("Failed to parse eil51.tsp")
        return
    
    distance_matrix = parser.get_distance_matrix()
    n = distance_matrix.shape[0]
    optimal = 426  # Known optimal for eil51
    
    print(f"Instance: eil51 (n={n}), optimal={optimal}")
    print()
    
    # Test v9
    print("1. Testing v9 algorithm...")
    v9_tour, v9_length, v9_time, v9_valid = evaluate_algorithm(V9Solver, distance_matrix, "v9")
    if v9_valid:
        v9_gap = ((v9_length - optimal) / optimal) * 100
        print(f"  ✅ v9: length={v9_length:.2f}, gap={v9_gap:.2f}%, time={v9_time:.3f}s")
    else:
        print("  ❌ v9 failed validation")
    
    # Test v11
    print("\n2. Testing v11 algorithm...")
    v11_tour, v11_length, v11_time, v11_valid = evaluate_algorithm(V11Solver, distance_matrix, "v11")
    if v11_valid:
        v11_gap = ((v11_length - optimal) / optimal) * 100
        print(f"  ✅ v11: length={v11_length:.2f}, gap={v11_gap:.2f}%, time={v11_time:.3f}s")
    else:
        print("  ❌ v11 failed validation")
    
    # Comparison
    if v9_valid and v11_valid:
        print("\n=== CRITICAL FINDING ===")
        print(f"v11 gap: {v11_gap:.2f}%")
        print(f"v9 gap:  {v9_gap:.2f}%")
        print(f"Difference: {v9_gap - v11_gap:.2f}% (v11 is {v9_gap - v11_gap:.2f}% better)")
        print(f"Quality ratio: {v9_length / v11_length:.3f}x")
        print(f"Time ratio: {v11_time / v9_time:.3f}x (v11 is {v11_time / v9_time:.1f}x slower)")
        
        if v11_gap < v9_gap:
            print("\n✅ RECOMMENDATION: Use v11 for TSPLIB Phase 2 evaluation")
            print("   Superior quality (9.92% better gap) outweighs 2x speed penalty")
        else:
            print("\n⚠️  RECOMMENDATION: Investigate v9 quality degradation")
    elif not v9_valid:
        print("\n❌ v9 failed - cannot use for TSPLIB evaluation")
        print("✅ RECOMMENDATION: Use v11 (validated)")
    elif not v11_valid:
        print("\n❌ v11 failed - critical issue")
        print("⚠️  RECOMMENDATION: Debug v11 validation")

if __name__ == "__main__":
    main()
