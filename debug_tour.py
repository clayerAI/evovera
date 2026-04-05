#!/usr/bin/env python3
"""
Debug tour format.
"""

import sys
import random
sys.path.append('.')

from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

points = generate_random_points(20, seed=42)
solver = ChristofidesHybridStructuralCorrected(points=points, seed=42)
tour = solver.solve(percentile_threshold=70)

print(f"Tour type: {type(tour)}")
print(f"Tour length (as Python len): {len(tour)}")
print(f"First 5 elements: {tour[:5] if hasattr(tour, '__getitem__') else 'N/A'}")

# Check if it's a numpy array
if hasattr(tour, 'shape'):
    print(f"Numpy array shape: {tour.shape}")
    print(f"First element type: {type(tour[0])}")
elif isinstance(tour, list):
    print(f"First element: {tour[0]}")
    print(f"First element type: {type(tour[0])}")
