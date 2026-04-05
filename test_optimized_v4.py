#!/usr/bin/env python3
"""
Test optimized v4 algorithm with original community detection.
"""

import sys
import random
import time
sys.path.append('.')

def main():
    random.seed(42)
    
    # Test with small instance
    n = 10
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== TESTING OPTIMIZED v4 (with original community detection) ===\n")
    
    # Run original algorithm
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp as solve_original
    start = time.time()
    tour_orig = solve_original(points, seed=42)
    time_orig = time.time() - start
    
    # Run optimized v4
    from solutions.tsp_v19_optimized_fixed_v4 import solve_tsp as solve_optimized
    start = time.time()
    tour_opt = solve_optimized(points, seed=42)
    time_opt = time.time() - start
    
    # Compute tour lengths
    def tour_length(points, tour):
        total = 0.0
        for i in range(len(tour) - 1):
            x1, y1 = points[tour[i]]
            x2, y2 = points[tour[i + 1]]
            total += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        return total
    
    len_orig = tour_length(points, tour_orig)
    len_opt = tour_length(points, tour_opt)
    
    print(f"Original tour length: {len_orig:.4f}")
    print(f"Optimized v4 tour length: {len_opt:.4f}")
    print(f"Difference: {len_opt - len_orig:.4f} ({((len_opt - len_orig) / len_orig * 100):.2f}%)")
    print(f"\nOriginal time: {time_orig:.4f}s")
    print(f"Optimized time: {time_opt:.4f}s")
    print(f"Speedup: {time_orig / time_opt:.2f}x")
    
    # Check if tours are identical
    if tour_orig == tour_opt:
        print("\n✅ TOURS ARE IDENTICAL!")
    else:
        print(f"\n⚠️  Tours differ")
        print(f"Original tour: {tour_orig}")
        print(f"Optimized tour: {tour_opt}")
        
        # Check if they're just rotations/reversals
        def normalize_tour(tour):
            # Remove closing vertex
            tour = tour[:-1]
            # Find index of 0
            idx = tour.index(0)
            # Rotate to start at 0
            tour = tour[idx:] + tour[:idx]
            # Return canonical form (smaller of forward and reverse)
            rev = list(reversed(tour[1:]))
            rev = [0] + rev
            return min(tour, rev)
        
        norm_orig = normalize_tour(tour_orig)
        norm_opt = normalize_tour(tour_opt)
        
        if norm_orig == norm_opt:
            print("✅ Tours are equivalent (rotation/reversal)")
        else:
            print("❌ Tours are fundamentally different")
    
    # Test with larger instance
    print("\n=== TESTING WITH n=50 ===")
    n = 50
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    start = time.time()
    tour_orig = solve_original(points, seed=42)
    time_orig = time.time() - start
    
    start = time.time()
    tour_opt = solve_optimized(points, seed=42)
    time_opt = time.time() - start
    
    len_orig = tour_length(points, tour_orig)
    len_opt = tour_length(points, tour_opt)
    
    print(f"Original tour length: {len_orig:.4f}")
    print(f"Optimized v4 tour length: {len_opt:.4f}")
    print(f"Difference: {len_opt - len_orig:.4f} ({((len_opt - len_orig) / len_orig * 100):.2f}%)")
    print(f"\nOriginal time: {time_orig:.4f}s")
    print(f"Optimized time: {time_opt:.4f}s")
    print(f"Speedup: {time_orig / time_opt:.2f}x")

if __name__ == "__main__":
    main()
