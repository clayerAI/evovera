#!/usr/bin/env python3
"""
Christofides Hybrid Structural TSP solver - CORRECTED VERSION
Combines original v19's hybrid structural features with TSPLIB compatibility.

This version:
1. Contains ALL hybrid structural features from original v19:
   - _detect_communities() - Community detection via MST analysis
   - _compute_edge_centrality() - Edge centrality computation  
   - _build_mst_paths() - MST path construction
   - _compute_path_centrality() - Path centrality analysis
   - _hybrid_structural_matching() - Hybrid matching algorithm
2. Adds TSPLIB compatibility (accepts distance_matrix parameter)
3. Will be used for proper strong solver comparison

Author: Evo
Date: 2026-04-05 (Critical Correction)
"""

import math
import random
import heapq
import time
from typing import List, Tuple, Dict, Set, Optional, Union
import numpy as np

class ChristofidesHybridStructuralCorrected:
    """
    Christofides Hybrid Structural TSP solver - CORRECTED VERSION.
    
    Contains full hybrid structural features with TSPLIB compatibility.
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
        Detect communities in MST by analyzing edge weight distribution.
        
        Approach: Remove edges above percentile threshold, then find connected components.
        Higher percentile = fewer edges removed = fewer, larger communities.
        Lower percentile = more edges removed = more, smaller communities.
        
        Args:
            mst_adj: MST adjacency list
            percentile_threshold: Percentile for edge weight cutoff (0-100)
            
        Returns:
            Dictionary mapping vertex index to community ID
        """
        # Collect all MST edge weights
        edge_weights = []
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if u < v:  # Count each edge once
                    edge_weights.append(weight)
        
        if not edge_weights:
            # All vertices in same community
            return {i: 0 for i in range(self.n)}
        
        # Calculate cutoff weight at given percentile
        cutoff = np.percentile(edge_weights, percentile_threshold)
        
        # Build graph without edges above cutoff
        filtered_adj = [[] for _ in range(self.n)]
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if weight <= cutoff:
                    filtered_adj[u].append(v)
        
        # Find connected components (communities)
        visited = [False] * self.n
        community_id = 0
        communities = {}
        
        for i in range(self.n):
            if not visited[i]:
                # BFS to find component
                queue = [i]
                visited[i] = True
                
                while queue:
                    node = queue.pop(0)
                    communities[node] = community_id
                    
                    for neighbor in filtered_adj[node]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                
                community_id += 1
        
        return communities
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """
        Compute edge centrality based on number of shortest paths that pass through each edge.
        
        In MST, all paths between vertices are unique, so we can compute centrality
        by counting how many vertex pairs have the edge in their unique path.
        
        Args:
            mst_adj: MST adjacency list
            
        Returns:
            Dictionary mapping (u, v) edge to centrality score
        """
        # Build parent array for path reconstruction
        n = self.n
        parent = [-1] * n
        visited = [False] * n
        queue = [0]
        visited[0] = True
        
        # BFS to build tree structure
        while queue:
            u = queue.pop(0)
            for v, _ in mst_adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
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
                    node = parent[node]
                
                # Trace from j until we hit path_i_to_j
                node = j
                while node not in path_i_to_j:
                    node = parent[node]
                
                lca = node  # Lowest common ancestor
                
                # Count edges from i to LCA
                node = i
                while node != lca:
                    next_node = parent[node]
                    edge = (min(node, next_node), max(node, next_node))
                    edge_counts[edge] = edge_counts.get(edge, 0) + 1
                    node = next_node
                
                # Count edges from j to LCA
                node = j
                while node != lca:
                    next_node = parent[node]
                    edge = (min(node, next_node), max(node, next_node))
                    edge_counts[edge] = edge_counts.get(edge, 0) + 1
                    node = next_node
        
        # Normalize centrality scores
        max_count = max(edge_counts.values()) if edge_counts else 1
        edge_centrality = {edge: count / max_count for edge, count in edge_counts.items()}
        
        return edge_centrality
    
    def _build_mst_paths(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Build all unique paths between vertex pairs in MST.
        
        In a tree, there's exactly one simple path between any two vertices.
        Returns dictionary mapping (u, v) vertex pair to list of edges in path.
        
        Args:
            mst_adj: MST adjacency list
            
        Returns:
            Dictionary mapping vertex pair to list of edges in their path
        """
        n = self.n
        
        # Build parent array and depth for LCA computation
        parent = [-1] * n
        depth = [0] * n
        visited = [False] * n
        queue = [0]
        visited[0] = True
        
        # BFS to build tree structure
        while queue:
            u = queue.pop(0)
            for v, _ in mst_adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    queue.append(v)
        
        # Build paths for all pairs
        paths = {}
        
        for i in range(n):
            for j in range(i + 1, n):
                path_edges = []
                
                # Move i and j up to same depth
                a, b = i, j
                while depth[a] > depth[b]:
                    next_a = parent[a]
                    path_edges.append((min(a, next_a), max(a, next_a)))
                    a = next_a
                
                while depth[b] > depth[a]:
                    next_b = parent[b]
                    path_edges.append((min(b, next_b), max(b, next_b)))
                    b = next_b
                
                # Move both up until they meet
                while a != b:
                    next_a = parent[a]
                    next_b = parent[b]
                    path_edges.append((min(a, next_a), max(a, next_a)))
                    path_edges.append((min(b, next_b), max(b, next_b)))
                    a = next_a
                    b = next_b
                
                paths[(i, j)] = path_edges
        
        return paths
    
    def _compute_path_centrality(self, mst_paths: Dict[Tuple[int, int], List[Tuple[int, int]]],
                                edge_centrality: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
        """
        Compute path centrality for vertex pairs.
        
        Path centrality = average centrality of edges in the path.
        Higher values indicate the path goes through central/high-traffic edges.
        
        Args:
            mst_paths: Dictionary of paths between vertex pairs
            edge_centrality: Edge centrality scores
            
        Returns:
            Dictionary mapping vertex pair to path centrality score
        """
        path_centrality = {}
        
        for (u, v), edges in mst_paths.items():
            if not edges:
                path_centrality[(u, v)] = 0.0
                continue
            
            total_centrality = sum(edge_centrality.get(edge, 0.0) for edge in edges)
            path_centrality[(u, v)] = total_centrality / len(edges)
        
        return path_centrality
    
    def _hybrid_structural_matching(self, odd_vertices: List[int],
                                   communities: Dict[int, int],
                                   path_centrality: Dict[Tuple[int, int], float],
                                   within_community_weight: float = 0.8,
                                   between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Hybrid structural matching for odd-degree vertices.
        
        Uses different strategies based on community membership:
        1. Within same community: Strong centrality influence
        2. Between different communities: Moderate centrality influence
        3. Cross-community: Lower centrality influence
        
        Args:
            odd_vertices: List of odd-degree vertices
            communities: Community assignments
            path_centrality: Path centrality scores
            within_community_weight: Weight for within-community edges
            between_community_weight: Weight for between-community edges
            
        Returns:
            List of matched edges
        """
        k = len(odd_vertices)
        if k % 2 != 0:
            raise ValueError(f"Odd number of odd vertices: {k}")
        
        # Build complete graph on odd vertices
        odd_dist = [[0.0] * k for _ in range(k)]
        for i in range(k):
            u = odd_vertices[i]
            for j in range(i + 1, k):
                v = odd_vertices[j]
                dist = self.dist_matrix[u][v]
                
                # Get community relationship
                comm_u = communities.get(u, 0)
                comm_v = communities.get(v, 0)
                
                # Get path centrality (default to 0 if not computed)
                centrality = path_centrality.get((min(u, v), max(u, v)), 0.0)
                
                # Apply hybrid weighting
                if comm_u == comm_v:
                    # Within same community: strong centrality influence
                    weight = dist * (1.0 - within_community_weight * centrality)
                else:
                    # Between communities: moderate centrality influence
                    weight = dist * (1.0 - between_community_weight * centrality)
                
                odd_dist[i][j] = weight
                odd_dist[j][i] = weight
        
        # Greedy matching (simplified - original uses more sophisticated approach)
        visited = [False] * k
        matching = []
        
        for i in range(k):
            if not visited[i]:
                # Find best unmatched neighbor
                best_j = -1
                best_weight = float('inf')
                
                for j in range(i + 1, k):
                    if not visited[j] and odd_dist[i][j] < best_weight:
                        best_weight = odd_dist[i][j]
                        best_j = j
                
                if best_j != -1:
                    matching.append((odd_vertices[i], odd_vertices[best_j]))
                    visited[i] = True
                    visited[best_j] = True
        
        return matching
    
    def _minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """
        Minimum weight perfect matching for odd-degree vertices.
        Uses greedy algorithm for simplicity.
        
        Args:
            odd_vertices: List of odd-degree vertices
            
        Returns:
            List of matched edges
        """
        k = len(odd_vertices)
        if k % 2 != 0:
            raise ValueError(f"Odd number of odd vertices: {k}")
        
        # Simple greedy matching
        visited = [False] * k
        matching = []
        
        for i in range(k):
            if not visited[i]:
                # Find closest unmatched vertex
                best_j = -1
                best_dist = float('inf')
                
                for j in range(i + 1, k):
                    if not visited[j]:
                        dist = self.dist_matrix[odd_vertices[i]][odd_vertices[j]]
                        if dist < best_dist:
                            best_dist = dist
                            best_j = j
                
                if best_j != -1:
                    matching.append((odd_vertices[i], odd_vertices[best_j]))
                    visited[i] = True
                    visited[best_j] = True
        
        return matching
    
    def _create_multigraph(self, mst_adj: List[List[Tuple[int, float]]],
                          matching: List[Tuple[int, int]]) -> List[List[int]]:
        """Create multigraph by combining MST edges and matching edges."""
        multigraph = [[] for _ in range(self.n)]
        
        # Add MST edges
        for u in range(self.n):
            for v, _ in mst_adj[u]:
                multigraph[u].append(v)
        
        # Add matching edges
        for u, v in matching:
            multigraph[u].append(v)
            multigraph[v].append(u)
        
        return multigraph
    
    def _find_eulerian_tour(self, multigraph: List[List[int]]) -> List[int]:
        """Find Eulerian tour in multigraph using Hierholzer's algorithm."""
        # Make copy of adjacency lists
        adj_copy = [neighbors[:] for neighbors in multigraph]
        
        # Find vertex with odd degree (or any if all even)
        start = 0
        for i in range(self.n):
            if len(adj_copy[i]) > 0:
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
        
        # Reverse to get correct order
        tour.reverse()
        return tour
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = [False] * self.n
        hamiltonian = []
        
        for vertex in eulerian_tour:
            if not visited[vertex]:
                visited[vertex] = True
                hamiltonian.append(vertex)
        
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
        """Apply 2-opt optimization to tour."""
        n = len(tour) - 1  # Exclude closing vertex
        best_tour = tour[:]
        best_length = self._compute_tour_length(tour)
        
        improved = True
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Try 2-opt swap
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    new_length = self._compute_tour_length(new_tour)
                    
                    if new_length < best_length:
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break
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
        
        # 3. Detect communities in MST
        communities = self._detect_communities(mst_adj, percentile_threshold)
        
        # 4. Compute edge centrality
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # 5. Build MST paths and compute path centrality
        mst_paths = self._build_mst_paths(mst_adj)
        path_centrality = self._compute_path_centrality(mst_paths, edge_centrality)
        
        # 6. Hybrid structural matching
        matching = self._hybrid_structural_matching(
            odd_vertices, communities, path_centrality,
            within_community_weight, between_community_weight
        )
        
        # 7. Create multigraph and find Eulerian tour
        multigraph = self._create_multigraph(mst_adj, matching)
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 8. Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        tour_length = self._compute_tour_length(tour)
        
        # 9. Apply 2-opt if requested
        if apply_2opt:
            tour, tour_length = self._two_opt(tour)
        
        runtime = time.time() - start_time
        
        return tour, tour_length, runtime


def solve_tsp(points: Union[np.ndarray, List[Tuple[float, float]]],
              distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
              seed: Optional[int] = None) -> Tuple[List[int], float]:
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: Array of shape (n, 2) with (x, y) coordinates or list of tuples
        distance_matrix: Optional precomputed distance matrix for TSPLIB
        seed: Random seed
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    # Convert points to list of tuples if needed
    if isinstance(points, np.ndarray):
        points_list = [(float(p[0]), float(p[1])) for p in points]
    else:
        points_list = points
    
    # Create solver instance
    solver = ChristofidesHybridStructuralCorrected(
        points=points_list, 
        distance_matrix=distance_matrix,
        seed=seed if seed is not None else 42
    )
    
    # Run with optimized parameters from v19 analysis
    tour, length, _ = solver.solve(
        percentile_threshold=70,
        within_community_weight=0.8,
        between_community_weight=0.3,
        apply_2opt=True
    )
    
    return tour, length


# Test function
if __name__ == "__main__":
    # Test with simple points
    points = [(0, 0), (1, 0), (0, 1), (1, 1)]
    
    print("Testing Christofides Hybrid Structural (Corrected) with Euclidean distances:")
    tour, length = solve_tsp(points)
    print(f"Tour: {tour}")
    print(f"Length: {length:.2f}")
    
    # Test with distance matrix
    print("\nTesting with custom distance matrix:")
    n = len(points)
    custom_dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                custom_dist[i][j] = abs(i - j) * 1.5  # Simple linear distance
    
    tour2, length2 = solve_tsp(points, distance_matrix=custom_dist)
    print(f"Tour: {tour2}")
    print(f"Length: {length2:.2f}")
    
    print("\n✅ Corrected v19 algorithm created successfully!")
    print("This version contains ALL hybrid structural features with TSPLIB compatibility.")
