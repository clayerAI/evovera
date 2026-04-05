#!/usr/bin/env python3
"""
Debug path centrality differences.
"""

import sys
import random
sys.path.append('.')

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

# Test with small n for debugging
n = 30
points = generate_random_points(n, seed=42)

# Run optimized algorithm
solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
solver_opt._build_mst()
solver_opt._build_lca_structure()
edge_centrality_opt = solver_opt._compute_edge_centrality_optimized(solver_opt._mst_adj)

# Run original algorithm
solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
solver_orig._build_mst()
mst_paths_orig = solver_orig._build_mst_paths()
edge_centrality_orig = solver_orig._compute_edge_centrality(mst_paths_orig)
path_centrality_orig = solver_orig._compute_path_centrality(mst_paths_orig, edge_centrality_orig)

print("=== PATH CENTRALITY COMPARISON ===\n")

# Compare edge centrality for a few edges
print("Edge centrality comparison (first 10 edges):")
orig_edges = list(edge_centrality_orig.keys())[:10]
for edge in orig_edges:
    orig_val = edge_centrality_orig.get(edge, 0.0)
    opt_val = edge_centrality_opt.get(edge, 0.0)
    diff = abs(orig_val - opt_val)
    print(f"  Edge {edge}: orig={orig_val:.6f}, opt={opt_val:.6f}, diff={diff:.6f}")

# Compare path centrality for a few pairs
print("\nPath centrality comparison (first 5 pairs):")
orig_pairs = list(path_centrality_orig.keys())[:5]
for pair in orig_pairs:
    u, v = pair
    orig_val = path_centrality_orig.get(pair, 0.0)
    
    # Compute optimized path centrality
    opt_val = solver_opt._compute_path_centrality_lazy(u, v, edge_centrality_opt)
    
    diff = abs(orig_val - opt_val)
    print(f"  Pair {pair}: orig={orig_val:.6f}, opt={opt_val:.6f}, diff={diff:.6f}")

# Check if MSTs are the same
print("\n=== MST COMPARISON ===")
print(f"Optimized MST edges: {len(solver_opt._mst_adj)}")
print(f"Original MST edges: {len(solver_orig._mst_adj)}")

# Check if parent arrays are consistent
print("\n=== LCA STRUCTURE CHECK ===")
print(f"Optimized parent[0]: {solver_opt._parent[0] if solver_opt._parent else 'None'}")
print(f"Optimized depth[0]: {solver_opt._depth[0] if solver_opt._depth else 'None'}")

# Test a specific path
print("\n=== SPECIFIC PATH EXAMPLE ===")
u, v = 0, 5
print(f"Path between {u} and {v}:")
print(f"  Original path edges: {mst_paths_orig.get((u, v), [])}")

# Get optimized path edges
opt_path_edges = solver_opt._get_path_edges_lazy(u, v)
print(f"  Optimized path edges: {opt_path_edges}")

# Compare edge sets
orig_edges_set = set(mst_paths_orig.get((u, v), []))
opt_edges_set = set(opt_path_edges)
print(f"  Edges in original but not optimized: {orig_edges_set - opt_edges_set}")
print(f"  Edges in optimized but not original: {opt_edges_set - orig_edges_set}")
