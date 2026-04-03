#!/usr/bin/env python3
"""
Christofides with Adaptive Matching based on Edge Centrality
Novel hybrid TSP algorithm combining Christofides MST with centrality-guided matching

Key Novelty: Uses Minimum Spanning Tree (MST) structural properties (edge centrality)
to guide matching selection instead of pure greedy matching by weight.

Concept: score = distance * (1 - centrality_weight * centrality)
where centrality measures how central an edge is in the MST structure.

This approach recognizes that edges in the MST that are more "central" (closer to tree center)
might be more important to preserve in the matching, even if they have slightly higher weight.

Author: Evo
Date: 2026-04-03
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq

class ChristofidesAdaptiveMatching:
    """Christofides algorithm with adaptive matching based on edge centrality in MST."""
    
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
    
    def _compute_mst(self) -> List[List[Tuple[int, float]]]:
        """
        Compute Minimum Spanning Tree using Prim's algorithm.
        Returns adjacency list representation.
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
        
        return mst_adj
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """
        Compute edge centrality in MST.
        
        Edge centrality measures how central an edge is in the tree structure.
        We compute it as: centrality(e) = 1 / (1 + min_distance_to_center)
        where center is defined as the vertex with minimum maximum distance to all leaves.
        
        Returns: Dictionary mapping (u, v) edge to centrality score (0-1)
        """
        n = self.n
        
        # First, find tree center using BFS from leaves
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
        # First BFS from arbitrary node to find farthest node
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
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _adaptive_minimum_weight_matching(self, odd_vertices: List[int], 
                                         edge_centrality: Dict[Tuple[int, int], float],
                                         centrality_weight: float = 0.3) -> List[Tuple[int, int]]:
        """
        Adaptive minimum weight matching using edge centrality.
        
        Instead of pure greedy matching by distance, we use:
        score = distance * (1 - centrality_weight * centrality)
        
        This gives preference to edges that are more central in the MST structure,
        potentially creating a more balanced matching.
        
        Args:
            odd_vertices: List of vertices with odd degree
            edge_centrality: Dictionary mapping edges to centrality scores
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
                
                # Get centrality score (default to 0 if edge not in MST)
                edge_key = (min(u, v), max(u, v))
                centrality = edge_centrality.get(edge_key, 0.0)
                
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
                    if j == i + 1:
                        continue
                    
                    # Current edges: (i-1, i) and (j, j+1)
                    # New edges: (i-1, j) and (i, j+1)
                    a, b, c, d = tour[i-1], tour[i], tour[j], tour[(j+1) % n]
                    
                    old_cost = (self.dist_matrix[a][b] + 
                               self.dist_matrix[c][d])
                    new_cost = (self.dist_matrix[a][c] + 
                               self.dist_matrix[b][d])
                    
                    gain = old_cost - new_cost
                    if gain > best_gain:
                        best_gain = gain
                        best_i = i
                        best_j = j
            
            if best_gain > 1e-9:
                # Reverse segment between i and j
                tour[best_i:best_j+1] = reversed(tour[best_i:best_j+1])
                improved = True
            
            iterations += 1
        
        return tour
    
    def solve(self, centrality_weight: float = 0.3, apply_2opt: bool = True) -> Tuple[List[int], float]:
        """
        Solve TSP using Christofides with adaptive matching.
        
        Args:
            centrality_weight: Weight given to edge centrality (0-1)
            apply_2opt: Whether to apply 2-opt optimization
        
        Returns:
            tour: List of vertex indices (starting and ending at same vertex)
            tour_length: Total tour length
        """
        start_time = time.time()
        
        # 1. Compute MST
        mst_adj = self._compute_mst()
        
        # 2. Compute edge centrality in MST
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # 3. Find odd degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # 4. Adaptive minimum weight matching
        matching = self._adaptive_minimum_weight_matching(odd_vertices, edge_centrality, centrality_weight)
        
        # 5. Create Eulerian multigraph
        multigraph = self._create_eulerian_multigraph(mst_adj, matching)
        
        # 6. Find Eulerian tour
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 7. Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        
        # 8. Apply 2-opt optimization if requested
        if apply_2opt:
            tour = self._two_opt(tour)
        
        # Calculate tour length
        tour_length = 0.0
        for i in range(len(tour) - 1):
            tour_length += self.dist_matrix[tour[i]][tour[i+1]]
        
        runtime = time.time() - start_time
        
        return tour, tour_length, runtime
    
    def benchmark(self, centrality_weights: List[float] = None, n_trials: int = 5) -> Dict:
        """
        Benchmark algorithm with different centrality weights.
        
        Args:
            centrality_weights: List of centrality weights to test
            n_trials: Number of trials per weight
        
        Returns:
            Dictionary with benchmark results
        """
        if centrality_weights is None:
            centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        results = {
            'algorithm': 'Christofides with Adaptive Matching based on Edge Centrality',
            'n_points': self.n,
            'centrality_weights': centrality_weights,
            'trials': []
        }
        
        for weight in centrality_weights:
            weight_results = {
                'centrality_weight': weight,
                'tour_lengths': [],
                'runtimes': [],
                'avg_tour_length': 0.0,
                'avg_runtime': 0.0
            }
            
            for trial in range(n_trials):
                # Use different seed for each trial
                self.seed = 42 + trial
                random.seed(self.seed)
                
                tour, length, runtime = self.solve(centrality_weight=weight, apply_2opt=True)
                
                weight_results['tour_lengths'].append(length)
                weight_results['runtimes'].append(runtime)
            
            weight_results['avg_tour_length'] = sum(weight_results['tour_lengths']) / n_trials
            weight_results['avg_runtime'] = sum(weight_results['runtimes']) / n_trials
            weight_results['min_tour_length'] = min(weight_results['tour_lengths'])
            weight_results['max_tour_length'] = max(weight_results['tour_lengths'])
            
            results['trials'].append(weight_results)
        
        # Find best weight
        best_result = min(results['trials'], key=lambda x: x['avg_tour_length'])
        results['best_centrality_weight'] = best_result['centrality_weight']
        results['best_avg_tour_length'] = best_result['avg_tour_length']
        results['best_avg_runtime'] = best_result['avg_runtime']
        
        return results


def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]


def test_algorithm():
    """Test the algorithm on small instance."""
    print("Testing Christofides with Adaptive Matching based on Edge Centrality")
    print("=" * 70)
    
    # Generate test points
    n = 20
    points = generate_random_points(n, seed=42)
    
    # Create solver
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # Test with different centrality weights
    print(f"Testing on n={n} random points")
    print()
    
    centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    for weight in centrality_weights:
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        print(f"Centrality weight {weight:.1f}: Tour length = {length:.4f}, Runtime = {runtime:.4f}s")
    
    print()
    print("Running benchmark...")
    results = solver.benchmark(centrality_weights=centrality_weights, n_trials=3)
    
    print(f"\nBenchmark Results (n={n}):")
    print(f"Best centrality weight: {results['best_centrality_weight']}")
    print(f"Best average tour length: {results['best_avg_tour_length']:.4f}")
    print(f"Best average runtime: {results['best_avg_runtime']:.4f}s")
    
    print("\nDetailed results:")
    for trial in results['trials']:
        weight = trial['centrality_weight']
        avg_len = trial['avg_tour_length']
        avg_rt = trial['avg_runtime']
        print(f"  Weight {weight:.1f}: avg length={avg_len:.4f}, avg runtime={avg_rt:.4f}s")


def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: List of (x, y) coordinates
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    solver = ChristofidesAdaptiveMatching(points, seed=seed)
    tour, length, runtime = solver.solve(centrality_weight=0.3, apply_2opt=True)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length


if __name__ == "__main__":
    test_algorithm()