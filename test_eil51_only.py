#!/usr/bin/env python3
"""Test eil51 instance only to debug performance."""

import sys
import os
import time
import numpy as np

sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')

from tsplib_parser import TSPLIBParser
from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
from tsp_v2_christofides_improved_fixed import ImprovedMatchingChristofides as V2Solver
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

print("Testing eil51 only...")
filepath = "data/tsplib/eil51.tsp"

parser = TSPLIBParser(filepath)
parser.parse()
print(f"Parsed {parser.name}, dimension={parser.dimension}")

points = np.array(parser.node_coords)
n = len(points)
dist_matrix = np.zeros((n, n))

# EUC_2D distance
for i in range(n):
    for j in range(i + 1, n):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        dist = round(np.sqrt(dx*dx + dy*dy))
        dist_matrix[i][j] = dist
        dist_matrix[j][i] = dist

print("Distance matrix calculated")

# Test V1
print("\nTesting V1...")
start = time.time()
solver = V1Solver(distance_matrix=dist_matrix, seed=42)
result = solver.solve()
print(f"V1 completed in {time.time()-start:.3f}s")
print(f"Result: {result[1]}")

# Test V2
print("\nTesting V2...")
start = time.time()
solver = V2Solver(distance_matrix=dist_matrix, seed=42)
result = solver.solve()
print(f"V2 completed in {time.time()-start:.3f}s")
print(f"Result: {result[1]}")

# Test V19
print("\nTesting V19...")
start = time.time()
solver = V19Solver(distance_matrix=dist_matrix, seed=42)
result = solver.solve()
print(f"V19 completed in {time.time()-start:.3f}s")
print(f"Result: {result[1]}")

print("\nAll tests completed successfully!")
