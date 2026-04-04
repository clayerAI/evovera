#!/usr/bin/env python3
"""
Benchmark v19: Christofides with Hybrid Structural Analysis at n=500
Run comprehensive multi-seed benchmark at n=500 as recommended by Vera's novelty review.
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
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist[current][city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    # Compute tour length
    def tour_length(tour):
        length = 0.0
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            length += dist[tour[i]][tour[j]]
        return length
    
    # 2-opt improvement
    best_tour = tour[:]
    best_length = tour_length(tour)
    improved = True
    
    while improved:
        improved = False
        for i in range(len(best_tour)):
            for j in range(i + 2, len(best_tour) + (i > 0)):
                if j == len(best_tour):
                    k = 0
                else:
                    k = j
                
                # Try 2-opt swap
                new_tour = best_tour[:i+1] + best_tour[i+1:k+1][::-1] + best_tour[k+1:]
                new_length = tour_length(new_tour)
                
                if new_length < best_length:
                    best_tour = new_tour
                    best_length = new_length
                    improved = True
                    break
            if improved:
                break
    
    return best_tour, best_length

def test_single_instance(points: List[Tuple[float, float]], seed: int) -> dict:
    """Test all algorithms on a single instance."""
    results = {
        'n': len(points),
        'seed': seed,
    }
    
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

def run_n500_benchmark(seeds: List[int] = [42, 123, 456, 789, 999, 1111, 2222, 3333, 4444, 5555],
                      output_file: str = "v19_n500_benchmark_results.json"):
    """Run comprehensive benchmark at n=500 with multiple seeds."""
    n = 500
    print(f"\n{'='*80}")
    print(f"V19 NOVELTY REVIEW: n=500 MULTI-SEED BENCHMARK")
    print(f"{'='*80}")
    print(f"Running benchmark with n={n}, {len(seeds)} seeds")
    print(f"Seeds: {seeds}")
    print(f"{'='*80}")
    
    all_results = []
    start_time = time.time()
    
    for seed_idx, seed in enumerate(seeds):
        print(f"\n[Seed {seed_idx+1}/{len(seeds)}] seed={seed}")
        print(f"  Generating {n} random points...")
        
        # Generate points
        points = generate_random_points(n, seed=seed)
        
        print(f"  Testing algorithms...")
        seed_start = time.time()
        
        # Test algorithms
        results = test_single_instance(points, seed)
        all_results.append(results)
        
        seed_time = time.time() - seed_start
        print(f"  Completed in {seed_time:.1f}s")
        print(f"    NN+2opt: {results['baseline_nn_2opt']:.2f}")
        print(f"    v16: {results['v16_length']:.2f} ({results['v16_improvement']:+.2f}%)")
        print(f"    v18: {results['v18_length']:.2f} ({results['v18_improvement']:+.2f}%)")
        print(f"    v19: {results['v19_length']:.2f} ({results['v19_improvement']:+.2f}%)")
        print(f"    v19 vs v16: {results['v19_vs_v16_improvement']:+.2f}%")
        print(f"    v19 vs v18: {results['v19_vs_v18_improvement']:+.2f}%")
    
    # Compute comprehensive statistics
    total_time = time.time() - start_time
    
    # Calculate averages
    avg_baseline = sum(r['baseline_nn_2opt'] for r in all_results) / len(all_results)
    avg_v16_length = sum(r['v16_length'] for r in all_results) / len(all_results)
    avg_v18_length = sum(r['v18_length'] for r in all_results) / len(all_results)
    avg_v19_length = sum(r['v19_length'] for r in all_results) / len(all_results)
    
    avg_v16_improvement = sum(r['v16_improvement'] for r in all_results) / len(all_results)
    avg_v18_improvement = sum(r['v18_improvement'] for r in all_results) / len(all_results)
    avg_v19_improvement = sum(r['v19_improvement'] for r in all_results) / len(all_results)
    
    avg_v19_vs_v16 = sum(r['v19_vs_v16_improvement'] for r in all_results) / len(all_results)
    avg_v19_vs_v18 = sum(r['v19_vs_v18_improvement'] for r in all_results) / len(all_results)
    
    # Count wins/losses
    v19_better_v16 = sum(1 for r in all_results if r['v19_vs_v16_improvement'] > 0)
    v19_better_v18 = sum(1 for r in all_results if r['v19_vs_v18_improvement'] > 0)
    v19_worse_v16 = sum(1 for r in all_results if r['v19_vs_v16_improvement'] < 0)
    v19_worse_v18 = sum(1 for r in all_results if r['v19_vs_v18_improvement'] < 0)
    
    # Count seeds meeting publication threshold (>0.1% improvement)
    v16_above_threshold = sum(1 for r in all_results if r['v16_improvement'] > 0.1)
    v18_above_threshold = sum(1 for r in all_results if r['v18_improvement'] > 0.1)
    v19_above_threshold = sum(1 for r in all_results if r['v19_improvement'] > 0.1)
    
    # Prepare summary
    summary = {
        'n': n,
        'num_seeds': len(seeds),
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
        'v19_worse_v16': v19_worse_v16,
        'v19_worse_v18': v19_worse_v18,
        'v16_above_threshold': v16_above_threshold,
        'v18_above_threshold': v18_above_threshold,
        'v19_above_threshold': v19_above_threshold,
        'v16_threshold_percentage': (v16_above_threshold / len(all_results)) * 100,
        'v18_threshold_percentage': (v18_above_threshold / len(all_results)) * 100,
        'v19_threshold_percentage': (v19_above_threshold / len(all_results)) * 100,
    }
    
    # Save results
    output_data = {
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'benchmark_type': 'v19_n500_multi_seed',
        'purpose': 'Vera novelty review completion - n=500 verification',
        'summary': summary,
        'detailed_results': all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Results saved to: {output_file}")
    print(f"\nSUMMARY STATISTICS (n={n}, {len(seeds)} seeds):")
    print(f"\nAverage improvements vs NN+2opt:")
    print(f"  v16: {avg_v16_improvement:+.3f}%")
    print(f"  v18: {avg_v18_improvement:+.3f}%")
    print(f"  v19: {avg_v19_improvement:+.3f}%")
    
    print(f"\nv19 vs parent algorithms:")
    print(f"  Better than v16: {v19_better_v16}/{len(seeds)} seeds ({avg_v19_vs_v16:+.3f}% avg)")
    print(f"  Better than v18: {v19_better_v18}/{len(seeds)} seeds ({avg_v19_vs_v18:+.3f}% avg)")
    
    print(f"\nPublication threshold (>0.1% improvement vs NN+2opt):")
    print(f"  v16: {v16_above_threshold}/{len(seeds)} seeds ({summary['v16_threshold_percentage']:.1f}%)")
    print(f"  v18: {v18_above_threshold}/{len(seeds)} seeds ({summary['v18_threshold_percentage']:.1f}%)")
    print(f"  v19: {v19_above_threshold}/{len(seeds)} seeds ({summary['v19_threshold_percentage']:.1f}%)")
    
    print(f"\n{'='*80}")
    print(f"NOVELTY ASSESSMENT FOR VERA:")
    print(f"{'='*80}")
    
    # Novelty assessment criteria
    v19_meets_performance = avg_v19_improvement > 0.1
    v19_consistent = v19_above_threshold >= (len(seeds) * 0.7)  # At least 70% of seeds
    
    print(f"Performance threshold (0.1%): {'MET' if v19_meets_performance else 'NOT MET'}")
    print(f"Consistency threshold (70% seeds >0.1%): {'MET' if v19_consistent else 'NOT MET'}")
    
    if v19_meets_performance and v19_consistent:
        print(f"\n✅ V19 PASSES n=500 NOVELTY VERIFICATION")
        print(f"   Average improvement: {avg_v19_improvement:+.3f}%")
        print(f"   Consistency: {v19_above_threshold}/{len(seeds)} seeds ({summary['v19_threshold_percentage']:.1f}%)")
    else:
        print(f"\n❌ V19 FAILS n=500 NOVELTY VERIFICATION")
        if not v19_meets_performance:
            print(f"   Reason: Average improvement ({avg_v19_improvement:+.3f}%) below 0.1% threshold")
        if not v19_consistent:
            print(f"   Reason: Only {v19_above_threshold}/{len(seeds)} seeds ({summary['v19_threshold_percentage']:.1f}%) exceed threshold")
    
    print(f"\n{'='*80}")
    
    return output_data

if __name__ == "__main__":
    # Run benchmark with 10 seeds for comprehensive assessment
    run_n500_benchmark(
        seeds=[42, 123, 456, 789, 999, 1111, 2222, 3333, 4444, 5555],
        output_file="v19_n500_benchmark_results.json"
    )