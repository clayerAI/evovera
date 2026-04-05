#!/usr/bin/env python3
"""
Prototype for optimized edge centrality computation using LCA structure.
"""

import random
import time
from typing import List, Tuple, Dict
import sys

class LCA:
    """Lowest Common Ancestor structure for O(1) path queries."""
    def __init__(self, n: int, adj: List[List[Tuple[int, float]]], root: int = 0):
        self.n = n
        self.log_n = (n).bit_length()
        self.depth = [0] * n
        self.parent = [-1] * n
        self.up = [[-1] * self.log_n for _ in range(n)]
        
        # DFS to build parent and depth
        stack = [(root, -1)]
        while stack:
            v, p = stack.pop()
            self.parent[v] = p
            if p != -1:
                self.depth[v] = self.depth[p] + 1
            self.up[v][0] = p
            
            for neighbor, _ in adj[v]:
                if neighbor != p:
                    stack.append((neighbor, v))
        
        # Build binary lifting table
        for j in range(1, self.log_n):
            for v in range(n):
                if self.up[v][j-1] != -1:
                    self.up[v][j] = self.up[self.up[v][j-1]][j-1]
    
    def lca(self, u: int, v: int) -> int:
        """Find lowest common ancestor of u and v."""
        if self.depth[u] < self.depth[v]:
            u, v = v, u
        
        # Lift u to same depth as v
        diff = self.depth[u] - self.depth[v]
        for j in range(self.log_n):
            if diff & (1 << j):
                u = self.up[u][j]
        
        if u == v:
            return u
        
        # Lift both nodes together
        for j in range(self.log_n - 1, -1, -1):
            if self.up[u][j] != self.up[v][j]:
                u = self.up[u][j]
                v = self.up[v][j]
        
        return self.parent[u]
    
    def get_path_edges(self, u: int, v: int, adj: List[List[Tuple[int, float]]]) -> List[Tuple[int, int]]:
        """Get edges on path from u to v."""
        lca_node = self.lca(u, v)
        path_edges = []
        
        # Collect edges from u to lca
        current = u
        while current != lca_node:
            parent = self.parent[current]
            path_edges.append((min(current, parent), max(current, parent)))
            current = parent
        
        # Collect edges from v to lca
        current = v
        while current != lca_node:
            parent = self.parent[current]
            path_edges.append((min(current, parent), max(current, parent)))
            current = parent
        
        return path_edges

class EdgeCentralityOptimizer:
    def __init__(self, n: int, mst_adj: List[List[Tuple[int, float]]]):
        self.n = n
        self.mst_adj = mst_adj
        self.lca = LCA(n, mst_adj)
    
    def compute_exact(self) -> Dict[Tuple[int, int], float]:
        """Exact O(n³) computation (original method)."""
        edge_counts = {}
        for u in range(self.n):
            for v, _ in self.mst_adj[u]:
                if u < v:
                    edge_counts[(u, v)] = 0
        
        for i in range(self.n):
            for j in range(i + 1, self.n):
                path_edges = self.lca.get_path_edges(i, j, self.mst_adj)
                for edge in path_edges:
                    edge_counts[edge] = edge_counts.get(edge, 0) + 1
        
        max_count = max(edge_counts.values()) if edge_counts else 1
        return {edge: count / max_count for edge, count in edge_counts.items()}
    
    def compute_sampling(self, sample_size: int = 1000) -> Dict[Tuple[int, int], float]:
        """Sampling-based approximation O(k log n)."""
        edge_counts = {}
        n_pairs = self.n * (self.n - 1) // 2
        k = min(sample_size, n_pairs)
        
        # Sample k vertex pairs
        for _ in range(k):
            i, j = random.sample(range(self.n), 2)
            path_edges = self.lca.get_path_edges(i, j, self.mst_adj)
            for edge in path_edges:
                edge_counts[edge] = edge_counts.get(edge, 0) + 1
        
        # Scale results
        scale_factor = n_pairs / k if k < n_pairs else 1
        scaled_counts = {edge: count * scale_factor for edge, count in edge_counts.items()}
        
        max_count = max(scaled_counts.values()) if scaled_counts else 1
        return {edge: count / max_count for edge, count in scaled_counts.items()}
    
    def compute_mst_property(self) -> Dict[Tuple[int, int], float]:
        """MST property-based computation O(n²)."""
        # Build component sizes for each edge removal
        edge_centrality = {}
        
        # For each edge in MST, compute component sizes
        for u in range(self.n):
            for v, _ in self.mst_adj[u]:
                if u < v:
                    # Count vertices in component containing u when edge (u,v) is removed
                    visited = [False] * self.n
                    stack = [u]
                    visited[u] = True
                    count = 0
                    
                    while stack:
                        node = stack.pop()
                        count += 1
                        for neighbor, _ in self.mst_adj[node]:
                            if not visited[neighbor] and not (node == u and neighbor == v) and not (node == v and neighbor == u):
                                visited[neighbor] = True
                                stack.append(neighbor)
                    
                    # Centrality = |component_u| × |component_v|
                    centrality = count * (self.n - count)
                    edge_centrality[(u, v)] = centrality
        
        max_centrality = max(edge_centrality.values()) if edge_centrality else 1
        return {edge: c / max_centrality for edge, c in edge_centrality.items()}
    
    def compute_adaptive(self) -> Dict[Tuple[int, int], float]:
        """Adaptive computation based on instance size."""
        if self.n <= 100:
            return self.compute_exact()
        elif self.n <= 300:
            sample_size = min(2000, self.n * (self.n - 1) // 2)
            return self.compute_sampling(sample_size)
        else:
            return self.compute_mst_property()

def generate_random_mst(n: int) -> List[List[Tuple[int, float]]]:
    """Generate a random tree (MST) with n nodes."""
    adj = [[] for _ in range(n)]
    
    # Create a random tree using Prüfer sequence
    if n <= 1:
        return adj
    
    # Generate random Prüfer sequence
    prufer = [random.randint(0, n-1) for _ in range(n-2)]
    
    # Count degree of each vertex
    degree = [1] * n
    for v in prufer:
        degree[v] += 1
    
    # Reconstruct tree
    for v in prufer:
        for u in range(n):
            if degree[u] == 1:
                # Add edge (u, v)
                adj[u].append((v, random.random()))
                adj[v].append((u, random.random()))
                degree[u] -= 1
                degree[v] -= 1
                break
    
    # Add last edge
    remaining = [u for u in range(n) if degree[u] == 1]
    if len(remaining) == 2:
        u, v = remaining
        adj[u].append((v, random.random()))
        adj[v].append((u, random.random()))
    
    return adj

def test_methods():
    """Test different centrality computation methods."""
    sizes = [50, 100, 150, 200]
    
    for n in sizes:
        print(f"\n=== Testing n={n} ===")
        mst_adj = generate_random_mst(n)
        optimizer = EdgeCentralityOptimizer(n, mst_adj)
        
        # Test exact method
        start = time.time()
        exact = optimizer.compute_exact()
        exact_time = time.time() - start
        print(f"Exact: {exact_time:.3f}s, {len(exact)} edges")
        
        # Test sampling method
        start = time.time()
        sampling = optimizer.compute_sampling(1000)
        sampling_time = time.time() - start
        
        # Compare with exact
        mae = 0.0
        for edge in exact:
            exact_val = exact.get(edge, 0)
            sampling_val = sampling.get(edge, 0)
            mae += abs(exact_val - sampling_val)
        mae /= len(exact) if exact else 1
        
        print(f"Sampling: {sampling_time:.3f}s, MAE={mae:.4f}")
        
        # Test MST property method
        start = time.time()
        mst_prop = optimizer.compute_mst_property()
        mst_time = time.time() - start
        
        # Compare with exact
        mae2 = 0.0
        for edge in exact:
            exact_val = exact.get(edge, 0)
            mst_val = mst_prop.get(edge, 0)
            mae2 += abs(exact_val - mst_val)
        mae2 /= len(exact) if exact else 1
        
        print(f"MST Property: {mst_time:.3f}s, MAE={mae2:.4f}")
        
        # Test adaptive
        start = time.time()
        adaptive = optimizer.compute_adaptive()
        adaptive_time = time.time() - start
        
        print(f"Adaptive: {adaptive_time:.3f}s")

if __name__ == "__main__":
    test_methods()
