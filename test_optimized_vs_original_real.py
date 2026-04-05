#!/usr/bin/env python3
"""Test optimized v19 vs ORIGINAL v19 algorithm (not fixed version)."""

import sys
sys.path.append('.')

from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural as OriginalV19
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
    print("Testing optimized v19 vs ORIGINAL v19 algorithm (not fixed version)...")
    
    # Test with small instance first
    points = create_random_points(20, seed=42)
    
    # Run original algorithm
    print("\nRunning ORIGINAL v19 algorithm (with hybrid features)...")
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
        
    return original_tour, optimized_tour, original_length, optimized_length

if __name__ == "__main__":
    test_algorithms()
