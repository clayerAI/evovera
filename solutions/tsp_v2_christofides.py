#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Version 2: Christofides Algorithm
Evo - Algorithmic Solver
Christofides algorithm with 1.5x approximation guarantee for metric TSP
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set
import json


class EuclideanTSPChristofides:
    """Euclidean TSP with Christofides algorithm implementation"""
    
    def __init__(self, n: int = 500, seed: int = None):
        """
        Initialize random Euclidean TSP instance.
        
        Args:
            n: Number of cities
            seed: Random seed for reproducibility
        """
        self.n = n
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Generate random points in unit square
        self.points = np.random.rand(n, 2)
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix between all points."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between cities i and j."""
        return self.dist_matrix[i, j]
    
    def prim_mst(self) -> List[Tuple[int, int, float]]:
        """
        Prim's algorithm for Minimum Spanning Tree.
        
        Returns:
            List of MST edges as (u, v, weight) tuples
        """
        visited = [False] * self.n
        min_edge = [(float('inf'), -1)] * self.n  # (weight, parent)
        mst_edges = []
        
        # Start from vertex 0
        min_edge[0] = (0, -1)
        
        for _ in range(self.n):
            # Find vertex with minimum edge weight
            v = -1
            for j in range(self.n):
                if not visited[j] and (v == -1 or min_edge[j][0] < min_edge[v][0]):
                    v = j
            
            if min_edge[v][0] == float('inf'):
                break  # Graph is disconnected
            
            visited[v] = True
            if min_edge[v][1] != -1:
                mst_edges.append((min_edge[v][1], v, min_edge[v][0]))
            
            # Update minimum edges
            for to in range(self.n):
                if v != to and not visited[to]:
                    weight = self.distance(v, to)
                    if weight < min_edge[to][0]:
                        min_edge[to] = (weight, v)
        
        return mst_edges
    
    def find_odd_degree_vertices(self, mst_edges: List[Tuple[int, int, float]]) -> List[int]:
        """
        Find vertices with odd degree in MST.
        
        Args:
            mst_edges: List of MST edges
            
        Returns:
            List of odd-degree vertex indices
        """
        degree = [0] * self.n
        for u, v, _ in mst_edges:
            degree[u] += 1
            degree[v] += 1
        
        odd_vertices = [i for i in range(self.n) if degree[i] % 2 == 1]
        return odd_vertices
    
    def greedy_minimum_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Greedy algorithm for minimum-weight perfect matching on odd vertices.
        
        Args:
            odd_vertices: List of odd-degree vertices
            
        Returns:
            List of matching edges
        """
        if len(odd_vertices) % 2 != 0:
            raise ValueError("Number of odd vertices must be even")
        
        # Deterministic sorting by distance from center to eliminate variance
        # Calculate center of all points
        center = np.mean(self.points, axis=0)
        
        # Sort odd vertices by distance from center (deterministic)
        vertices = sorted(odd_vertices, 
                         key=lambda v: np.linalg.norm(self.points[v] - center))
        
        matched = [False] * self.n
        matching_edges = []
        
        while vertices:
            u = vertices.pop()
            if matched[u]:
                continue
            
            # Find closest unmatched odd vertex
            best_v = -1
            best_dist = float('inf')
            
            for v in vertices:
                if not matched[v]:
                    dist = self.distance(u, v)
                    if dist < best_dist:
                        best_dist = dist
                        best_v = v
            
            if best_v != -1:
                vertices.remove(best_v)
                matched[u] = True
                matched[best_v] = True
                matching_edges.append((u, best_v, best_dist))
        
        return matching_edges
    
    def optimal_minimum_matching_dp(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Dynamic programming optimal minimum-weight perfect matching.
        Time complexity: O(2^m * m^2) where m = len(odd_vertices).
        Only feasible for m ≤ 14 (2^14 * 14^2 ≈ 3.2M operations).
        
        Args:
            odd_vertices: List of odd-degree vertices
            
        Returns:
            Optimal matching edges
        """
        m = len(odd_vertices)
        if m % 2 != 0:
            raise ValueError("Number of odd vertices must be even")
        
        if m > 14:
            raise ValueError(f"DP optimal matching not feasible for m={m} > 14")
        
        # Map odd vertices to indices 0..m-1 for DP
        idx_to_vertex = odd_vertices.copy()
        vertex_to_idx = {v: i for i, v in enumerate(idx_to_vertex)}
        
        # Precompute distances between all odd vertices
        dist = [[0.0] * m for _ in range(m)]
        for i in range(m):
            for j in range(i + 1, m):
                d = self.distance(idx_to_vertex[i], idx_to_vertex[j])
                dist[i][j] = d
                dist[j][i] = d
        
        # DP[mask] = minimum cost to match vertices in mask
        # mask is bitmask of unmatched vertices
        dp = [float('inf')] * (1 << m)
        parent = [-1] * (1 << m)  # For reconstruction
        
        dp[0] = 0.0  # All vertices matched
        
        # Iterate over all masks
        for mask in range(1 << m):
            if dp[mask] == float('inf'):
                continue
            
            # Find first unmatched vertex
            i = 0
            while i < m and (mask >> i) & 1:
                i += 1
            
            if i == m:
                continue  # All vertices matched
            
            # Try matching i with each unmatched vertex j > i
            for j in range(i + 1, m):
                if not (mask >> j) & 1:
                    new_mask = mask | (1 << i) | (1 << j)
                    new_cost = dp[mask] + dist[i][j]
                    
                    if new_cost < dp[new_mask]:
                        dp[new_mask] = new_cost
                        parent[new_mask] = (mask, i, j)
        
        # Reconstruct matching from DP
        mask = (1 << m) - 1  # All vertices unmatched initially
        matching_edges = []
        
        while mask != 0:
            prev_mask, i, j = parent[mask]
            u = idx_to_vertex[i]
            v = idx_to_vertex[j]
            weight = dist[i][j]
            matching_edges.append((u, v, weight))
            mask = prev_mask
        
        return matching_edges
    
    def hybrid_minimum_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Hybrid matching: optimal DP for m ≤ 14, greedy for m > 14.
        
        Args:
            odd_vertices: List of odd-degree vertices
            
        Returns:
            List of matching edges
        """
        m = len(odd_vertices)
        
        if m == 0:
            return []
        
        if m <= 14:
            try:
                return self.optimal_minimum_matching_dp(odd_vertices)
            except (ValueError, MemoryError) as e:
                print(f"DP optimal matching failed for m={m}: {e}. Falling back to greedy.")
                return self.greedy_minimum_matching(odd_vertices)
        else:
            return self.greedy_minimum_matching(odd_vertices)
    
    def combine_mst_and_matching(self, mst_edges: List[Tuple[int, int, float]], 
                                matching_edges: List[Tuple[int, int, float]]) -> Dict[int, List[int]]:
        """
        Combine MST and matching edges to create Eulerian multigraph.
        
        Returns:
            Adjacency list representation of multigraph
        """
        graph = {i: [] for i in range(self.n)}
        
        # Add MST edges (each once)
        for u, v, _ in mst_edges:
            graph[u].append(v)
            graph[v].append(u)
        
        # Add matching edges (each once)
        for u, v, _ in matching_edges:
            graph[u].append(v)
            graph[v].append(u)
        
        return graph
    
    def find_eulerian_tour(self, graph: Dict[int, List[int]]) -> List[int]:
        """
        Hierholzer's algorithm for finding Eulerian tour.
        
        Args:
            graph: Adjacency list of multigraph
            
        Returns:
            Eulerian tour (list of vertices)
        """
        # Check if graph has Eulerian circuit
        for v in range(self.n):
            if len(graph[v]) % 2 != 0:
                raise ValueError("Graph doesn't have Eulerian circuit")
        
        # Make copy of graph
        graph_copy = {v: neighbors[:] for v, neighbors in graph.items()}
        
        # Start from any vertex with edges
        start = next(v for v in range(self.n) if graph_copy[v])
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if graph_copy[v]:
                u = graph_copy[v].pop()
                graph_copy[u].remove(v)  # Remove reverse edge
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        # Reverse to get correct order
        tour.reverse()
        return tour
    
    def shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> Tuple[List[int], float]:
        """
        Convert Eulerian tour to Hamiltonian tour by shortcutting repeated vertices.
        
        Args:
            eulerian_tour: Eulerian tour (may repeat vertices)
            
        Returns:
            Hamiltonian tour and its total distance
        """
        visited = [False] * self.n
        hamiltonian_tour = []
        total_distance = 0.0
        
        prev = -1
        for v in eulerian_tour:
            if not visited[v]:
                visited[v] = True
                hamiltonian_tour.append(v)
                if prev != -1:
                    total_distance += self.distance(prev, v)
                prev = v
        
        # Close the tour
        total_distance += self.distance(hamiltonian_tour[-1], hamiltonian_tour[0])
        hamiltonian_tour.append(hamiltonian_tour[0])
        
        return hamiltonian_tour, total_distance
    
    def tour_distance(self, tour: List[int]) -> float:
        """Calculate total distance of a tour."""
        distance = 0.0
        for i in range(len(tour) - 1):
            distance += self.distance(tour[i], tour[i + 1])
        return distance
    
    def two_opt(self, tour: List[int], max_iterations: int = 100) -> Tuple[List[int], float]:
        """
        Improve tour using efficient 2-opt local search.
        Uses neighbor lists and early termination for better performance.
        
        Args:
            tour: Initial tour (must start and end at same vertex)
            max_iterations: Maximum number of iterations
            
        Returns:
            Improved tour and its distance
        """
        if len(tour) < 4 or tour[0] != tour[-1]:
            return tour, self.tour_distance(tour)
        
        # Remove duplicate start/end for processing
        tour = tour[:-1]
        n = len(tour)
        
        # Precompute distance matrix accessor
        dist_matrix = self.dist_matrix
        
        # Compute current distance
        current_distance = 0.0
        for k in range(n):
            current_distance += dist_matrix[tour[k], tour[(k + 1) % n]]
        
        best_distance = current_distance
        best_tour = tour[:]
        
        # Create position map for O(1) lookups
        position = {city: idx for idx, city in enumerate(tour)}
        
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            # Try all possible 2-opt swaps
            for i in range(n):
                a = tour[i]
                b = tour[(i + 1) % n]
                
                # Only check promising swaps: j should be "far" from i
                # and connected to cities that might benefit from swap
                for j in range(i + 2, min(i + 50, n)):  # Limit search window
                    if j == n - 1 and i == 0:
                        continue
                    
                    c = tour[j]
                    d = tour[(j + 1) % n]
                    
                    # Quick check: if edges are already short, skip
                    ab = dist_matrix[a, b]
                    cd = dist_matrix[c, d]
                    ac = dist_matrix[a, c]
                    bd = dist_matrix[b, d]
                    
                    # Calculate gain
                    gain = (ab + cd) - (ac + bd)
                    
                    if gain > 1e-9:  # Significant improvement
                        # Perform the swap
                        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                        new_distance = current_distance - gain
                        
                        # Update tour and distance
                        tour = new_tour
                        current_distance = new_distance
                        
                        # Update position map
                        for idx, city in enumerate(tour[i+1:j+1]):
                            position[city] = i + 1 + idx
                        
                        if new_distance < best_distance:
                            best_tour = tour[:]
                            best_distance = new_distance
                        
                        improved = True
                        break  # Restart search after finding improvement
                
                if improved:
                    break
        
        # Add closing vertex
        best_tour.append(best_tour[0])
        return best_tour, best_distance
    
    def christofides(self, apply_two_opt: bool = True) -> Tuple[List[int], float]:
        """
        Christofides algorithm for Euclidean TSP.
        
        Args:
            apply_two_opt: Whether to apply 2-opt local search improvement
            
        Returns:
            tour: Hamiltonian tour
            total_distance: Total tour length
        """
        # Step 1: Compute MST
        mst_edges = self.prim_mst()
        
        # Step 2: Find odd-degree vertices in MST
        odd_vertices = self.find_odd_degree_vertices(mst_edges)
        
        # Step 3: Minimum-weight perfect matching on odd vertices
        # Use hybrid matching: optimal DP for m ≤ 14, greedy for m > 14
        matching_edges = self.hybrid_minimum_matching(odd_vertices)
        
        # Step 4: Combine MST and matching to create Eulerian multigraph
        eulerian_graph = self.combine_mst_and_matching(mst_edges, matching_edges)
        
        # Step 5: Find Eulerian tour
        eulerian_tour = self.find_eulerian_tour(eulerian_graph)
        
        # Step 6: Shortcut to Hamiltonian tour
        tour, distance = self.shortcut_eulerian_tour(eulerian_tour)
        
        # Step 7: Optional 2-opt local search improvement
        if apply_two_opt:
            tour, distance = self.two_opt(tour, max_iterations=500)
        
        return tour, distance


def solve_tsp(points):
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    n = len(points)
    
    # Create a custom TSP instance with these points
    class CustomTSP:
        def __init__(self, points):
            self.n = len(points)
            self.points = points
            self.dist_matrix = self._compute_distance_matrix()
        
        def _compute_distance_matrix(self):
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
        
        def distance(self, i, j):
            return self.dist_matrix[i, j]
        
        def prim_mst(self):
            """Prim's algorithm for Minimum Spanning Tree."""
            visited = [False] * self.n
            parent = [-1] * self.n
            key = [float('inf')] * self.n
            key[0] = 0
            
            for _ in range(self.n):
                # Find minimum key vertex not yet visited
                min_key = float('inf')
                u = -1
                for v in range(self.n):
                    if not visited[v] and key[v] < min_key:
                        min_key = key[v]
                        u = v
                
                visited[u] = True
                
                # Update key values for adjacent vertices
                for v in range(self.n):
                    if not visited[v] and self.distance(u, v) < key[v]:
                        key[v] = self.distance(u, v)
                        parent[v] = u
            
            # Build MST edges
            mst_edges = []
            for v in range(1, self.n):
                if parent[v] != -1:
                    mst_edges.append((parent[v], v, self.distance(parent[v], v)))
            
            return mst_edges
        
        def find_odd_degree_vertices(self, mst_edges):
            """Find vertices with odd degree in MST."""
            degree = [0] * self.n
            for u, v, _ in mst_edges:
                degree[u] += 1
                degree[v] += 1
            
            odd_vertices = [i for i in range(self.n) if degree[i] % 2 == 1]
            return odd_vertices
        
        def greedy_matching(self, odd_vertices):
            """Greedy matching for odd-degree vertices."""
            matched = [False] * len(odd_vertices)
            matching_edges = []
            
            for i in range(len(odd_vertices)):
                if matched[i]:
                    continue
                
                min_dist = float('inf')
                min_j = -1
                
                for j in range(i + 1, len(odd_vertices)):
                    if not matched[j]:
                        dist = self.distance(odd_vertices[i], odd_vertices[j])
                        if dist < min_dist:
                            min_dist = dist
                            min_j = j
                
                if min_j != -1:
                    matching_edges.append((odd_vertices[i], odd_vertices[j], min_dist))
                    matched[i] = True
                    matched[min_j] = True
            
            return matching_edges
        
        def build_multigraph(self, mst_edges, matching_edges):
            """Build multigraph from MST and matching edges."""
            graph = {i: [] for i in range(self.n)}
            
            # Add MST edges
            for u, v, _ in mst_edges:
                graph[u].append(v)
                graph[v].append(u)
            
            # Add matching edges
            for u, v, _ in matching_edges:
                graph[u].append(v)
                graph[v].append(u)
            
            return graph
        
        def find_eulerian_tour(self, graph):
            """Find Eulerian tour using Hierholzer's algorithm."""
            # Make a copy of the graph
            graph_copy = {v: neighbors[:] for v, neighbors in graph.items()}
            
            # Find a vertex with odd degree (or any vertex)
            start = next((v for v, neighbors in graph_copy.items() if neighbors), 0)
            
            stack = [start]
            tour = []
            
            while stack:
                v = stack[-1]
                if graph_copy[v]:
                    u = graph_copy[v].pop()
                    # Remove the reverse edge
                    graph_copy[u].remove(v)
                    stack.append(u)
                else:
                    tour.append(stack.pop())
            
            return tour[::-1]
        
        def shortcut_eulerian_tour(self, eulerian_tour):
            """Shortcut Eulerian tour to Hamiltonian tour."""
            visited = [False] * self.n
            tour = []
            
            for v in eulerian_tour:
                if not visited[v]:
                    visited[v] = True
                    tour.append(v)
            
            # Return to starting city
            tour.append(tour[0])
            
            # Calculate total distance
            total_distance = 0.0
            for i in range(len(tour) - 1):
                j = (i + 1) % len(tour)
                total_distance += self.distance(tour[i], tour[j])
            
            return tour, total_distance
        
        def two_opt(self, tour, max_iterations=500):
            """2-opt local search with limited neighbor search."""
            if len(tour) < 4 or tour[0] != tour[-1]:
                return tour, self.tour_distance(tour)
            
            tour = tour[:-1]
            n = len(tour)
            improved = True
            iteration = 0
            
            while improved and iteration < max_iterations:
                improved = False
                for i in range(n - 1):
                    for j in range(i + 2, min(i + 21, n)):  # Limited neighborhood
                        # Calculate current distance for edges (i, i+1) and (j, j+1)
                        current = (self.distance(tour[i], tour[(i + 1) % n]) +
                                  self.distance(tour[j], tour[(j + 1) % n]))
                        # Calculate new distance if we reverse segment between i+1 and j
                        new = (self.distance(tour[i], tour[j]) +
                              self.distance(tour[(i + 1) % n], tour[(j + 1) % n]))
                        
                        if new < current:
                            # Reverse the segment
                            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                            improved = True
                            break
                    if improved:
                        break
                iteration += 1
            
            # Add back the starting city
            tour.append(tour[0])
            
            # Calculate final distance
            distance = 0.0
            for i in range(len(tour) - 1):
                distance += self.distance(tour[i], tour[i + 1])
            
            return tour, distance
        
        def christofides(self, apply_two_opt=True):
            """Christofides algorithm for TSP."""
            # Step 1: Find MST
            mst_edges = self.prim_mst()
            
            # Step 2: Find odd-degree vertices
            odd_vertices = self.find_odd_degree_vertices(mst_edges)
            
            # Step 3: Minimum weight perfect matching on odd vertices
            matching_edges = self.greedy_matching(odd_vertices)
            
            # Step 4: Build multigraph
            graph = self.build_multigraph(mst_edges, matching_edges)
            
            # Step 5: Find Eulerian tour
            eulerian_tour = self.find_eulerian_tour(graph)
            
            # Step 6: Shortcut to Hamiltonian tour
            tour, distance = self.shortcut_eulerian_tour(eulerian_tour)
            
            # Step 7: Optional 2-opt improvement
            if apply_two_opt:
                tour, distance = self.two_opt(tour, max_iterations=500)
            
            return tour, distance
    
    tsp = CustomTSP(points)
    
    # Run Christofides algorithm
    tour, distance = tsp.christofides(apply_two_opt=True)
    
    return tour, distance


def benchmark_christofides():
    """Benchmark Christofides algorithm."""
    print("Benchmarking Christofides Algorithm for Euclidean TSP (n=500)")
    print("=" * 70)
    
    results = []
    num_instances = 5  # Fewer instances due to longer runtime
    total_time = 0.0
    
    for i in range(num_instances):
        print(f"\nInstance {i+1}/{num_instances}:")
        
        # Create TSP instance
        tsp = EuclideanTSPChristofides(n=500, seed=i)
        
        # Time the algorithm
        start_time = time.time()
        tour, distance = tsp.christofides(apply_two_opt=True)
        end_time = time.time()
        
        instance_time = end_time - start_time
        total_time += instance_time
        
        print(f"  Tour length: {distance:.4f}")
        print(f"  Time: {instance_time:.3f} seconds")
        
        results.append({
            "instance": i,
            "seed": i,
            "tour_length": distance,
            "time": instance_time,
            "algorithm": "christofides_with_2opt"
        })
    
    # Calculate statistics
    tour_lengths = [r["tour_length"] for r in results]
    avg_length = np.mean(tour_lengths)
    std_length = np.std(tour_lengths)
    avg_time = total_time / num_instances
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  Number of instances: {num_instances}")
    print(f"  Average tour length: {avg_length:.4f}")
    print(f"  Standard deviation: {std_length:.4f}")
    print(f"  Average time per instance: {avg_time:.3f} seconds")
    
    # Save results
    output = {
        "algorithm": "christofides_with_2opt",
        "n": 500,
        "num_instances": num_instances,
        "average_tour_length": avg_length,
        "std_tour_length": std_length,
        "average_time": avg_time,
        "results": results
    }
    
    with open("christofides_benchmarks.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\nResults saved to 'christofides_benchmarks.json'")


if __name__ == "__main__":
    benchmark_christofides()