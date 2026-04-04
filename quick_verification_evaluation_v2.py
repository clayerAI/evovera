#!/usr/bin/env python3
"""
Quick verification of corrected TSPLIB evaluation - Version 2.
Handles different return signatures for algorithms.
"""

import sys
import os
import time
import numpy as np

# Add paths
sys.path.insert(0, '.')
sys.path.insert(0, 'solutions')

from tsplib_parser import TSPLIBParser
from tsp_v1_nearest_neighbor_fixed import NearestNeighborTSP as V1Solver
from tsp_v2_christofides_improved_fixed import ImprovedMatchingChristofides as V2Solver
from tsp_v19_christofides_hybrid_structural_fixed import ChristofidesHybridStructural as V19Solver

print("=" * 60)
print("QUICK VERIFICATION OF CORRECTED TSPLIB EVALUATION - V2")
print("Testing eil51 instance only")
print("=" * 60)

# Test eil51 instance
filepath = "data/tsplib/eil51.tsp"
if not os.path.exists(filepath):
    print(f"❌ File not found: {filepath}")
    sys.exit(1)

# Parse instance
parser = TSPLIBParser(filepath)
if not parser.parse():
    print("❌ Failed to parse instance")
    sys.exit(1)

print(f"\n📊 Instance: {parser.name}")
print(f"  Dimension: {parser.dimension}")
print(f"  Edge weight type: {parser.edge_weight_type}")
print(f"  Optimal value: {parser.optimal_value}")

# Calculate distance matrix
points = np.array(parser.node_coords)
n = len(points)
dist_matrix = np.zeros((n, n))

for i in range(n):
    for j in range(i + 1, n):
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        dist = round(np.sqrt(dx*dx + dy*dy))  # EUC_2D
        dist_matrix[i][j] = dist
        dist_matrix[j][i] = dist

print(f"\n🚀 Testing algorithms...")

# Test V1
print(f"\n1. Nearest Neighbor (Fixed):")
try:
    solver = V1Solver(distance_matrix=dist_matrix, seed=42)
    start = time.time()
    result = solver.solve()
    elapsed = time.time() - start
    
    # Handle return value
    if isinstance(result, tuple) and len(result) >= 2:
        tour, length = result[0], result[1]
        print(f"   Tour length: {length:.2f}")
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Gap to optimal: {((length - parser.optimal_value) / parser.optimal_value * 100):.2f}%")
    else:
        print(f"   ❌ Unexpected return value: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test V2
print(f"\n2. Christofides Improved (Fixed):")
try:
    solver = V2Solver(distance_matrix=dist_matrix, seed=42)
    start = time.time()
    result = solver.solve()
    elapsed = time.time() - start
    
    # Handle return value
    if isinstance(result, tuple) and len(result) >= 2:
        tour, length = result[0], result[1]
        print(f"   Tour length: {length:.2f}")
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Gap to optimal: {((length - parser.optimal_value) / parser.optimal_value * 100):.2f}%")
    else:
        print(f"   ❌ Unexpected return value: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test V19
print(f"\n3. Christofides Hybrid Structural (Fixed):")
try:
    solver = V19Solver(distance_matrix=dist_matrix, seed=42)
    start = time.time()
    result = solver.solve()
    elapsed = time.time() - start
    
    # Handle return value - V19 returns (tour, length, modularity_score)
    if isinstance(result, tuple) and len(result) >= 2:
        tour, length = result[0], result[1]
        print(f"   Tour length: {length:.2f}")
        print(f"   Time: {elapsed:.3f}s")
        print(f"   Gap to optimal: {((length - parser.optimal_value) / parser.optimal_value * 100):.2f}%")
        if len(result) > 2:
            print(f"   Modularity score: {result[2]:.4f}")
    else:
        print(f"   ❌ Unexpected return value: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
