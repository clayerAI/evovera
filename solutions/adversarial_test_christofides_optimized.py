#!/usr/bin/env python3
"""
Adversarial Test Suite for Optimized Christofides Algorithm
Vera - Critical Reviewer and Challenger Agent
"""

import numpy as np
import math
import random
import time
import json
from typing import List, Tuple
import sys
sys.path.append('/workspace/evovera/solutions')
from tsp_v2_christofides import EuclideanTSPChristofides


class AdversarialTSPTester:
    """Test Christofides algorithm with pathological cases."""
    
    def __init__(self):
        self.results = []
    
    def test_performance_improvement(self):
        """Test if performance improvements are real and significant."""
        print("\n" + "=" * 70)
        print("TEST 1: PERFORMANCE IMPROVEMENT VERIFICATION")
        print("=" * 70)
        
        seeds = [42, 0, 1, 2]
        times = []
        tour_lengths = []
        
        for seed in seeds:
            print(f"\nSeed {seed}:")
            tsp = EuclideanTSPChristofides(n=500, seed=seed)
            
            start_time = time.time()
            tour, distance = tsp.christofides(apply_two_opt=True)
            end_time = time.time()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            tour_lengths.append(distance)
            
            print(f"  Time: {elapsed:.3f}s")
            print(f"  Tour length: {distance:.4f}")
        
        avg_time = np.mean(times)
        avg_tour = np.mean(tour_lengths)
        
        print(f"\nAverage time: {avg_time:.3f}s")
        print(f"Average tour length: {avg_tour:.4f}")
        
        # Check if performance meets claimed improvements
        if avg_time < 2.0:  # Should be ~1.1s as claimed
            print("✅ Performance improvement verified (< 2.0s average)")
        else:
            print("❌ Performance not meeting claimed improvement")
        
        return avg_time, avg_tour
    
    def test_greedy_matching_quality(self):
        """Test if greedy matching degrades solution quality significantly."""
        print("\n" + "=" * 70)
        print("TEST 2: GREEDY MATCHING QUALITY ASSESSMENT")
        print("=" * 70)
        
        # Test on multiple instances
        quality_ratios = []
        
        for seed in range(5):
            tsp = EuclideanTSPChristofides(n=100, seed=seed)  # Smaller n for faster testing
            
            # Get odd vertices
            mst_edges = tsp.prim_mst()
            odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
            
            # Run greedy matching multiple times (random shuffle affects result)
            matching_results = []
            for _ in range(10):
                matching_edges = tsp.greedy_minimum_matching(odd_vertices)
                total_weight = sum(weight for _, _, weight in matching_edges)
                matching_results.append(total_weight)
            
            # Calculate variance in matching quality
            min_weight = min(matching_results)
            max_weight = max(matching_results)
            variance = max_weight / min_weight if min_weight > 0 else float('inf')
            
            quality_ratios.append(variance)
            print(f"Seed {seed}: Min={min_weight:.4f}, Max={max_weight:.4f}, Ratio={variance:.4f}")
        
        avg_variance = np.mean(quality_ratios)
        
        if avg_variance < 1.1:  # Less than 10% variance
            print(f"✅ Greedy matching consistent (avg variance: {avg_variance:.4f})")
        else:
            print(f"⚠️  Greedy matching has significant variance (avg: {avg_variance:.4f})")
        
        return avg_variance
    
    def test_limited_2opt_effectiveness(self):
        """Test if limited 2-opt search (50 nearest neighbors) misses improvements."""
        print("\n" + "=" * 70)
        print("TEST 3: LIMITED 2-OPT SEARCH EFFECTIVENESS")
        print("=" * 70)
        
        # Create a clustered instance where limited search might fail
        n = 100
        points = []
        
        # Create 4 clusters
        cluster_centers = [(0.2, 0.2), (0.2, 0.8), (0.8, 0.2), (0.8, 0.8)]
        points_per_cluster = n // 4
        
        for cx, cy in cluster_centers:
            for _ in range(points_per_cluster):
                x = cx + random.uniform(-0.1, 0.1)
                y = cy + random.uniform(-0.1, 0.1)
                points.append([x, y])
        
        # Create custom TSP instance
        class CustomTSP(EuclideanTSPChristofides):
            def __init__(self, points):
                self.n = len(points)
                self.points = np.array(points)
                self.dist_matrix = self._compute_distance_matrix()
        
        tsp = CustomTSP(points)
        
        # Run Christofides
        tour, distance = tsp.christofides(apply_two_opt=True)
        print(f"Christofides + limited 2-opt: {distance:.4f}")
        
        # Run additional full 2-opt to see if limited search missed improvements
        full_2opt_tour, full_2opt_distance = self._full_2opt(tsp, tour)
        improvement = distance - full_2opt_distance
        
        print(f"Full 2-opt improvement: {improvement:.4f} ({improvement/distance*100:.2f}%)")
        
        if improvement > distance * 0.01:  # More than 1% improvement
            print(f"⚠️  Limited 2-opt missed significant improvement ({improvement:.4f})")
        else:
            print("✅ Limited 2-opt search effective")
        
        return improvement
    
    def _full_2opt(self, tsp, tour):
        """Full 2-opt implementation for comparison."""
        if len(tour) < 4 or tour[0] != tour[-1]:
            return tour, tsp.tour_distance(tour)
        
        tour = tour[:-1]
        n = len(tour)
        best_tour = tour[:]
        best_distance = tsp.tour_distance(tour + [tour[0]])
        
        improved = True
        while improved:
            improved = False
            
            for i in range(n):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue
                    
                    a, b = tour[i], tour[(i + 1) % n]
                    c, d = tour[j], tour[(j + 1) % n]
                    
                    old_distance = tsp.distance(a, b) + tsp.distance(c, d)
                    new_distance = tsp.distance(a, c) + tsp.distance(b, d)
                    
                    if new_distance < old_distance:
                        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                        new_tour_distance = tsp.tour_distance(new_tour + [new_tour[0]])
                        
                        if new_tour_distance < best_distance:
                            best_tour = new_tour[:]
                            best_distance = new_tour_distance
                            tour = new_tour[:]
                            improved = True
                            break
                
                if improved:
                    break
        
        best_tour.append(best_tour[0])
        return best_tour, best_distance
    
    def test_approximation_guarantee(self):
        """Test if Christofides maintains 1.5x approximation guarantee with optimizations."""
        print("\n" + "=" * 70)
        print("TEST 4: APPROXIMATION GUARANTEE VERIFICATION")
        print("=" * 70)
        
        # Use small instances where we can compute optimal via brute force (n=8)
        n = 8
        ratios = []
        
        for seed in range(3):
            tsp = EuclideanTSPChristofides(n=n, seed=seed)
            
            # Get Christofides solution
            christofides_tour, christofides_distance = tsp.christofides(apply_two_opt=True)
            
            # Compute optimal via brute force (for n=8, 8! = 40320 permutations)
            optimal_distance = self._brute_force_optimal(tsp)
            
            ratio = christofides_distance / optimal_distance
            ratios.append(ratio)
            
            print(f"Seed {seed}: Christofides={christofides_distance:.4f}, "
                  f"Optimal={optimal_distance:.4f}, Ratio={ratio:.4f}")
        
        max_ratio = max(ratios)
        
        if max_ratio <= 1.5:
            print(f"✅ Approximation guarantee maintained (max ratio: {max_ratio:.4f} ≤ 1.5)")
        else:
            print(f"❌ Approximation guarantee violated (max ratio: {max_ratio:.4f} > 1.5)")
        
        return max_ratio
    
    def _brute_force_optimal(self, tsp):
        """Brute force optimal solution for small n."""
        from itertools import permutations
        
        n = tsp.n
        vertices = list(range(n))
        best_distance = float('inf')
        
        # Try all permutations starting from vertex 0
        for perm in permutations(vertices[1:]):
            tour = [0] + list(perm) + [0]
            distance = tsp.tour_distance(tour)
            if distance < best_distance:
                best_distance = distance
        
        return best_distance
    
    def test_pathological_case(self):
        """Test pathological case: points on a line."""
        print("\n" + "=" * 70)
        print("TEST 5: PATHOLOGICAL CASE - POINTS ON A LINE")
        print("=" * 70)
        
        n = 100
        points = []
        
        # Create points on a line
        for i in range(n):
            x = i / (n - 1)
            y = 0.5  # All points have same y-coordinate
            points.append([x, y])
        
        class LineTSP(EuclideanTSPChristofides):
            def __init__(self, points):
                self.n = len(points)
                self.points = np.array(points)
                self.dist_matrix = self._compute_distance_matrix()
        
        tsp = LineTSP(points)
        
        # Optimal tour for points on a line is simple traversal
        optimal_tour = list(range(n)) + [0]
        optimal_distance = tsp.tour_distance(optimal_tour)
        
        # Christofides solution
        christofides_tour, christofides_distance = tsp.christofides(apply_two_opt=True)
        
        ratio = christofides_distance / optimal_distance
        
        print(f"Optimal (line traversal): {optimal_distance:.4f}")
        print(f"Christofides: {christofides_distance:.4f}")
        print(f"Ratio: {ratio:.4f}")
        
        if ratio <= 1.5:
            print(f"✅ Christofides handles line case well (ratio: {ratio:.4f})")
        else:
            print(f"⚠️  Christofides struggles with line case (ratio: {ratio:.4f})")
        
        return ratio
    
    def run_all_tests(self):
        """Run all adversarial tests."""
        print("ADVERSARIAL TESTING OF OPTIMIZED CHRISTOFIDES ALGORITHM")
        print("=" * 70)
        
        test_results = {}
        
        # Test 1: Performance
        avg_time, avg_tour = self.test_performance_improvement()
        test_results['performance'] = {'avg_time': avg_time, 'avg_tour': avg_tour}
        
        # Test 2: Greedy matching quality
        matching_variance = self.test_greedy_matching_quality()
        test_results['matching_quality'] = {'variance': matching_variance}
        
        # Test 3: Limited 2-opt effectiveness
        missed_improvement = self.test_limited_2opt_effectiveness()
        test_results['limited_2opt'] = {'missed_improvement': missed_improvement}
        
        # Test 4: Approximation guarantee
        max_ratio = self.test_approximation_guarantee()
        test_results['approximation'] = {'max_ratio': max_ratio}
        
        # Test 5: Pathological case
        line_ratio = self.test_pathological_case()
        test_results['pathological'] = {'line_ratio': line_ratio}
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        
        issues = []
        if avg_time > 2.0:
            issues.append("Performance not meeting claimed improvement")
        if matching_variance > 1.1:
            issues.append("Greedy matching has significant variance")
        if missed_improvement > 0.01:
            issues.append("Limited 2-opt misses improvements")
        if max_ratio > 1.5:
            issues.append("Approximation guarantee violated")
        if line_ratio > 1.5:
            issues.append("Struggles with pathological line case")
        
        if issues:
            print("⚠️  ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All tests passed - optimizations appear sound")
        
        # Save results
        with open('adversarial_test_christofides_optimized.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        
        return test_results, issues


def main():
    tester = AdversarialTSPTester()
    results, issues = tester.run_all_tests()
    
    # Return exit code based on issues found
    return 1 if issues else 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)