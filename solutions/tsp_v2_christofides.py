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
        
        vertices = odd_vertices[:]
        random.shuffle(vertices)  # Randomize for different matchings
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
    
    def two_opt(self, tour: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """
        Improve tour using 2-opt local search.
        
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
        best_tour = tour[:]
        best_distance = self.tour_distance(tour + [tour[0]])
        
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(n):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue  # Don't swap first and last
                    
                    # Calculate gain from 2-opt swap
                    a, b = tour[i], tour[(i + 1) % n]
                    c, d = tour[j], tour[(j + 1) % n]
                    
                    old_distance = self.distance(a, b) + self.distance(c, d)
                    new_distance = self.distance(a, c) + self.distance(b, d)
                    
                    if new_distance < old_distance:
                        # Perform 2-opt swap
                        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                        new_tour_distance = self.tour_distance(new_tour + [new_tour[0]])
                        
                        if new_tour_distance < best_distance:
                            best_tour = new_tour[:]
                            best_distance = new_tour_distance
                            tour = new_tour[:]
                            improved = True
                            break  # Restart search after improvement
                
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
        matching_edges = self.greedy_minimum_matching(odd_vertices)
        
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


def solve_tsp(coordinates: List[Tuple[float, float]]) -> List[int]:
    """
    Solve TSP using Christofides algorithm with 2-opt (Evo's algorithm).
    Wrapper for adversarial testing framework.
    
    Args:
        coordinates: List of (x, y) coordinates for each city
    
    Returns:
        List of city indices in visitation order (0-based)
    """
    n = len(coordinates)
    
    # Convert coordinates to numpy array
    points = np.array(coordinates)
    
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
            """Prim's algorithm for MST."""
            visited = [False] * self.n
            min_edge = [float('inf')] * self.n
            parent = [-1] * self.n
            min_edge[0] = 0
            
            for _ in range(self.n):
                # Find minimum edge vertex
                u = -1
                for v in range(self.n):
                    if not visited[v] and (u == -1 or min_edge[v] < min_edge[u]):
                        u = v
                
                visited[u] = True
                
                # Update adjacent vertices
                for v in range(self.n):
                    if not visited[v] and self.distance(u, v) < min_edge[v]:
                        min_edge[v] = self.distance(u, v)
                        parent[v] = u
            
            # Build MST edges
            mst_edges = []
            for v in range(1, self.n):
                if parent[v] != -1:
                    mst_edges.append((parent[v], v))
            return mst_edges
        
        def find_odd_degree_vertices(self, edges):
            """Find vertices with odd degree in the MST."""
            degree = [0] * self.n
            for u, v in edges:
                degree[u] += 1
                degree[v] += 1
            
            odd_vertices = [i for i in range(self.n) if degree[i] % 2 == 1]
            return odd_vertices
        
        def greedy_minimum_matching(self, odd_vertices):
            """Greedy minimum-weight perfect matching on odd vertices (O(m²))."""
            if not odd_vertices:
                return []
            
            matched = [False] * self.n
            matching_edges = []
            
            # Create list of odd vertices
            odd_list = odd_vertices.copy()
            
            while odd_list:
                u = odd_list.pop(0)
                if matched[u]:
                    continue
                
                # Find closest unmatched odd vertex
                best_v = None
                best_dist = float('inf')
                
                for v in odd_list:
                    if not matched[v]:
                        dist = self.distance(u, v)
                        if dist < best_dist:
                            best_dist = dist
                            best_v = v
                
                if best_v is not None:
                    matching_edges.append((u, best_v))
                    matched[u] = True
                    matched[best_v] = True
                    odd_list.remove(best_v)
            
            return matching_edges
        
        def combine_mst_and_matching(self, mst_edges, matching_edges):
            """Combine MST and matching edges to create Eulerian multigraph."""
            # Use adjacency list representation
            graph = [[] for _ in range(self.n)]
            
            # Add MST edges
            for u, v in mst_edges:
                graph[u].append(v)
                graph[v].append(u)
            
            # Add matching edges
            for u, v in matching_edges:
                graph[u].append(v)
                graph[v].append(u)
            
            return graph
        
        def find_eulerian_tour(self, graph):
            """Find Eulerian tour using Hierholzer's algorithm."""
            # Make a copy of the graph
            graph_copy = [neighbors.copy() for neighbors in graph]
            
            # Find a vertex with neighbors
            start = 0
            for i in range(self.n):
                if graph_copy[i]:
                    start = i
                    break
            
            stack = [start]
            tour = []
            
            while stack:
                v = stack[-1]
                if graph_copy[v]:
                    u = graph_copy[v].pop()
                    graph_copy[u].remove(v)
                    stack.append(u)
                else:
                    tour.append(stack.pop())
            
            return tour[::-1]
        
        def shortcut_eulerian_tour(self, eulerian_tour):
            """Shortcut Eulerian tour to Hamiltonian tour."""
            visited = [False] * self.n
            tour = []
            total_distance = 0.0
            
            for v in eulerian_tour:
                if not visited[v]:
                    visited[v] = True
                    tour.append(v)
            
            # Calculate total distance
            for i in range(len(tour)):
                j = (i + 1) % len(tour)
                total_distance += self.distance(tour[i], tour[j])
            
            return tour, total_distance
        
        def two_opt(self, tour, max_iterations=500):
            """2-opt local search with limited neighbor search."""
            best_tour = tour.copy()
            best_distance = self.tour_distance(tour)
            
            n = len(tour)
            improved = True
            iterations = 0
            
            while improved and iterations < max_iterations:
                improved = False
                
                for i in range(n):
                    # Only check limited window of neighbors for speed
                    window_size = min(50, n)
                    for k in range(1, window_size):
                        j = (i + k) % n
                        
                        # Calculate potential improvement
                        a1, a2 = best_tour[i], best_tour[(i + 1) % n]
                        b1, b2 = best_tour[j], best_tour[(j + 1) % n]
                        
                        current = self.distance(a1, a2) + self.distance(b1, b2)
                        new = self.distance(a1, b1) + self.distance(a2, b2)
                        
                        if new < current:
                            # Perform 2-opt swap
                            if i < j:
                                best_tour[i+1:j+1] = reversed(best_tour[i+1:j+1])
                            else:
                                # Handle wrap-around case
                                segment = best_tour[i+1:] + best_tour[:j+1]
                                segment.reverse()
                                best_tour[i+1:] = segment[:len(best_tour)-i-1]
                                best_tour[:j+1] = segment[len(best_tour)-i-1:]
                            
                            best_distance = self.tour_distance(best_tour)
                            improved = True
                            break
                    
                    if improved:
                        break
                
                iterations += 1
            
            return best_tour, best_distance
        
        def tour_distance(self, tour):
            """Calculate total distance of a tour."""
            total = 0.0
            for i in range(len(tour)):
                j = (i + 1) % len(tour)
                total += self.distance(tour[i], tour[j])
            return total
        
        def christofides(self, apply_two_opt: bool = True):
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
            matching_edges = self.greedy_minimum_matching(odd_vertices)
            
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
    
    tsp = CustomTSP(points)
    
    # Run Christofides algorithm
    tour, distance = tsp.christofides(apply_two_opt=True)
    
    return tour


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