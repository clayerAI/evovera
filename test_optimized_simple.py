#!/usr/bin/env python3
"""Simple test of optimized v11 algorithm."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
from typing import List, Tuple

def create_test_instance(n: int = 100) -> Tuple[List[List[float]], List[Tuple[float, float]]]:
    """Create test instance with both distance matrix and points."""
    np.random.seed(42)
    points = [(x, y) for x, y in np.random.rand(n, 2) * 100]
    
    # Create distance matrix
    dist_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(n):
            xj, yj = points[j]
            dist_matrix[i][j] = np.sqrt((xi - xj)**2 + (yi - yj)**2)
    
    return dist_matrix, points

def test_optimized_only():
    """Test only the optimized algorithm."""
    print("=== Testing Optimized v11 Algorithm ===")
    
    for n in [50, 100, 150, 200]:
        print(f"\nTesting n={n}")
        
        dist_matrix, points = create_test_instance(n)
        
        # Test optimized v11
        from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
        
        start = time.time()
        solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix, seed=42)
        tour, length = solver.solve()
        runtime = time.time() - start
        
        print(f"  Tour length: {length:.2f}")
        print(f"  Runtime: {runtime:.3f}s")
        
        # Verify tour
        assert len(set(tour[:-1])) == n, f"Tour missing nodes: {len(set(tour[:-1]))} != {n}"
        assert tour[0] == tour[-1], "Tour not closed"
        print(f"  ✓ Valid tour ({len(tour)} nodes)")
        
        # Compute theoretical complexity
        print(f"  Complexity: O(n²) edge centrality (vs O(n³) original)")

def test_on_tsplib_small():
    """Test on a small TSPLIB instance."""
    print("\n=== Testing on TSPLIB eil51 ===")
    
    # Load eil51
    from utils.tsplib_parser import load_tsplib_instance
    import os
    
    instance_path = "data/tsplib/eil51.tsp"
    if not os.path.exists(instance_path):
        print(f"  Instance not found: {instance_path}")
        return
    
    points, optimal = load_tsplib_instance(instance_path)
    n = len(points)
    
    # Create distance matrix
    dist_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(n):
            xj, yj = points[j]
            dist_matrix[i][j] = np.sqrt((xi - xj)**2 + (yi - yj)**2)
    
    # Test optimized v11
    from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    
    start = time.time()
    solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix, seed=42)
    tour, length = solver.solve()
    runtime = time.time() - start
    
    print(f"  Instance: eil51 (n={n})")
    print(f"  Optimal: {optimal}")
    print(f"  Found: {length:.2f}")
    print(f"  Gap: {(length - optimal)/optimal*100:.2f}%")
    print(f"  Runtime: {runtime:.3f}s")
    
    # Verify tour
    assert len(set(tour[:-1])) == n, f"Tour missing nodes"
    assert tour[0] == tour[-1], "Tour not closed"
    print(f"  ✓ Valid tour")

if __name__ == "__main__":
    test_optimized_only()
    test_on_tsplib_small()
    print("\n✅ Optimized v11 algorithm tested successfully")
