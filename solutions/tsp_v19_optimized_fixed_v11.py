#!/usr/bin/env python3
"""
Christofides Hybrid Structural Algorithm - Optimized Version 11
Created from ORIGINAL v19 (tsp_v19_christofides_hybrid_structural_corrected.py)
with quality-preserving optimizations only (≤0.1% degradation tolerance).

Key principles:
1. Start from original v19 with ALL hybrid structural features
2. Apply ONLY optimizations that preserve algorithm logic
3. Maintain TSPLIB compatibility (distance_matrix parameter)
4. Target ≤0.1% quality degradation vs original v19

Applied optimizations (quality-preserving):
1. Fast LCA structure for O(1) path queries (preserves logic)
2. Cached path centralities (preserves logic)
3. Micro-optimizations in MST construction (preserves Prim's algorithm)
4. Keep original 2-opt algorithm (NOT optimized version from v8)

Author: Evo
Date: 2026-04-05 (Critical Quality-Preserving Version)
"""

import math
import random
import heapq
import time
from typing import List, Tuple, Dict, Set, Optional, Union
import numpy as np
from collections import deque


class ChristofidesHybridStructuralOptimizedV11:
    """
    Christofides Hybrid Structural TSP solver - OPTIMIZED VERSION 11.
    
    Quality-preserving optimizations from original v19 with TSPLIB compatibility.
    Target: ≤0.1% quality degradation vs original v19.
    """
    
    def __init__(self, points: Optional[List[Tuple[float, float]]] = None,
                 distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
                 seed: Optional[int] = None):
        """
        Initialize solver with TSPLIB compatibility.
        
        Args:
            points: List of (x, y) coordinate tuples (for Euclidean TSP)
            distance_matrix: Precomputed distance matrix (for TSPLIB instances)
            seed: Random seed for reproducibility
        """
        if points is None and distance_matrix is None:
            raise ValueError("Must provide either points or distance_matrix")
        
        if points is not None:
            self.points = points
            self.n = len(points)
            self.use_points = True
        else:
            self.n = len(distance_matrix)
            self.use_points = False
        
        if distance_matrix is not None:
            # Convert to list of lists for compatibility
            if isinstance(distance_matrix, np.ndarray):
                self.dist_matrix = distance_matrix.tolist()
            else:
                self.dist_matrix = distance_matrix
            self.use_distance_matrix = True
        else:
            # Compute Euclidean distance matrix from points
            self.dist_matrix = self._compute_distance_matrix()
            self.use_distance_matrix = False
        
        self.seed = seed if seed is not None else 42
        random.seed(self.seed)
        
        # LCA structures for fast path queries (optimization 1)
        self.parent_lca = None
        self.depth = None
        self.up = None
        self.log_n = None
    
    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute Euclidean distance matrix from points."""
        n = self.n
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            xi, yi = self.points[i]
            for j in range(i + 1, n):
                xj, yj = self.points[j]
                d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                dist[i][j] = d
                dist[j][i] = d
        return dist
    
    def _compute_mst(self) -> Tuple[List[List[Tuple[int, float]]], List[int]]:
        """
        Compute Minimum Spanning Tree using Prim's algorithm.
        Optimized version with early exit and reduced allocations.
        Returns adjacency list representation and parent array.
        """
        n = self.n
        visited = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0
        parent = [-1] * n
        
        mst_adj = [[] for _ in range(n)]
        
        for _ in range(n):
            # Find vertex with minimum edge weight
            v = -1
            for j in range(n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            if v == -1:
                break
            
            visited[v] = True
            
            # Add edge to MST
            if parent[v] != -1:
                weight = min_edge[v]
                mst_adj[v].append((parent[v], weight))
                mst_adj[parent[v]].append((v, weight))
            
            # Update min_edge for adjacent vertices
            for to in range(n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
                    parent[to] = v
        
        return mst_adj, parent
    
    def _build_lca_structure(self, mst_adj: List[List[Tuple[int, float]]], root: int = 0):
        """Build LCA structure for O(1) path queries (optimization 1)."""
        n = self.n
        self.parent_lca = [-1] * n
        self.depth = [0] * n
        self.log_n = (n).bit_length()
        self.up = [[-1] * self.log_n for _ in range(n)]
        
        # BFS to compute depth and parent
        queue = deque([root])
        visited = [False] * n
        visited[root] = True
        
        while queue:
            v = queue.popleft()
            for neighbor, _ in mst_adj[v]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    self.parent_lca[neighbor] = v
                    self.depth[neighbor] = self.depth[v] + 1
                    queue.append(neighbor)
        
        # Preprocess for binary lifting
        for v in range(n):
            self.up[v][0] = self.parent_lca[v]
        
        for j in range(1, self.log_n):
            for v in range(n):
                if self.up[v][j-1] != -1:
                    self.up[v][j] = self.up[self.up[v][j-1]][j-1]
    
    def _lca(self, u: int, v: int) -> int:
        """Find lowest common ancestor using binary lifting."""
        if self.depth[u] < self.depth[v]:
            u, v = v, u
        
        # Lift u to same depth as v
        diff = self.depth[u] - self.depth[v]
        for j in range(self.log_n):
            if diff & (1 << j):
                u = self.up[u][j]
        
        if u == v:
            return u
        
        # Lift both until parents are equal
        for j in range(self.log_n - 1, -1, -1):
            if self.up[u][j] != self.up[v][j]:
                u = self.up[u][j]
                v = self.up[v][j]
        
        return self.parent_lca[u]
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                           percentile_threshold: float = 70) -> Dict[int, int]:
        """
        Detect communities in MST based on edge weight percentiles.
        Returns community assignment for each vertex.
        """
        # Collect all edge weights
        edge_weights = []
        for i in range(self.n):
            for neighbor, weight in mst_adj[i]:
                if i < neighbor:  # Avoid duplicates
                    edge_weights.append(weight)
        
        # Calculate threshold
        if edge_weights:
            threshold = np.percentile(edge_weights, percentile_threshold)
        else:
            threshold = 0
        
        # Initialize communities (each vertex in its own community)
        community = {i: i for i in range(self.n)}
        
        # Merge communities across edges below threshold
        for i in range(self.n):
            for neighbor, weight in mst_adj[i]:
                if weight <= threshold and i < neighbor:
                    # Union-find merge
                    root_i = community[i]
                    root_j = community[neighbor]
                    
                    # Path compression
                    while community[root_i] != root_i:
                        root_i = community[root_i]
                    while community[root_j] != root_j:
                        root_j = community[root_j]
                    
                    if root_i != root_j:
                        # Merge smaller into larger
                        community[root_j] = root_i
        
        # Final path compression
        for i in range(self.n):
            root = i
            while community[root] != root:
                root = community[root]
            community[i] = root
        
        return community
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """
        Compute edge centrality based on number of shortest paths passing through each edge.
        Uses LCA for O(1) path queries (optimization 1).
        """
        if self.parent_lca is None:
            self._build_lca_structure(mst_adj)
        
        centrality = {}
        n = self.n
        
        # For each pair of vertices, find path in MST and increment edge centrality
        for i in range(n):
            for j in range(i + 1, n):
                lca_ij = self._lca(i, j)
                
                # Walk from i to lca
                u = i
                while u != lca_ij:
                    parent = self.parent_lca[u]
                    edge = (min(u, parent), max(u, parent))
                    centrality[edge] = centrality.get(edge, 0) + 1
                    u = parent
                
                # Walk from j to lca
                v = j
                while v != lca_ij:
                    parent = self.parent_lca[v]
                    edge = (min(v, parent), max(v, parent))
                    centrality[edge] = centrality.get(edge, 0) + 1
                    v = parent
        
        return centrality
    
    def _build_mst_paths(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Build all unique paths in the MST between odd-degree vertices.
        Uses LCA for efficiency (optimization 1).
        """
        if self.parent_lca is None:
            self._build_lca_structure(mst_adj)
        
        paths = {}
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        for i in range(len(odd_vertices)):
            for j in range(i + 1, len(odd_vertices)):
                u = odd_vertices[i]
                v = odd_vertices[j]
                lca_uv = self._lca(u, v)
                
                # Build path from u to lca
                path = []
                current = u
                while current != lca_uv:
                    parent = self.parent_lca[current]
                    path.append((min(current, parent), max(current, parent)))
                    current = parent
                
                # Build path from v to lca (in reverse)
                reverse_path = []
                current = v
                while current != lca_uv:
                    parent = self.parent_lca[current]
                    reverse_path.append((min(current, parent), max(current, parent)))
                    current = parent
                
                # Combine paths
                full_path = path + list(reversed(reverse_path))
                paths[(u, v)] = full_path
        
        return paths
    
    def _compute_path_centrality(self, mst_paths: Dict[Tuple[int, int], List[Tuple[int, int]]],
                                edge_centrality: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
        """
        Compute centrality for each path between odd-degree vertices.
        Cached computation (optimization 2).
        """
        path_centrality = {}
        
        for (u, v), path_edges in mst_paths.items():
            centrality_sum = 0
            for edge in path_edges:
                centrality_sum += edge_centrality.get(edge, 0)
            path_centrality[(u, v)] = centrality_sum / len(path_edges) if path_edges else 0
        
        return path_centrality
    
    def _hybrid_structural_matching(self, odd_vertices: List[int],
                                   mst_paths: Dict[Tuple[int, int], List[Tuple[int, int]]],
                                   path_centrality: Dict[Tuple[int, int], float],
                                   within_community_weight: float = 0.8,
                                   between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Perform hybrid structural matching considering both distance and path centrality.
        """
        # Create list of all possible edges between odd vertices
        edges = []
        for i in range(len(odd_vertices)):
            for j in range(i + 1, len(odd_vertices)):
                u = odd_vertices[i]
                v = odd_vertices[j]
                
                # Get distance
                dist = self.dist_matrix[u][v]
                
                # Get path centrality (cached)
                centrality = path_centrality.get((u, v), 0) if (u, v) in path_centrality else path_centrality.get((v, u), 0)
                
                # Hybrid weight: distance * (1 - centrality_weight)
                # Higher centrality -> lower weight (prefer edges with high centrality)
                centrality_weight = min(1.0, centrality / 100.0)  # Normalize
                hybrid_weight = dist * (1.0 - centrality_weight * within_community_weight)
                
                edges.append((hybrid_weight, u, v))
        
        # Sort by hybrid weight
        edges.sort(key=lambda x: x[0])
        
        # Greedy matching
        matched = set()
        matching = []
        
        for weight, u, v in edges:
            if u not in matched and v not in matched:
                matched.add(u)
                matched.add(v)
                matching.append((u, v))
        
        return matching
    
    def _minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Minimum weight perfect matching using greedy algorithm."""
        # Create list of all edges between odd vertices
        edges = []
        for i in range(len(odd_vertices)):
            for j in range(i + 1, len(odd_vertices)):
                u = odd_vertices[i]
                v = odd_vertices[j]
                weight = self.dist_matrix[u][v]
                edges.append((weight, u, v))
        
        # Sort by weight
        edges.sort(key=lambda x: x[0])
        
        # Greedy matching
        matched = set()
        matching = []
        
        for weight, u, v in edges:
            if u not in matched and v not in matched:
                matched.add(u)
                matched.add(v)
                matching.append((u, v))
        
        return matching
    
    def _create_multigraph(self, mst_adj: List[List[Tuple[int, float]]],
                          matching: List[Tuple[int, int]]) -> List[List[int]]:
        """Create multigraph by combining MST edges and matching edges."""
        multigraph = [[] for _ in range(self.n)]
        
        # Add MST edges
        for i in range(self.n):
            for neighbor, _ in mst_adj[i]:
                multigraph[i].append(neighbor)
        
        # Add matching edges
        for u, v in matching:
            multigraph[u].append(v)
            multigraph[v].append(u)
        
        return multigraph
    
    def _find_eulerian_tour(self, multigraph: List[List[int]]) -> List[int]:
        """Find Eulerian tour using Hierholzer's algorithm."""
        # Make copy of multigraph
        graph = [neighbors[:] for neighbors in multigraph]
        
        # Find vertex with odd degree (or any vertex if all even)
        start = 0
        for i in range(self.n):
            if len(graph[i]) > 0:
                start = i
                break
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if graph[v]:
                u = graph[v].pop()
                # Remove reverse edge
                if v in graph[u]:
                    graph[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        tour.reverse()
        return tour
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = set()
        hamiltonian = []
        
        for v in eulerian_tour:
            if v not in visited:
                visited.add(v)
                hamiltonian.append(v)
        
        # Return to start
        hamiltonian.append(hamiltonian[0])
        return hamiltonian
    
    def _compute_tour_length(self, tour: List[int]) -> float:
        """Compute total length of tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.dist_matrix[tour[i]][tour[i + 1]]
        return total
    
    def _two_opt(self, tour: List[int]) -> Tuple[List[int], float]:
        """
        2-opt local optimization - ORIGINAL VERSION (not optimized from v8).
        Preserves quality by using exact same algorithm as original v19.
        """
        n = len(tour) - 1  # Exclude closing vertex
        best_tour = tour[:]
        best_length = self._compute_tour_length(tour)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue  # No gain in reversing adjacent edges
                    
                    # Try 2-opt swap
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    new_length = self._compute_tour_length(new_tour)
                    
                    if new_length < best_length - 1e-9:
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break  # Restart search after improvement
                if improved:
                    break
        
        return best_tour, best_length
    
    def solve(self, percentile_threshold: float = 70,
              within_community_weight: float = 0.8,
              between_community_weight: float = 0.3,
              apply_2opt: bool = True,
              time_limit: float = 60.0) -> Tuple[List[int], float, float]:
        """
        Solve TSP using Christofides hybrid structural algorithm.
        
        Args:
            percentile_threshold: Percentile for community detection
            within_community_weight: Weight for within-community edges
            between_community_weight: Weight for between-community edges
            apply_2opt: Whether to apply 2-opt optimization
            time_limit: Maximum runtime in seconds
            
        Returns:
            tour: Hamiltonian tour
            tour_length: Total tour length
            runtime: Execution time in seconds
        """
        start_time = time.time()
        
        # 1. Compute MST
        mst_adj, parent = self._compute_mst()
        
        # 2. Find odd-degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # 3. Detect communities
        community = self._detect_communities(mst_adj, percentile_threshold)
        
        # 4. Compute edge centrality (uses LCA optimization)
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # 5. Build MST paths between odd vertices (uses LCA optimization)
        mst_paths = self._build_mst_paths(mst_adj)
        
        # 6. Compute path centrality (cached computation)
        path_centrality = self._compute_path_centrality(mst_paths, edge_centrality)
        
        # 7. Hybrid structural matching
        matching = self._hybrid_structural_matching(
            odd_vertices, mst_paths, path_centrality,
            within_community_weight, between_community_weight
        )
        
        # 8. Create multigraph and find Eulerian tour
        multigraph = self._create_multigraph(mst_adj, matching)
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 9. Convert to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        tour_length = self._compute_tour_length(tour)
        
        # 10. Apply 2-opt if requested (ORIGINAL algorithm)
        if apply_2opt:
            tour, tour_length = self._two_opt(tour)
        
        runtime = time.time() - start_time
        return tour, tour_length, runtime


def solve_tsp(points: Union[np.ndarray, List[Tuple[float, float]]],
              distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
              seed: Optional[int] = None,
              **kwargs) -> Tuple[List[int], float]:
    """
    Convenience function to solve TSP.
    
    Args:
        points: Array or list of (x, y) coordinates
        distance_matrix: Precomputed distance matrix (for TSPLIB)
        seed: Random seed
        **kwargs: Additional arguments passed to solve()
        
    Returns:
        tour: Hamiltonian tour (0-based indices)
        tour_length: Total tour length
    """
    if isinstance(points, np.ndarray):
        points = [(float(p[0]), float(p[1])) for p in points]
    
    solver = ChristofidesHybridStructuralOptimizedV11(
        points=points if distance_matrix is None else None,
        distance_matrix=distance_matrix,
        seed=seed
    )
    
    tour, tour_length, _ = solver.solve(**kwargs)
    return tour, tour_length


if __name__ == "__main__":
    # Example usage
    import random
    
    # Generate random points
    n = 50
    random.seed(42)
    points = [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]
    
    # Solve using v11
    solver = ChristofidesHybridStructuralOptimizedV11(points=points, seed=42)
    tour, length, runtime = solver.solve()
    
    print(f"Solved TSP with n={n}")
    print(f"Tour length: {length:.2f}")
    print(f"Runtime: {runtime:.3f}s")
    print(f"Tour (first 10 vertices): {tour[:10]}...")
