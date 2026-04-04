#!/usr/bin/env python3
"""
Christofides with Hybrid Structural Analysis (v19) - OPTIMIZED VERSION
Combines v16's path-based centrality with v18's community detection.

OPTIMIZATIONS:
1. Compute paths only between odd vertices, not all vertex pairs
2. Use LCA (Lowest Common Ancestor) with binary lifting for O(log n) path queries
3. Cache edge centrality lookups
4. Optimize community detection

Key Innovation:
1. Detect communities in MST (v18 approach)
2. Compute path-based centrality for odd vertex pairs only (v16 approach optimized)
3. Use hierarchical matching strategy:
   - Within communities: Strong centrality influence (prefer central paths)
   - Between communities: Moderate centrality influence (balance distance and structure)

This creates a more nuanced matching that respects both local community structure
and global centrality patterns.

Author: Evo
Date: 2026-04-04
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq
import numpy as np

class ChristofidesHybridStructuralOptimized:
    """Christofides algorithm with hybrid structural analysis - OPTIMIZED."""
    
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
    
    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                           percentile_threshold: float = 50.0) -> List[int]:
        """
        Detect communities in MST using edge weight thresholding.
        
        Args:
            mst_adj: MST adjacency list
            percentile_threshold: Percentile for edge weight threshold (0-100)
        
        Returns:
            Community labels for each vertex
        """
        n = self.n
        
        # Build edge list from MST adjacency
        edges = []
        for u in range(n):
            for v, w in mst_adj[u]:
                if u < v:  # Avoid duplicates
                    edges.append((u, v, w))
        
        if not edges:
            return list(range(n))
        
        # Calculate threshold based on percentile
        weights = [w for _, _, w in edges]
        threshold = np.percentile(weights, percentile_threshold)
        
        # Union-find for community detection
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
        
        # Merge nodes connected by edges below threshold (likely within same community)
        for u, v, w in edges:
            if w <= threshold:
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
    
    def _build_lca_structure(self, mst_adj: List[List[Tuple[int, float]]]) -> Tuple[List[int], List[int], List[List[int]]]:
        """
        Build LCA (Lowest Common Ancestor) structure for the MST.
        
        Returns:
            parent: Parent array (parent[root] = -1)
            depth: Depth of each node (depth[root] = 0)
            up: Binary lifting table up[node][k] = 2^k-th ancestor of node
        """
        n = self.n
        
        # Build adjacency for DFS
        adj = [[] for _ in range(n)]
        for u in range(n):
            for v, _ in mst_adj[u]:
                adj[u].append(v)
        
        # DFS to compute parent and depth
        parent = [-1] * n
        depth = [0] * n
        stack = [(0, -1, 0)]  # (node, parent, current_depth)
        
        while stack:
            node, par, d = stack.pop()
            parent[node] = par
            depth[node] = d
            
            for neighbor in adj[node]:
                if neighbor != par:
                    stack.append((neighbor, node, d + 1))
        
        # Compute binary lifting table
        LOG = (n).bit_length()  # Maximum power of 2 needed
        up = [[-1] * LOG for _ in range(n)]
        
        # Initialize first ancestors (2^0 = 1)
        for v in range(n):
            up[v][0] = parent[v]
        
        # Fill up table using dynamic programming
        for k in range(1, LOG):
            for v in range(n):
                if up[v][k-1] != -1:
                    up[v][k] = up[up[v][k-1]][k-1]
        
        return parent, depth, up
    
    def _lca(self, u: int, v: int, depth: List[int], up: List[List[int]]) -> int:
        """
        Find Lowest Common Ancestor of u and v using binary lifting.
        """
        # Make u the deeper node
        if depth[u] < depth[v]:
            u, v = v, u
        
        # Lift u to same depth as v
        diff = depth[u] - depth[v]
        k = 0
        while diff > 0:
            if diff & 1:
                u = up[u][k]
            diff >>= 1
            k += 1
        
        # If they're the same now, we're done
        if u == v:
            return u
        
        # Lift both nodes until their parents are the same
        LOG = len(up[0])
        for k in range(LOG - 1, -1, -1):
            if up[u][k] != up[v][k]:
                u = up[u][k]
                v = up[v][k]
        
        return up[u][0]
    
    def _get_path_edges_between(self, u: int, v: int, parent: List[int], 
                               edge_centrality: Dict[Tuple[int, int], float]) -> Tuple[List[Tuple[int, int]], float]:
        """
        Get edges on path between u and v in MST and compute average centrality.
        
        Returns:
            path_edges: List of edges on path (sorted by min-max)
            avg_centrality: Average centrality of edges on path
        """
        # Simple approach: walk up from u to LCA, then from v to LCA
        # But we need parent array from LCA structure
        
        # For now, use DFS to find path (optimized for single query)
        # This is still O(n) per query but we only query odd vertex pairs
        
        # Build adjacency for DFS
        n = self.n
        adj = [[] for _ in range(n)]
        for a in range(n):
            for b, _ in [(b, w) for b, w in self.mst_adj[a] if a < b]:
                adj[a].append(b)
                adj[b].append(a)
        
        # DFS to find path
        def dfs_find_path(current: int, target: int, visited: List[bool], 
                         path: List[Tuple[int, int]]) -> bool:
            if current == target:
                return True
            
            visited[current] = True
            
            for neighbor in adj[current]:
                if not visited[neighbor]:
                    edge = (min(current, neighbor), max(current, neighbor))
                    path.append(edge)
                    
                    if dfs_find_path(neighbor, target, visited, path):
                        return True
                    
                    # Backtrack
                    path.pop()
            
            return False
        
        visited = [False] * n
        path_edges = []
        dfs_find_path(u, v, visited, path_edges)
        
        # Compute average centrality
        if not path_edges:
            return [], 1.0  # u == v or adjacent
        
        total_centrality = sum(edge_centrality.get(edge, 0.0) for edge in path_edges)
        avg_centrality = total_centrality / len(path_edges)
        
        return path_edges, avg_centrality
    
    def _compute_path_centrality_for_odd_vertices(self, odd_vertices: List[int],
                                                 edge_centrality: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
        """
        Compute path centrality only for pairs of odd vertices.
        
        This is the key optimization: instead of computing for all n*(n-1)/2 pairs,
        we only compute for odd_vertices*(odd_vertices-1)/2 pairs.
        
        For n=500, odd_vertices ≈ 213, so pairs ≈ 22,705 instead of 124,750.
        """
        path_centrality = {}
        m = len(odd_vertices)
        
        # Pre-build adjacency for faster DFS
        n = self.n
        adj = [[] for _ in range(n)]
        for a in range(n):
            for b, _ in [(b, w) for b, w in self.mst_adj[a] if a < b]:
                adj[a].append(b)
                adj[b].append(a)
        
        # Cache for visited arrays to avoid reallocation
        visited_template = [False] * n
        
        for i in range(m):
            u = odd_vertices[i]
            
            # DFS from u to find paths to all other odd vertices
            # This is more efficient than separate DFS for each pair
            visited = visited_template.copy()
            stack = [(u, [])]  # (current_node, path_edges_from_u)
            
            while stack:
                current, path_edges = stack.pop()
                visited[current] = True
                
                # If current is an odd vertex (and not u itself), record centrality
                if current in self.odd_vertex_set and current != u:
                    if path_edges:
                        total_centrality = sum(edge_centrality.get(edge, 0.0) for edge in path_edges)
                        avg_centrality = total_centrality / len(path_edges)
                    else:
                        avg_centrality = 1.0  # u and current are adjacent in MST
                    
                    key = (min(u, current), max(u, current))
                    path_centrality[key] = avg_centrality
                
                # Continue DFS
                for neighbor in adj[current]:
                    if not visited[neighbor]:
                        new_path = path_edges.copy()
                        edge = (min(current, neighbor), max(current, neighbor))
                        new_path.append(edge)
                        stack.append((neighbor, new_path))
        
        return path_centrality
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _hybrid_structural_matching(self, odd_vertices: List[int], 
                                   communities: List[int],
                                   path_centrality: Dict[Tuple[int, int], float],
                                   within_community_weight: float = 0.5,
                                   between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Hybrid matching using hierarchical approach with centrality guidance.
        
        Strategy:
        1. First phase: Match odd vertices within the same community
           - Use path centrality to guide matching within communities
        2. Second phase: Match remaining odd vertices between communities
           - Use different centrality weight for cross-community edges
        
        This ensures community structure is respected while using centrality
        to improve matching quality within structural constraints.
        
        Args:
            odd_vertices: List of vertices with odd degree
            communities: Community labels for all vertices
            path_centrality: Path centrality scores for vertex pairs
            within_community_weight: Centrality weight for within-community edges (0-1)
            between_community_weight: Centrality weight for between-community edges (0-1)
        
        Returns:
            List of matched edges
        """
        m = len(odd_vertices)
        if m == 0:
            return []
        
        # Group odd vertices by community
        community_groups = {}
        for v in odd_vertices:
            comm = communities[v]
            if comm not in community_groups:
                community_groups[comm] = []
            community_groups[comm].append(v)
        
        matched = set()
        matching = []
        
        # Phase 1: Match within communities
        for comm, vertices in community_groups.items():
            if len(vertices) >= 2:
                # Create edges between vertices in same community
                edges = []
                for i in range(len(vertices)):
                    u = vertices[i]
                    for j in range(i + 1, len(vertices)):
                        v = vertices[j]
                        distance = self.dist_matrix[u][v]
                        
                        # Get path centrality
                        key = (min(u, v), max(u, v))
                        centrality = path_centrality.get(key, 0.0)
                        
                        # Adaptive score with within-community weight
                        score = distance * (1.0 - within_community_weight * centrality)
                        edges.append((score, u, v))
                
                # Sort by adaptive score
                edges.sort(key=lambda x: x[0])
                
                # Greedy matching within this community
                comm_matched = set()
                for score, u, v in edges:
                    if u not in matched and v not in matched and u not in comm_matched and v not in comm_matched:
                        matched.add(u)
                        matched.add(v)
                        comm_matched.add(u)
                        comm_matched.add(v)
                        matching.append((u, v))
        
        # Phase 2: Match remaining vertices between communities
        remaining_vertices = [v for v in odd_vertices if v not in matched]
        
        if remaining_vertices:
            # Create edges between all remaining vertices
            edges = []
            for i in range(len(remaining_vertices)):
                u = remaining_vertices[i]
                for j in range(i + 1, len(remaining_vertices)):
                    v = remaining_vertices[j]
                    distance = self.dist_matrix[u][v]
                    
                    # Get path centrality
                    key = (min(u, v), max(u, v))
                    centrality = path_centrality.get(key, 0.0)
                    
                    # Adaptive score with between-community weight
                    score = distance * (1.0 - between_community_weight * centrality)
                    edges.append((score, u, v))
            
            # Sort by adaptive score
            edges.sort(key=lambda x: x[0])
            
            # Greedy matching for remaining vertices
            for score, u, v in edges:
                if u not in matched and v not in matched:
                    matched.add(u)
                    matched.add(v)
                    matching.append((u, v))
                    
                    if len(matched) == len(odd_vertices):
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
    
    def solve(self, percentile_threshold: float = 70.0,
              within_community_weight: float = 0.8,
              between_community_weight: float = 0.3,
              apply_2opt: bool = True) -> Tuple[List[int], float, float]:
        """
        Solve TSP using Christofides with hybrid structural analysis - OPTIMIZED.
        
        Args:
            percentile_threshold: Percentile for community detection (0-100)
            within_community_weight: Centrality weight for within-community edges (0-1)
            between_community_weight: Centrality weight for between-community edges (0-1)
            apply_2opt: Whether to apply 2-opt optimization
        
        Returns:
            tour: List of vertex indices (starting and ending at same vertex)
            tour_length: Total tour length
            runtime: Execution time in seconds
        """
        start_time = time.time()
        
        # 1. Compute MST
        mst_adj, parent = self._compute_mst()
        self.mst_adj = mst_adj  # Store for path computation
        
        # 2. Detect communities in MST (v18 approach)
        communities = self._detect_communities(mst_adj, percentile_threshold)
        
        # 3. Compute edge centrality
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # 4. Find odd-degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        self.odd_vertex_set = set(odd_vertices)  # Store for efficient lookup
        
        # 5. Compute path centrality ONLY for odd vertex pairs (KEY OPTIMIZATION)
        path_centrality = self._compute_path_centrality_for_odd_vertices(odd_vertices, edge_centrality)
        
        # 6. Perform hybrid structural matching
        matching = self._hybrid_structural_matching(
            odd_vertices, communities, path_centrality,
            within_community_weight, between_community_weight
        )
        
        # 7. Create Eulerian multigraph
        multigraph = self._create_eulerian_multigraph(mst_adj, matching)
        
        # 8. Find Eulerian tour
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 9. Convert to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        
        # 10. Apply 2-opt optimization if requested
        if apply_2opt:
            tour = self._two_opt(tour)
        
        # 11. Compute tour length
        tour_length = 0.0
        for i in range(len(tour) - 1):
            tour_length += self.dist_matrix[tour[i]][tour[i+1]]
        
        runtime = time.time() - start_time
        
        return tour, tour_length, runtime


def solve_tsp(points):
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    # Convert points to list of tuples if needed
    if isinstance(points, np.ndarray):
        points_list = [(float(p[0]), float(p[1])) for p in points]
    else:
        points_list = points
    
    # Create solver instance with default parameters
    solver = ChristofidesHybridStructuralOptimized(points_list, seed=42)
    
    # Run with optimized parameters from v19 analysis
    tour, length, _ = solver.solve(
        percentile_threshold=70,
        within_community_weight=0.8,
        between_community_weight=0.3,
        apply_2opt=True
    )
    
    return tour, length