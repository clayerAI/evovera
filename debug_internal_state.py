#!/usr/bin/env python3
"""
Debug internal state differences.
"""

import sys
import random
import numpy as np
sys.path.append('.')

# Monkey patch to access internal state
from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized as OptSolver
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OrigSolver

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

n = 20  # Small for debugging
points = generate_random_points(n, seed=42)

print("=== INTERNAL STATE COMPARISON ===\n")

# Create solvers
solver_opt = OptSolver(points=points, seed=42)
solver_orig = OrigSolver(points=points, seed=42)

# 1. Compare MST
print("1. MST COMPARISON:")
mst_adj_opt, parent_opt = solver_opt._compute_mst()
mst_adj_orig, parent_orig = solver_orig._compute_mst()

print(f"  MST parent arrays equal: {parent_opt == parent_orig}")
if parent_opt != parent_orig:
    print(f"  Differences:")
    for i in range(n):
        if parent_opt[i] != parent_orig[i]:
            print(f"    Vertex {i}: opt parent={parent_opt[i]}, orig parent={parent_orig[i]}")

# 2. Compare edge weights in MST
print("\n2. MST EDGE WEIGHTS:")
dist_matrix = solver_opt._compute_distance_matrix()

# Get MST edges from optimized
opt_edges = set()
for u in range(n):
    for v, _ in mst_adj_opt[u]:
        if u < v:
            opt_edges.add((u, v))

# Get MST edges from original
orig_edges = set()
for u in range(n):
    for v, _ in mst_adj_orig[u]:
        if u < v:
            orig_edges.add((u, v))

print(f"  Optimized MST has {len(opt_edges)} edges")
print(f"  Original MST has {len(orig_edges)} edges")
print(f"  Edges in both: {len(opt_edges & orig_edges)}")
print(f"  Edges only in optimized: {opt_edges - orig_edges}")
print(f"  Edges only in original: {orig_edges - opt_edges}")

# 3. Compare total MST weight
opt_weight = sum(dist_matrix[u][v] for u, v in opt_edges)
orig_weight = sum(dist_matrix[u][v] for u, v in orig_edges)
print(f"  Optimized MST weight: {opt_weight:.2f}")
print(f"  Original MST weight:  {orig_weight:.2f}")
print(f"  Weight difference: {opt_weight - orig_weight:.2f}")

# 4. Build LCA structure for optimized
solver_opt._build_lca_structure(mst_adj_opt)

# 5. Compare edge centrality
print("\n3. EDGE CENTRALITY COMPARISON:")
edge_cent_opt = solver_opt._compute_edge_centrality_optimized(mst_adj_opt)
edge_cent_orig = solver_orig._compute_edge_centrality(mst_adj_orig)

# Compare for common edges
common_edges = opt_edges & orig_edges
if common_edges:
    print(f"  Comparing {len(common_edges)} common edges:")
    diffs = []
    for edge in sorted(common_edges):
        c_opt = edge_cent_opt.get(edge, 0.0)
        c_orig = edge_cent_orig.get(edge, 0.0)
        diff = abs(c_opt - c_orig)
        if diff > 0.01:
            diffs.append((edge, c_opt, c_orig, diff))
    
    if diffs:
        print(f"  Found {len(diffs)} edges with >0.01 difference:")
        for edge, c_opt, c_orig, diff in diffs[:5]:  # Show first 5
            print(f"    Edge {edge}: opt={c_opt:.3f}, orig={c_orig:.3f}, diff={diff:.3f}")
    else:
        print("  Edge centrality values match closely (<0.01 difference)")
else:
    print("  No common edges to compare!")

# 6. Compare communities
print("\n4. COMMUNITY DETECTION COMPARISON:")
communities_opt = solver_opt._detect_communities(mst_adj_opt, percentile_threshold=70.0)
communities_orig = solver_orig._detect_communities(mst_adj_orig, percentile_threshold=70.0)

print(f"  Optimized communities: {set(communities_opt.values())}")
print(f"  Original communities:  {set(communities_orig.values())}")

# Check if vertex assignments match
mismatches = []
for v in range(n):
    if communities_opt.get(v) != communities_orig.get(v):
        mismatches.append(v)

print(f"  Community mismatches for {len(mismatches)} vertices:")
if mismatches:
    for v in mismatches[:10]:  # Show first 10
        print(f"    Vertex {v}: opt={communities_opt.get(v)}, orig={communities_orig.get(v)}")

# 7. Compare odd vertices
print("\n5. ODD VERTEX COMPARISON:")
odd_opt = solver_opt._find_odd_degree_vertices(mst_adj_opt)
odd_orig = solver_orig._find_odd_degree_vertices(mst_adj_orig)

print(f"  Optimized odd vertices ({len(odd_opt)}): {sorted(odd_opt)}")
print(f"  Original odd vertices ({len(odd_orig)}): {sorted(odd_orig)}")
print(f"  Same set: {set(odd_opt) == set(odd_orig)}")
print(f"  Difference: {set(odd_opt) ^ set(odd_orig)}")
