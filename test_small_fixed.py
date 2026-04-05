#!/usr/bin/env python3
"""Test the optimized v11 algorithm on a small instance."""

import sys
import os
import time
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11 as V11Solver

# Test on eil51 (small instance)
parser = TSPLIBParser("data/tsplib/eil51.tsp")
instance_data = parser.parse()
distance_matrix = parser.get_distance_matrix(instance_data)

print(f"Testing optimized v11 on eil51 ({len(distance_matrix)} nodes)...")
start = time.time()
solver = V11Solver(distance_matrix=distance_matrix)
tour, length = solver.solve()
elapsed = time.time() - start

print(f"Tour length: {length:.2f}")
print(f"Runtime: {elapsed:.2f}s")
print(f"Tour valid: {len(tour) == len(distance_matrix) + 1}")
print(f"Tour starts/ends at same node: {tour[0] == tour[-1]}")
print(f"Unique nodes visited: {len(set(tour[:-1]))}")
