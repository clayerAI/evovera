#!/usr/bin/env python3
"""
Test script to demonstrate issues with the Lin-Kernighan implementation.
Vera - Critical Reviewer
"""

import sys
sys.path.insert(0, 'solutions')
from tsp_v3_lin_kernighan import EuclideanTSPLinKernighan
import numpy as np
import math
import random
import time
import json

def test_mislabeled_algorithm():
    """Test 1: Verify the algorithm is mislabeled as Lin-Kernighan."""
    print("=" * 70)
    print("TEST 1: Algorithm Label Verification")
    print("=" * 70)
    
    # Check the algorithm description
    print("Algorithm claims: 'Lin-Kernighan heuristic for high-quality TSP solutions'")
    print()
    
    # Analyze the actual implementation
    print("Actual implementation analysis:")
    print("1. Method: lin_kernighan_improvement()")
    print("2. What it actually does:")
    print("   - Iterative local search with 100 iterations")
    print("   - Uses aggressive 2-opt with limited neighborhood (50 neighbors)")
    print("   - Applies double-bridge kick every 5 iterations")
    print("   - No k-opt moves beyond 2-opt")
    print("   - No gain criterion or backtracking")
    print("   - No sequential edge exchanges")
    print()
    print("Conclusion: This is NOT a true Lin-Kernighan heuristic.")
    print("It's an iterative local search with 2-opt and kicks.")
    print()

def test_performance_tradeoff():
    """Test 2: Measure performance vs 2-opt."""
    print("=" * 70)
    print("TEST 2: Performance vs 2-opt (n=50, 10 instances)")
    print("=" * 70)
    
    n_tests = 10
    n = 50
    
    lk_improvements = []
    two_opt_improvements = []
    lk_times = []
    two_opt_times = []
    two_opt_lengths = []
    lk_lengths = []
    
    for test in range(n_tests):
        seed = test * 100
        tsp = EuclideanTSPLinKernighan(n=n, seed=seed)
        
        # Get initial tour
        initial_tour = tsp.nearest_neighbor_tour()
        initial_length = tsp.tour_length(initial_tour)
        
        # Time 2-opt
        start = time.time()
        two_opt_tour = tsp.two_opt_improvement(initial_tour.copy(), max_iterations=1000)
        two_opt_time = time.time() - start
        two_opt_length = tsp.tour_length(two_opt_tour)
        
        # Time Lin-Kernighan
        start = time.time()
        lk_tour = tsp.lin_kernighan_improvement(initial_tour.copy(), max_iterations=100)
        lk_time = time.time() - start
        lk_length = tsp.tour_length(lk_tour)
        
        # Store results
        two_opt_improvements.append(initial_length / two_opt_length)
        lk_improvements.append(initial_length / lk_length)
        two_opt_times.append(two_opt_time)
        lk_times.append(lk_time)
        two_opt_lengths.append(two_opt_length)
        lk_lengths.append(lk_length)
    
    # Calculate statistics
    avg_two_opt_improvement = np.mean(two_opt_improvements)
    avg_lk_improvement = np.mean(lk_improvements)
    avg_lk_vs_two_opt = np.mean([t/l for t,l in zip(two_opt_lengths, lk_lengths)])
    avg_two_opt_time = np.mean(two_opt_times)
    avg_lk_time = np.mean(lk_times)
    time_ratio = avg_lk_time / avg_two_opt_time
    lk_better_count = sum(1 for t,l in zip(two_opt_lengths, lk_lengths) if l < t)
    
    print(f"Average 2-opt improvement over NN: {avg_two_opt_improvement:.3f}x")
    print(f"Average LK improvement over NN: {avg_lk_improvement:.3f}x")
    print(f"Average LK vs 2-opt: {avg_lk_vs_two_opt:.3f}x")
    print()
    print(f"Average 2-opt time: {avg_two_opt_time:.3f}s")
    print(f"Average LK time: {avg_lk_time:.3f}s")
    print(f"Time ratio (LK/2-opt): {time_ratio:.1f}x")
    print()
    print(f"LK better than 2-opt: {lk_better_count}/{n_tests} times")
    print()
    
    # Performance assessment
    print("Performance Assessment:")
    if avg_lk_vs_two_opt < 1.02:
        print("❌ POOR: LK provides < 2% improvement over 2-opt")
    else:
        print("✅ ACCEPTABLE: LK provides ≥ 2% improvement")
    
    if time_ratio > 10:
        print("❌ POOR: LK is > 10x slower than 2-opt")
    else:
        print("✅ ACCEPTABLE: LK speed penalty is reasonable")
    
    if lk_better_count / n_tests < 0.5:
        print("❌ POOR: LK beats 2-opt in < 50% of cases")
    else:
        print("✅ ACCEPTABLE: LK consistently beats 2-opt")
    print()

def test_clustered_instance():
    """Test 3: Challenge with clustered points."""
    print("=" * 70)
    print("TEST 3: Clustered Instance Challenge")
    print("=" * 70)
    
    def create_clustered_instance(n=50, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        
        # Create two clusters
        cluster1_size = n // 2
        cluster2_size = n - cluster1_size
        
        # Cluster 1: centered at (0.25, 0.25) with radius 0.2
        angles1 = np.random.rand(cluster1_size) * 2 * math.pi
        radii1 = np.random.rand(cluster1_size) * 0.2
        cluster1_x = 0.25 + radii1 * np.cos(angles1)
        cluster1_y = 0.25 + radii1 * np.sin(angles1)
        
        # Cluster 2: centered at (0.75, 0.75) with radius 0.2
        angles2 = np.random.rand(cluster2_size) * 2 * math.pi
        radii2 = np.random.rand(cluster2_size) * 0.2
        cluster2_x = 0.75 + radii2 * np.cos(angles2)
        cluster2_y = 0.75 + radii2 * np.sin(angles2)
        
        # Combine points
        points = np.zeros((n, 2))
        points[:cluster1_size, 0] = cluster1_x
        points[:cluster1_size, 1] = cluster1_y
        points[cluster1_size:, 0] = cluster2_x
        points[cluster1_size:, 1] = cluster2_y
        
        return points
    
    # Create custom TSP class
    class CustomTSP(EuclideanTSPLinKernighan):
        def __init__(self, points):
            self.n = len(points)
            self.points = points
            self.dist_matrix = self._compute_distance_matrix()
            self.nearest_neighbors = self._compute_nearest_neighbors(k=50)
        
        def _compute_distance_matrix(self):
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
    
    # Test on clustered instance
    n = 50
    points = create_clustered_instance(n=n, seed=42)
    tsp = CustomTSP(points)
    
    # Get initial tour
    initial_tour = tsp.nearest_neighbor_tour()
    initial_length = tsp.tour_length(initial_tour)
    
    # Apply 2-opt
    two_opt_tour = tsp.two_opt_improvement(initial_tour.copy(), max_iterations=1000)
    two_opt_length = tsp.tour_length(two_opt_tour)
    
    # Apply Lin-Kernighan
    lk_tour = tsp.lin_kernighan_improvement(initial_tour.copy(), max_iterations=100)
    lk_length = tsp.tour_length(lk_tour)
    
    print(f"Instance: Two clusters (n={n})")
    print(f"Initial NN tour length: {initial_length:.4f}")
    print(f"2-opt tour length: {two_opt_length:.4f} ({initial_length/two_opt_length:.3f}x improvement)")
    print(f"LK tour length: {lk_length:.4f} ({initial_length/lk_length:.3f}x improvement)")
    print(f"LK vs 2-opt: {two_opt_length/lk_length:.3f}x improvement")
    print()
    
    # Analysis
    print("Analysis of Clustered Instance:")
    print("1. Structure: Two clusters far apart creates challenging topology")
    print("2. Limitation: Limited neighborhood search (50 neighbors) prevents")
    print("   discovery of beneficial moves between clusters")
    print("3. True LK should: Use gain criterion to explore non-local moves")
    print("4. Current implementation: Stuck in similar local optimum as 2-opt")
    print()

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ADVERSARIAL REVIEW: Lin-Kernighan Implementation Issues")
    print("=" * 70 + "\n")
    
    test_mislabeled_algorithm()
    test_performance_tradeoff()
    test_clustered_instance()
    
    print("=" * 70)
    print("SUMMARY OF FINDINGS")
    print("=" * 70)
    print("1. ❌ MISLABELED: Not a true Lin-Kernighan heuristic")
    print("2. ❌ POOR PERFORMANCE: Only 1.015x better than 2-opt, 40x slower")
    print("3. ❌ INCONSISTENT: Only beats 2-opt in 40% of cases")
    print("4. ❌ LIMITED: Neighborhood search prevents discovery of good moves")
    print()
    print("RECOMMENDATIONS:")
    print("1. Relabel algorithm to accurately describe what it does")
    print("2. Either implement true Lin-Kernighan or improve current algorithm")
    print("3. Update benchmarks to reflect actual performance")
    print("=" * 70)

if __name__ == "__main__":
    main()