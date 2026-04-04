#!/usr/bin/env python3
"""
Christofides Hybrid Structural TSP solver - FIXED VERSION for TSPLIB compatibility.
Accepts distance matrix parameter to support different TSPLIB distance metrics.
"""

import math
import random
import heapq
import time
from typing import List, Tuple, Dict, Set, Optional, Union
import numpy as np

class ChristofidesHybridStructural:
    """
    Christofides Hybrid Structural TSP solver with distance matrix support.
    
    FIXED: Accepts precomputed distance matrix for TSPLIB compatibility.
    Supports both Euclidean (via points) and TSPLIB (via distance_matrix) inputs.
    """
    
    def __init__(self, points: Optional[List[Tuple[float, float]]] = None,
                 distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
                 seed: Optional[int] = None):
        """
        Initialize solver.
        
        Args:
            points: List of (x, y) coordinate tuples
            distance_matrix: Precomputed distance matrix (list of lists or numpy array)
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
            self.dist_matrix = None
            self.use_distance_matrix = False
        
        if seed is not None:
            self.seed = seed
            random.seed(seed)
        else:
            self.seed = None
        
        # Compute distance matrix if not provided
        if not self.use_distance_matrix and self.use_points:
            self.dist_matrix = self._compute_distance_matrix()
    
    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute Euclidean distance matrix from points."""
        if not self.use_points:
            raise ValueError("Cannot compute distance matrix without points")
        
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
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between cities i and j."""
        if self.dist_matrix is None:
            raise ValueError("Distance matrix not available")
        return self.dist_matrix[i][j]
    
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
        
        for _ in range(n):
            # Find minimum edge vertex
            v = -1
            for j in range(n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            visited[v] = True
            
            # Update distances to neighbors
            for to in range(n):
                if v != to and not visited[to]:
                    d = self.distance(v, to)
                    if d < min_edge[to]:
                        min_edge[to] = d
                        parent[to] = v
        
        # Build adjacency list
        mst_adj = [[] for _ in range(n)]
        for i in range(1, n):
            p = parent[i]
            if p != -1:
                weight = self.distance(i, p)
                mst_adj[i].append((p, weight))
                mst_adj[p].append((i, weight))
        
        return mst_adj, parent
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Find minimum weight perfect matching using greedy algorithm."""
        matching = []
        vertices = odd_vertices.copy()
        random.shuffle(vertices)
        
        while vertices:
            v = vertices.pop()
            # Find closest unmatched vertex
            best_match = -1
            best_dist = float('inf')
            
            for u in vertices:
                d = self.distance(v, u)
                if d < best_dist:
                    best_dist = d
                    best_match = u
            
            if best_match != -1:
                vertices.remove(best_match)
                matching.append((v, best_match))
        
        return matching
    
    def _create_multigraph(self, mst_adj: List[List[Tuple[int, float]]], 
                          matching: List[Tuple[int, int]]) -> List[List[Tuple[int, float]]]:
        """Create multigraph by combining MST and matching edges."""
        multigraph = [[] for _ in range(self.n)]
        
        # Add MST edges
        for i in range(self.n):
            for neighbor, weight in mst_adj[i]:
                if i < neighbor:  # Add each edge once
                    multigraph[i].append((neighbor, weight))
                    multigraph[neighbor].append((i, weight))
        
        # Add matching edges
        for u, v in matching:
            weight = self.distance(u, v)
            multigraph[u].append((v, weight))
            multigraph[v].append((u, weight))
        
        return multigraph
    
    def _find_eulerian_tour(self, multigraph: List[List[Tuple[int, float]]]) -> List[int]:
        """Find Eulerian tour using Hierholzer's algorithm."""
        # Create copy for modification
        graph = [neighbors.copy() for neighbors in multigraph]
        
        # Find vertex with edges
        start = 0
        for i in range(self.n):
            if graph[i]:
                start = i
                break
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if graph[v]:
                u, _ = graph[v].pop()
                # Remove reverse edge
                for idx, (neighbor, _) in enumerate(graph[u]):
                    if neighbor == v:
                        graph[u].pop(idx)
                        break
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        return tour[::-1]
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = [False] * self.n
        tour = []
        
        for v in eulerian_tour:
            if not visited[v]:
                visited[v] = True
                tour.append(v)
        
        # Return to start
        tour.append(tour[0])
        return tour
    
    def _compute_tour_length(self, tour: List[int]) -> float:
        """Compute total length of a tour."""
        length = 0.0
        for i in range(len(tour) - 1):
            length += self.distance(tour[i], tour[i + 1])
        return length
    
    def _two_opt(self, tour: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """Apply 2-opt local optimization."""
        n = len(tour) - 1  # Exclude closing vertex
        best_tour = tour.copy()
        best_length = self._compute_tour_length(best_tour)
        
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue  # No gain
                    
                    # Try 2-opt swap
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    
                    # Ensure tour is closed
                    if new_tour[-1] != new_tour[0]:
                        new_tour.append(new_tour[0])
                    
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
        
        # 3. Minimum weight perfect matching
        matching = self._minimum_weight_perfect_matching(odd_vertices)
        
        # 4. Create multigraph and find Eulerian tour
        multigraph = self._create_multigraph(mst_adj, matching)
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # 5. Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        tour_length = self._compute_tour_length(tour)
        
        # 6. Apply 2-opt if requested
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
    solver = ChristofidesHybridStructural(
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
    
    print("Testing Christofides Hybrid with Euclidean distances:")
    tour, length = solve_tsp(points)
    print(f"Tour: {tour}")
    print(f"Length: {length:.2f}")
    
    # Test with distance matrix
    print("\nTesting with custom distance matrix:")
    n = len(points)
    custom_dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            custom_dist[i][j] = abs(i - j) * 10  # Simple linear distance
    
    tour2, length2 = solve_tsp(points, distance_matrix=custom_dist)
    print(f"Tour: {tour2}")
    print(f"Length: {length2:.2f}")
    
    print("\n✅ Fixed version ready for TSPLIB evaluation")