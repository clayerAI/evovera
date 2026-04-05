#!/usr/bin/env python3
"""
Simple verification of v19 optimized v9 vs original v19 on small test instances.
"""

import sys
import os
import numpy as np
import time
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalV19
from solutions.tsp_v19_optimized_fixed_v9 import ChristofidesHybridStructuralOptimizedV8 as OptimizedV9

def create_test_instance(n=50):
    """Create a test instance with known properties."""
    np.random.seed(42)
    points = np.random.rand(n, 2) * 100
    
    # Compute Euclidean distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    return points, dist_matrix

def test_algorithm_equivalence(n=50, num_seeds=5):
    """Test that both algorithms produce identical results."""
    print(f"Testing algorithm equivalence (n={n}, seeds={num_seeds})")
    print("=" * 60)
    
    points, dist_matrix = create_test_instance(n)
    
    all_identical = True
    results = []
    
    for seed in range(num_seeds):
        np.random.seed(seed)
        
        # Test original v19
        start_time = time.time()
        solver_original = OriginalV19(distance_matrix=dist_matrix, seed=seed)
        tour_original, length_original, _ = solver_original.solve()
        time_original = time.time() - start_time
        
        # Test optimized v9
        start_time = time.time()
        solver_optimized = OptimizedV9(distance_matrix=dist_matrix)
        tour_optimized, length_optimized, _ = solver_optimized.solve()
        time_optimized = time.time() - start_time
        
        # Check if results are identical
        identical = abs(length_original - length_optimized) < 1e-6
        diff_pct = abs(length_original - length_optimized) / length_original * 100
        
        results.append({
            "seed": seed,
            "original_length": length_original,
            "optimized_length": length_optimized,
            "identical": identical,
            "diff_pct": diff_pct,
            "time_original": time_original,
            "time_optimized": time_optimized
        })
        
        status = "✅" if identical else "❌"
        print(f"Seed {seed}: {status} Original={length_original:.2f}, "
              f"Optimized={length_optimized:.2f}, Diff={diff_pct:.6f}%, "
              f"Time: {time_original:.3f}s → {time_optimized:.3f}s ({time_original/time_optimized:.1f}x)")
        
        if not identical:
            all_identical = False
    
    # Calculate statistics
    diffs = [r["diff_pct"] for r in results]
    times_original = [r["time_original"] for r in results]
    times_optimized = [r["time_optimized"] for r in results]
    
    print(f"\nSummary:")
    print(f"  All results identical: {'✅ YES' if all_identical else '❌ NO'}")
    print(f"  Max difference: {max(diffs):.6f}%")
    print(f"  Mean time - Original: {np.mean(times_original):.3f}s")
    print(f"  Mean time - Optimized: {np.mean(times_optimized):.3f}s")
    print(f"  Average speedup: {np.mean(times_original)/np.mean(times_optimized):.2f}x")
    
    return all_identical, results

def test_att_metric():
    """Test ATT metric compatibility."""
    print("\n" + "=" * 60)
    print("Testing ATT metric compatibility")
    print("=" * 60)
    
    # Create test points
    np.random.seed(42)
    n = 30
    points = np.random.rand(n, 2) * 100
    
    # Compute Euclidean distance matrix
    euclidean_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = math.sqrt(dx * dx + dy * dy)
            euclidean_matrix[i][j] = dist
            euclidean_matrix[j][i] = dist
    
    # Compute ATT distance matrix
    att_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = math.ceil(math.sqrt((dx * dx + dy * dy) / 10.0))
            att_matrix[i][j] = dist
            att_matrix[j][i] = dist
    
    # Test both algorithms with ATT matrix
    print("Testing with ATT distance matrix:")
    
    # Original v19
    solver_original = OriginalV19(distance_matrix=att_matrix, seed=42)
    tour_original, length_original, _ = solver_original.solve()
    
    # Optimized v9
    solver_optimized = OptimizedV9(distance_matrix=att_matrix)
    tour_optimized, length_optimized, _ = solver_optimized.solve()
    
    diff_pct = abs(length_original - length_optimized) / length_original * 100
    
    print(f"  Original v19: {length_original:.2f}")
    print(f"  Optimized v9: {length_optimized:.2f}")
    print(f"  Difference: {diff_pct:.6f}%")
    
    if diff_pct < 0.0001:
        print("✅ ATT metric compatibility verified")
        return True
    else:
        print(f"❌ ATT results differ by {diff_pct:.6f}%")
        return False

def main():
    """Run all verification tests."""
    print("v19 Optimized v9 Algorithm Verification")
    print("=" * 80)
    
    # Test 1: Algorithm equivalence
    equiv_ok, results = test_algorithm_equivalence(n=50, num_seeds=5)
    
    # Test 2: ATT metric compatibility
    att_ok = test_att_metric()
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY:")
    print(f"Algorithm equivalence: {'✅ PASS' if equiv_ok else '❌ FAIL'}")
    print(f"ATT metric compatibility: {'✅ PASS' if att_ok else '❌ FAIL'}")
    
    all_ok = equiv_ok and att_ok
    
    if all_ok:
        print("\n✅ ALL VERIFICATIONS PASSED")
        print("Optimized v9 produces identical results to original v19")
        print("TSPLIB compatibility with ATT metric confirmed")
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
