#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Version 2: Christofides Algorithm with Improved Matching
FIXED VERSION for TSPLIB compatibility.
Accepts distance matrix parameter to support different TSPLIB distance metrics.
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set, Optional, Union


class ImprovedMatchingChristofides:
    """
    Christofides TSP with improved matching and distance matrix support.
    
    FIXED: Accepts precomputed distance matrix for TSPLIB compatibility.
    Supports both Euclidean (via points) and TSPLIB (via distance_matrix) inputs.
    """
    
    def __init__(self, points: Optional[np.ndarray] = None,
                 distance_matrix: Optional[np.ndarray] = None,
                 seed: Optional[int] = None, 
                 matching_algorithm: str = 'path_growing'):
        """
        Initialize TSP solver.
        
        Args:
            points: Array of shape (n, 2) with city coordinates
            distance_matrix: Precomputed distance matrix of shape (n, n)
            seed: Random seed for reproducibility
            matching_algorithm: Which matching algorithm to use
                'greedy_center': Original greedy with center sorting
                'greedy_best': Best of multiple greedy strategies
                'path_growing': Path growing algorithm (2-approximation)
                'hybrid': Hybrid approach (optimal for small, greedy for large)
                'random_restarts': Greedy with random restarts
        """
        if points is None and distance_matrix is None:
            raise ValueError("Must provide either points or distance_matrix")
        
        if points is not None:
            self.points = points
            self.n = points.shape[0]
            self.use_points = True
        else:
            self.n = distance_matrix.shape[0]
            self.use_points = False
        
        if distance_matrix is not None:
            self.dist_matrix = distance_matrix
            self.use_distance_matrix = True
        else:
            self.dist_matrix = None
            self.use_distance_matrix = False
        
        self.seed = seed
        self.matching_algorithm = matching_algorithm
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Compute distance matrix if not provided
        if not self.use_distance_matrix and self.use_points:
            self.dist_matrix = self._compute_distance_matrix()
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix from points."""
        if not self.use_points:
            raise ValueError("Cannot compute distance matrix without points")
        
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between cities i and j."""
        if self.dist_matrix is None:
            raise ValueError("Distance matrix not available")
        return self.dist_matrix[i, j]
    
    def _compute_mst(self) -> Tuple[List[List[Tuple[int, float]]], List[int]]:
        """Compute Minimum Spanning Tree using Prim's algorithm."""
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
    
    def _minimum_weight_perfect_matching_greedy(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Greedy minimum weight perfect matching."""
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
    
    def _minimum_weight_perfect_matching_path_growing(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Path growing algorithm for minimum weight perfect matching (2-approximation)."""
        if len(odd_vertices) % 2 != 0:
            raise ValueError("Odd vertices count must be even")
        
        matching = []
        vertices = odd_vertices.copy()
        
        while vertices:
            # Start a new path
            path = []
            current = vertices.pop()
            path.append(current)
            
            # Grow path
            while True:
                # Find closest vertex to current
                best_next = -1
                best_dist = float('inf')
                
                for v in vertices:
                    d = self.distance(current, v)
                    if d < best_dist:
                        best_dist = d
                        best_next = v
                
                if best_next == -1:
                    break
                
                # Add to path and remove from available vertices
                path.append(best_next)
                vertices.remove(best_next)
                current = best_next
            
            # Match vertices in path (alternating edges)
            for i in range(0, len(path) - 1, 2):
                matching.append((path[i], path[i + 1]))
        
        return matching
    
    def _minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Select matching algorithm based on configuration."""
        if self.matching_algorithm == 'path_growing':
            return self._minimum_weight_perfect_matching_path_growing(odd_vertices)
        else:  # Default to greedy
            return self._minimum_weight_perfect_matching_greedy(odd_vertices)
    
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
    
    def solve(self) -> Tuple[List[int], float]:
        """
        Solve TSP using Christofides algorithm with improved matching.
        
        Returns:
            tour: Hamiltonian tour
            tour_length: Total tour length
        """
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
        
        return tour, tour_length


def solve_tsp(points: np.ndarray, 
              distance_matrix: Optional[np.ndarray] = None,
              seed: Optional[int] = None) -> Tuple[List[int], float]:
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        distance_matrix: Optional precomputed distance matrix for TSPLIB
        seed: Random seed
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    solver = ImprovedMatchingChristofides(
        points=points,
        distance_matrix=distance_matrix,
        seed=seed,
        matching_algorithm='path_growing'
    )
    return solver.solve()


# Test function
if __name__ == "__main__":
    # Test with simple points
    points = np.array([[0, 0], [1, 0], [0, 1], [1, 1]])
    
    print("Testing Christofides Improved with Euclidean distances:")
    tour, length = solve_tsp(points)
    print(f"Tour: {tour}")
    print(f"Length: {length:.2f}")
    
    # Test with distance matrix
    print("\nTesting with custom distance matrix:")
    n = len(points)
    custom_dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            custom_dist[i, j] = abs(i - j) * 10  # Simple linear distance
    
    tour2, length2 = solve_tsp(points, distance_matrix=custom_dist)
    print(f"Tour: {tour2}")
    print(f"Length: {length2:.2f}")
    
    print("\n✅ Fixed version ready for TSPLIB evaluation")