#!/usr/bin/env python3
"""
Simple matching comparison.
"""

import sys
import random
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def main():
    n = 20
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== SIMPLE MATCHING COMPARISON ===\n")
    
    # Run optimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    tour_opt, length_opt = solver_opt.solve(percentile_threshold=70.0)
    
    # Run original
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    result_orig = solver_orig.solve(percentile_threshold=70.0)
    tour_orig, length_orig, _ = result_orig
    
    print(f"Optimized matching (inferred from tour):")
    # Extract matching from tour by looking at added edges beyond MST
    # This is simplified - just show the tours
    print(f"  Tour: {tour_opt}")
    print(f"  Length: {length_opt:.2f}")
    
    print(f"\nOriginal matching:")
    print(f"  Tour: {tour_orig}")
    print(f"  Length: {length_orig:.2f}")
    
    print(f"\nDifference: {((length_opt - length_orig)/length_orig*100):+.1f}%")
    
    # The key insight from earlier trace: optimized matched (2,10), (5,6), (15,16)
    # Let's see what the original would match
    print("\n=== PATH CENTRALITY DIFFERENCE HYPOTHESIS ===")
    print("The optimized algorithm computes path centrality lazily (on-demand)")
    print("The original precomputes all-pairs path centrality")
    print("If path centrality values differ significantly, matching will differ")
    print("\nThis could explain the 1.6% quality degradation for n=20")
    print("For larger n (50+), degradation is 7-17% which is problematic")
    
    print("\n=== POSSIBLE FIXES ===")
    print("1. Verify lazy path centrality matches precomputed values")
    print("2. If not, fix the lazy computation")
    print("3. Consider caching computed path centrality values")
    print("4. Accept some quality degradation for massive speedup (22.9x!)")

if __name__ == "__main__":
    main()
