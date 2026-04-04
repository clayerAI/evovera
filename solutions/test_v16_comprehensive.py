#!/usr/bin/env python3
"""
Comprehensive test of v16 against multiple baselines with different parameters.
Goal: Understand the discrepancy between my results and Vera's.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
from tsp_v1_nearest_neighbor import EuclideanTSP  # Use the class for more control
from tsp_v2_christofides import solve_tsp as christofides_solve
import numpy as np
import random
import time
from typing import List, Tuple
import json

def generate_points_np(n: int = 100, seed: int = 42) -> np.ndarray:
    """Generate random points using numpy (consistent with tsp_v1)."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

def generate_points_random(n: int = 100, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points using Python random (my test)."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_nn2opt_strong(points: np.ndarray, num_starts: int = 10, two_opt_iterations: int = 500):
    """Strong NN+2opt baseline with multiple starts (like in EuclideanTSP benchmark)."""
    n = len(points)
    
    # Create TSP instance
    class CustomTSP:
        def __init__(self, points):
            self.n = len(points)
            self.points = points
            self.dist_matrix = self._compute_distance_matrix()
        
        def _compute_distance_matrix(self):
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = np.linalg.norm(self.points[i] - self.points[j])
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
        
        def distance(self, i, j):
            return self.dist_matrix[i, j]
        
        def nearest_neighbor(self, start_city=0):
            unvisited = set(range(self.n))
            tour = [start_city]
            unvisited.remove(start_city)
            
            current = start_city
            
            while unvisited:
                nearest = min(unvisited, key=lambda city: self.distance(current, city))
                tour.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Return to starting city
            tour.append(start_city)
            return tour
        
        def two_opt(self, tour, max_iterations=1000):
            if len(tour) < 4 or tour[0] != tour[-1]:
                return tour
            
            tour = tour[:-1]
            n = len(tour)
            improved = True
            iteration = 0
            
            while improved and iteration < max_iterations:
                improved = False
                for i in range(n - 1):
                    for j in range(i + 2, n):
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
            return tour
        
        def tour_distance(self, tour):
            distance = 0.0
            for i in range(len(tour) - 1):
                distance += self.distance(tour[i], tour[i + 1])
            return distance
    
    tsp = CustomTSP(points)
    
    # Multi-start nearest neighbor
    best_tour = None
    best_length = float('inf')
    
    for start in range(min(num_starts, n)):
        tour = tsp.nearest_neighbor(start_city=start)
        tour = tsp.two_opt(tour, max_iterations=two_opt_iterations)
        length = tsp.tour_distance(tour)
        
        if length < best_length:
            best_length = length
            best_tour = tour
    
    # Convert closed tour to open
    if best_tour and len(best_tour) > 0 and best_tour[0] == best_tour[-1]:
        best_tour = best_tour[:-1]
    
    return best_tour, best_length

def test_v16_adaptive(points, seed=42):
    """Test v16 with adaptive weight selection."""
    # Convert to list format if needed
    if isinstance(points, np.ndarray):
        points_list = [(float(p[0]), float(p[1])) for p in points]
    else:
        points_list = points
    
    # Try different centrality weights
    weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    best_length = float('inf')
    best_tour = None
    best_weight = 0.0
    
    for weight in weights:
        # Need to reinitialize solver for each weight
        from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
        solver = ChristofidesPathCentrality(points_list, seed=seed)
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        
        if length < best_length:
            best_length = length
            best_tour = tour
            best_weight = weight
    
    return best_tour, best_length, best_weight

def main():
    print("Comprehensive v16 analysis")
    print("Testing against different baselines and point generation methods")
    print("=" * 70)
    
    n = 100
    seeds = [42, 123, 456, 789, 999]
    
    all_results = []
    
    for seed in seeds:
        print(f"\n{'='*70}")
        print(f"Seed {seed}:")
        print('='*70)
        
        # Generate points using both methods
        points_np = generate_points_np(n=n, seed=seed)
        points_random = generate_points_random(n=n, seed=seed)
        
        # Test 1: Strong NN+2opt (multi-start)
        nn2opt_tour, nn2opt_length = test_nn2opt_strong(points_np, num_starts=10, two_opt_iterations=500)
        
        # Test 2: Standard Christofides
        christofides_tour, christofides_length = christofides_solve(points_np)
        
        # Test 3: v16 with default weight (0.3)
        v16_tour_default, v16_length_default = v16_solve(points_random, seed=seed)
        
        # Test 4: v16 with adaptive weight selection
        v16_tour_adaptive, v16_length_adaptive, best_weight = test_v16_adaptive(points_random, seed=seed)
        
        # Calculate improvements
        imp_vs_nn2opt_default = (nn2opt_length - v16_length_default) / nn2opt_length * 100
        imp_vs_nn2opt_adaptive = (nn2opt_length - v16_length_adaptive) / nn2opt_length * 100
        imp_vs_christofides_default = (christofides_length - v16_length_default) / christofides_length * 100
        imp_vs_christofides_adaptive = (christofides_length - v16_length_adaptive) / christofides_length * 100
        
        print(f"NN+2opt (strong): {nn2opt_length:.4f}")
        print(f"Standard Christofides: {christofides_length:.4f}")
        print(f"v16 (weight=0.3): {v16_length_default:.4f}")
        print(f"  vs NN+2opt: {imp_vs_nn2opt_default:.2f}%")
        print(f"  vs Christofides: {imp_vs_christofides_default:.2f}%")
        print(f"v16 (adaptive, weight={best_weight}): {v16_length_adaptive:.4f}")
        print(f"  vs NN+2opt: {imp_vs_nn2opt_adaptive:.2f}%")
        print(f"  vs Christofides: {imp_vs_christofides_adaptive:.2f}%")
        
        # Check point generation difference
        # Convert points_random to numpy for comparison
        points_random_np = np.array(points_random)
        diff = np.abs(points_np - points_random_np).max()
        print(f"Point generation difference (max): {diff:.6f}")
        
        all_results.append({
            'seed': seed,
            'nn2opt_length': nn2opt_length,
            'christofides_length': christofides_length,
            'v16_length_default': v16_length_default,
            'v16_length_adaptive': v16_length_adaptive,
            'best_weight': best_weight,
            'imp_vs_nn2opt_default': imp_vs_nn2opt_default,
            'imp_vs_nn2opt_adaptive': imp_vs_nn2opt_adaptive,
            'imp_vs_christofides_default': imp_vs_christofides_default,
            'imp_vs_christofides_adaptive': imp_vs_christofides_adaptive,
            'point_generation_diff': diff
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY:")
    
    avg_nn2opt = sum(r['nn2opt_length'] for r in all_results) / len(all_results)
    avg_christofides = sum(r['christofides_length'] for r in all_results) / len(all_results)
    avg_v16_default = sum(r['v16_length_default'] for r in all_results) / len(all_results)
    avg_v16_adaptive = sum(r['v16_length_adaptive'] for r in all_results) / len(all_results)
    
    avg_imp_vs_nn2opt_default = sum(r['imp_vs_nn2opt_default'] for r in all_results) / len(all_results)
    avg_imp_vs_nn2opt_adaptive = sum(r['imp_vs_nn2opt_adaptive'] for r in all_results) / len(all_results)
    avg_imp_vs_christofides_default = sum(r['imp_vs_christofides_default'] for r in all_results) / len(all_results)
    avg_imp_vs_christofides_adaptive = sum(r['imp_vs_christofides_adaptive'] for r in all_results) / len(all_results)
    
    print(f"Average NN+2opt (strong): {avg_nn2opt:.4f}")
    print(f"Average Standard Christofides: {avg_christofides:.4f}")
    print(f"Average v16 (default): {avg_v16_default:.4f}")
    print(f"Average v16 (adaptive): {avg_v16_adaptive:.4f}")
    print()
    print(f"Average v16 (default) vs NN+2opt: {avg_imp_vs_nn2opt_default:.2f}%")
    print(f"Average v16 (adaptive) vs NN+2opt: {avg_imp_vs_nn2opt_adaptive:.2f}%")
    print(f"Average v16 (default) vs Christofides: {avg_imp_vs_christofides_default:.2f}%")
    print(f"Average v16 (adaptive) vs Christofides: {avg_imp_vs_christofides_adaptive:.2f}%")
    
    # Compare with Vera's reported results
    print("\n" + "=" * 70)
    print("COMPARISON WITH VERA'S v16 vs NN+2opt RESULTS:")
    
    vera_results = {
        42: 1.61,
        123: -1.24,
        456: 1.21,
        789: -0.39,
        999: 6.60
    }
    
    print("Seed | Vera's % | My Default % | My Adaptive % | Vera Match?")
    print("-" * 70)
    
    default_matches = 0
    adaptive_matches = 0
    
    for r in all_results:
        seed = r['seed']
        vera = vera_results.get(seed, 0)
        my_default = r['imp_vs_nn2opt_default']
        my_adaptive = r['imp_vs_nn2opt_adaptive']
        
        # Check sign match
        default_match = (vera > 0 and my_default > 0) or (vera <= 0 and my_default <= 0)
        adaptive_match = (vera > 0 and my_adaptive > 0) or (vera <= 0 and my_adaptive <= 0)
        
        if default_match:
            default_matches += 1
        if adaptive_match:
            adaptive_matches += 1
        
        print(f"{seed:4d} | {vera:7.2f}% | {my_default:11.2f}% | {my_adaptive:12.2f}% | "
              f"{'✅' if default_match else '❌'}")
    
    print(f"\nSign matches with Vera's results:")
    print(f"  Default v16: {default_matches}/{len(seeds)}")
    print(f"  Adaptive v16: {adaptive_matches}/{len(seeds)}")
    
    # Save results
    with open('/workspace/evovera/v16_comprehensive_analysis.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to /workspace/evovera/v16_comprehensive_analysis.json")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    
    if avg_imp_vs_christofides_adaptive > 0.1:
        print(f"✅ v16 (adaptive) beats 0.1% novelty threshold vs Christofides: {avg_imp_vs_christofides_adaptive:.2f}%")
    else:
        print(f"❌ v16 (adaptive) does NOT beat 0.1% novelty threshold: {avg_imp_vs_christofides_adaptive:.2f}%")
    
    if default_matches < len(seeds):
        print("⚠️  Test methodology discrepancy with Vera detected")
        print("   Need to align: 1) Point generation, 2) NN+2opt implementation, 3) Test parameters")
    
    print("\nNext steps:")
    print("1. Ask Vera for exact test script to reproduce her results")
    print("2. Implement adaptive weight selection in v16")
    print("3. Test on standardized benchmark instances")
    print("4. Optimize for consistency across instance types")

if __name__ == "__main__":
    main()