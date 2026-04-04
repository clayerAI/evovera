#!/usr/bin/env python3
"""
Simple TSPLIB evaluation to verify fixed algorithms work.
"""

import sys
import os
import time
import json
from datetime import datetime

# Import TSP algorithms
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

# Import fixed algorithms
try:
    from solutions.tsp_v1_nearest_neighbor_fixed import tsp_v1_nearest_neighbor_fixed
    from solutions.tsp_v2_christofides_improved_fixed import tsp_v2_christofides_improved_fixed
    from solutions.tsp_v19_christofides_hybrid_structural_fixed import tsp_v19_christofides_hybrid_structural_fixed
    ALGORITHMS = {
        'tsp_v1_nearest_neighbor_fixed': tsp_v1_nearest_neighbor_fixed,
        'tsp_v2_christofides_improved_fixed': tsp_v2_christofides_improved_fixed,
        'tsp_v19_christofides_hybrid_structural_fixed': tsp_v19_christofides_hybrid_structural_fixed
    }
    print("✅ Imported all fixed algorithms")
except ImportError as e:
    print(f"❌ Error importing algorithms: {e}")
    sys.exit(1)

# Test with just eil51 first
instance_path = "data/tsplib/eil51.tsp"
if not os.path.exists(instance_path):
    print(f"❌ Instance not found: {instance_path}")
    sys.exit(1)

print(f"\n📊 Testing with {instance_path}")
parser = TSPLIBParser(instance_path)
points, optimal, name, comment, dimension, edge_weight_type = parser.parse(instance_path)

print(f"  Instance: {name} (dimension={dimension}, type={edge_weight_type})")
print(f"  Optimal tour length: {optimal}")

# Create distance matrix
import numpy as np
n = len(points)
dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        if edge_weight_type == "ATT":
            # ATT distance: ceil(sqrt((dx²+dy²)/10.0))
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
        else:  # EUC_2D
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dist = np.sqrt(dx*dx + dy*dy)
        dist_matrix[i][j] = dist
        dist_matrix[j][i] = dist

print(f"  Created {n}x{n} distance matrix")

# Test each algorithm
results = {}
for algo_name, algo_func in ALGORITHMS.items():
    print(f"\n  🧪 Running {algo_name}...")
    start_time = time.time()
    try:
        tour, tour_length = algo_func(points, dist_matrix)
        elapsed = time.time() - start_time
        
        # Calculate gap
        gap = ((tour_length - optimal) / optimal) * 100 if optimal > 0 else float('inf')
        
        results[algo_name] = {
            'tour_length': tour_length,
            'gap': gap,
            'time': elapsed,
            'optimal': optimal
        }
        
        print(f"    Tour length: {tour_length:.2f}")
        print(f"    Gap to optimal: {gap:.2f}%")
        print(f"    Time: {elapsed:.2f}s")
    except Exception as e:
        print(f"    ❌ Error: {e}")
        results[algo_name] = {'error': str(e)}

print(f"\n✅ Simple evaluation complete!")
print(f"Results: {json.dumps(results, indent=2)}")
