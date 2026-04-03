#!/usr/bin/env python3
"""
Improved matching algorithms for Christofides TSP.
Includes multiple greedy variants, path growing algorithm, and hybrid approaches.
"""

import numpy as np
import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq

class ImprovedMatching:
    """
    Collection of improved matching algorithms for Christofides TSP.
    
    Provides multiple algorithms with different quality/runtime tradeoffs.
    """
    
    def __init__(self, points: np.ndarray, dist_matrix: np.ndarray):
        """
        Initialize with problem instance.
        
        Args:
            points: Array of (x, y) coordinates
            dist_matrix: Precomputed distance matrix
        """
        self.points = points
        self.dist_matrix = dist_matrix
        self.n = len(points)
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between cities i and j."""
        return self.dist_matrix[i, j]
    
    # ===== CORE MATCHING ALGORITHMS =====
    
    def greedy_matching_basic(self, odd_vertices: List[int], 
                             sort_key: str = 'center') -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Basic greedy matching with configurable sorting.
        
        Args:
            odd_vertices: List of odd-degree vertices
            sort_key: How to sort vertices ('center', 'x', 'y', 'random')
        
        Returns:
            (matching_edges, total_cost)
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
        total_cost = 0.0
        
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
                total_cost += best_dist
        
        return matching_edges, total_cost
    
    def greedy_matching_multiple_restarts(self, odd_vertices: List[int], 
                                         restarts: int = 20) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Greedy matching with multiple random restarts, keep best.
        
        Args:
            odd_vertices: List of odd-degree vertices
            restarts: Number of random restarts
        
        Returns:
            (best_matching_edges, best_cost)
        """
        best_edges = None
        best_cost = float('inf')
        
        for _ in range(restarts):
            edges, cost = self.greedy_matching_basic(odd_vertices, sort_key='random')
            
            if cost < best_cost:
                best_cost = cost
                best_edges = edges
        
        return best_edges, best_cost
    
    def greedy_matching_best_of_k(self, odd_vertices: List[int], 
                                 strategies: List[str] = None) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Try multiple greedy strategies, keep best.
        
        Args:
            odd_vertices: List of odd-degree vertices
            strategies: List of sort keys to try
        
        Returns:
            (best_matching_edges, best_cost)
        """
        if strategies is None:
            strategies = ['center', 'x', 'y', 'random']
        
        best_edges = None
        best_cost = float('inf')
        
        for strategy in strategies:
            edges, cost = self.greedy_matching_basic(odd_vertices, sort_key=strategy)
            
            if cost < best_cost:
                best_cost = cost
                best_edges = edges
        
        return best_edges, best_cost
    
    def path_growing_matching(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
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
            (matching_edges, total_cost)
        """
        vertices = set(odd_vertices)
        matched = [False] * self.n
        matching_edges = []
        total_cost = 0.0
        
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
                    total_cost += dist
        
        return matching_edges, total_cost
    
    def matching_with_local_search(self, odd_vertices: List[int], 
                                  initial_matching: List[Tuple[int, int, float]] = None,
                                  max_iterations: int = 100) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Improve matching with local search (2-opt swaps for matchings).
        
        Args:
            odd_vertices: List of odd-degree vertices
            initial_matching: Starting matching (if None, use greedy)
            max_iterations: Maximum number of improvement iterations
        
        Returns:
            (improved_matching_edges, improved_cost)
        """
        # Start with initial matching
        if initial_matching is None:
            edges, cost = self.greedy_matching_best_of_k(odd_vertices)
        else:
            edges = initial_matching.copy()
            cost = sum(edge[2] for edge in edges)
        
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            # Try all possible 2-opt swaps in the matching
            m = len(edges)
            for i in range(m):
                for j in range(i + 1, m):
                    u1, v1, d1 = edges[i]
                    u2, v2, d2 = edges[j]
                    
                    # Current cost of these two edges
                    current_cost = d1 + d2
                    
                    # Try swapping: (u1, v1) + (u2, v2) -> (u1, u2) + (v1, v2)
                    new_d1 = self.distance(u1, u2)
                    new_d2 = self.distance(v1, v2)
                    new_cost = new_d1 + new_d2
                    
                    # Or try: (u1, v1) + (u2, v2) -> (u1, v2) + (v1, u2)
                    alt_d1 = self.distance(u1, v2)
                    alt_d2 = self.distance(v1, u2)
                    alt_cost = alt_d1 + alt_d2
                    
                    # Check if either swap improves the matching
                    if new_cost < current_cost and new_cost < alt_cost:
                        # Swap to (u1, u2) and (v1, v2)
                        edges[i] = (u1, u2, new_d1)
                        edges[j] = (v1, v2, new_d2)
                        cost = cost - current_cost + new_cost
                        improved = True
                        break
                    
                    elif alt_cost < current_cost:
                        # Swap to (u1, v2) and (v1, u2)
                        edges[i] = (u1, v2, alt_d1)
                        edges[j] = (v1, u2, alt_d2)
                        cost = cost - current_cost + alt_cost
                        improved = True
                        break
                
                if improved:
                    break
        
        return edges, cost
    
    def hybrid_matching(self, odd_vertices: List[int], 
                       threshold: int = 20) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Hybrid matching: use optimal algorithm for small instances, greedy for large.
        
        Args:
            odd_vertices: List of odd-degree vertices
            threshold: Use exhaustive search if |odd_vertices| ≤ threshold
        
        Returns:
            (matching_edges, total_cost)
        """
        m = len(odd_vertices)
        
        if m <= threshold:
            # Try exhaustive search for small instances
            try:
                return self.exhaustive_matching(odd_vertices)
            except Exception as e:
                print(f"Exhaustive search failed: {e}, falling back to greedy")
        
        # For larger instances, use best greedy + local search
        edges, cost = self.greedy_matching_best_of_k(odd_vertices)
        edges, cost = self.matching_with_local_search(odd_vertices, edges, max_iterations=50)
        
        return edges, cost
    
    def exhaustive_matching(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Exhaustive search for minimum-weight perfect matching.
        Only for very small instances (m ≤ 10).
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            (optimal_matching_edges, optimal_cost)
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
        return best_edges, best_cost
    
    # ===== UTILITY METHODS =====
    
    def benchmark_algorithms(self, odd_vertices: List[int]) -> Dict:
        """
        Benchmark all matching algorithms on given odd vertices.
        
        Args:
            odd_vertices: List of odd-degree vertices
        
        Returns:
            Dictionary with benchmark results
        """
        results = {}
        
        algorithms = [
            ("Greedy (center)", lambda: self.greedy_matching_basic(odd_vertices, 'center')),
            ("Greedy (x)", lambda: self.greedy_matching_basic(odd_vertices, 'x')),
            ("Greedy (y)", lambda: self.greedy_matching_basic(odd_vertices, 'y')),
            ("Greedy (random restarts)", lambda: self.greedy_matching_multiple_restarts(odd_vertices, 20)),
            ("Greedy (best of k)", lambda: self.greedy_matching_best_of_k(odd_vertices)),
            ("Path growing", lambda: self.path_growing_matching(odd_vertices)),
            ("Greedy + local search", lambda: self.matching_with_local_search(odd_vertices)),
            ("Hybrid", lambda: self.hybrid_matching(odd_vertices)),
        ]
        
        for name, func in algorithms:
            try:
                start_time = time.time()
                edges, cost = func()
                elapsed = time.time() - start_time
                
                results[name] = {
                    'cost': cost,
                    'time': elapsed,
                    'edges': len(edges),
                    'success': True
                }
            except Exception as e:
                results[name] = {
                    'cost': float('inf'),
                    'time': 0.0,
                    'edges': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Try exhaustive search for small instances
        if len(odd_vertices) <= 10:
            try:
                start_time = time.time()
                edges, cost = self.exhaustive_matching(odd_vertices)
                elapsed = time.time() - start_time
                
                results["Exhaustive (optimal)"] = {
                    'cost': cost,
                    'time': elapsed,
                    'edges': len(edges),
                    'success': True
                }
            except Exception as e:
                results["Exhaustive (optimal)"] = {
                    'cost': float('inf'),
                    'time': 0.0,
                    'edges': 0,
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def print_benchmark_results(self, results: Dict, odd_vertices: List[int]):
        """
        Print formatted benchmark results.
        
        Args:
            results: Benchmark results from benchmark_algorithms()
            odd_vertices: Original odd vertices list
        """
        print(f"\n=== Matching Algorithm Benchmark ===")
        print(f"Odd vertices: {len(odd_vertices)} vertices")
        print(f"Vertex indices: {odd_vertices}")
        print(f"{'='*60}")
        
        # Find best cost (excluding failed algorithms)
        successful_results = {k: v for k, v in results.items() if v['success']}
        if successful_results:
            best_cost = min(v['cost'] for v in successful_results.values())
        else:
            best_cost = float('inf')
        
        # Print results
        for name, data in results.items():
            if data['success']:
                gap = (data['cost'] - best_cost) / best_cost * 100 if best_cost > 0 else 0
                print(f"{name:25} Cost: {data['cost']:10.6f}  Time: {data['time']:8.6f}s  "
                      f"Edges: {data['edges']:2d}  Gap: {gap:6.2f}%")
            else:
                print(f"{name:25} FAILED: {data.get('error', 'Unknown error')}")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY:")
        
        if successful_results:
            # Sort by cost
            sorted_results = sorted(successful_results.items(), key=lambda x: x[1]['cost'])
            
            print("\nRanked by cost (best first):")
            for i, (name, data) in enumerate(sorted_results[:5], 1):
                gap = (data['cost'] - best_cost) / best_cost * 100 if best_cost > 0 else 0
                print(f"{i:2d}. {name:25} {data['cost']:10.6f} ({gap:6.2f}% gap)")
            
            print("\nRanked by speed (fastest first):")
            sorted_by_time = sorted(successful_results.items(), key=lambda x: x[1]['time'])
            for i, (name, data) in enumerate(sorted_by_time[:5], 1):
                print(f"{i:2d}. {name:25} {data['time']:8.6f}s")
        
        print(f"{'='*60}")


# ===== TEST AND DEMONSTRATION =====

def test_improved_matching():
    """Test the improved matching algorithms."""
    print("Testing Improved Matching Algorithms")
    print("=" * 60)
    
    # Create test instance
    n = 30
    seed = 42
    np.random.seed(seed)
    random.seed(seed)
    
    points = np.random.rand(n, 2)
    
    # Compute distance matrix
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = math.sqrt(((points[i] - points[j]) ** 2).sum())
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d
    
    # Create matching tester
    matcher = ImprovedMatching(points, dist_matrix)
    
    # Generate odd vertices
    odd_count = 10
    vertices = list(range(n))
    random.shuffle(vertices)
    odd_vertices = vertices[:odd_count]
    
    print(f"Test instance: n={n}, {odd_count} odd vertices, seed={seed}")
    
    # Run benchmarks
    results = matcher.benchmark_algorithms(odd_vertices)
    matcher.print_benchmark_results(results, odd_vertices)
    
    # Test with different sizes
    print(f"\n{'='*60}")
    print("Testing with different problem sizes")
    print(f"{'='*60}")
    
    test_sizes = [6, 8, 10, 12, 14, 16]
    all_results = {}
    
    for size in test_sizes:
        print(f"\n--- Testing with {size} odd vertices ---")
        
        # Generate odd vertices
        vertices = list(range(n))
        random.shuffle(vertices)
        odd_vertices = vertices[:size]
        
        # Run benchmarks
        results = matcher.benchmark_algorithms(odd_vertices)
        
        # Store best cost for each algorithm
        for algo, data in results.items():
            if data['success']:
                if algo not in all_results:
                    all_results[algo] = []
                all_results[algo].append(data['cost'])
    
    # Print summary statistics
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS (across all test sizes)")
    print(f"{'='*60}")
    
    for algo in sorted(all_results.keys()):
        costs = all_results[algo]
        if costs:
            avg = np.mean(costs)
            std = np.std(costs)
            print(f"{algo:25} Avg: {avg:8.6f}  Std: {std:8.6f}  N: {len(costs)}")
    
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS:")
    print("1. For small instances (≤10 odd vertices): Use hybrid or exhaustive")
    print("2. For medium instances (10-20): Use greedy + local search")
    print("3. For large instances (>20): Use greedy best-of-k or random restarts")
    print("4. Always benchmark multiple algorithms for critical applications")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_improved_matching()