#!/usr/bin/env python3
"""
Test different matching algorithms for Christofides TSP.
Compare greedy variants and research optimal matching approaches.
"""

import numpy as np
import math
import random
import time
from typing import List, Tuple, Dict, Set
import itertools

class MatchingTester:
    """Test different matching algorithms on TSP instances."""
    
    def __init__(self, n: int = 20, seed: int = None):
        """
        Initialize test instance.
        
        Args:
            n: Number of cities (small for exhaustive testing)
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
    
    def generate_odd_vertices(self, count: int = None) -> List[int]:
        """
        Generate a set of odd-degree vertices for testing.
        
        Args:
            count: Number of odd vertices (must be even)
        
        Returns:
            List of odd vertex indices
        """
        if count is None:
            count = min(self.n, 10)  # Small for exhaustive testing
        if count % 2 != 0:
            count += 1
        
        # Select random vertices
        vertices = list(range(self.n))
        random.shuffle(vertices)
        return vertices[:count]
    
    # ===== MATCHING ALGORITHMS =====
    
    def greedy_matching_center_sorted(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Current implementation: greedy matching with vertices sorted by distance from center.
        """
        # Calculate center of all points
        center = np.mean(self.points, axis=0)
        
        # Sort odd vertices by distance from center (deterministic)
        vertices = sorted(odd_vertices, 
                         key=lambda v: np.linalg.norm(self.points[v] - center))
        
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
    
    def greedy_matching_x_sorted(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Greedy matching with vertices sorted by x-coordinate.
        """
        # Sort by x-coordinate
        vertices = sorted(odd_vertices, key=lambda v: self.points[v][0])
        
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
    
    def greedy_matching_y_sorted(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Greedy matching with vertices sorted by y-coordinate.
        """
        # Sort by y-coordinate
        vertices = sorted(odd_vertices, key=lambda v: self.points[v][1])
        
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
    
    def greedy_matching_random_restarts(self, odd_vertices: List[int], restarts: int = 10) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Greedy matching with multiple random restarts, keep best.
        """
        best_edges = None
        best_cost = float('inf')
        
        for _ in range(restarts):
            # Random shuffle
            vertices = odd_vertices.copy()
            random.shuffle(vertices)
            
            matched = [False] * self.n
            matching_edges = []
            total_cost = 0.0
            
            temp_vertices = vertices.copy()
            
            while temp_vertices:
                u = temp_vertices.pop()
                if matched[u]:
                    continue
                
                # Find closest unmatched odd vertex
                best_v = -1
                best_dist = float('inf')
                
                for v in temp_vertices:
                    if not matched[v]:
                        dist = self.distance(u, v)
                        if dist < best_dist:
                            best_dist = dist
                            best_v = v
                
                if best_v != -1:
                    temp_vertices.remove(best_v)
                    matched[u] = True
                    matched[best_v] = True
                    matching_edges.append((u, best_v, best_dist))
                    total_cost += best_dist
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_edges = matching_edges
        
        return best_edges, best_cost
    
    def greedy_matching_lookahead(self, odd_vertices: List[int], lookahead: int = 2) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Greedy matching with k-lookahead: consider k best matches at each step.
        """
        # Sort by distance from center (baseline)
        center = np.mean(self.points, axis=0)
        vertices = sorted(odd_vertices, 
                         key=lambda v: np.linalg.norm(self.points[v] - center))
        
        matched = [False] * self.n
        matching_edges = []
        total_cost = 0.0
        
        while vertices:
            u = vertices.pop()
            if matched[u]:
                continue
            
            # Find k closest unmatched vertices
            candidates = []
            for v in vertices:
                if not matched[v]:
                    dist = self.distance(u, v)
                    candidates.append((dist, v))
            
            if not candidates:
                break
            
            # Sort by distance and take k best
            candidates.sort()
            k_best = candidates[:min(lookahead, len(candidates))]
            
            # For simplicity, just take the best (same as greedy)
            # In full implementation, would explore all k options
            best_dist, best_v = k_best[0]
            
            vertices.remove(best_v)
            matched[u] = True
            matched[best_v] = True
            matching_edges.append((u, best_v, best_dist))
            total_cost += best_dist
        
        return matching_edges, total_cost
    
    def exhaustive_matching(self, odd_vertices: List[int]) -> Tuple[List[Tuple[int, int, float]], float]:
        """
        Exhaustive search for minimum-weight perfect matching.
        Only feasible for very small instances (n ≤ 10).
        
        Returns optimal matching and cost.
        """
        m = len(odd_vertices)
        if m > 10:
            print(f"Warning: Exhaustive search not feasible for {m} vertices")
            return [], float('inf')
        
        # Generate all perfect matchings
        vertices = odd_vertices.copy()
        best_edges = None
        best_cost = float('inf')
        
        # Generate all permutations and pair them
        # This is inefficient but works for small m
        for perm in itertools.permutations(vertices):
            # Create matching from permutation
            edges = []
            cost = 0.0
            valid = True
            
            for i in range(0, m, 2):
                u = perm[i]
                v = perm[i + 1]
                # Check if this is a valid perfect matching (no repeated vertices)
                # Actually, any pairing of all vertices is a perfect matching
                edges.append((u, v, self.distance(u, v)))
                cost += self.distance(u, v)
            
            if cost < best_cost:
                best_cost = cost
                best_edges = edges
        
        return best_edges, best_cost
    
    def run_comparison(self, odd_vertices: List[int]):
        """
        Run all matching algorithms and compare results.
        """
        print(f"\n=== Matching Algorithm Comparison ===")
        print(f"Odd vertices: {len(odd_vertices)} vertices")
        print(f"Vertices: {odd_vertices}")
        
        results = {}
        
        # Test each algorithm
        algorithms = [
            ("Center-sorted greedy", self.greedy_matching_center_sorted),
            ("X-sorted greedy", self.greedy_matching_x_sorted),
            ("Y-sorted greedy", self.greedy_matching_y_sorted),
            ("Random restarts (10)", lambda v: self.greedy_matching_random_restarts(v, 10)),
            ("Lookahead k=2", lambda v: self.greedy_matching_lookahead(v, 2)),
        ]
        
        for name, func in algorithms:
            start_time = time.time()
            edges, cost = func(odd_vertices)
            elapsed = time.time() - start_time
            
            results[name] = {
                'cost': cost,
                'time': elapsed,
                'edges': edges
            }
            
            print(f"\n{name}:")
            print(f"  Cost: {cost:.6f}")
            print(f"  Time: {elapsed:.6f}s")
            print(f"  Edges: {len(edges)}")
        
        # Exhaustive search for small instances
        if len(odd_vertices) <= 10:
            start_time = time.time()
            edges, cost = self.exhaustive_matching(odd_vertices)
            elapsed = time.time() - start_time
            
            results["Exhaustive (optimal)"] = {
                'cost': cost,
                'time': elapsed,
                'edges': edges
            }
            
            print(f"\nExhaustive (optimal):")
            print(f"  Cost: {cost:.6f}")
            print(f"  Time: {elapsed:.6f}s")
            print(f"  Edges: {len(edges)}")
            
            # Calculate optimality gaps
            print(f"\n=== Optimality Gaps ===")
            for name in [a[0] for a in algorithms]:
                if name in results and "Exhaustive (optimal)" in results:
                    gap = (results[name]['cost'] - results["Exhaustive (optimal)"]['cost']) / results["Exhaustive (optimal)"]['cost'] * 100
                    print(f"{name}: {gap:.2f}% gap from optimal")
        
        return results

def main():
    """Run comprehensive matching algorithm tests."""
    print("Matching Algorithm Research for Christofides TSP")
    print("=" * 60)
    
    # Test with different seeds and sizes
    test_cases = [
        (20, 8, 1),   # n=20, 8 odd vertices, seed=1
        (20, 8, 2),   # n=20, 8 odd vertices, seed=2  
        (20, 8, 5),   # n=20, 8 odd vertices, seed=5 (problematic case)
        (30, 10, 3),  # n=30, 10 odd vertices, seed=3
    ]
    
    all_results = {}
    
    for n, odd_count, seed in test_cases:
        print(f"\n{'='*60}")
        print(f"Test Case: n={n}, odd_count={odd_count}, seed={seed}")
        print(f"{'='*60}")
        
        tester = MatchingTester(n=n, seed=seed)
        odd_vertices = tester.generate_odd_vertices(odd_count)
        
        results = tester.run_comparison(odd_vertices)
        all_results[(n, odd_count, seed)] = results
    
    # Summary analysis
    print(f"\n{'='*60}")
    print("SUMMARY ANALYSIS")
    print(f"{'='*60}")
    
    # Collect statistics
    algorithm_names = ["Center-sorted greedy", "X-sorted greedy", "Y-sorted greedy", 
                      "Random restarts (10)", "Lookahead k=2"]
    
    for algo in algorithm_names:
        costs = []
        for key in all_results:
            if algo in all_results[key]:
                costs.append(all_results[key][algo]['cost'])
        
        if costs:
            avg_cost = np.mean(costs)
            std_cost = np.std(costs)
            print(f"{algo}: avg={avg_cost:.6f}, std={std_cost:.6f}")
    
    print(f"\nRecommendations:")
    print("1. Implement multiple greedy variants and select best")
    print("2. Add random restarts for probabilistic improvement")
    print("3. Research Blossom algorithm for optimal matching")
    print("4. Consider hybrid approach: optimal for small n, greedy for large n")

if __name__ == "__main__":
    main()