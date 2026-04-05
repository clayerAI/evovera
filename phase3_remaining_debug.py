#!/usr/bin/env python3
"""Debug script for remaining Phase 3 instances."""

import sys
import os
import time
import json
sys.path.append('.')

# Import v11 algorithm
try:
    from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("✓ Loaded v11 algorithm")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Import TSPLIB parser
try:
    from tsplib_parser import TSPLIBParser
    print("✓ Loaded TSPLIB parser")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Load Phase 2 results
phase2_file = "v11_tsplib_phase2_comprehensive_results.json"
try:
    with open(phase2_file, 'r') as f:
        phase2_results = json.load(f)
    print(f"✓ Loaded Phase 2 results from {phase2_file}")
except FileNotFoundError:
    print(f"ERROR: Phase 2 results file {phase2_file} not found")
    sys.exit(1)

# Test just lin318
instance_name = "lin318"
instance_file = "data/tsplib/lin318.tsp"
optimal = 42029

print(f"Testing {instance_name}...")

# Parse instance
parser = TSPLIBParser(instance_file)
if not parser.parse():
    print(f'ERROR: Failed to parse {instance_file}')
    sys.exit(1)

n_nodes = parser.dimension
print(f"  ✓ Parsed {instance_name}: {n_nodes} nodes, optimal={parser.optimal_value}")

# Get distance matrix
dist_matrix_np = parser.get_distance_matrix()

# Check Phase 2 results
print(f"Checking Phase 2 results for {instance_name}...")
if instance_name in phase2_results and "seeds" in phase2_results[instance_name]:
    print(f"  Found Phase 2 results for {instance_name}")
    seed_key = "seed_1"
    if seed_key in phase2_results[instance_name]["seeds"]:
        v11_gap = phase2_results[instance_name]["seeds"][seed_key]["gap_percent"]
        v11_time = phase2_results[instance_name]["seeds"][seed_key]["time_seconds"]
        print(f"  Seed 1: gap={v11_gap}%, time={v11_time}s")
    else:
        print(f"  Seed 1 not found in Phase 2 results")
else:
    print(f"  No Phase 2 results found for {instance_name}")

# Test v11 algorithm
print(f"\nTesting v11 algorithm...")
v11 = ChristofidesHybridStructuralOptimizedV11(dist_matrix_np, seed=1)
start = time.time()
tour, tour_length = v11.solve()
v11_time = time.time() - start
v11_gap = (tour_length - optimal) / optimal * 100
print(f"  v11: tour_length={tour_length:.2f}, gap={v11_gap:.2f}%, time={v11_time:.2f}s")
print(f"  Tour length: {len(tour)} nodes")
print(f"  First 5 nodes: {tour[:5]}")

print("\n✓ Debug complete")
