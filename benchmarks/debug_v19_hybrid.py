#!/usr/bin/env python3
"""
Debug script for v19 hybrid algorithm.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
from typing import List, Tuple

from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def debug_hybrid_algorithm():
    """Debug the hybrid algorithm to understand why it matches v16."""
    n = 30
    seed = 42
    
    print(f"Debugging v19 hybrid algorithm with n={n}, seed={seed}")
    print("=" * 60)
    
    # Generate points
    points = generate_random_points(n, seed)
    
    # Create solver
    solver = ChristofidesHybridStructural(points, seed=seed)
    
    # Compute MST
    mst_adj, parent = solver._compute_mst()
    print(f"MST computed with {len(mst_adj)} vertices")
    
    # Detect communities
    communities = solver._detect_communities(mst_adj, percentile_threshold=50.0)
    print(f"Communities detected: {len(set(communities))} unique communities")
    print(f"Community distribution: {communities}")
    
    # Compute edge centrality
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    print(f"Edge centrality computed for {len(edge_centrality)} edges")
    
    # Build MST paths
    mst_paths = solver._build_mst_paths(mst_adj)
    print(f"MST paths computed for {len(mst_paths)} vertex pairs")
    
    # Compute path centrality
    path_centrality = solver._compute_path_centrality(mst_paths, edge_centrality)
    print(f"Path centrality computed for {len(path_centrality)} vertex pairs")
    
    # Find odd-degree vertices
    odd_vertices = solver._find_odd_degree_vertices(mst_adj)
    print(f"Odd-degree vertices: {odd_vertices} (count: {len(odd_vertices)})")
    
    # Test hybrid matching with different weights
    print("\nTesting hybrid matching with different weight configurations:")
    
    # Configuration 1: Default weights (should behave like v16 if communities don't affect matching)
    matching1 = solver._hybrid_structural_matching(
        odd_vertices, communities, path_centrality,
        within_community_weight=0.5,
        between_community_weight=0.3,
        cross_community_weight=0.1
    )
    print(f"  Default weights: {len(matching1)} matches")
    
    # Configuration 2: Zero centrality influence (pure greedy)
    matching2 = solver._hybrid_structural_matching(
        odd_vertices, communities, path_centrality,
        within_community_weight=0.0,
        between_community_weight=0.0,
        cross_community_weight=0.0
    )
    print(f"  Zero centrality: {len(matching2)} matches")
    
    # Configuration 3: Maximum centrality influence
    matching3 = solver._hybrid_structural_matching(
        odd_vertices, communities, path_centrality,
        within_community_weight=1.0,
        between_community_weight=1.0,
        cross_community_weight=1.0
    )
    print(f"  Max centrality: {len(matching3)} matches")
    
    # Check if matchings are different
    print(f"\nMatching comparisons:")
    print(f"  Default vs Zero: {matching1 == matching2}")
    print(f"  Default vs Max: {matching1 == matching3}")
    
    # Let's examine community relationships for odd vertices
    print(f"\nCommunity analysis for odd vertices:")
    for i, v in enumerate(odd_vertices):
        print(f"  Vertex {v}: community {communities[v]}")
    
    # Count how many odd vertices are in each community
    community_counts = {}
    for v in odd_vertices:
        comm = communities[v]
        community_counts[comm] = community_counts.get(comm, 0) + 1
    
    print(f"\nOdd vertices per community: {community_counts}")
    
    # Check if communities affect matching decisions
    print(f"\nChecking if community structure affects edge scores:")
    sample_edges = []
    for i in range(min(5, len(odd_vertices))):
        for j in range(i+1, min(5, len(odd_vertices))):
            u = odd_vertices[i]
            v = odd_vertices[j]
            distance = solver.dist_matrix[u][v]
            key = (min(u, v), max(u, v))
            centrality = path_centrality.get(key, 0.0)
            
            # Determine community relationship
            if communities[u] == communities[v]:
                weight = 0.5  # within_community_weight
                rel = "WITHIN"
            else:
                weight = 0.3  # between_community_weight
                rel = "BETWEEN"
            
            score = distance * (1.0 - weight * centrality)
            sample_edges.append((u, v, distance, centrality, weight, score, rel))
    
    print(f"  Sample edges (u, v, distance, centrality, weight, score, relationship):")
    for edge in sample_edges:
        print(f"    {edge[0]}-{edge[1]}: dist={edge[2]:.2f}, cent={edge[3]:.3f}, "
              f"weight={edge[4]}, score={edge[5]:.2f}, {edge[6]}")

if __name__ == "__main__":
    debug_hybrid_algorithm()