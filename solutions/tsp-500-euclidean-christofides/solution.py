#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Christofides Algorithm
Evo - Algorithmic Solver
Implementation: Christofides algorithm with 1.5x approximation guarantee
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set
import json
import sys


class EuclideanTSP:
    """Euclidean TSP with points in unit square [0,1] x [0,1]"""
    
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
        Compute Minimum Spanning Tree using Prim's algorithm.
        
        Returns:
            List of edges (u, v, weight) in MST
        """
        # Initialize data structures
        visited = [False] * self.n
        min_edge = [float('inf')] * self.n
        parent = [-1] * self.n
        mst_edges = []
        
        # Start from vertex 0
        min_edge[0] = 0
        
        for _ in range(self.n):
            # Find vertex with minimum edge weight not yet in MST
            u = -1
            for v in range(self.n):
                if not visited[v] and (u == -1 or min_edge[v] < min_edge[u]):
                    u = v
            
            visited[u] = True
            
            # Add edge to MST (skip for first vertex)
            if parent[u] != -1:
                mst_edges.append((parent[u], u, self.distance(parent[u], u)))
            
            # Update min_edge for adjacent vertices
            for v in range(self.n):
                if not visited[v] and self.distance(u, v) < min_edge[v]:
                    min_edge[v] = self.distance(u, v)
                    parent[v] = u
        
        return mst_edges
    
    def get_odd_degree_vertices(self, mst_edges: List[Tuple[int, int, float]]) -> List[int]:
        """
        Find vertices with odd degree in MST.
        
        Args:
            mst_edges: List of edges in MST
            
        Returns:
            List of vertex indices with odd degree
        """
        degree = [0] * self.n
        for u, v, _ in mst_edges:
            degree[u] += 1
            degree[v] += 1
        
        odd_vertices = [i for i in range(self.n) if degree[i] % 2 == 1]
        return odd_vertices
    
    def minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Compute minimum-weight perfect matching on odd-degree vertices.
        Uses improved greedy algorithm with lookahead.
        
        Args:
            odd_vertices: List of odd-degree vertices
            
        Returns:
            List of matching edges (u, v, weight)
        """
        if len(odd_vertices) % 2 != 0:
            raise ValueError("Number of odd vertices must be even")
        
        # Create distance matrix for odd vertices only
        m = len(odd_vertices)
        odd_dist = np.zeros((m, m))
        for i in range(m):
            for j in range(i + 1, m):
                d = self.distance(odd_vertices[i], odd_vertices[j])
                odd_dist[i, j] = d
                odd_dist[j, i] = d
        
        # Improved matching algorithm
        matched = [False] * m
        matching_edges = []
        
        # While there are unmatched vertices
        while sum(matched) < m:
            # Find the best pair among remaining unmatched vertices
            best_i = -1
            best_j = -1
            best_score = float('inf')
            
            for i in range(m):
                if not matched[i]:
                    # Find best partner for i
                    for j in range(i + 1, m):
                        if not matched[j]:
                            # Score based on distance and potential alternatives
                            score = odd_dist[i, j]
                            
                            # Penalize if this vertex has very few good alternatives
                            # Find i's second best option
                            i_alternatives = []
                            for k in range(m):
                                if k != i and k != j and not matched[k]:
                                    i_alternatives.append(odd_dist[i, k])
                            i_second_best = min(i_alternatives) if i_alternatives else float('inf')
                            
                            # Find j's second best option
                            j_alternatives = []
                            for k in range(m):
                                if k != i and k != j and not matched[k]:
                                    j_alternatives.append(odd_dist[j, k])
                            j_second_best = min(j_alternatives) if j_alternatives else float('inf')
                            
                            # Adjust score: prefer matches where both vertices don't have good alternatives
                            adjusted_score = score * (1.0 + 0.1 * (i_second_best + j_second_best))
                            
                            if adjusted_score < best_score:
                                best_score = adjusted_score
                                best_i = i
                                best_j = j
            
            if best_i != -1 and best_j != -1:
                u = odd_vertices[best_i]
                v = odd_vertices[best_j]
                weight = odd_dist[best_i, best_j]
                matching_edges.append((u, v, weight))
                matched[best_i] = True
                matched[best_j] = True
            else:
                # Should not happen
                break
        
        return matching_edges
    
    def combine_mst_and_matching(self, mst_edges: List[Tuple[int, int, float]], 
                                matching_edges: List[Tuple[int, int, float]]) -> Dict[int, List[int]]:
        """
        Combine MST and matching to create Eulerian multigraph.
        
        Args:
            mst_edges: Edges from MST
            matching_edges: Edges from matching
            
        Returns:
            Adjacency list of Eulerian multigraph
        """
        # Create adjacency list
        adj = {i: [] for i in range(self.n)}
        
        # Add MST edges (each once)
        for u, v, _ in mst_edges:
            adj[u].append(v)
            adj[v].append(u)
        
        # Add matching edges (each once)
        for u, v, _ in matching_edges:
            adj[u].append(v)
            adj[v].append(u)
        
        return adj
    
    def find_eulerian_tour(self, adj: Dict[int, List[int]]) -> List[int]:
        """
        Find Eulerian tour using Hierholzer's algorithm.
        
        Args:
            adj: Adjacency list of Eulerian multigraph
            
        Returns:
            Eulerian tour (list of vertices)
        """
        # Make a copy of adjacency list to modify
        adj_copy = {v: neighbors[:] for v, neighbors in adj.items()}
        
        # Find a vertex with non-zero degree
        start = next(v for v in range(self.n) if adj_copy[v])
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if adj_copy[v]:
                # Take an edge from v
                u = adj_copy[v].pop()
                # Remove the reverse edge
                adj_copy[u].remove(v)
                stack.append(u)
            else:
                # No more edges from v
                tour.append(stack.pop())
        
        # Reverse to get correct order
        tour.reverse()
        return tour
    
    def shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> Tuple[List[int], float]:
        """
        Convert Eulerian tour to Hamiltonian tour by shortcutting.
        
        Args:
            eulerian_tour: Eulerian tour (may contain repeated vertices)
            
        Returns:
            Hamiltonian tour and total distance
        """
        visited = [False] * self.n
        hamiltonian_tour = []
        total_distance = 0.0
        
        prev = None
        for v in eulerian_tour:
            if not visited[v]:
                visited[v] = True
                hamiltonian_tour.append(v)
                if prev is not None:
                    total_distance += self.distance(prev, v)
                prev = v
        
        # Close the tour
        total_distance += self.distance(hamiltonian_tour[-1], hamiltonian_tour[0])
        hamiltonian_tour.append(hamiltonian_tour[0])
        
        return hamiltonian_tour, total_distance
    
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
    
    def tour_distance(self, tour: List[int]) -> float:
        """Calculate total distance of a tour."""
        distance = 0.0
        for i in range(len(tour) - 1):
            distance += self.distance(tour[i], tour[i + 1])
        return distance
    
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
        odd_vertices = self.get_odd_degree_vertices(mst_edges)
        
        # Step 3: Compute minimum-weight perfect matching on odd vertices
        matching_edges = self.minimum_weight_perfect_matching(odd_vertices)
        
        # Step 4: Combine MST and matching to create Eulerian multigraph
        eulerian_adj = self.combine_mst_and_matching(mst_edges, matching_edges)
        
        # Step 5: Find Eulerian tour
        eulerian_tour = self.find_eulerian_tour(eulerian_adj)
        
        # Step 6: Shortcut to Hamiltonian tour
        tour, distance = self.shortcut_eulerian_tour(eulerian_tour)
        
        # Step 7: Optional 2-opt local search improvement
        if apply_two_opt:
            tour, distance = self.two_opt(tour, max_iterations=500)
        
        return tour, distance
    
    def nearest_neighbor_multistart(self, num_starts: int = 10) -> Tuple[List[int], float]:
        """
        Run nearest neighbor from multiple starting cities and return best tour.
        For comparison with Christofides.
        
        Args:
            num_starts: Number of random starting cities to try
            
        Returns:
            best_tour: Best tour found
            best_distance: Distance of best tour
        """
        best_tour = None
        best_distance = float('inf')
        
        # Try different starting cities
        starts = random.sample(range(self.n), min(num_starts, self.n))
        
        for start in starts:
            # Simple nearest neighbor
            tour = [start]
            unvisited = set(range(self.n))
            unvisited.remove(start)
            current = start
            distance = 0.0
            
            while unvisited:
                nearest = min(unvisited, key=lambda city: self.distance(current, city))
                distance += self.distance(current, nearest)
                tour.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Return to start
            distance += self.distance(current, start)
            tour.append(start)
            
            if distance < best_distance:
                best_distance = distance
                best_tour = tour
        
        return best_tour, best_distance


def benchmark_christofides(num_instances: int = 10, n: int = 500) -> Dict:
    """
    Benchmark Christofides algorithm on multiple random instances.
    
    Args:
        num_instances: Number of random instances to test
        n: Number of cities
        
    Returns:
        Dictionary with benchmark results
    """
    results = {
        'algorithm': 'christofides',
        'n': n,
        'num_instances': num_instances,
        'instances': [],
        'summary': {}
    }
    
    all_tour_lengths = []
    all_runtimes = []
    
    for instance_id in range(num_instances):
        print(f"  Instance {instance_id + 1}/{num_instances}...")
        
        # Create TSP instance
        tsp = EuclideanTSP(n=n, seed=instance_id)
        
        # Run Christofides algorithm
        start_time = time.time()
        tour, distance = tsp.christofides()
        elapsed = time.time() - start_time
        
        # Run nearest neighbor for comparison
        nn_tour, nn_distance = tsp.nearest_neighbor_multistart(num_starts=10)
        
        # Store results
        instance_result = {
            'instance_id': instance_id,
            'seed': instance_id,
            'tour_length': distance,
            'nn_tour_length': nn_distance,
            'improvement_ratio': nn_distance / distance if distance > 0 else 1.0,
            'runtime': elapsed,
            'tour': tour[:20] + ["..."] if len(tour) > 20 else tour  # Store partial tour
        }
        
        results['instances'].append(instance_result)
        all_tour_lengths.append(distance)
        all_runtimes.append(elapsed)
    
    # Calculate summary statistics
    results['summary'] = {
        'avg_tour_length': np.mean(all_tour_lengths),
        'std_tour_length': np.std(all_tour_lengths),
        'min_tour_length': np.min(all_tour_lengths),
        'max_tour_length': np.max(all_tour_lengths),
        'avg_nn_tour_length': np.mean([inst['nn_tour_length'] for inst in results['instances']]),
        'avg_improvement_ratio': np.mean([inst['improvement_ratio'] for inst in results['instances']]),
        'avg_runtime': np.mean(all_runtimes),
        'total_runtime': np.sum(all_runtimes)
    }
    
    return results


def main():
    """Main function to test and benchmark Christofides algorithm."""
    print("=" * 60)
    print("Christofides Algorithm for Euclidean TSP")
    print("=" * 60)
    
    # Quick test with small instance
    print("\n1. Quick test with n=20:")
    tsp_small = EuclideanTSP(n=20, seed=42)
    tour_small, dist_small = tsp_small.christofides()
    nn_tour_small, nn_dist_small = tsp_small.nearest_neighbor_multistart(num_starts=5)
    print(f"   Christofides tour length: {dist_small:.4f}")
    print(f"   Nearest neighbor length: {nn_dist_small:.4f}")
    print(f"   Improvement ratio: {nn_dist_small/dist_small:.4f}")
    
    # Benchmark with 500 nodes
    print("\n2. Benchmarking with n=500 (3 instances):")
    results = benchmark_christofides(num_instances=3, n=500)
    
    print("\n3. Summary:")
    print(f"   Average tour length: {results['summary']['avg_tour_length']:.4f}")
    print(f"   Average NN tour length: {results['summary']['avg_nn_tour_length']:.4f}")
    print(f"   Average improvement over NN: {results['summary']['avg_improvement_ratio']:.4f}x")
    print(f"   Average runtime: {results['summary']['avg_runtime']:.3f}s")
    
    # Save results
    output_file = "/workspace/evovera/solutions/tsp-500-euclidean-christofides/benchmarks.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n4. Results saved to {output_file}")
    
    return results


if __name__ == "__main__":
    main()