#!/usr/bin/env python3
"""
Simple debug to understand quality difference.
"""

import sys
import random
import time
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed import ChristofidesHybridStructuralOptimized
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

# Test with small n
n = 20
points = generate_random_points(n, seed=42)

print("=== SIMPLE DEBUG ===\n")
print(f"Testing with n={n}")

# Run optimized
solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
tour_opt, length_opt = solver_opt.solve(percentile_threshold=70.0)
print(f"Optimized tour length: {length_opt:.2f}")
print(f"Optimized tour: {tour_opt}")

# Run original
solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
result_orig = solver_orig.solve(percentile_threshold=70.0)
tour_orig, length_orig, _ = result_orig
print(f"\nOriginal tour length: {length_orig:.2f}")
print(f"Original tour: {tour_orig}")

# Compare
print(f"\nQuality difference: {(length_opt - length_orig)/length_orig*100:+.1f}%")

# Check if tours are valid
print(f"\nTour validity check:")
print(f"  Optimized tour starts/ends at 0: {tour_opt[0] == 0 and tour_opt[-1] == 0}")
print(f"  Original tour starts/ends at 0: {tour_orig[0] == 0 and tour_orig[-1] == 0}")
print(f"  Optimized tour length: {len(tour_opt)} vertices")
print(f"  Original tour length: {len(tour_orig)} vertices")

# Check if they visit all vertices
all_vertices = set(range(n))
opt_visited = set(tour_opt[:-1])  # Exclude final 0
orig_visited = set(tour_orig[:-1])

print(f"\nVertex coverage:")
print(f"  Optimized covers all vertices: {opt_visited == all_vertices}")
print(f"  Original covers all vertices: {orig_visited == all_vertices}")
print(f"  Missing in optimized: {all_vertices - opt_visited}")
print(f"  Missing in original: {all_vertices - orig_visited}")

# Check for duplicates
print(f"\nDuplicate check:")
opt_counts = {}
for v in tour_opt[:-1]:  # Exclude final 0
    opt_counts[v] = opt_counts.get(v, 0) + 1
dup_opt = {v: c for v, c in opt_counts.items() if c > 1}

orig_counts = {}
for v in tour_orig[:-1]:
    orig_counts[v] = orig_counts.get(v, 0) + 1
dup_orig = {v: c for v, c in orig_counts.items() if c > 1}

print(f"  Optimized duplicates: {dup_opt}")
print(f"  Original duplicates: {dup_orig}")
