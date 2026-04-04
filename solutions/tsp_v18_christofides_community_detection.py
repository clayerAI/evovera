#!/usr/bin/env python3
"""
TSP v18: Christofides with MST Community Detection

Novel hybrid algorithm that:
1. Builds Minimum Spanning Tree (MST)
2. Detects communities in MST using modularity optimization
3. Performs perfect matching within communities first, then between communities
4. Combines MST, matching, and Eulerian tour
5. Applies 2-opt local search

This is a structural analysis approach that leverages community structure
in the MST to guide matching decisions.
"""

import math
import random
import heapq
from typing import List, Tuple, Dict, Set, Optional
import numpy as np
from collections import defaultdict, deque

class ChristofidesCommunityDetection:
    """Christofides algorithm enhanced with MST community detection for matching."""
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        self.points = points
        self.n = len(points)
        self.seed = seed
        random.seed(seed)
        
        # Precompute distances
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
    
    def _compute_mst(self) -> Tuple[List[Tuple[int, int, float]], List[List[int]]]:
        """Compute Minimum Spanning Tree using Prim's algorithm."""
        n = self.n
        visited = [False] * n
        min_edge = [float('inf')] * n
        parent = [-1] * n
        mst_edges = []
        
        # Start from vertex 0
        min_edge[0] = 0
        
        for _ in range(n):
            # Find minimum edge
            v = -1
            for j in range(n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            visited[v] = True
            
            # Add edge to MST if not the root
            if parent[v] != -1:
                weight = self.dist_matrix[v][parent[v]]
                mst_edges.append((parent[v], v, weight))
            
            # Update min edges
            for to in range(n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
                    parent[to] = v
        
        # Build adjacency list for MST
        mst_adj = [[] for _ in range(n)]
        for u, v, w in mst_edges:
            mst_adj[u].append((v, w))
            mst_adj[v].append((u, w))
        
        return mst_edges, mst_adj
    
    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """
        Detect communities in MST using modularity optimization.
        Returns community labels for each vertex.
        """
        n = self.n
        
        # Simple community detection based on MST structure
        # We'll use a greedy approach that maximizes modularity
        
        # Initialize each node as its own community
        communities = list(range(n))
        
        # Build edge list from MST adjacency
        edges = []
        for u in range(n):
            for v, w in mst_adj[u]:
                if u < v:  # Avoid duplicates
                    edges.append((u, v, w))
        
        # Sort edges by weight (heavier edges might be better community boundaries)
        edges.sort(key=lambda x: x[2], reverse=True)
        
        # Merge communities based on edge weights
        # Heavier edges are more likely to be community boundaries, so we don't merge across them
        # Instead, we merge nodes connected by lighter edges
        
        # Create union-find for community merging
        parent = list(range(n))
        rank = [0] * n
        
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                parent[rx] = ry
            elif rank[rx] > rank[ry]:
                parent[ry] = rx
            else:
                parent[ry] = rx
                rank[rx] += 1
            return True
        
        # Merge nodes connected by lighter edges (below median weight)
        if edges:
            weights = [w for _, _, w in edges]
            median_weight = np.median(weights)
            
            for u, v, w in edges:
                if w <= median_weight:
                    union(u, v)
        
        # Assign community labels
        community_map = {}
        next_community_id = 0
        final_communities = [-1] * n
        
        for i in range(n):
            root = find(i)
            if root not in community_map:
                community_map[root] = next_community_id
                next_community_id += 1
            final_communities[i] = community_map[root]
        
        return final_communities
    
    def _get_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Get vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _perfect_matching_with_communities(self, odd_vertices: List[int], 
                                          communities: List[int]) -> List[Tuple[int, int]]:
        """
        Perform perfect matching with community-aware strategy:
        1. First match vertices within the same community
        2. Then match remaining vertices across communities
        """
        n = self.n
        matched = [False] * n
        matching = []
        
        # Group odd vertices by community
        community_vertices = defaultdict(list)
        for v in odd_vertices:
            community_vertices[communities[v]].append(v)
        
        # Phase 1: Match within communities
        for comm_id, vertices in community_vertices.items():
            if len(vertices) % 2 == 1:
                # Odd number in community - leave one unmatched for cross-community matching
                vertices_to_match = vertices[:-1]
            else:
                vertices_to_match = vertices
            
            # Greedy matching within community
            while len(vertices_to_match) >= 2:
                # Find closest pair
                best_pair = None
                best_dist = float('inf')
                
                for i in range(len(vertices_to_match)):
                    for j in range(i + 1, len(vertices_to_match)):
                        u, v = vertices_to_match[i], vertices_to_match[j]
                        d = self.dist_matrix[u][v]
                        if d < best_dist:
                            best_dist = d
                            best_pair = (i, j)
                
                if best_pair:
                    i, j = best_pair
                    u, v = vertices_to_match[i], vertices_to_match[j]
                    matching.append((u, v))
                    matched[u] = True
                    matched[v] = True
                    
                    # Remove matched vertices
                    vertices_to_match = [v for idx, v in enumerate(vertices_to_match) 
                                        if idx not in (i, j)]
        
        # Phase 2: Match remaining vertices across communities
        remaining_odd = [v for v in odd_vertices if not matched[v]]
        
        # Greedy matching for remaining vertices
        while remaining_odd:
            u = remaining_odd.pop()
            best_v = -1
            best_dist = float('inf')
            
            for v in remaining_odd:
                d = self.dist_matrix[u][v]
                if d < best_dist:
                    best_dist = d
                    best_v = v
            
            if best_v != -1:
                matching.append((u, best_v))
                matched[u] = True
                matched[best_v] = True
                remaining_odd.remove(best_v)
        
        return matching
    
    def _combine_mst_and_matching(self, mst_adj: List[List[Tuple[int, float]]], 
                                 matching: List[Tuple[int, int]]) -> List[List[int]]:
        """Combine MST and matching to create multigraph."""
        multigraph = [[] for _ in range(self.n)]
        
        # Add MST edges
        for u in range(self.n):
            for v, w in mst_adj[u]:
                if u < v:  # Avoid duplicates
                    multigraph[u].append(v)
                    multigraph[v].append(u)
        
        # Add matching edges
        for u, v in matching:
            multigraph[u].append(v)
            multigraph[v].append(u)
        
        return multigraph
    
    def _find_eulerian_tour(self, multigraph: List[List[int]]) -> List[int]:
        """Find Eulerian tour using Hierholzer's algorithm."""
        # Make copies of adjacency lists
        adj_copy = [deque(neighbors) for neighbors in multigraph]
        
        # Find vertex with odd degree (or any if all even)
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
                u = adj_copy[v].popleft()
                # Remove reverse edge
                if v in adj_copy[u]:
                    adj_copy[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        tour.reverse()
        return tour
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = [False] * self.n
        tour = []
        
        for v in eulerian_tour:
            if not visited[v]:
                visited[v] = True
                tour.append(v)
        
        # Close the tour
        tour.append(tour[0])
        return tour
    
    def _compute_tour_length(self, tour: List[int]) -> float:
        """Compute total length of tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            total += self.dist_matrix[u][v]
        return total
    
    def _apply_2opt(self, tour: List[int]) -> Tuple[List[int], float]:
        """Apply 2-opt local search to improve tour."""
        n = len(tour)
        if n <= 3:  # Need at least 4 nodes for 2-opt
            return tour, self._compute_tour_length(tour)
        
        improved = True
        best_tour = tour[:]
        best_length = self._compute_tour_length(tour)
        
        while improved:
            improved = False
            
            for i in range(1, n - 2):
                for j in range(i + 1, n - 1):
                    # Check if swap would improve
                    a, b = best_tour[i-1], best_tour[i]
                    c, d = best_tour[j], best_tour[j+1]
                    
                    current = (self.dist_matrix[a][b] + self.dist_matrix[c][d])
                    new = (self.dist_matrix[a][c] + self.dist_matrix[b][d])
                    
                    if new < current - 1e-9:  # Small epsilon for floating point
                        # Perform 2-opt swap
                        new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                        new_length = best_length - current + new
                        
                        if new_length < best_length - 1e-9:
                            best_tour = new_tour
                            best_length = new_length
                            improved = True
                            break
                if improved:
                    break
        
        return best_tour, best_length
    
    def solve(self, apply_2opt: bool = True) -> Tuple[List[int], float, float]:
        """
        Solve TSP using Christofides with community detection.
        
        Returns:
            Tuple of (tour, length, runtime)
        """
        import time
        start_time = time.time()
        
        # Step 1: Compute MST
        mst_edges, mst_adj = self._compute_mst()
        
        # Step 2: Detect communities in MST
        communities = self._detect_communities(mst_adj)
        
        # Step 3: Find odd-degree vertices
        odd_vertices = self._get_odd_degree_vertices(mst_adj)
        
        # Step 4: Perfect matching with community awareness
        matching = self._perfect_matching_with_communities(odd_vertices, communities)
        
        # Step 5: Combine MST and matching
        multigraph = self._combine_mst_and_matching(mst_adj, matching)
        
        # Step 6: Find Eulerian tour
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # Step 7: Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        length = self._compute_tour_length(tour)
        
        # Step 8: Apply 2-opt if requested
        if apply_2opt:
            tour, length = self._apply_2opt(tour)
        
        runtime = time.time() - start_time
        
        return tour, length, runtime


def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: List of (x, y) coordinates
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    solver = ChristofidesCommunityDetection(points, seed=seed)
    tour, length, runtime = solver.solve(apply_2opt=True)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length


# Quick test
if __name__ == "__main__":
    # Generate random points
    random.seed(42)
    n = 50
    points = [(random.random(), random.random()) for _ in range(n)]
    
    # Solve
    tour, length = solve_tsp(points, seed=42)
    
    print(f"v18 Christofides with Community Detection")
    print(f"Number of points: {n}")
    print(f"Tour length: {length:.4f}")
    print(f"Tour (first 10 nodes): {tour[:10]}...")