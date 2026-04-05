#!/usr/bin/env python3
"""
Compare edge centrality computations.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== COMPARING EDGE CENTRALITY ===\n")
    
    # Get MST from original algorithm
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=42)
    
    # We need to run part of the algorithm to get MST
    # Let me copy the relevant code
    n = solver_orig.n
    
    # Compute MST using Prim's (same as in original)
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
    
    print(f"MST edges:")
    for u in range(n):
        for v, w in mst_adj[u]:
            if u < v:
                print(f"  ({u},{v}): weight={w:.2f}")
    
    # Compute edge centrality using original method
    print("\n=== ORIGINAL EDGE CENTRALITY ===")
    
    # Build parent array for path reconstruction (BFS from 0)
    parent_bfs = [-1] * n
    visited_bfs = [False] * n
    queue = [0]
    visited_bfs[0] = True
    
    while queue:
        u = queue.pop(0)
        for v, _ in mst_adj[u]:
            if not visited_bfs[v]:
                visited_bfs[v] = True
                parent_bfs[v] = u
                queue.append(v)
    
    # Initialize edge counts
    edge_counts = {}
    for u in range(n):
        for v, _ in mst_adj[u]:
            if u < v:
                edge_counts[(u, v)] = 0
    
    # Count paths through each edge
    for i in range(n):
        for j in range(i + 1, n):
            # Find path from i to j in tree
            path_i_to_j = set()
            
            # Trace from i to root
            node = i
            while node != -1:
                path_i_to_j.add(node)
                node = parent_bfs[node]
            
            # Trace from j until we hit path_i_to_j
            node = j
            while node not in path_i_to_j:
                node = parent_bfs[node]
            
            lca = node  # Lowest common ancestor
            
            # Count edges from i to LCA
            node = i
            while node != lca:
                next_node = parent_bfs[node]
                edge = (min(node, next_node), max(node, next_node))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1
                node = next_node
            
            # Count edges from j to LCA
            node = j
            while node != lca:
                next_node = parent_bfs[node]
                edge = (min(node, next_node), max(node, next_node))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1
                node = next_node
    
    # Normalize
    max_count = max(edge_counts.values()) if edge_counts else 1
    edge_centrality_orig = {edge: count / max_count for edge, count in edge_counts.items()}
    
    for edge, cent in sorted(edge_centrality_orig.items()):
        print(f"  {edge}: {cent:.4f}")
    
    # Compute edge centrality using optimized method (subtree sizes)
    print("\n=== OPTIMIZED EDGE CENTRALITY (subtree sizes) ===")
    
    # DFS to compute subtree sizes
    visited_dfs = [False] * n
    subtree_size = [0] * n
    edge_centrality_opt = {}
    
    def dfs(node: int) -> int:
        visited_dfs[node] = True
        size = 1
        
        for neighbor, _ in mst_adj[node]:
            if not visited_dfs[neighbor]:
                child_size = dfs(neighbor)
                size += child_size
                
                # Edge centrality = (child_size) * (n - child_size)
                edge = (min(node, neighbor), max(node, neighbor))
                edge_centrality_opt[edge] = child_size * (n - child_size)
        
        subtree_size[node] = size
        return size
    
    dfs(0)
    
    # Normalize
    max_val = max(edge_centrality_opt.values()) if edge_centrality_opt else 1
    for edge in edge_centrality_opt:
        edge_centrality_opt[edge] /= max_val
    
    for edge, cent in sorted(edge_centrality_opt.items()):
        print(f"  {edge}: {cent:.4f}")
    
    # Compare
    print("\n=== COMPARISON ===")
    all_edges = set(edge_centrality_orig.keys()) | set(edge_centrality_opt.keys())
    
    for edge in sorted(all_edges):
        orig = edge_centrality_orig.get(edge, 0.0)
        opt = edge_centrality_opt.get(edge, 0.0)
        diff = abs(orig - opt)
        print(f"  {edge}: orig={orig:.6f}, opt={opt:.6f}, diff={diff:.6f} {'✅' if diff < 1e-10 else '❌'}")

if __name__ == "__main__":
    main()
