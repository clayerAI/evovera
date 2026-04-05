#!/usr/bin/env python3
"""
Debug matching order sensitivity.
"""

import sys
import random
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized

def main():
    n = 20
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== MATCHING ORDER SENSITIVITY ===\n")
    
    # Run multiple times with same seed
    print("Running optimized algorithm 3 times with same seed:")
    tours = []
    lengths = []
    
    for i in range(3):
        solver = ChristofidesHybridStructuralOptimized(points=points, seed=42)
        tour, length = solver.solve(percentile_threshold=70.0)
        tours.append(tour)
        lengths.append(length)
        print(f"  Run {i+1}: length={length:.2f}, tour starts with {tour[:5]}...")
    
    # Check consistency
    consistent = all(t == tours[0] for t in tours)
    print(f"\nConsistent across runs: {consistent}")
    
    if not consistent:
        print("Algorithm is non-deterministic even with fixed seed!")
    
    # Check if floating point differences could cause different matching
    print("\n=== FLOATING POINT SENSITIVITY ===")
    print("The greedy matching algorithm finds the minimum adjusted weight.")
    print("If two pairs have very similar adjusted weights, floating point")
    print("precision or computation order could affect which is chosen.")
    print("\nThis could create a 'butterfly effect' where early matching")
    print("choices cascade to completely different tours.")
    
    # Test with n=50 to see if issue gets worse
    print("\n=== TESTING n=50 ===")
    n50 = 50
    points50 = [(random.random() * 100, random.random() * 100) for _ in range(n50)]
    
    solver1 = ChristofidesHybridStructuralOptimized(points=points50, seed=42)
    tour1, length1 = solver1.solve(percentile_threshold=70.0)
    
    solver2 = ChristofidesHybridStructuralOptimized(points=points50, seed=42)
    tour2, length2 = solver2.solve(percentile_threshold=70.0)
    
    print(f"Run 1 length: {length1:.2f}")
    print(f"Run 2 length: {length2:.2f}")
    print(f"Same tour: {tour1 == tour2}")
    print(f"Length difference: {abs(length1 - length2):.2f} ({abs(length1 - length2)/length1*100:.1f}%)")

if __name__ == "__main__":
    main()
