#!/usr/bin/env python3
"""Debug tour format from optimized v19 algorithm."""

import sys
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized as OptimizedV19
import random

def create_random_points(n=10, seed=42):
    random.seed(seed)
    points = []
    for i in range(n):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        points.append((x, y))
    return points

points = create_random_points(10, seed=42)
optimized = OptimizedV19(points, seed=42)
tour = optimized.solve()

print(f"Tour type: {type(tour)}")
print(f"Tour length (len): {len(tour)}")
print(f"First few elements: {tour[:5] if len(tour) > 5 else tour}")
print(f"Element types: {[type(x) for x in tour[:3]] if len(tour) >= 3 else []}")

# Check if it's a list of lists
if tour and isinstance(tour[0], list):
    print(f"Tour is list of lists, first inner list: {tour[0]}")
    print(f"Inner list length: {len(tour[0])}")
