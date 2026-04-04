#!/usr/bin/env python3
"""
Debug centrality calculation in v14.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching
import random
import math

def generate_random_points(n: int = 30, seed: int = 42) -> list:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def analyze_centrality_calculation(points):
    """Analyze how centrality is calculated."""
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # Compute MST
    mst_adj = solver._compute_mst()
    
    # Compute edge centrality
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    
    print(f"Total edges in MST: {sum(len(adj) for adj in mst_adj)//2}")
    print(f"Edges with centrality > 0: {sum(1 for c in edge_centrality.values() if c > 0)}")
    
    # Print centrality values
    print("\n=== Edge centrality values ===")
    for (u, v), centrality in sorted(edge_centrality.items(), key=lambda x: x[1], reverse=True):
        if centrality > 0:
            print(f"Edge ({u}, {v}): centrality={centrality:.4f}")
    
    # Analyze MST structure
    print("\n=== MST structure analysis ===")
    
    # Build adjacency for analysis
    adj = [[] for _ in range(len(points))]
    for u in range(len(points)):
        for v, _ in mst_adj[u]:
            if u < v:
                adj[u].append(v)
                adj[v].append(u)
    
    # Find tree center and distances
    n = len(points)
    
    def bfs_distances(start):
        dist = [-1] * n
        dist[start] = 0
        queue = [start]
        while queue:
            u = queue.pop(0)
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        return dist
    
    # Find tree center
    # First BFS from arbitrary node
    dist1 = bfs_distances(0)
    farthest1 = max(range(n), key=lambda i: dist1[i])
    
    # Second BFS from farthest node
    dist2 = bfs_distances(farthest1)
    farthest2 = max(range(n), key=lambda i: dist2[i])
    
    # Third BFS from second farthest
    dist3 = bfs_distances(farthest2)
    
    # Eccentricity = max distance to any leaf
    eccentricity = [max(dist2[i], dist3[i]) for i in range(n)]
    center = min(range(n), key=lambda i: eccentricity[i])
    
    print(f"Tree center: vertex {center}")
    print(f"Center eccentricity: {eccentricity[center]}")
    
    # Distances from center
    dist_from_center = bfs_distances(center)
    
    print("\n=== Vertex distances from center ===")
    for i in range(min(20, n)):
        print(f"Vertex {i}: distance from center = {dist_from_center[i]}")
    
    # Show edges with their endpoint distances
    print("\n=== Edges with endpoint distances from center ===")
    for (u, v), centrality in edge_centrality.items():
        if centrality > 0:
            min_dist = min(dist_from_center[u], dist_from_center[v])
            print(f"Edge ({u}, {v}): centrality={centrality:.4f}, "
                  f"min_dist_to_center={min_dist}, "
                  f"formula=1/(1+{min_dist})={1/(1+min_dist):.4f}")

def main():
    points = generate_random_points(n=30, seed=42)
    analyze_centrality_calculation(points)

if __name__ == "__main__":
    main()