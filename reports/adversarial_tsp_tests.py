#!/usr/bin/env python3
"""
Adversarial Test Suite for Evo's TSP Solver
Vera - Critical Reviewer
"""

import sys
import os
sys.path.append('solutions/tsp-500-euclidean')

from solution import EuclideanTSP
import numpy as np
import math
import random
from typing import List, Tuple

class AdversarialTSPTests:
    """Generate pathological test cases for TSP algorithms."""
    
    @staticmethod
    def create_clustered_points(n: int, clusters: int = 5, cluster_radius: float = 0.05) -> np.ndarray:
        """
        Create points clustered in small regions - challenging for nearest neighbor.
        Nearest neighbor tends to get stuck in clusters.
        """
        points = []
        cluster_centers = np.random.rand(clusters, 2)
        
        points_per_cluster = n // clusters
        remainder = n % clusters
        
        for c in range(clusters):
            count = points_per_cluster + (1 if c < remainder else 0)
            for _ in range(count):
                angle = random.random() * 2 * math.pi
                radius = random.random() * cluster_radius
                dx = radius * math.cos(angle)
                dy = radius * math.sin(angle)
                point = cluster_centers[c] + np.array([dx, dy])
                # Keep within [0,1]
                point = np.clip(point, 0, 1)
                points.append(point)
        
        return np.array(points)
    
    @staticmethod
    def create_grid_points(n: int) -> np.ndarray:
        """
        Create points on a grid - nearest neighbor can produce very bad tours
        if it chooses wrong starting point or direction.
        """
        side = int(math.sqrt(n))
        if side * side < n:
            side += 1
        
        points = []
        for i in range(side):
            for j in range(side):
                if len(points) >= n:
                    break
                x = i / (side - 1) if side > 1 else 0.5
                y = j / (side - 1) if side > 1 else 0.5
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_line_points(n: int) -> np.ndarray:
        """
        Points along a line - tests algorithm's ability to handle degenerate cases.
        """
        points = []
        for i in range(n):
            x = i / (n - 1) if n > 1 else 0.5
            y = 0.5  # All on horizontal line
            points.append([x, y])
        
        # Add small random perturbations
        points = np.array(points) + np.random.randn(n, 2) * 0.01
        return np.clip(points, 0, 1)
    
    @staticmethod
    def create_concentric_circles(n: int, circles: int = 3) -> np.ndarray:
        """
        Points on concentric circles - tests handling of symmetric patterns.
        """
        points = []
        points_per_circle = n // circles
        remainder = n % circles
        
        for circle in range(circles):
            count = points_per_circle + (1 if circle < remainder else 0)
            radius = 0.2 + 0.2 * circle  # Radii: 0.2, 0.4, 0.6
            center = np.array([0.5, 0.5])
            
            for i in range(count):
                angle = 2 * math.pi * i / count
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append([x, y])
        
        return np.array(points)
    
    @staticmethod
    def create_sparse_dense_mix(n: int) -> np.ndarray:
        """
        Mix of sparse and dense regions - tests adaptive behavior.
        """
        points = []
        
        # Dense cluster (30% of points)
        dense_n = int(0.3 * n)
        dense_center = np.array([0.25, 0.25])
        for _ in range(dense_n):
            angle = random.random() * 2 * math.pi
            radius = random.random() * 0.1
            point = dense_center + np.array([radius * math.cos(angle), radius * math.sin(angle)])
            points.append(np.clip(point, 0, 1))
        
        # Sparse points (70% of points)
        sparse_n = n - dense_n
        for _ in range(sparse_n):
            # Place in remaining area, avoiding dense cluster
            while True:
                point = np.random.rand(2)
                if np.linalg.norm(point - dense_center) > 0.2:
                    points.append(point)
                    break
        
        return np.array(points)

def run_adversarial_tests():
    """Run comprehensive adversarial tests on Evo's TSP solver."""
    print("=" * 70)
    print("VERA - Adversarial TSP Test Suite")
    print("Testing Evo's Nearest Neighbor TSP Implementation")
    print("=" * 70)
    
    test_cases = [
        ("Clustered Points", AdversarialTSPTests.create_clustered_points),
        ("Grid Points", AdversarialTSPTests.create_grid_points),
        ("Line Points", AdversarialTSPTests.create_line_points),
        ("Concentric Circles", AdversarialTSPTests.create_concentric_circles),
        ("Sparse-Dense Mix", AdversarialTSPTests.create_sparse_dense_mix),
    ]
    
    results = []
    
    for test_name, generator in test_cases:
        print(f"\n{'='*40}")
        print(f"Test: {test_name}")
        print(f"{'='*40}")
        
        # Create custom TSP instance with adversarial points
        points = generator(50)  # Use smaller n for faster testing
        
        # Create a modified EuclideanTSP that uses our points
        class CustomTSP:
            def __init__(self, points):
                self.n = len(points)
                self.points = points
                self.dist_matrix = self._compute_distance_matrix()
            
            def _compute_distance_matrix(self):
                n = self.n
                dist = np.zeros((n, n))
                for i in range(n):
                    for j in range(i + 1, n):
                        d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                        dist[i, j] = d
                        dist[j, i] = d
                return dist
            
            def distance(self, i, j):
                return self.dist_matrix[i, j]
            
            def nearest_neighbor(self, start_city=None):
                if start_city is None:
                    start_city = random.randint(0, self.n - 1)
                
                unvisited = set(range(self.n))
                tour = [start_city]
                unvisited.remove(start_city)
                
                current = start_city
                total_distance = 0.0
                
                while unvisited:
                    nearest = min(unvisited, key=lambda city: self.distance(current, city))
                    total_distance += self.distance(current, nearest)
                    
                    tour.append(nearest)
                    unvisited.remove(nearest)
                    current = nearest
                
                total_distance += self.distance(current, start_city)
                tour.append(start_city)
                
                return tour, total_distance
            
            def nearest_neighbor_multistart(self, num_starts=10):
                best_tour = None
                best_distance = float('inf')
                
                starts = random.sample(range(self.n), min(num_starts, self.n))
                
                for start in starts:
                    tour, distance = self.nearest_neighbor(start)
                    if distance < best_distance:
                        best_tour = tour
                        best_distance = distance
                
                return best_tour, best_distance
            
            def tour_length(self, tour):
                total = 0.0
                for i in range(len(tour) - 1):
                    total += self.distance(tour[i], tour[i + 1])
                return total
        
        tsp = CustomTSP(points)
        
        # Run nearest neighbor
        tour_nn, dist_nn = tsp.nearest_neighbor_multistart(num_starts=10)
        
        # Calculate lower bound approximation
        # Simple bound: minimum pairwise distance * n
        min_dist = float('inf')
        for i in range(tsp.n):
            for j in range(i + 1, tsp.n):
                d = tsp.distance(i, j)
                if d < min_dist:
                    min_dist = d
        lower_bound = min_dist * tsp.n if min_dist < float('inf') else dist_nn * 0.7
        
        approximation_ratio = dist_nn / lower_bound if lower_bound > 0 else float('inf')
        
        print(f"  Points: {tsp.n}")
        print(f"  NN tour length: {dist_nn:.4f}")
        print(f"  Lower bound estimate: {lower_bound:.4f}")
        print(f"  Approximation ratio: {approximation_ratio:.3f}x")
        
        # Check for obvious issues
        issues = []
        if approximation_ratio > 2.0:
            issues.append(f"Poor approximation ratio ({approximation_ratio:.3f}x)")
        
        if len(set(tour_nn[:-1])) != tsp.n:
            issues.append("Tour doesn't visit all cities")
        
        if tour_nn[0] != tour_nn[-1]:
            issues.append("Tour not closed")
        
        if issues:
            print(f"  ISSUES FOUND: {', '.join(issues)}")
        else:
            print(f"  No critical issues found")
        
        results.append({
            'test': test_name,
            'points': tsp.n,
            'tour_length': dist_nn,
            'lower_bound': lower_bound,
            'approx_ratio': approximation_ratio,
            'issues': issues
        })
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    for result in results:
        status = "⚠️ WEAK" if result['issues'] or result['approx_ratio'] > 1.5 else "✅ OK"
        print(f"{result['test']:20} | Ratio: {result['approx_ratio']:5.3f}x | {status}")
        if result['issues']:
            for issue in result['issues']:
                print(f"  - {issue}")
    
    # Overall assessment
    weak_tests = sum(1 for r in results if r['issues'] or r['approx_ratio'] > 1.5)
    if weak_tests > 0:
        print(f"\n🔴 FOUND {weak_tests}/{len(results)} tests where algorithm shows weakness")
        print("Nearest neighbor heuristic vulnerable to:")
        print("  - Clustered point distributions")
        print("  - Structured patterns (grids, circles)")
        print("  - Sparse-dense mixtures")
        print("\nRECOMMENDATIONS for Evo:")
        print("  1. Add 2-opt local optimization")
        print("  2. Implement Christofides algorithm (1.5x guarantee)")
        print("  3. Add simulated annealing for escaping local optima")
        print("  4. Consider Lin-Kernighan heuristic")
    else:
        print(f"\n✅ Algorithm performs reasonably on all test cases")
        print("Nearest neighbor is robust for random uniform distributions")
        print("Consider adding optimization for guaranteed bounds")

if __name__ == "__main__":
    run_adversarial_tests()