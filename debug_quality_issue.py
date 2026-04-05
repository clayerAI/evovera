#!/usr/bin/env python3
"""Debug why optimized algorithm produces worse solutions."""

import sys
sys.path.append(".")

import random
import math
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalSolver
from solutions.tsp_v19_optimized_fixed_v5 import ChristofidesHybridStructuralOptimized as OptimizedSolver

def generate_points(n, seed=42):
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def compare_mst(points):
    """Compare MST construction between original and optimized."""
    solver1 = OriginalSolver(points, seed=42)
    solver2 = OptimizedSolver(points, seed=42)
    
    # Get MST from original
    mst_adj1, parent1 = solver1._compute_mst()
    
    # Get MST from optimized
    mst_adj2, parent2 = solver2._compute_mst()
    
    print("\n=== MST COMPARISON ===")
    
    # Compare parent arrays
    if parent1 == parent2:
        print("✓ Parent arrays are identical")
    else:
        print("✗ Parent arrays differ")
        diff_count = sum(1 for i in range(len(parent1)) if parent1[i] != parent2[i])
        print(f"  {diff_count}/{len(parent1)} vertices have different parents")
    
    # Compare MST adjacency
    edges1 = set()
    for u in range(len(mst_adj1)):
        for v, w in mst_adj1[u]:
            if u < v:
                edges1.add((u, v))
    
    edges2 = set()
    for u in range(len(mst_adj2)):
        for v, w in mst_adj2[u]:
            if u < v:
                edges2.add((u, v))
    
    if edges1 == edges2:
        print("✓ MST edges are identical")
    else:
        print("✗ MST edges differ")
        print(f"  Original has {len(edges1)} edges")
        print(f"  Optimized has {len(edges2)} edges")
        print(f"  Common edges: {len(edges1 & edges2)}")
        print(f"  Only in original: {len(edges1 - edges2)}")
        print(f"  Only in optimized: {len(edges2 - edges1)}")
    
    # Compare MST total weight
    weight1 = 0
    for u in range(len(mst_adj1)):
        for v, w in mst_adj1[u]:
            if u < v:
                weight1 += w
    
    weight2 = 0
    for u in range(len(mst_adj2)):
        for v, w in mst_adj2[u]:
            if u < v:
                weight2 += w
    
    print(f"\nMST total weight:")
    print(f"  Original: {weight1:.2f}")
    print(f"  Optimized: {weight2:.2f}")
    print(f"  Difference: {weight2 - weight1:.2f} ({((weight2/weight1)-1)*100:.2f}%)")
    
    return edges1, edges2, weight1, weight2

def compare_edge_centrality(points, edges1, edges2):
    """Compare edge centrality computation."""
    solver1 = OriginalSolver(points, seed=42)
    solver2 = OptimizedSolver(points, seed=42)
    
    # Get MST for each
    mst_adj1, parent1 = solver1._compute_mst()
    mst_adj2, parent2 = solver2._compute_mst()
    
    # Build LCA structure for optimized
    solver2._build_lca_structure(parent2)
    
    print("\n=== EDGE CENTRALITY COMPARISON ===")
    
    # Original edge centrality
    edge_cent1 = solver1._compute_edge_centrality(mst_adj1)
    
    # Optimized edge centrality
    edge_cent2 = solver2._compute_edge_centrality(mst_adj2)
    
    # Compare common edges
    common_edges = set(edge_cent1.keys()) & set(edge_cent2.keys())
    print(f"Common edges: {len(common_edges)}")
    
    if common_edges:
        max_diff = 0
        total_diff = 0
        for edge in list(common_edges)[:10]:  # Sample first 10
            diff = abs(edge_cent1[edge] - edge_cent2[edge])
            total_diff += diff
            if diff > max_diff:
                max_diff = diff
            if diff > 0.01:
                print(f"  Edge {edge}: original={edge_cent1[edge]:.4f}, optimized={edge_cent2[edge]:.4f}, diff={diff:.4f}")
        
        avg_diff = total_diff / len(common_edges)
        print(f"\nAverage difference: {avg_diff:.6f}")
        print(f"Maximum difference: {max_diff:.6f}")
    
    return edge_cent1, edge_cent2

def compare_communities(points):
    """Compare community detection."""
    solver1 = OriginalSolver(points, seed=42)
    solver2 = OptimizedSolver(points, seed=42)
    
    mst_adj1, parent1 = solver1._compute_mst()
    mst_adj2, parent2 = solver2._compute_mst()
    
    print("\n=== COMMUNITY DETECTION COMPARISON ===")
    
    comm1 = solver1._detect_communities(mst_adj1, percentile_threshold=70)
    comm2 = solver2._detect_communities(mst_adj2, percentile_threshold=70)
    
    # Count communities
    unique1 = len(set(comm1.values()))
    unique2 = len(set(comm2.values()))
    
    print(f"Original: {unique1} communities")
    print(f"Optimized: {unique2} communities")
    
    # Check if assignments match
    matches = sum(1 for i in range(len(points)) if comm1.get(i, -1) == comm2.get(i, -1))
    print(f"Vertex assignments match: {matches}/{len(points)} ({matches/len(points)*100:.1f}%)")
    
    return comm1, comm2

if __name__ == "__main__":
    n = 50
    points = generate_points(n, 42)
    
    print(f"Testing with n={n} points")
    
    # Compare MST
    edges1, edges2, weight1, weight2 = compare_mst(points)
    
    # Compare edge centrality
    edge_cent1, edge_cent2 = compare_edge_centrality(points, edges1, edges2)
    
    # Compare communities
    comm1, comm2 = compare_communities(points)
    
    # Run full algorithms to see final tours
    print("\n=== FINAL TOUR COMPARISON ===")
    
    solver1 = OriginalSolver(points, seed=42)
    tour1, length1, _ = solver1.solve(apply_2opt=False)
    
    solver2 = OptimizedSolver(points, seed=42)
    tour2, length2, _ = solver2.solve(apply_2opt=False)
    
    print(f"Original tour length: {length1:.2f}")
    print(f"Optimized tour length: {length2:.2f}")
    print(f"Difference: {length2 - length1:.2f} ({((length2/length1)-1)*100:.2f}%)")
    
    # Check if tours are valid
    def is_valid_tour(tour, n):
        return len(set(tour)) == n and tour[0] == tour[-1] and len(tour) == n + 1
    
    print(f"\nTour validity:")
    print(f"  Original: {is_valid_tour(tour1, n)} (length {len(tour1)}, unique {len(set(tour1))})")
    print(f"  Optimized: {is_valid_tour(tour2, n)} (length {len(tour2)}, unique {len(set(tour2))})")
