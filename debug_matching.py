#!/usr/bin/env python3
"""Debug matching step differences."""

import sys
sys.path.append(".")

import random
import math
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected as OriginalSolver
from solutions.tsp_v19_optimized_fixed_v5 import ChristofidesHybridStructuralOptimized as OptimizedSolver

def generate_points(n, seed=42):
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def compare_matching(points):
    """Compare matching step between original and optimized."""
    solver1 = OriginalSolver(points, seed=42)
    solver2 = OptimizedSolver(points, seed=42)
    
    # Run up to matching step
    mst_adj1, parent1 = solver1._compute_mst()
    mst_adj2, parent2 = solver2._compute_mst()
    
    # Build LCA for optimized
    solver2._build_lca_structure(parent2)
    
    # Get edge centrality
    edge_cent1 = solver1._compute_edge_centrality(mst_adj1)
    edge_cent2 = solver2._compute_edge_centrality(mst_adj2)
    
    # Get communities
    comm1 = solver1._detect_communities(mst_adj1, percentile_threshold=70)
    comm2 = solver2._detect_communities(mst_adj2, percentile_threshold=70)
    
    # Get odd vertices
    degrees1 = [0] * len(points)
    degrees2 = [0] * len(points)
    for u in range(len(points)):
        degrees1[u] = len(mst_adj1[u])
        degrees2[u] = len(mst_adj2[u])
    
    odd1 = [i for i in range(len(points)) if degrees1[i] % 2 == 1]
    odd2 = [i for i in range(len(points)) if degrees2[i] % 2 == 1]
    
    print("\n=== ODD VERTICES COMPARISON ===")
    print(f"Original odd vertices ({len(odd1)}): {sorted(odd1)}")
    print(f"Optimized odd vertices ({len(odd2)}): {sorted(odd2)}")
    
    if odd1 == odd2:
        print("✓ Odd vertices are identical")
    else:
        print("✗ Odd vertices differ")
    
    # Get matching
    matching1 = solver1._hybrid_structural_matching(
        odd1, comm1, edge_cent1,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    
    matching2 = solver2._hybrid_structural_matching_optimized(
        odd2, comm2, edge_cent2,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    
    print("\n=== MATCHING COMPARISON ===")
    print(f"Original matching ({len(matching1)} pairs): {sorted(matching1)}")
    print(f"Optimized matching ({len(matching2)} pairs): {sorted(matching2)}")
    
    # Convert to sets for comparison
    matching1_set = set(tuple(sorted(pair)) for pair in matching1)
    matching2_set = set(tuple(sorted(pair)) for pair in matching2)
    
    if matching1_set == matching2_set:
        print("✓ Matchings are identical")
    else:
        print("✗ Matchings differ")
        print(f"  Common pairs: {len(matching1_set & matching2_set)}")
        print(f"  Only in original: {matching1_set - matching2_set}")
        print(f"  Only in optimized: {matching2_set - matching1_set}")
    
    # Compare matching weights
    total_weight1 = 0
    for u, v in matching1:
        total_weight1 += solver1.dist_matrix[u][v]
    
    total_weight2 = 0
    for u, v in matching2:
        total_weight2 += solver2.dist_matrix[u][v]
    
    print(f"\nMatching total weight:")
    print(f"  Original: {total_weight1:.2f}")
    print(f"  Optimized: {total_weight2:.2f}")
    print(f"  Difference: {total_weight2 - total_weight1:.2f}")
    
    return matching1, matching2, odd1, odd2

def compare_euler_circuit(points, matching1, matching2, odd1, odd2):
    """Compare Euler circuit construction."""
    solver1 = OriginalSolver(points, seed=42)
    solver2 = OptimizedSolver(points, seed=42)
    
    mst_adj1, parent1 = solver1._compute_mst()
    mst_adj2, parent2 = solver2._compute_mst()
    
    print("\n=== EULER CIRCUIT COMPARISON ===")
    
    # Build Euler graph for original
    euler_adj1 = [[] for _ in range(len(points))]
    for u in range(len(points)):
        for v, _ in mst_adj1[u]:
            if u < v:
                euler_adj1[u].append(v)
                euler_adj1[v].append(u)
    
    for u, v in matching1:
        euler_adj1[u].append(v)
        euler_adj1[v].append(u)
    
    # Build Euler graph for optimized
    euler_adj2 = [[] for _ in range(len(points))]
    for u in range(len(points)):
        for v, _ in mst_adj2[u]:
            if u < v:
                euler_adj2[u].append(v)
                euler_adj2[v].append(u)
    
    for u, v in matching2:
        euler_adj2[u].append(v)
        euler_adj2[v].append(u)
    
    # Check if graphs are identical
    identical = True
    for u in range(len(points)):
        if sorted(euler_adj1[u]) != sorted(euler_adj2[u]):
            print(f"✗ Vertex {u} adjacency differs:")
            print(f"  Original: {sorted(euler_adj1[u])}")
            print(f"  Optimized: {sorted(euler_adj2[u])}")
            identical = False
    
    if identical:
        print("✓ Euler graphs are identical")
    
    return euler_adj1, euler_adj2

if __name__ == "__main__":
    n = 30  # Smaller for debugging
    points = generate_points(n, 42)
    
    print(f"Testing with n={n} points")
    
    # Compare matching
    matching1, matching2, odd1, odd2 = compare_matching(points)
    
    # Compare Euler circuit
    euler_adj1, euler_adj2 = compare_euler_circuit(points, matching1, matching2, odd1, odd2)
    
    # Run full algorithms to see where difference occurs
    print("\n=== STEP-BY-STEP COMPARISON ===")
    
    solver1 = OriginalSolver(points, seed=42)
    
    # Original step by step
    print("\nOriginal algorithm steps:")
    mst_adj1, parent1 = solver1._compute_mst()
    print(f"1. MST computed: {len(mst_adj1)} vertices")
    
    edge_cent1 = solver1._compute_edge_centrality(mst_adj1)
    print(f"2. Edge centrality: {len(edge_cent1)} edges")
    
    comm1 = solver1._detect_communities(mst_adj1, percentile_threshold=70)
    print(f"3. Communities: {len(set(comm1.values()))} communities")
    
    degrees1 = [len(mst_adj1[u]) for u in range(n)]
    odd1 = [i for i in range(n) if degrees1[i] % 2 == 1]
    print(f"4. Odd vertices: {len(odd1)} vertices")
    
    matching1 = solver1._hybrid_structural_matching(
        odd1, comm1, edge_cent1,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    print(f"5. Matching: {len(matching1)} pairs")
    
    # Build Euler graph
    euler_adj1 = [[] for _ in range(n)]
    for u in range(n):
        for v, _ in mst_adj1[u]:
            if u < v:
                euler_adj1[u].append(v)
                euler_adj1[v].append(u)
    
    for u, v in matching1:
        euler_adj1[u].append(v)
        euler_adj1[v].append(u)
    
    print(f"6. Euler graph degrees: {[len(euler_adj1[u]) for u in range(n)]}")
    
    # Check if all vertices have even degree (required for Euler circuit)
    all_even1 = all(len(euler_adj1[u]) % 2 == 0 for u in range(n))
    print(f"7. All vertices have even degree: {all_even1}")
