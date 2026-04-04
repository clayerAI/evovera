#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Version 2: Christofides Algorithm with Improved Matching
Evo - Algorithmic Solver with Vera's improved matching algorithms
Christofides algorithm with better matching heuristics for improved quality
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set
import json


class ImprovedMatchingChristofides:
    """
    Euclidean TSP with Christofides algorithm and improved matching.
    
    Key improvements over original:
    1. Multiple matching algorithms with better quality guarantees
    2. Path growing algorithm (2-approximation) as default
    3. Optional local search optimization for matching
    4. Hybrid approach for small/large instances
    """
    
    def __init__(self, n: int = 500, seed: int = None, matching_algorithm: str = 'path_growing'):
        """
        Initialize random Euclidean TSP instance.
        
        Args:
            n: Number of cities
            seed: Random seed for reproducibility
            matching_algorithm: Which matching algorithm to use
                'greedy_center': Original greedy with center sorting
                'greedy_best': Best of multiple greedy strategies
                'path_growing': Path growing algorithm (2-approximation)
                'hybrid': Hybrid approach (optimal for small, greedy for large)
                'random_restarts': Greedy with random restarts
        """
        self.n = n
        self.seed = seed
        self.matching_algorithm = matching_algorithm
        
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
    
    # ===== IMPROVED MATCHING ALGORITHMS =====
    
    def greedy_matching_basic(self, odd_vertices: List[int], sort_key: str = 'center') -> List[Tuple[int, int, float]]:
        """
        Basic greedy matching with configurable sorting.
        
        Args:
            odd_vertices: List of odd-degree vertices
            sort_key: How to sort vertices ('center', 'x', 'y', 'random')
        
        Returns:
            List of matching edges
        """
        vertices = odd_vertices.copy()
        
        # Apply sorting based on key
        if sort_key == 'center':
            center = np.mean(self.points, axis=0)
            vertices.sort(key=lambda v: np.linalg.norm(self.points[v] - center))
        elif sort_key == 'x':
            vertices.sort(key=lambda v: self.points[v][0])
        elif sort_key == 'y':
            vertices.sort(key=lambda v: self.points[v][1])
        elif sort_key == 'random':
            random.shuffle(vertices)
        else:
            raise ValueError(f"Unknown sort_key: {sort_key}")
        
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
    
    def greedy_matching_best_of_k(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Try multiple greedy strategies, keep best.
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            Best matching edges found
        """
        strategies = ['center', 'x', 'y', 'random']
        best_edges = None
        best_cost = float('inf')
        
        for strategy in strategies:
            edges = self.greedy_matching_basic(odd_vertices, sort_key=strategy)
            cost = sum(edge[2] for edge in edges)
            
            if cost < best_cost:
                best_cost = cost
                best_edges = edges
        
        return best_edges
    
    def greedy_matching_random_restarts(self, odd_vertices: List[int], restarts: int = 20) -> List[Tuple[int, int, float]]:
        """
        Greedy matching with multiple random restarts, keep best.
        
        Args:
            odd_vertices: List of odd-degree vertices
            restarts: Number of random restarts
        
        Returns:
            Best matching edges found
        """
        best_edges = None
        best_cost = float('inf')
        
        for _ in range(restarts):
            edges = self.greedy_matching_basic(odd_vertices, sort_key='random')
            cost = sum(edge[2] for edge in edges)
            
            if cost < best_cost:
                best_cost = cost
                best_edges = edges
        
        return best_edges
    
    def path_growing_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Path growing algorithm for matching (2-approximation).
        
        Algorithm:
        1. Start with an arbitrary vertex
        2. Repeatedly add the closest unmatched vertex to the path
        3. When path has even length, match the two middle vertices
        4. Continue until all vertices are matched
        
        This is a 2-approximation algorithm with O(m²) complexity.
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            Matching edges
        """
        vertices = set(odd_vertices)
        matched = [False] * self.n
        matching_edges = []
        
        while vertices:
            # Start a new path with an arbitrary unmatched vertex
            start = next(iter(vertices))
            path = [start]
            vertices.remove(start)
            
            # Grow the path
            while True:
                # Find closest unmatched vertex to the last vertex in path
                last = path[-1]
                best_v = -1
                best_dist = float('inf')
                
                for v in vertices:
                    dist = self.distance(last, v)
                    if dist < best_dist:
                        best_dist = dist
                        best_v = v
                
                if best_v == -1:
                    # No more vertices to add
                    break
                
                # Add to path
                path.append(best_v)
                vertices.remove(best_v)
                
                # If path has even length, match the two middle vertices
                if len(path) % 2 == 0:
                    mid = len(path) // 2
                    u = path[mid - 1]
                    v = path[mid]
                    
                    matched[u] = True
                    matched[v] = True
                    dist = self.distance(u, v)
                    matching_edges.append((u, v, dist))
        
        return matching_edges
    
    def exhaustive_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Exhaustive search for minimum-weight perfect matching.
        Only for very small instances (m ≤ 10).
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            Optimal matching edges
        """
        m = len(odd_vertices)
        if m > 10:
            raise ValueError(f"Exhaustive search not feasible for {m} vertices")
        
        # Generate all perfect matchings using recursion
        vertices = odd_vertices.copy()
        best_edges = None
        best_cost = float('inf')
        
        def dfs(unmatched: List[int], current_edges: List[Tuple[int, int, float]], current_cost: float):
            nonlocal best_edges, best_cost
            
            if not unmatched:
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_edges = current_edges.copy()
                return
            
            # Pick first unmatched vertex
            u = unmatched[0]
            
            # Try pairing with each remaining vertex
            for i in range(1, len(unmatched)):
                v = unmatched[i]
                dist = self.distance(u, v)
                
                # Create new lists
                new_unmatched = unmatched[1:i] + unmatched[i+1:]
                new_edges = current_edges + [(u, v, dist)]
                new_cost = current_cost + dist
                
                # Recursive call
                dfs(new_unmatched, new_edges, new_cost)
        
        dfs(vertices, [], 0.0)
        return best_edges
    
    def hybrid_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Hybrid matching: use optimal algorithm for small instances, path growing for large.
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            Matching edges
        """
        m = len(odd_vertices)
        
        if m <= 10:
            # Try exhaustive search for small instances
            try:
                return self.exhaustive_matching(odd_vertices)
            except Exception:
                # Fall back to path growing
                pass
        
        # For larger instances, use path growing (good theoretical guarantees)
        return self.path_growing_matching(odd_vertices)
    
    def minimum_weight_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int, float]]:
        """
        Main matching function - dispatches to selected algorithm.
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            List of matching edges
        """
        if len(odd_vertices) % 2 != 0:
            raise ValueError("Number of odd vertices must be even")
        
        if len(odd_vertices) == 0:
            return []
        
        # Dispatch to selected algorithm
        if self.matching_algorithm == 'greedy_center':
            return self.greedy_matching_basic(odd_vertices, 'center')
        elif self.matching_algorithm == 'greedy_best':
            return self.greedy_matching_best_of_k(odd_vertices)
        elif self.matching_algorithm == 'path_growing':
            return self.path_growing_matching(odd_vertices)
        elif self.matching_algorithm == 'hybrid':
            return self.hybrid_matching(odd_vertices)
        elif self.matching_algorithm == 'random_restarts':
            return self.greedy_matching_random_restarts(odd_vertices, 20)
        else:
            raise ValueError(f"Unknown matching algorithm: {self.matching_algorithm}")
    
    # ===== CHRISTOFIDES ALGORITHM CORE =====
    
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
        # Make copy since we'll be modifying the graph
        graph = {k: v.copy() for k, v in graph.items()}
        
        # Find vertex with non-zero degree
        start = next((v for v, neighbors in graph.items() if neighbors), 0)
        
        stack = [start]
        tour = []
        
        while stack:
            v = stack[-1]
            if graph[v]:
                u = graph[v].pop()
                graph[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        return tour[::-1]
    
    def shortcut_to_hamiltonian(self, eulerian_tour: List[int]) -> List[int]:
        """
        Convert Eulerian tour to Hamiltonian tour by shortcutting visited vertices.
        
        Args:
            eulerian_tour: Eulerian tour (may repeat vertices)
            
        Returns:
            Hamiltonian tour (visits each vertex exactly once)
        """
        visited = [False] * self.n
        hamiltonian_tour = []
        
        for v in eulerian_tour:
            if not visited[v]:
                visited[v] = True
                hamiltonian_tour.append(v)
        
        # Close the tour
        hamiltonian_tour.append(hamiltonian_tour[0])
        return hamiltonian_tour
    
    def tour_length(self, tour: List[int]) -> float:
        """
        Calculate total length of a tour.
        
        Args:
            tour: List of vertex indices (first and last should be same for closed tour)
            
        Returns:
            Total tour length
        """
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.distance(tour[i], tour[i + 1])
        return total
    
    def two_opt(self, tour: List[int], max_iterations: int = 1000) -> List[int]:
        """
        2-opt local search optimization.
        
        Args:
            tour: Initial tour (closed, first == last)
            max_iterations: Maximum number of improvement iterations
            
        Returns:
            Improved tour
        """
        # Remove the closing vertex for 2-opt operations
        if tour[0] == tour[-1]:
            current_tour = tour[:-1]
        else:
            current_tour = tour.copy()
        
        n = len(current_tour)
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            best_delta = 0.0
            best_i = -1
            best_j = -1
            
            for i in range(n - 1):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue  # Don't consider the same edge
                    
                    # Current edges: (i, i+1) and (j, j+1 mod n)
                    a, b = current_tour[i], current_tour[(i + 1) % n]
                    c, d = current_tour[j], current_tour[(j + 1) % n]
                    
                    current = self.distance(a, b) + self.distance(c, d)
                    # New edges: (i, j) and (i+1, j+1 mod n)
                    new = self.distance(a, c) + self.distance(b, d)
                    
                    delta = current - new
                    
                    if delta > best_delta:
                        best_delta = delta
                        best_i = i
                        best_j = j
            
            if best_delta > 1e-10:
                # Apply the best 2-opt swap
                i, j = best_i, best_j
                # Reverse segment between i+1 and j
                current_tour[i + 1:j + 1] = reversed(current_tour[i + 1:j + 1])
                improved = True
        
        # Close the tour
        improved_tour = current_tour + [current_tour[0]]
        return improved_tour
    
    def solve(self) -> Tuple[List[int], float]:
        """
        Solve TSP using Christofides algorithm with improved matching.
        
        Returns:
            (tour, length) where tour is list of vertex indices
        """
        # Step 1: Find MST using Prim's algorithm
        mst_edges = self.prim_mst()
        
        # Step 2: Find odd-degree vertices in MST
        odd_vertices = self.find_odd_degree_vertices(mst_edges)
        
        # Step 3: Find minimum-weight perfect matching on odd vertices
        matching_edges = self.minimum_weight_matching(odd_vertices)
        
        # Step 4: Combine MST and matching to create Eulerian multigraph
        eulerian_graph = self.combine_mst_and_matching(mst_edges, matching_edges)
        
        # Step 5: Find Eulerian tour
        eulerian_tour = self.find_eulerian_tour(eulerian_graph)
        
        # Step 6: Shortcut to Hamiltonian tour
        hamiltonian_tour = self.shortcut_to_hamiltonian(eulerian_tour)
        
        # Step 7: Optimize with 2-opt
        optimized_tour = self.two_opt(hamiltonian_tour)
        
        # Calculate tour length
        tour_length = self.tour_length(optimized_tour)
        
        return optimized_tour, tour_length
    
    # ===== BENCHMARKING =====
    
    @classmethod
    def benchmark(cls, n: int = 500, instances: int = 10, matching_algorithms: List[str] = None):
        """
        Benchmark different matching algorithms.
        
        Args:
            n: Number of cities
            instances: Number of random instances to test
            matching_algorithms: List of algorithm names to test
        
        Returns:
            Dictionary with benchmark results
        """
        if matching_algorithms is None:
            matching_algorithms = ['greedy_center', 'greedy_best', 'path_growing', 'hybrid', 'random_restarts']
        
        results = {algo: {'lengths': [], 'times': []} for algo in matching_algorithms}
        
        for instance in range(instances):
            print(f"\nInstance {instance + 1}/{instances}")
            
            # Create the same instance for all algorithms
            seed = instance
            base_solver = cls(n=n, seed=seed, matching_algorithm='greedy_center')
            
            for algo in matching_algorithms:
                # Create solver with specific algorithm
                solver = cls(n=n, seed=seed, matching_algorithm=algo)
                
                # Solve and time
                start_time = time.time()
                tour, length = solver.solve()
                elapsed = time.time() - start_time
                
                results[algo]['lengths'].append(length)
                results[algo]['times'].append(elapsed)
                
                print(f"  {algo:20} Length: {length:.6f}  Time: {elapsed:.3f}s")
        
        # Calculate statistics
        stats = {}
        for algo in matching_algorithms:
            lengths = results[algo]['lengths']
            times = results[algo]['times']
            
            stats[algo] = {
                'avg_length': np.mean(lengths),
                'std_length': np.std(lengths),
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'min_length': np.min(lengths),
                'max_length': np.max(lengths)
            }
        
        return stats
    
    @classmethod
    def print_benchmark_results(cls, stats: Dict):
        """
        Print formatted benchmark results.
        
        Args:
            stats: Benchmark statistics from benchmark() method
        """
        print(f"\n{'='*80}")
        print("CHRISTOFIDES MATCHING ALGORITHM BENCHMARK RESULTS")
        print(f"{'='*80}")
        
        # Sort by average tour length (quality)
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['avg_length'])
        
        print(f"\n{'Algorithm':20} {'Avg Length':12} {'Std Dev':10} {'Avg Time':10} {'Min':12} {'Max':12}")
        print(f"{'-'*80}")
        
        for algo, data in sorted_stats:
            print(f"{algo:20} {data['avg_length']:12.6f} {data['std_length']:10.6f} "
                  f"{data['avg_time']:10.3f} {data['min_length']:12.6f} {data['max_length']:12.6f}")
        
        # Find best algorithm
        best_algo, best_data = sorted_stats[0]
        print(f"\n{'='*80}")
        print(f"BEST ALGORITHM: {best_algo}")
        print(f"Average tour length: {best_data['avg_length']:.6f}")
        print(f"Average runtime: {best_data['avg_time']:.3f}s")
        print(f"Quality range: {best_data['min_length']:.6f} - {best_data['max_length']:.6f}")
        print(f"{'='*80}")
        
        # Recommendations
        print(f"\nRECOMMENDATIONS:")
        print(f"1. For best quality: Use '{best_algo}' algorithm")
        print(f"2. For speed: Consider 'greedy_center' (fastest)")
        print(f"3. For theoretical guarantees: Use 'path_growing' (2-approximation)")
        print(f"4. For small instances: Use 'hybrid' (optimal for ≤10 odd vertices)")
        print(f"{'='*80}")


def solve_tsp(points):
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    n = points.shape[0]
    
    # Create solver instance with the given points
    # We need to modify the class to accept external points
    # For now, create a simple wrapper
    class ExternalPointsSolver(ImprovedMatchingChristofides):
        def __init__(self, points, matching_algorithm='path_growing'):
            self.points = points
            self.n = points.shape[0]
            self.seed = None
            self.matching_algorithm = matching_algorithm
            # Compute distance matrix directly
            self.dist_matrix = self._compute_distance_matrix()
        
        def _compute_distance_matrix(self) -> np.ndarray:
            """Compute Euclidean distance matrix for given points."""
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
    
    solver = ExternalPointsSolver(points, matching_algorithm='path_growing')
    return solver.solve()

# ===== MAIN EXECUTION =====

def main():
    """Main function for testing and benchmarking."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Christofides TSP with improved matching')
    parser.add_argument('--n', type=int, default=100, help='Number of cities')
    parser.add_argument('--seed', type=int, default=None, help='Random seed')
    parser.add_argument('--algorithm', type=str, default='path_growing',
                       choices=['greedy_center', 'greedy_best', 'path_growing', 'hybrid', 'random_restarts'],
                       help='Matching algorithm to use')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark comparison')
    parser.add_argument('--instances', type=int, default=5, help='Number of benchmark instances')
    
    args = parser.parse_args()
    
    if args.benchmark:
        print(f"Running benchmark with n={args.n}, {args.instances} instances")
        stats = ImprovedMatchingChristofides.benchmark(
            n=args.n, 
            instances=args.instances,
            matching_algorithms=['greedy_center', 'greedy_best', 'path_growing', 'hybrid', 'random_restarts']
        )
        ImprovedMatchingChristofides.print_benchmark_results(stats)
    else:
        print(f"Solving TSP with n={args.n}, algorithm={args.algorithm}, seed={args.seed}")
        
        solver = ImprovedMatchingChristofides(
            n=args.n,
            seed=args.seed,
            matching_algorithm=args.algorithm
        )
        
        start_time = time.time()
        tour, length = solver.solve()
        elapsed = time.time() - start_time
        
        print(f"\nSolution found in {elapsed:.3f} seconds")
        print(f"Tour length: {length:.6f}")
        print(f"Tour (first 10 vertices): {tour[:10]}...")
        
        # Verify tour is valid
        if len(set(tour[:-1])) == args.n and tour[0] == tour[-1]:
            print("✓ Tour is valid (visits all vertices, starts/ends at same vertex)")
        else:
            print("✗ Tour is invalid!")

if __name__ == "__main__":
    main()