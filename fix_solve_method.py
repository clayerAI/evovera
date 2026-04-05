#!/usr/bin/env python3
"""
Fix solve method to accept percentile_threshold parameter.
"""

import sys
import os

# Read the optimized algorithm
with open('solutions/tsp_v19_optimized_fixed.py', 'r') as f:
    content = f.read()

# Find and update solve method
lines = content.split('\n')

# Find solve method
solve_start = -1
for i, line in enumerate(lines):
    if 'def solve(self) -> Tuple[List[int], float]:' in line:
        solve_start = i
        break

if solve_start == -1:
    print("ERROR: Could not find solve method")
    sys.exit(1)

# Update method signature
lines[solve_start] = '    def solve(self, percentile_threshold: float = 70.0) -> Tuple[List[int], float]:'

# Find where _detect_communities is called
for i in range(solve_start, len(lines)):
    if 'communities = self._detect_communities(mst_adj)' in lines[i]:
        # Update to pass percentile_threshold
        lines[i] = '        communities = self._detect_communities(mst_adj, percentile_threshold)'
        break

# Write back
with open('solutions/tsp_v19_optimized_fixed.py', 'w') as f:
    f.write('\n'.join(lines))

print("Updated solve method to accept percentile_threshold")

# Test the fix
print("\n=== Testing Fixed Algorithm ===")

sys.path.append('.')
import random
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

# Test with n=50
points = generate_random_points(50, seed=50)

print("Testing optimized algorithm with percentile_threshold=70:")
solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=50)
tour_opt, length_opt = solver_opt.solve(percentile_threshold=70)
print(f"  Tour length: {length_opt:.2f}")
print(f"  Valid tour: {len(set(tour_opt)) == 50}")

print("\nTesting original algorithm with percentile_threshold=70:")
solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=50)
result_orig = solver_orig.solve(percentile_threshold=70)
if isinstance(result_orig, tuple):
    tour_orig, length_orig = result_orig
else:
    tour_orig = result_orig
    # Compute length
    dist_matrix = solver_orig._compute_distance_matrix()
    length_orig = 0.0
    for i in range(len(tour_orig)):
        u = tour_orig[i]
        v = tour_orig[(i + 1) % len(tour_orig)]
        length_orig += dist_matrix[u][v]

print(f"  Tour length: {length_orig:.2f}")
print(f"  Length difference: {((length_opt - length_orig) / length_orig * 100):.1f}%")

# Test different thresholds
print("\n=== Testing Different Thresholds ===")
for threshold in [60, 70, 80]:
    print(f"\nThreshold {threshold}%:")
    
    # Optimized
    tour_opt, length_opt = solver_opt.solve(percentile_threshold=threshold)
    
    # Original
    result_orig = solver_orig.solve(percentile_threshold=threshold)
    if isinstance(result_orig, tuple):
        tour_orig, length_orig = result_orig
    else:
        tour_orig = result_orig
        length_orig = 0.0
        for i in range(len(tour_orig)):
            u = tour_orig[i]
            v = tour_orig[(i + 1) % len(tour_orig)]
            length_orig += dist_matrix[u][v]
    
    diff_pct = (length_opt - length_orig) / length_orig * 100
    print(f"  Optimized: {length_opt:.2f}")
    print(f"  Original:  {length_orig:.2f}")
    print(f"  Difference: {diff_pct:.1f}%")
