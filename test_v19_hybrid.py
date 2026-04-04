#!/usr/bin/env python3
"""
Test script for v19: Christofides with Hybrid Structural Analysis
Compares performance against v16 and v18.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
import time
from typing import List, Tuple
import json

# Import algorithms
from solutions.tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from solutions.tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def compute_nn_2opt_tour(points: List[Tuple[float, float]]) -> Tuple[List[int], float]:
    """Compute Nearest Neighbor + 2-opt baseline tour."""
    n = len(points)
    
    # Compute distance matrix
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
            dist[i][j] = d
            dist[j][i] = d
    
    # Nearest Neighbor
    start = random.randint(0, n-1)
    tour = [start]
    unvisited = set(range(n))
    unvisited.remove(start)
    
    current = start
    while unvisited:
        # Find nearest unvisited neighbor
        nearest = min(unvisited, key=lambda x: dist[current][x])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Close tour
    tour.append(start)
    
    # 2-opt optimization
    improved = True
    while improved:
        improved = False
        best_gain = 0
        best_i = -1
        best_j = -1
        
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b = tour[i-1], tour[i]
                c, d = tour[j], tour[j+1]
                
                old_distance = dist[a][b] + dist[c][d]
                new_distance = dist[a][c] + dist[b][d]
                gain = old_distance - new_distance
                
                if gain > best_gain:
                    best_gain = gain
                    best_i = i
                    best_j = j
        
        if best_gain > 0:
            tour[best_i:best_j+1] = reversed(tour[best_i:best_j+1])
            improved = True
    
    # Compute tour length
    tour_length = 0.0
    for i in range(len(tour) - 1):
        tour_length += dist[tour[i]][tour[i+1]]
    
    return tour, tour_length

def test_single_instance(points: List[Tuple[float, float]], seed: int) -> dict:
    """Test all algorithms on a single instance."""
    results = {}
    
    # Baseline: NN + 2-opt
    nn_tour, nn_length = compute_nn_2opt_tour(points)
    results['baseline_nn_2opt'] = nn_length
    
    # v16: Christofides with Path-Based Centrality
    v16_solver = ChristofidesPathCentrality(points, seed=seed)
    v16_tour, v16_length, v16_time = v16_solver.solve(centrality_weight=0.3, apply_2opt=True)
    results['v16_length'] = v16_length
    results['v16_time'] = v16_time
    results['v16_improvement'] = ((nn_length - v16_length) / nn_length) * 100
    
    # v18: Christofides with Community Detection
    v18_solver = ChristofidesCommunityDetection(points, seed=seed)
    v18_tour, v18_length, v18_time = v18_solver.solve(apply_2opt=True)
    results['v18_length'] = v18_length
    results['v18_time'] = v18_time
    results['v18_improvement'] = ((nn_length - v18_length) / nn_length) * 100
    
    # v19: Hybrid Structural Analysis
    v19_solver = ChristofidesHybridStructural(points, seed=seed)
    v19_tour, v19_length, v19_time = v19_solver.solve(
        percentile_threshold=70.0,  # Optimized based on testing
        within_community_weight=0.5,
        between_community_weight=0.3,
        apply_2opt=True
    )
    results['v19_length'] = v19_length
    results['v19_time'] = v19_time
    results['v19_improvement'] = ((nn_length - v19_length) / nn_length) * 100
    
    # Compare v19 vs v16 and v18
    results['v19_vs_v16_improvement'] = ((v16_length - v19_length) / v16_length) * 100
    results['v19_vs_v18_improvement'] = ((v18_length - v19_length) / v18_length) * 100
    
    return results

def run_comprehensive_test(n_values: List[int] = [30, 50, 75, 100], 
                          seeds: List[int] = [42, 123, 456, 789, 999],
                          output_file: str = "v19_hybrid_benchmark_results.json"):
    """Run comprehensive benchmark across different problem sizes and seeds."""
    all_results = {}
    
    for n in n_values:
        print(f"\n{'='*60}")
        print(f"Testing n = {n}")
        print(f"{'='*60}")
        
        n_results = []
        
        for seed_idx, seed in enumerate(seeds):
            print(f"  Seed {seed_idx+1}/{len(seeds)} (seed={seed})...")
            
            # Generate points
            points = generate_random_points(n, seed=seed)
            
            # Test algorithms
            results = test_single_instance(points, seed)
            results['n'] = n
            results['seed'] = seed
            n_results.append(results)
            
            # Print quick summary
            print(f"    NN+2opt: {results['baseline_nn_2opt']:.2f}")
            print(f"    v16: {results['v16_length']:.2f} ({results['v16_improvement']:+.2f}%)")
            print(f"    v18: {results['v18_length']:.2f} ({results['v18_improvement']:+.2f}%)")
            print(f"    v19: {results['v19_length']:.2f} ({results['v19_improvement']:+.2f}%)")
            print(f"    v19 vs v16: {results['v19_vs_v16_improvement']:+.2f}%")
            print(f"    v19 vs v18: {results['v19_vs_v18_improvement']:+.2f}%")
        
        # Compute averages for this n
        avg_results = {
            'n': n,
            'num_seeds': len(seeds),
            'avg_baseline': sum(r['baseline_nn_2opt'] for r in n_results) / len(n_results),
            'avg_v16_length': sum(r['v16_length'] for r in n_results) / len(n_results),
            'avg_v18_length': sum(r['v18_length'] for r in n_results) / len(n_results),
            'avg_v19_length': sum(r['v19_length'] for r in n_results) / len(n_results),
            'avg_v16_improvement': sum(r['v16_improvement'] for r in n_results) / len(n_results),
            'avg_v18_improvement': sum(r['v18_improvement'] for r in n_results) / len(n_results),
            'avg_v19_improvement': sum(r['v19_improvement'] for r in n_results) / len(n_results),
            'avg_v19_vs_v16': sum(r['v19_vs_v16_improvement'] for r in n_results) / len(n_results),
            'avg_v19_vs_v18': sum(r['v19_vs_v18_improvement'] for r in n_results) / len(n_results),
            'v19_better_v16': sum(1 for r in n_results if r['v19_vs_v16_improvement'] > 0),
            'v19_better_v18': sum(1 for r in n_results if r['v19_vs_v18_improvement'] > 0),
            'v19_worse_v16': sum(1 for r in n_results if r['v19_vs_v16_improvement'] < 0),
            'v19_worse_v18': sum(1 for r in n_results if r['v19_vs_v18_improvement'] < 0),
        }
        
        print(f"\n  Summary for n={n}:")
        print(f"    Average improvements vs NN+2opt:")
        print(f"      v16: {avg_results['avg_v16_improvement']:+.2f}%")
        print(f"      v18: {avg_results['avg_v18_improvement']:+.2f}%")
        print(f"      v19: {avg_results['avg_v19_improvement']:+.2f}%")
        print(f"    v19 vs individual algorithms:")
        print(f"      Better than v16: {avg_results['v19_better_v16']}/{len(seeds)} seeds")
        print(f"      Better than v18: {avg_results['v19_better_v18']}/{len(seeds)} seeds")
        
        all_results[n] = {
            'detailed': n_results,
            'summary': avg_results
        }
    
    # Save results to file
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Benchmark complete! Results saved to {output_file}")
    print(f"{'='*60}")
    
    # Print final summary
    print("\nFINAL SUMMARY:")
    for n in n_values:
        summary = all_results[n]['summary']
        print(f"\nn={n}:")
        print(f"  v19 avg improvement vs NN+2opt: {summary['avg_v19_improvement']:+.2f}%")
        print(f"  v19 better than v16: {summary['v19_better_v16']}/{summary['num_seeds']} seeds")
        print(f"  v19 better than v18: {summary['v19_better_v18']}/{summary['num_seeds']} seeds")
    
    return all_results

if __name__ == "__main__":
    print("Testing v19: Christofides with Hybrid Structural Analysis")
    print("Comparing against v16 (path-based centrality) and v18 (community detection)")
    
    # Run benchmark
    results = run_comprehensive_test(
        n_values=[30, 50, 75, 100],
        seeds=[42, 123, 456, 789, 999],
        output_file="v19_hybrid_benchmark_results.json"
    )