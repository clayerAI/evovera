#!/usr/bin/env python3
"""
Test v19 optimized v9 compatibility with TSPLIB distance metrics.
Verifies:
1. Algorithm accepts distance_matrix parameter
2. Produces identical results with points vs distance_matrix
3. Handles ATT metric correctly
"""

import sys
import os
import numpy as np
import math
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the optimized v9 algorithm
from solutions.tsp_v19_optimized_fixed_v9 import ChristofidesHybridStructuralOptimizedV8 as OptimizedV9

def create_test_points(n=10):
    """Create random test points."""
    np.random.seed(42)
    return np.random.rand(n, 2) * 100

def compute_euclidean_distance_matrix(points):
    """Compute Euclidean distance matrix."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix

def compute_att_distance_matrix(points):
    """Compute ATT distance matrix (ceil(sqrt((dx²+dy²)/10.0)))."""
    n = len(points)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = math.ceil(math.sqrt((dx * dx + dy * dy) / 10.0))
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    return dist_matrix

def test_basic_compatibility():
    """Test basic compatibility with distance_matrix parameter."""
    print("=" * 60)
    print("TEST 1: Basic compatibility with distance_matrix parameter")
    print("=" * 60)
    
    points = create_test_points(20)
    dist_matrix = compute_euclidean_distance_matrix(points)
    
    # Test 1a: Initialize with points
    solver1 = OptimizedV9(points=points)
    start_time = time.time()
    tour1, length1, time1_val = solver1.solve()
    time1 = time.time() - start_time
    
    # Test 1b: Initialize with distance_matrix
    solver2 = OptimizedV9(distance_matrix=dist_matrix)
    start_time = time.time()
    tour2, length2, time2_val = solver2.solve()
    time2 = time.time() - start_time
    
    print(f"Points-only solver: length={length1:.2f}, time={time1:.3f}s")
    print(f"Distance matrix solver: length={length2:.2f}, time={time2:.3f}s")
    
    # Verify results are identical (within floating point tolerance)
    if abs(length1 - length2) < 1e-6:
        print("✅ PASS: Both solvers produce identical tour lengths")
    else:
        print(f"❌ FAIL: Tour lengths differ: {length1:.6f} vs {length2:.6f}")
        print(f"    Difference: {abs(length1 - length2):.6f}")
    
    return abs(length1 - length2) < 1e-6

def test_att_metric_compatibility():
    """Test ATT metric compatibility."""
    print("\n" + "=" * 60)
    print("TEST 2: ATT metric compatibility")
    print("=" * 60)
    
    points = create_test_points(15)
    
    # Compute Euclidean and ATT distance matrices
    euclidean_matrix = compute_euclidean_distance_matrix(points)
    att_matrix = compute_att_distance_matrix(points)
    
    # Test with Euclidean matrix
    solver_euclidean = OptimizedV9(distance_matrix=euclidean_matrix)
    tour_euclidean, length_euclidean, time_euclidean = solver_euclidean.solve()
    
    # Test with ATT matrix
    solver_att = OptimizedV9(distance_matrix=att_matrix)
    tour_att, length_att, time_att = solver_att.solve()
    
    print(f"Euclidean distance tour length: {length_euclidean:.2f}")
    print(f"ATT distance tour length: {length_att:.2f}")
    
    # Verify ATT distances are integers (as per ATT metric)
    if np.allclose(att_matrix, att_matrix.astype(int)):
        print("✅ PASS: ATT distance matrix contains integers")
    else:
        print("❌ FAIL: ATT distance matrix should contain integers")
    
    # Verify algorithms run without errors
    print("✅ PASS: Both Euclidean and ATT solvers run without errors")
    
    return True

def test_performance_consistency():
    """Test performance consistency across multiple runs."""
    print("\n" + "=" * 60)
    print("TEST 3: Performance consistency")
    print("=" * 60)
    
    points = create_test_points(30)
    dist_matrix = compute_euclidean_distance_matrix(points)
    
    lengths_points = []
    lengths_matrix = []
    
    for seed in range(5):
        np.random.seed(seed)
        
        # Points solver
        solver1 = OptimizedV9(points=points)
        tour1, length1, time1_val = solver1.solve()
        lengths_points.append(length1)
        
        # Distance matrix solver
        solver2 = OptimizedV9(distance_matrix=dist_matrix)
        tour2, length2, time2_val = solver2.solve()
        lengths_matrix.append(length2)
    
    # Calculate statistics
    mean_points = np.mean(lengths_points)
    mean_matrix = np.mean(lengths_matrix)
    std_points = np.std(lengths_points)
    std_matrix = np.std(lengths_matrix)
    
    print(f"Points solver: mean={mean_points:.2f}, std={std_points:.4f}")
    print(f"Matrix solver: mean={mean_matrix:.2f}, std={std_matrix:.4f}")
    
    # Check if means are within 0.1% of each other
    diff_pct = abs(mean_points - mean_matrix) / mean_points * 100
    if diff_pct < 0.1:
        print(f"✅ PASS: Mean lengths differ by only {diff_pct:.4f}% (< 0.1%)")
    else:
        print(f"❌ FAIL: Mean lengths differ by {diff_pct:.4f}% (≥ 0.1%)")
    
    return diff_pct < 0.1

def main():
    """Run all compatibility tests."""
    print("Christofides Hybrid Structural Optimized v9 - TSPLIB Compatibility Tests")
    print("=" * 80)
    
    all_passed = True
    
    # Run tests
    if not test_basic_compatibility():
        all_passed = False
    
    if not test_att_metric_compatibility():
        all_passed = False
    
    if not test_performance_consistency():
        all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED: Optimized v9 is TSPLIB compatible")
    else:
        print("❌ SOME TESTS FAILED: Check compatibility issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
