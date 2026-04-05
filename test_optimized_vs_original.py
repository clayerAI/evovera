#!/usr/bin/env python3
"""Test optimized v19 vs original v19 algorithm."""

import sys
sys.path.append('.')

from solutions.tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as OriginalV19
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized as OptimizedV19
import random

def create_random_points(n=20, seed=42):
    random.seed(seed)
    points = []
    for i in range(n):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        points.append((x, y))
    return points

def test_algorithms():
    print("Testing optimized v19 vs original v19 algorithm...")
    
    # Test with small instance first
    points = create_random_points(20, seed=42)
    
    # Run original algorithm
    print("\nRunning original v19 algorithm...")
    original = OriginalV19(points, seed=42)
    original_result = original.solve()
    original_tour = original_result[0]
    original_length = original_result[1]
    print(f"Original tour length: {original_length:.2f}")
    
    # Run optimized algorithm
    print("\nRunning optimized v19 algorithm...")
    optimized = OptimizedV19(points, seed=42)
    optimized_result = optimized.solve()
    optimized_tour = optimized_result[0]
    optimized_length = optimized_result[1]
    print(f"Optimized tour length: {optimized_length:.2f}")
    
    # Compare
    diff = abs(original_length - optimized_length)
    diff_pct = (diff / original_length) * 100 if original_length > 0 else 0
    
    print(f"\nComparison:")
    print(f"  Original length: {original_length:.2f}")
    print(f"  Optimized length: {optimized_length:.2f}")
    print(f"  Difference: {diff:.2f} ({diff_pct:.4f}%)")
    
    if diff_pct < 0.01:
        print("✅ Algorithms produce identical results (within 0.01%)")
    else:
        print("❌ Algorithms produce different results")
        
    # Check if tours are the same (ignoring starting point and direction)
    def normalize_tour(tour):
        # Remove duplicate start/end node if present
        if tour[0] == tour[-1]:
            tour = tour[:-1]
        # Find minimum index and rotate
        min_idx = tour.index(min(tour))
        normalized = tour[min_idx:] + tour[:min_idx]
        # Also check reverse direction
        normalized_rev = list(reversed(normalized))
        return normalized, normalized_rev
    
    orig_norm, orig_norm_rev = normalize_tour(original_tour)
    opt_norm, opt_norm_rev = normalize_tour(optimized_tour)
    
    if orig_norm == opt_norm or orig_norm == opt_norm_rev:
        print("✅ Tours are identical (allowing for rotation/reversal)")
    else:
        print("❌ Tours are different")
        print(f"  Original normalized: {orig_norm[:10]}...")
        print(f"  Optimized normalized: {opt_norm[:10]}...")
        
    return original_tour, optimized_tour, original_length, optimized_length

if __name__ == "__main__":
    test_algorithms()
