#!/usr/bin/env python3
"""
Compare community detection.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== COMPARING COMMUNITY DETECTION ===\n")
    
    # Get MST (same for both)
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    
    # Compute MST
    n = solver_orig.n
    mst_adj = [[] for _ in range(n)]
    parent = [-1] * n
    visited = [False] * n
    min_edge = [float('inf')] * n
    min_edge[0] = 0.0
    
    for _ in range(n):
        u = -1
        for i in range(n):
            if not visited[i] and (u == -1 or min_edge[i] < min_edge[u]):
                u = i
        
        visited[u] = True
        
        if parent[u] != -1:
            p = parent[u]
            weight = solver_orig.dist_matrix[u][p]
            mst_adj[u].append((p, weight))
            mst_adj[p].append((u, weight))
        
        for v in range(n):
            if not visited[v] and solver_orig.dist_matrix[u][v] < min_edge[v]:
                min_edge[v] = solver_orig.dist_matrix[u][v]
                parent[v] = u
    
    # Run original community detection
    print("Running original community detection...")
    communities_orig = solver_orig._detect_communities(mst_adj)
    
    print(f"Original communities:")
    for i in range(n):
        print(f"  Vertex {i}: community {communities_orig.get(i, 0)}")
    
    # Run optimized community detection
    print("\nRunning optimized community detection...")
    from solutions.tsp_v19_optimized_fixed_v3 import ChristofidesHybridStructuralOptimized
    solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=42)
    communities_opt = solver_opt._detect_communities(mst_adj)
    
    print(f"Optimized communities:")
    for i in range(n):
        print(f"  Vertex {i}: community {communities_opt.get(i, 0)}")
    
    # Compare
    print("\n=== COMPARISON ===")
    match = all(communities_orig.get(i, 0) == communities_opt.get(i, 0) for i in range(n))
    print(f"Communities identical: {match}")
    
    if not match:
        print("\nDifferences:")
        for i in range(n):
            orig = communities_orig.get(i, 0)
            opt = communities_opt.get(i, 0)
            if orig != opt:
                print(f"  Vertex {i}: orig={orig}, opt={opt}")

if __name__ == "__main__":
    main()
