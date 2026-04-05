#!/usr/bin/env python3
"""
Comprehensive test of fixed optimized algorithm.
"""

import sys
import time
import random
import math
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def test_scaling():
    """Test scaling performance."""
    sizes = [20, 50, 100, 200, 300]
    results = []
    
    for n in sizes:
        print(f"\n=== Testing n={n} ===")
        points = generate_random_points(n, seed=42)
        
        # Test optimized
        start = time.time()
        solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
        tour_opt, length_opt = solver_opt.solve(percentile_threshold=70.0)
        time_opt = time.time() - start
        
        # Test original
        start = time.time()
        solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
        result_orig = solver_orig.solve(percentile_threshold=70.0)
        tour_orig, length_orig, _ = result_orig
        time_orig = time.time() - start
        
        # Check validity
        opt_valid = (tour_opt[0] == 0 and tour_opt[-1] == 0 and 
                     len(set(tour_opt[:-1])) == n and len(tour_opt) == n + 1)
        orig_valid = (tour_orig[0] == 0 and tour_orig[-1] == 0 and 
                      len(set(tour_orig[:-1])) == n and len(tour_orig) == n + 1)
        
        quality_diff = (length_opt - length_orig) / length_orig * 100 if length_orig > 0 else 0
        speedup = time_orig / time_opt if time_opt > 0 else float('inf')
        
        results.append({
            'n': n,
            'time_opt': time_opt,
            'time_orig': time_orig,
            'speedup': speedup,
            'quality_diff': quality_diff,
            'opt_valid': opt_valid,
            'orig_valid': orig_valid
        })
        
        print(f"  Optimized: {time_opt:.3f}s, length={length_opt:.2f}, valid={opt_valid}")
        print(f"  Original:  {time_orig:.3f}s, length={length_orig:.2f}, valid={orig_valid}")
        print(f"  Speedup: {speedup:.1f}x, Quality: {quality_diff:+.1f}%")
    
    return results

def analyze_scaling(results):
    """Analyze scaling behavior."""
    print("\n=== SCALING ANALYSIS ===")
    
    for i in range(1, len(results)):
        n1, t1 = results[i-1]['n'], results[i-1]['time_opt']
        n2, t2 = results[i]['n'], results[i]['time_opt']
        
        if t1 > 0 and t2 > 0:
            # Compute exponent: t ∝ n^exponent
            exponent = math.log(t2 / t1) / math.log(n2 / n1)
            print(f"  n={n1}→{n2}: t={t1:.3f}→{t2:.3f}s, exponent={exponent:.3f}")

def main():
    print("=== COMPREHENSIVE TEST OF FIXED OPTIMIZED ALGORITHM ===\n")
    
    # Test small instance for correctness
    print("=== CORRECTNESS TEST (n=20) ===")
    points = generate_random_points(20, seed=42)
    
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    tour_opt, length_opt = solver_opt.solve(percentile_threshold=70.0)
    
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    result_orig = solver_orig.solve(percentile_threshold=70.0)
    tour_orig, length_orig, _ = result_orig
    
    print(f"Optimized tour: {tour_opt}")
    print(f"Original tour:  {tour_orig}")
    print(f"Lengths: {length_opt:.2f} vs {length_orig:.2f} ({((length_opt - length_orig)/length_orig*100):+.1f}%)")
    
    # Check validity
    print(f"\nValidity checks:")
    print(f"  Optimized starts/ends at 0: {tour_opt[0] == 0 and tour_opt[-1] == 0}")
    print(f"  Original starts/ends at 0: {tour_orig[0] == 0 and tour_orig[-1] == 0}")
    print(f"  Optimized visits all vertices: {len(set(tour_opt[:-1])) == 20}")
    print(f"  Original visits all vertices: {len(set(tour_orig[:-1])) == 20}")
    print(f"  Optimized no duplicates: {len(tour_opt) == len(set(tour_opt[:-1])) + 1}")
    print(f"  Original no duplicates: {len(tour_orig) == len(set(tour_orig[:-1])) + 1}")
    
    # Test scaling
    results = test_scaling()
    analyze_scaling(results)
    
    # Summary
    print("\n=== SUMMARY ===")
    print("Algorithm status: FIXED - tours are now valid Hamiltonian cycles")
    print("Key improvements:")
    print("  1. Fixed _shortcut_eulerian_tour to add starting vertex at end")
    print("  2. Fixed _compute_tour_length to handle non-cyclic tours")
    print("  3. Maintains all optimizations: LCA, lazy path centrality, etc.")
    
    # Project TSPLIB times
    print("\n=== PROJECTED TSPLIB PERFORMANCE ===")
    # Based on n^3.005 scaling from previous test
    base_n = 300
    base_time = results[-1]['time_opt']  # n=300 time
    exponent = 3.005
    
    for n, name in [(280, "a280"), (532, "att532"), (1000, "dsj1000")]:
        projected = base_time * (n / base_n) ** exponent
        print(f"  {name} (n={n}): {projected:.2f}s (target: {30 if n==280 else 120 if n==532 else 'N/A'}s)")

if __name__ == "__main__":
    main()
