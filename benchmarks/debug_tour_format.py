#!/usr/bin/env python3
"""Debug tour format issue."""

import sys
import os
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'solutions'))

from tsp_v1_nearest_neighbor import solve_tsp as v1_nn_2opt

def generate_random_points(n, seed):
    np.random.seed(seed)
    return np.random.rand(n, 2)

points = generate_random_points(30, 42)
tour = v1_nn_2opt(points)

print(f"Tour type: {type(tour)}")
print(f"Tour length: {len(tour)}")
print(f"First 5 elements: {tour[:5]}")
print(f"Element types: {[type(x) for x in tour[:5]]}")
print(f"Tour: {tour}")