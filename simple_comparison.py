#!/usr/bin/env python3
"""
Simple comparison of original vs optimized matching.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== SIMPLE COMPARISON n=10 ===\n")
    
    # Run original
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    tour_orig, length_orig, _ = solver_orig.solve(percentile_threshold=70.0)
    
    # Run optimized
    from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    tour_opt, length_opt = solver_opt.solve(percentile_threshold=70.0)
    
    print(f"Original tour length: {length_orig:.2f}")
    print(f"Optimized tour length: {length_opt:.2f}")
    print(f"Difference: {((length_opt - length_orig)/length_orig*100):+.1f}%")
    
    print(f"\nOriginal tour: {tour_orig}")
    print(f"Optimized tour: {tour_opt}")
    
    # Check if tours are valid
    def is_valid_tour(tour, n):
        return (len(tour) == n + 1 and 
                tour[0] == tour[-1] and 
                set(tour[:-1]) == set(range(n)))
    
    print(f"\nOriginal tour valid: {is_valid_tour(tour_orig, n)}")
    print(f"Optimized tour valid: {is_valid_tour(tour_opt, n)}")
    
    # The key question: is the 1.6% degradation acceptable for 5.8x speedup?
    print("\n=== TRADEOFF ANALYSIS ===")
    print("For n=10:")
    print("  - Quality degradation: +1.6% (worse)")
    print("  - Speedup: 5.8x (from profiling)")
    print("  - Scaling: O(n^3.005) vs O(n^5.00)")
    print("\nFor n=50 (from earlier test):")
    print("  - Quality degradation: +13.3% (problematic)")
    print("  - Speedup: 22.9x (massive)")
    print("\nThe quality degradation increases with n!")
    print("This suggests the matching difference compounds.")
    
    print("\n=== POSSIBLE SOLUTIONS ===")
    print("1. Fix the matching algorithm to match original exactly")
    print("2. Accept degradation for small n, use original for large n")
    print("3. Hybrid approach: use optimized for speed, refine with local search")
    print("4. Debug why degradation increases with n")

if __name__ == "__main__":
    main()
