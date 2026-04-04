#!/usr/bin/env python3
"""
Christofides with Path-Based Centrality Matching
Novel hybrid TSP algorithm improving on v14 concept.

Key Improvement: Instead of using edge centrality only for MST edges,
we compute path centrality for ANY pair of vertices by:
1. Finding the unique path between vertices in the MST
2. Computing average centrality of edges along that path
3. Using this propagated centrality to guide matching selection

This addresses v14's limitation where most odd-vertex pairs aren't
directly connected in the MST (only 6.7% coverage).

Concept: score = distance * (1 - centrality_weight * path_centrality)
where path_centrality = average centrality of edges in MST path between vertices.

Author: Evo
Date: 2026-04-03
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq

class ChristofidesPathCentrality:
    """Christofides algorithm with path-based centrality matching."""
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        """
        Initialize with Euclidean points.
        
        Args:
            points: List of (x, y) coordinates
            seed: Random seed for reproducibility
        """
        self.points = points
        self.n = len(points)
        self.seed = seed
        random.seed(seed)
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
        
    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute Euclidean distance matrix."""
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
            
            visited[v] = True
            
            # Add edge to MST if not the root
            if parent[v] != -1:
                weight = self.dist_matrix[v][parent[v]]
                mst_adj[v].append((parent[v], weight))
                mst_adj[parent[v]].append((v, weight))
            
            # Update minimum edges
            for to in range(n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
                    parent[to] = v
        
        return mst_adj, parent
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """
        Compute edge centrality in MST.
        
        Edge centrality measures how central an edge is in the tree structure.
        We compute it as: centrality(e) = 1 / (1 + min_distance_to_center)
        where center is defined as the vertex with minimum maximum distance to all leaves.
        """
        n = self.n
        
        # Build adjacency without weights for BFS
        adj = [[] for _ in range(n)]
        edge_set = set()
        for u in range(n):
            for v, _ in mst_adj[u]:
                if u < v:
                    adj[u].append(v)
                    adj[v].append(u)
                    edge_set.add((u, v))
        
        # Find tree center using two BFS passes
        def bfs_farthest(start: int) -> Tuple[int, List[int]]:
            dist = [-1] * n
            dist[start] = 0
            queue = [start]
            farthest = start
            
            while queue:
                u = queue.pop(0)
                farthest = u
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        queue.append(v)
            
            return farthest, dist
        
        # Find diameter endpoints
        endpoint1, _ = bfs_farthest(0)
        endpoint2, dist_from_endpoint1 = bfs_farthest(endpoint1)
        _, dist_from_endpoint2 = bfs_farthest(endpoint2)
        
        # Tree center is vertex with minimum eccentricity
        eccentricity = [max(dist_from_endpoint1[i], dist_from_endpoint2[i]) for i in range(n)]
        center = min(range(n), key=lambda i: eccentricity[i])
        
        # Compute distances from center
        dist_from_center = [-1] * n
        dist_from_center[center] = 0
        queue = [center]
        while queue:
            u = queue.pop(0)
            for v in adj[u]:
                if dist_from_center[v] == -1:
                    dist_from_center[v] = dist_from_center[u] + 1
                    queue.append(v)
        
        # Compute edge centrality: 1 / (1 + min distance to center of edge endpoints)
        centrality = {}
        for u in range(n):
            for v, _ in mst_adj[u]:
                if u < v:
                    min_dist_to_center = min(dist_from_center[u], dist_from_center[v])
                    centrality[(u, v)] = 1.0 / (1.0 + min_dist_to_center)
        
        return centrality
    
    def _build_mst_paths(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Build dictionary of paths between all vertex pairs in MST.
        Returns: (u, v) -> list of edges in path from u to v in MST.
        """
        n = self.n
        
        # Build adjacency for DFS
        adj = [[] for _ in range(n)]
        for u in range(n):
            for v, _ in mst_adj[u]:
                adj[u].append(v)
        
        # Precompute paths using DFS from each vertex
        paths = {}
        
        def dfs(current: int, target: int, visited: List[bool], path_edges: List[Tuple[int, int]]) -> bool:
            """DFS to find path from current to target in MST."""
            if current == target:
                return True
            
            visited[current] = True
            
            for neighbor in adj[current]:
                if not visited[neighbor]:
                    # Add edge to path
                    edge = (min(current, neighbor), max(current, neighbor))
                    path_edges.append(edge)
                    
                    if dfs(neighbor, target, visited, path_edges):
                        return True
                    
                    # Backtrack
                    path_edges.pop()
            
            return False
        
        # Compute paths for all pairs
        for u in range(n):
            for v in range(u + 1, n):
                visited = [False] * n
                path_edges = []
                dfs(u, v, visited, path_edges)
                paths[(u, v)] = path_edges.copy()
        
        return paths
    
    def _compute_path_centrality(self, mst_paths: Dict[Tuple[int, int], List[Tuple[int, int]]],
                                edge_centrality: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
        """
        Compute path centrality for all vertex pairs.
        
        Path centrality = average centrality of edges in MST path between vertices.
        If path is empty (vertices are the same), centrality = 1.0 (maximum).
        """
        path_centrality = {}
        
        for (u, v), path_edges in mst_paths.items():
            if not path_edges:
                # u == v or vertices are adjacent in MST
                path_centrality[(u, v)] = 1.0
            else:
                # Average centrality of edges in path
                total_centrality = sum(edge_centrality.get(edge, 0.0) for edge in path_edges)
                path_centrality[(u, v)] = total_centrality / len(path_edges)
        
        return path_centrality
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _path_centrality_matching(self, odd_vertices: List[int], 
                                 path_centrality: Dict[Tuple[int, int], float],
                                 centrality_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Minimum weight matching using path-based centrality.
        
        Uses: score = distance * (1 - centrality_weight * path_centrality)
        
        This gives preference to edges whose endpoints are connected by
        central paths in the MST structure.
        
        Args:
            odd_vertices: List of vertices with odd degree
            path_centrality: Dictionary mapping vertex pairs to path centrality scores
            centrality_weight: Weight given to centrality (0 = pure greedy, 1 = max centrality influence)
        
        Returns: List of matched edges
        """
        m = len(odd_vertices)
        if m == 0:
            return []
        
        # Create all possible edges between odd vertices
        edges = []
        for i in range(m):
            u = odd_vertices[i]
            for j in range(i + 1, m):
                v = odd_vertices[j]
                distance = self.dist_matrix[u][v]
                
                # Get path centrality
                key = (min(u, v), max(u, v))
                centrality = path_centrality.get(key, 0.0)
                
                # Adaptive score: lower is better
                score = distance * (1.0 - centrality_weight * centrality)
                edges.append((score, distance, centrality, u, v))
        
        # Sort by adaptive score
        edges.sort(key=lambda x: x[0])
        
        # Greedy matching with adaptive scores
        matched = set()
        matching = []
        
        for score, distance, centrality, u, v in edges:
            if u not in matched and v not in matched:
                matched.add(u)
                matched.add(v)
                matching.append((u, v))
                
                if len(matched) == m:
                    break
        
        return matching
    
    def _create_eulerian_multigraph(self, mst_adj: List[List[Tuple[int, float]]], 
                                   matching: List[Tuple[int, int]]) -> List[List[int]]:
        """Create Eulerian multigraph by combining MST edges and matching edges."""
        # Start with MST edges
        multigraph = [[] for _ in range(self.n)]
        for u in range(self.n):
            for v, _ in mst_adj[u]:
                multigraph[u].append(v)
        
        # Add matching edges (each appears twice for undirected)
        for u, v in matching:
            multigraph[u].append(v)
            multigraph[v].append(u)
        
        return multigraph
    
    def _find_eulerian_tour(self, multigraph: List[List[int]]) -> List[int]:
        """Find Eulerian tour using Hierholzer's algorithm."""
        # Make copies of adjacency lists
        adj_copy = [neighbors[:] for neighbors in multigraph]
        
        # Find vertex with non-zero degree
        start = 0
        for i in range(self.n):
            if adj_copy[i]:
                start = i
                break
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if adj_copy[v]:
                u = adj_copy[v].pop()
                # Remove reverse edge
                adj_copy[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        tour.reverse()
        return tour
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = set()
        tour = []
        
        for v in eulerian_tour:
            if v not in visited:
                visited.add(v)
                tour.append(v)
        
        # Close the tour
        tour.append(tour[0])
        return tour
    
    def _two_opt(self, tour: List[int], max_iterations: int = 100) -> List[int]:
        """Apply 2-opt local optimization to improve tour."""
        n = len(tour) - 1  # Excluding the closing vertex
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            best_gain = 0
            best_i = -1
            best_j = -1
            
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Calculate gain from 2-opt swap
                    a, b = tour[i-1], tour[i]
                    c, d = tour[j], tour[j+1]
                    
                    old_distance = self.dist_matrix[a][b] + self.dist_matrix[c][d]
                    new_distance = self.dist_matrix[a][c] + self.dist_matrix[b][d]
                    gain = old_distance - new_distance
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i
                        best_j = j
            
            if best_gain > 0:
                # Perform 2-opt swap
                tour[best_i:best_j+1] = reversed(tour[best_i:best_j+1])
                improved = True
                iterations += 1
            else:
                break
        
        return tour
    
    def solve(self, centrality_weight: float = 0.3, apply_2opt: bool = True) -> Tuple[List[int], float, float]:
        """
        Solve TSP using Christofides with path-based centrality matching.
        
        Args:
            centrality_weight: Weight given to path centrality (0-1)
            apply_2opt: Whether to apply 2-opt optimization
        
        Returns:
            tour: List of vertex indices (starting and ending at same vertex)
            tour_length: Total tour length
            runtime: Execution time in seconds
        """
        start_time = time.time()
        
        # 1. Compute MST
        mst_adj, _ = self._compute_mst()
        
        # 2. Compute edge centrality in MST
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # 3. Build MST paths and compute path centrality
        mst_paths = self._build_mst_paths(mst_adj)
        path_centrality = self._compute_path_centrality(mst_paths, edge_centrality)
        
        # 4. Find odd degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # 5. Path centrality matching
        matching = self._path_centrality_matching(odd_vertices, path_centrality, centrality_weight)
        
        # 6. Create Eulerian multigraph
        multigraph = self._create_eulerian_multigraph(mst_adj, matching)
        
        # 7. Find Eulerian tour
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 8. Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        
        # 9. Apply 2-opt optimization if requested
        if apply_2opt:
            tour = self._two_opt(tour)
        
        # Calculate tour length
        tour_length = 0.0
        for i in range(len(tour) - 1):
            tour_length += self.dist_matrix[tour[i]][tour[i+1]]
        
        runtime = time.time() - start_time
        
        return tour, tour_length, runtime


def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: List of (x, y) coordinates
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    solver = ChristofidesPathCentrality(points, seed=seed)
    tour, length, runtime = solver.solve(centrality_weight=0.3, apply_2opt=True)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length


def test_algorithm():
    """Test the algorithm with a small example."""
    points = [(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)]
    
    solver = ChristofidesPathCentrality(points, seed=42)
    tour, length, runtime = solver.solve(centrality_weight=0.3, apply_2opt=True)
    
    print(f"Test points: {points}")
    print(f"Tour: {tour}")
    print(f"Length: {length:.4f}")
    print(f"Runtime: {runtime:.4f}s")
    
    # Also test via standard interface
    tour2, length2 = solve_tsp(points, seed=42)
    print(f"\nStandard interface test:")
    print(f"Tour: {tour2}")
    print(f"Length: {length2:.4f}")
    
    return length


if __name__ == "__main__":
    test_algorithm()