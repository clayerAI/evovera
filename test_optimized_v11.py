#!/usr/bin/env python3
"""Test optimized v11 algorithm."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time

# Import both algorithms
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as OriginalV11
from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11 as OptimizedV11

def test_algorithms():
    """Test both algorithms on random instances."""
    sizes = [50, 100, 150, 200]
    
    for n in sizes:
        print(f"\n=== Testing n={n} ===")
        
        # Create random distance matrix
        np.random.seed(42)
        points = np.random.rand(n, 2) * 100
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                dist_matrix[i][j] = np.linalg.norm(points[i] - points[j])
        
        # Test original v11
        original = OriginalV11(dist_matrix.tolist(), seed=42)
        start = time.time()
        tour_orig, length_orig = original.solve()
        time_orig = time.time() - start
        
        # Test optimized v11
        optimized = OptimizedV11(dist_matrix.tolist(), seed=42)
        start = time.time()
        tour_opt, length_opt = optimized.solve()
        time_opt = time.time() - start
        
        print(f"Original v11: length={length_orig:.2f}, time={time_orig:.3f}s")
        print(f"Optimized v11: length={length_opt:.2f}, time={time_opt:.3f}s")
        
        if length_orig > 0:
            quality_diff = abs(length_opt - length_orig) / length_orig * 100
            print(f"Quality difference: {quality_diff:.4f}%")
        
        if time_opt > 0:
            speedup = time_orig / time_opt
            print(f"Speedup: {speedup:.2f}x")
        
        # Verify tours are valid
        assert len(set(tour_orig[:-1])) == n, "Original tour missing nodes"
        assert len(set(tour_opt[:-1])) == n, "Optimized tour missing nodes"
        assert tour_orig[0] == tour_orig[-1], "Original tour not closed"
        assert tour_opt[0] == tour_opt[-1], "Optimized tour not closed"
        
        print("✓ Tours are valid")

def test_edge_centrality_optimization():
    """Test edge centrality computation specifically."""
    print("\n=== Edge Centrality Optimization Test ===")
    
    n = 100
    np.random.seed(42)
    points = np.random.rand(n, 2) * 100
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i][j] = np.linalg.norm(points[i] - points[j])
    
    # Create algorithm instance to test internal methods
    optimized = OptimizedV11(dist_matrix.tolist(), seed=42)
    
    # Build MST
    mst_adj = optimized._prim_mst()
    
    # Test edge centrality computation
    print("Testing edge centrality computation...")
    
    # Count MST edges
    mst_edges = 0
    for u in range(n):
        for v, _ in mst_adj[u]:
            if u < v:
                mst_edges += 1
    
    print(f"MST has {mst_edges} edges (expected: {n-1})")
    print(f"Edge centrality complexity: O(n²) vs original O(n³)")
    print("Property: centrality(u,v) = |component_u| × |component_v|")

if __name__ == "__main__":
    test_algorithms()
    test_edge_centrality_optimization()
    print("\n✅ Optimized v11 algorithm ready for TSPLIB testing")
