#!/usr/bin/env python3
"""
Christofides with Learning-Based Matching
Novel hybrid TSP algorithm using reinforcement learning concepts.

Key Concept: Instead of static centrality measures, we use a simple
learning mechanism that adapts matching preferences based on historical
performance of edge selections.

Approach:
1. Maintain Q-values for edges between odd vertices
2. Q-value combines distance and learned preference
3. Update Q-values based on tour quality
4. Use ε-greedy exploration vs exploitation

This represents a novel integration of reinforcement learning concepts
with Christofides algorithm structure.

Author: Evo
Date: 2026-04-03
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq

class ChristofidesLearningMatching:
    """Christofides algorithm with learning-based matching."""
    
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
        
        # Q-learning parameters
        self.q_values = {}  # (u, v) -> Q-value
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # Exploration rate
        
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
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _initialize_q_values(self, odd_vertices: List[int]):
        """Initialize Q-values for edges between odd vertices."""
        m = len(odd_vertices)
        for i in range(m):
            u = odd_vertices[i]
            for j in range(i + 1, m):
                v = odd_vertices[j]
                key = (min(u, v), max(u, v))
                # Initialize with inverse distance (shorter edges have higher initial Q)
                distance = self.dist_matrix[u][v]
                self.q_values[key] = 1.0 / (1.0 + distance)
    
    def _get_q_value(self, u: int, v: int) -> float:
        """Get Q-value for edge (u, v)."""
        key = (min(u, v), max(u, v))
        return self.q_values.get(key, 0.0)
    
    def _update_q_value(self, u: int, v: int, reward: float):
        """Update Q-value using Q-learning update rule."""
        key = (min(u, v), max(u, v))
        old_q = self.q_values.get(key, 0.0)
        
        # Q-learning update: Q(s,a) = Q(s,a) + α * (reward + γ * max_a' Q(s',a') - Q(s,a))
        # Simplified: Q = Q + α * (reward - Q)
        new_q = old_q + self.learning_rate * (reward - old_q)
        self.q_values[key] = new_q
    
    def _learning_based_matching(self, odd_vertices: List[int], iteration: int = 0) -> List[Tuple[int, int]]:
        """
        Learning-based matching using Q-values.
        
        Uses ε-greedy strategy:
        - With probability ε: explore (choose random edges)
        - With probability 1-ε: exploit (choose edges with highest Q/distance ratio)
        
        Args:
            odd_vertices: List of vertices with odd degree
            iteration: Current iteration (for annealing epsilon)
        
        Returns: List of matched edges
        """
        m = len(odd_vertices)
        if m == 0:
            return []
        
        # Anneal epsilon (less exploration over time)
        current_epsilon = self.epsilon * (0.9 ** iteration)
        
        # Create all possible edges between odd vertices
        edges = []
        for i in range(m):
            u = odd_vertices[i]
            for j in range(i + 1, m):
                v = odd_vertices[j]
                distance = self.dist_matrix[u][v]
                q_value = self._get_q_value(u, v)
                
                # Score combines distance and Q-value
                # Higher Q-value means better historical performance
                score = distance / (1.0 + q_value)  # Lower is better
                edges.append((score, distance, q_value, u, v))
        
        # Sort by score
        edges.sort(key=lambda x: x[0])
        
        # ε-greedy selection
        matched = set()
        matching = []
        
        # With probability ε, shuffle edges for exploration
        if random.random() < current_epsilon:
            random.shuffle(edges)
        
        for score, distance, q_value, u, v in edges:
            if u not in matched and v not in matched:
                matched.add(u)
                matched.add(v)
                matching.append((u, v))
                
                if len(matched) == m:
                    break
        
        return matching
    
    def _compute_matching_reward(self, matching: List[Tuple[int, int]], tour_length: float) -> float:
        """
        Compute reward for matching based on resulting tour quality.
        
        Reward = 1 / (1 + normalized_tour_length)
        where normalized_tour_length = tour_length / baseline_estimate
        
        Higher reward means better tour quality.
        """
        # Estimate baseline (MST length * 2 is rough Christofides upper bound)
        mst_length = self._estimate_mst_length()
        baseline = mst_length * 2.0
        
        if baseline > 0:
            normalized_length = tour_length / baseline
            reward = 1.0 / (1.0 + normalized_length)
        else:
            reward = 0.5  # Default reward
        
        return reward
    
    def _estimate_mst_length(self) -> float:
        """Estimate MST length quickly."""
        # Use Prim's algorithm to compute MST length
        n = self.n
        visited = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0
        total_length = 0.0
        
        for _ in range(n):
            # Find vertex with minimum edge weight
            v = -1
            for j in range(n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            visited[v] = True
            
            # Add edge weight to total if not the root
            if min_edge[v] != float('inf'):
                total_length += min_edge[v]
            
            # Update minimum edges
            for to in range(n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
        
        return total_length
    
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
    
    def solve(self, learning_iterations: int = 3, apply_2opt: bool = True) -> Tuple[List[int], float, float]:
        """
        Solve TSP using Christofides with learning-based matching.
        
        Args:
            learning_iterations: Number of learning iterations
            apply_2opt: Whether to apply 2-opt optimization
        
        Returns:
            tour: List of vertex indices (starting and ending at same vertex)
            tour_length: Total tour length
            runtime: Execution time in seconds
        """
        start_time = time.time()
        
        best_tour = None
        best_length = float('inf')
        
        # 1. Compute MST (same for all iterations)
        mst_adj = self._compute_mst()
        
        # 2. Find odd degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # 3. Initialize Q-values
        self._initialize_q_values(odd_vertices)
        
        # Learning iterations
        for iteration in range(learning_iterations):
            # 4. Learning-based matching
            matching = self._learning_based_matching(odd_vertices, iteration)
            
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
            
            # Update best solution
            if tour_length < best_length:
                best_length = tour_length
                best_tour = tour
            
            # Compute reward and update Q-values
            reward = self._compute_matching_reward(matching, tour_length)
            for u, v in matching:
                self._update_q_value(u, v, reward)
        
        runtime = time.time() - start_time
        
        return best_tour, best_length, runtime


def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """
    Standard interface function for TSP algorithms.
    
    Args:
        points: List of (x, y) coordinates
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (tour, length) where tour is list of node indices
    """
    solver = ChristofidesLearningMatching(points, seed=seed)
    tour, length, runtime = solver.solve(learning_iterations=3, apply_2opt=True)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length


def test_algorithm():
    """Test the algorithm with a small example."""
    points = [(0, 0), (1, 0), (0, 1), (1, 1), (0.5, 0.5)]
    
    solver = ChristofidesLearningMatching(points, seed=42)
    tour, length, runtime = solver.solve(learning_iterations=3, apply_2opt=True)
    
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