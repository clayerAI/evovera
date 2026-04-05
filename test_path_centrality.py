#!/usr/bin/env python3
"""
Test if lazy path centrality matches precomputed values.
"""

import sys
import random
sys.path.append('.')

# We need to modify the original algorithm to expose mst_paths
# Let's create a custom test

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

# Small n for testing
n = 10
points = generate_random_points(n, seed=42)

print("=== PATH CENTRALITY COMPARISON ===\n")
print(f"Testing with n={n}")

# We'll manually compute what the original algorithm does
# First, compute MST
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
solver = ChristofidesHybridStructuralCorrected(points=points, seed=42)

# Get MST
mst_adj, _ = solver._compute_mst()

# Get edge centrality
edge_centrality = solver._compute_edge_centrality(mst_adj)

# Build MST paths (this is O(n²) in original)
print("Building MST paths (original O(n²) method)...")
mst_paths = solver._build_mst_paths(mst_adj)

# Compute path centrality for all pairs (original)
print("Computing path centrality for all pairs...")
path_centrality_orig = solver._compute_path_centrality(mst_paths, edge_centrality)

print(f"\nComputed path centrality for {len(path_centrality_orig)} pairs")

# Now test the optimized lazy computation
print("\nTesting optimized lazy computation...")
from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)

# Build LCA structure
solver_opt._build_lca_structure(mst_adj)

# Test a few pairs
test_pairs = [(0, 1), (0, 5), (2, 7), (3, 8), (4, 9)]
print(f"\nComparing {len(test_pairs)} pairs:")
mismatches = []

for u, v in test_pairs:
    # Original (precomputed)
    key = (min(u, v), max(u, v))
    orig_val = path_centrality_orig.get(key, 0.0)
    
    # Optimized (lazy)
    opt_val = solver_opt._compute_path_centrality_lazy(u, v, edge_centrality)
    
    diff = abs(orig_val - opt_val)
    match = diff < 0.001
    
    print(f"  Pair ({u}, {v}): orig={orig_val:.4f}, opt={opt_val:.4f}, diff={diff:.4f}, match={match}")
    
    if not match:
        mismatches.append((u, v, orig_val, opt_val, diff))

if mismatches:
    print(f"\nFound {len(mismatches)} mismatches!")
    for u, v, orig, opt, diff in mismatches:
        print(f"  ({u}, {v}): orig={orig:.4f}, opt={opt:.4f}, diff={diff:.4f}")
else:
    print("\nAll tested pairs match! Lazy computation is correct.")

# Let's also check what edges are on the path
print("\n=== PATH EDGE COMPARISON ===")
for u, v in test_pairs:
    # Get path edges using optimized method
    path_edges_opt = solver_opt._get_path_edges_lazy(u, v)
    
    # Get path edges from original
    key = (min(u, v), max(u, v))
    path_edges_orig = mst_paths.get(key, [])
    
    # Convert to sets for comparison
    set_opt = set(path_edges_opt)
    set_orig = set(path_edges_orig)
    
    print(f"\nPair ({u}, {v}):")
    print(f"  Optimized path edges ({len(path_edges_opt)}): {sorted(path_edges_opt)}")
    print(f"  Original path edges ({len(path_edges_orig)}): {sorted(path_edges_orig)}")
    print(f"  Same edges: {set_opt == set_orig}")
    if set_opt != set_orig:
        print(f"  Only in optimized: {set_opt - set_orig}")
        print(f"  Only in original: {set_orig - set_opt}")
