#!/usr/bin/env python3
"""
Quick test of v19 at n=500 with 3 seeds for verification.
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
from solutions.tsp_v16_christofides_path_centrality import solve_tsp as solve_v16
from solutions.tsp_v18_christofides_community_detection import solve_tsp as solve_v18
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
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist[current][city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Simple 2-opt improvement (limited iterations for speed)
    def tour_length(t):
        total = 0.0
        for i in range(len(t)):
            j = (i + 1) % len(t)
            total += dist[t[i]][t[j]]
        return total
    
    improved = True
    for _ in range(100):  # Limit iterations
        improved = False
        for i in range(n):
            for j in range(i + 2, n):
                if j == n - 1 and i == 0:
                    continue
                
                # Try 2-opt swap
                a, b = tour[i], tour[(i + 1) % n]
                c, d = tour[j], tour[(j + 1) % n]
                
                current_dist = dist[a][b] + dist[c][d]
                new_dist = dist[a][c] + dist[b][d]
                
                if new_dist < current_dist:
                    # Reverse segment between b and c
                    if i < j:
                        tour[i+1:j+1] = reversed(tour[i+1:j+1])
                    else:
                        tour[i+1:] = reversed(tour[i+1:])
                        tour[:j+1] = reversed(tour[:j+1])
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    
    length = tour_length(tour)
    return tour, length

def run_single_seed(n: int, seed: int):
    """Run benchmark for a single seed."""
    print(f"  Seed {seed}: Generating {n} points...")
    points = generate_random_points(n, seed)
    
    # Compute baseline
    print(f"    Computing NN+2opt baseline...")
    baseline_tour, baseline_length = compute_nn_2opt_tour(points)
    
    # Run v16
    print(f"    Running v16...")
    v16_tour, v16_length = solve_v16(points, seed=seed)
    
    # Run v18
    print(f"    Running v18...")
    v18_tour, v18_length = solve_v18(points, seed=seed)
    
    # Run v19
    print(f"    Running v19...")
    v19_solver = ChristofidesHybridStructural(points, seed=seed)
    v19_tour, v19_length, _ = v19_solver.solve(
        percentile_threshold=70.0,
        within_community_weight=0.5,
        between_community_weight=0.3,
        apply_2opt=True
    )
    
    # Calculate improvements
    v16_improvement = ((baseline_length - v16_length) / baseline_length) * 100
    v18_improvement = ((baseline_length - v18_length) / baseline_length) * 100
    v19_improvement = ((baseline_length - v19_length) / baseline_length) * 100
    
    # Compare v19 vs parent algorithms
    v19_vs_v16 = ((v16_length - v19_length) / v16_length) * 100
    v19_vs_v18 = ((v18_length - v19_length) / v18_length) * 100
    
    return {
        'seed': seed,
        'baseline_length': baseline_length,
        'v16_length': v16_length,
        'v18_length': v18_length,
        'v19_length': v19_length,
        'v16_improvement': v16_improvement,
        'v18_improvement': v18_improvement,
        'v19_improvement': v19_improvement,
        'v19_vs_v16_improvement': v19_vs_v16,
        'v19_vs_v18_improvement': v19_vs_v18,
    }

def main():
    n = 500
    seeds = [42, 123, 456]  # Just 3 seeds for quick test
    
    print(f"\n{'='*80}")
    print(f"QUICK V19 TEST: n=500 with {len(seeds)} seeds")
    print(f"{'='*80}")
    
    all_results = []
    start_time = time.time()
    
    for seed in seeds:
        result = run_single_seed(n, seed)
        all_results.append(result)
        print(f"  Result: v19 improvement = {result['v19_improvement']:+.3f}%")
    
    total_time = time.time() - start_time
    
    # Calculate averages
    avg_baseline = sum(r['baseline_length'] for r in all_results) / len(all_results)
    avg_v16_length = sum(r['v16_length'] for r in all_results) / len(all_results)
    avg_v18_length = sum(r['v18_length'] for r in all_results) / len(all_results)
    avg_v19_length = sum(r['v19_length'] for r in all_results) / len(all_results)
    
    avg_v16_improvement = sum(r['v16_improvement'] for r in all_results) / len(all_results)
    avg_v18_improvement = sum(r['v18_improvement'] for r in all_results) / len(all_results)
    avg_v19_improvement = sum(r['v19_improvement'] for r in all_results) / len(all_results)
    
    avg_v19_vs_v16 = sum(r['v19_vs_v16_improvement'] for r in all_results) / len(all_results)
    avg_v19_vs_v18 = sum(r['v19_vs_v18_improvement'] for r in all_results) / len(all_results)
    
    # Count seeds where v19 beats parents
    v19_better_v16 = sum(1 for r in all_results if r['v19_vs_v16_improvement'] > 0)
    v19_better_v18 = sum(1 for r in all_results if r['v19_vs_v18_improvement'] > 0)
    
    # Count seeds meeting publication threshold
    v19_above_threshold = sum(1 for r in all_results if r['v19_improvement'] > 0.1)
    
    print(f"\n{'='*80}")
    print(f"QUICK TEST RESULTS (n={n}, {len(seeds)} seeds)")
    print(f"{'='*80}")
    print(f"Total time: {total_time:.1f}s")
    print(f"\nAverage improvements vs NN+2opt:")
    print(f"  v16: {avg_v16_improvement:+.3f}%")
    print(f"  v18: {avg_v18_improvement:+.3f}%")
    print(f"  v19: {avg_v19_improvement:+.3f}%")
    
    print(f"\nv19 vs parent algorithms:")
    print(f"  Better than v16: {v19_better_v16}/{len(seeds)} seeds ({avg_v19_vs_v16:+.3f}% avg)")
    print(f"  Better than v18: {v19_better_v18}/{len(seeds)} seeds ({avg_v19_vs_v18:+.3f}% avg)")
    
    print(f"\nPublication threshold (>0.1% improvement vs NN+2opt):")
    print(f"  v19: {v19_above_threshold}/{len(seeds)} seeds ({(v19_above_threshold/len(all_results))*100:.1f}%)")
    
    # Save results
    output_data = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'benchmark_type': 'v19_n500_quick_test',
        'seeds': seeds,
        'total_time_seconds': total_time,
        'avg_baseline': avg_baseline,
        'avg_v16_length': avg_v16_length,
        'avg_v18_length': avg_v18_length,
        'avg_v19_length': avg_v19_length,
        'avg_v16_improvement': avg_v16_improvement,
        'avg_v18_improvement': avg_v18_improvement,
        'avg_v19_improvement': avg_v19_improvement,
        'avg_v19_vs_v16': avg_v19_vs_v16,
        'avg_v19_vs_v18': avg_v19_vs_v18,
        'v19_better_v16': v19_better_v16,
        'v19_better_v18': v19_better_v18,
        'v19_above_threshold': v19_above_threshold,
        'detailed_results': all_results
    }
    
    with open("v19_n500_quick_test.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to: v19_n500_quick_test.json")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()