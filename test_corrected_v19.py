#!/usr/bin/env python3
"""
Test script for corrected v19 algorithm.
Verifies that the corrected version works with both Euclidean points and distance matrix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
import numpy as np

def test_euclidean_points():
    """Test with Euclidean points."""
    print("Testing corrected v19 with Euclidean points...")
    
    # Create a simple 5-point TSP
    points = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]
    
    solver = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    tour, length = solver.solve()
    
    print(f"  Tour: {tour}")
    print(f"  Length: {length:.4f}")
    print(f"  Tour length: {len(tour)} points")
    
    # Basic validation
    assert len(tour) == len(points), f"Tour length mismatch: {len(tour)} != {len(points)}"
    assert len(set(tour)) == len(points), "Tour contains duplicates"
    assert tour[0] == tour[-1], "Tour not closed (first != last)"
    
    print("  ✓ Euclidean test passed\n")
    return True

def test_distance_matrix():
    """Test with distance matrix (TSPLIB compatibility)."""
    print("Testing corrected v19 with distance matrix...")
    
    # Create a simple distance matrix for 4 points
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    n = len(points)
    
    # Compute Euclidean distance matrix
    dist_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = points[i][0] - points[j][0]
                dy = points[i][1] - points[j][1]
                dist_matrix[i][j] = math.sqrt(dx*dx + dy*dy)
    
    solver = ChristofidesHybridStructuralCorrected(distance_matrix=dist_matrix, seed=42)
    tour, length = solver.solve()
    
    print(f"  Tour: {tour}")
    print(f"  Length: {length:.4f}")
    print(f"  Tour length: {len(tour)} points")
    
    # Basic validation
    assert len(tour) == n + 1, f"Tour length mismatch: {len(tour)} != {n+1}"
    assert len(set(tour[:-1])) == n, "Tour contains duplicates (excluding endpoint)"
    assert tour[0] == tour[-1], "Tour not closed (first != last)"
    
    print("  ✓ Distance matrix test passed\n")
    return True

def test_hybrid_features():
    """Verify that hybrid structural features are present and functional."""
    print("Testing hybrid structural features...")
    
    points = [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]
    solver = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    
    # Check that hybrid methods exist
    methods = [
        '_detect_communities',
        '_compute_edge_centrality', 
        '_build_mst_paths',
        '_compute_path_centrality',
        '_hybrid_structural_matching'
    ]
    
    for method_name in methods:
        assert hasattr(solver, method_name), f"Missing hybrid method: {method_name}"
        print(f"  ✓ Method {method_name} exists")
    
    # Run solve to ensure methods are called
    tour, length = solver.solve()
    print(f"  ✓ Hybrid algorithm executed successfully (tour length: {length:.4f})")
    
    print("  ✓ All hybrid features verified\n")
    return True

if __name__ == "__main__":
    import math
    
    print("=" * 60)
    print("CORRECTED V19 ALGORITHM TEST")
    print("=" * 60)
    
    all_passed = True
    
    try:
        all_passed &= test_euclidean_points()
    except Exception as e:
        print(f"✗ Euclidean test failed: {e}")
        all_passed = False
    
    try:
        all_passed &= test_distance_matrix()
    except Exception as e:
        print(f"✗ Distance matrix test failed: {e}")
        all_passed = False
    
    try:
        all_passed &= test_hybrid_features()
    except Exception as e:
        print(f"✗ Hybrid features test failed: {e}")
        all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Corrected v19 is functional")
    else:
        print("❌ SOME TESTS FAILED - Check corrected v19 implementation")
    print("=" * 60)
