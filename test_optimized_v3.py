#!/usr/bin/env python3
"""
Test optimized v3 with sequential greedy matching.
"""

import sys
import random
import time
sys.path.append('.')

def main():
    # Test with n=10
    n = 10
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== TESTING OPTIMIZED v3 (sequential greedy) ===\n")
    
    # Run original
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp as solve_orig
    start = time.time()
    tour_orig, length_orig, _ = solve_orig(points, seed=42, percentile_threshold=70.0)
    time_orig = time.time() - start
    
    # Run optimized v3
    from solutions.tsp_v19_optimized_fixed_v3 import solve_tsp as solve_opt
    start = time.time()
    tour_opt, length_opt, _ = solve_opt(points, seed=42, percentile_threshold=70.0)
    time_opt = time.time() - start
    
    print(f"n = {n}")
    print(f"Original length: {length_orig:.2f}, time: {time_orig:.4f}s")
    print(f"Optimized length: {length_opt:.2f}, time: {time_opt:.4f}s")
    print(f"Difference: {((length_opt - length_orig)/length_orig*100):+.2f}%")
    print(f"Speedup: {time_orig/time_opt:.2f}x")
    
    # Check if tours are identical
    if tour_orig == tour_opt:
        print("\n✅ Tours are IDENTICAL!")
    else:
        print(f"\n⚠️  Tours differ")
        print(f"Original: {tour_orig}")
        print(f"Optimized: {tour_opt}")
    
    # Test with n=20
    print("\n=== TESTING n=20 ===")
    n = 20
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    start = time.time()
    tour_orig, length_orig, _ = solve_orig(points, seed=42, percentile_threshold=70.0)
    time_orig = time.time() - start
    
    start = time.time()
    tour_opt, length_opt, _ = solve_opt(points, seed=42, percentile_threshold=70.0)
    time_opt = time.time() - start
    
    print(f"n = {n}")
    print(f"Original length: {length_orig:.2f}, time: {time_orig:.4f}s")
    print(f"Optimized length: {length_opt:.2f}, time: {time_opt:.4f}s")
    print(f"Difference: {((length_opt - length_orig)/length_orig*100):+.2f}%")
    print(f"Speedup: {time_orig/time_opt:.2f}x")
    
    # Test with n=50
    print("\n=== TESTING n=50 ===")
    n = 50
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    start = time.time()
    tour_orig, length_orig, _ = solve_orig(points, seed=42, percentile_threshold=70.0)
    time_orig = time.time() - start
    
    start = time.time()
    tour_opt, length_opt, _ = solve_opt(points, seed=42, percentile_threshold=70.0)
    time_opt = time.time() - start
    
    print(f"n = {n}")
    print(f"Original length: {length_orig:.2f}, time: {time_orig:.4f}s")
    print(f"Optimized length: {length_opt:.2f}, time: {time_opt:.4f}s")
    print(f"Difference: {((length_opt - length_orig)/length_orig*100):+.2f}%")
    print(f"Speedup: {time_orig/time_opt:.2f}x")

if __name__ == "__main__":
    main()
