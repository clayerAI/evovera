#!/usr/bin/env python3
"""
Analyze MST connections between odd-degree vertices.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching
import random

def generate_random_points(n: int = 30, seed: int = 42) -> list:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def analyze_mst_odd_connections(points):
    """Analyze which odd-degree vertices are connected in MST."""
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # Compute MST
    mst_adj = solver._compute_mst()
    
    # Find odd degree vertices
    odd_vertices = solver._find_odd_degree_vertices(mst_adj)
    
    print(f"Total vertices: {len(points)}")
    print(f"Odd-degree vertices: {odd_vertices}")
    print(f"Number of odd vertices: {len(odd_vertices)}")
    
    # Check which odd vertices are connected in MST
    mst_edges = set()
    for u in range(len(points)):
        for v, _ in mst_adj[u]:
            if u < v:
                mst_edges.add((u, v))
    
    print("\n=== MST edges between odd vertices ===")
    odd_connections = []
    for u in odd_vertices:
        for v in odd_vertices:
            if u < v and (u, v) in mst_edges:
                odd_connections.append((u, v))
                print(f"Odd vertices {u} and {v} are connected in MST")
    
    print(f"\nTotal MST edges between odd vertices: {len(odd_connections)}")
    
    # Check all possible edges between odd vertices
    print("\n=== All possible edges between odd vertices ===")
    total_possible = len(odd_vertices) * (len(odd_vertices) - 1) // 2
    print(f"Total possible edges between odd vertices: {total_possible}")
    print(f"MST edges cover {len(odd_connections)}/{total_possible} = {len(odd_connections)/total_possible*100:.1f}%")
    
    # Analyze centrality for edges between odd vertices
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    
    print("\n=== Centrality for edges between odd vertices ===")
    for u, v in odd_connections:
        centrality = edge_centrality.get((min(u, v), max(u, v)), 0.0)
        print(f"Edge ({u}, {v}): centrality={centrality:.4f}")
    
    # Check a sample of non-MST edges between odd vertices
    print("\n=== Sample of non-MST edges between odd vertices ===")
    sample_count = 0
    for i in range(len(odd_vertices)):
        for j in range(i + 1, len(odd_vertices)):
            u, v = odd_vertices[i], odd_vertices[j]
            if (u, v) not in mst_edges and (v, u) not in mst_edges:
                if sample_count < 10:
                    centrality = edge_centrality.get((min(u, v), max(u, v)), 0.0)
                    distance = solver.dist_matrix[u][v]
                    print(f"Non-MST edge ({u}, {v}): distance={distance:.4f}, centrality={centrality:.4f}")
                    sample_count += 1

def main():
    points = generate_random_points(n=30, seed=42)
    analyze_mst_odd_connections(points)

if __name__ == "__main__":
    main()