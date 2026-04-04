#!/usr/bin/env python3
"""
Benchmark OPTIMIZED v19: Christofides with Hybrid Structural Analysis at n=500
Run comprehensive multi-seed benchmark at n=500 as recommended by Vera's novelty review.
Uses the optimized version that only computes paths between odd vertices.
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
from solutions.tsp_v19_christofides_hybrid_structural_optimized import ChristofidesHybridStructuralOptimized

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
        'algorithms': {}
    }
    
    n = len(points)
    
    # Test NN+2opt baseline
    start = time.time()
    nn_tour, nn_length = compute_nn_2opt_tour(points)
    nn_time = time.time() - start
    results['algorithms']['nn_2opt'] = {
        'length': nn_length,
        'time': nn_time
    }
    
    # Test v16: Christofides with Path-Based Centrality
    try:
        start = time.time()
        solver_v16 = ChristofidesPathCentrality(points, seed=seed)
        tour_v16, length_v16, time_v16 = solver_v16.solve(
            centrality_weight=0.3,
            apply_2opt=True
        )
        v16_time = time.time() - start
        v16_improvement = (nn_length - length_v16) / nn_length * 100 if nn_length > 0 else 0
        results['algorithms']['v16_path_centrality'] = {
            'length': length_v16,
            'time': v16_time,
            'improvement_percent': v16_improvement
        }
    except Exception as e:
        results['algorithms']['v16_path_centrality'] = {
            'error': str(e)
        }
    
    # Test v18: Christofides with Community Detection
    try:
        start = time.time()
        solver_v18 = ChristofidesCommunityDetection(points, seed=seed)
        tour_v18, length_v18, time_v18 = solver_v18.solve(
            percentile_threshold=50,
            apply_2opt=True
        )
        v18_time = time.time() - start
        v18_improvement = (nn_length - length_v18) / nn_length * 100 if nn_length > 0 else 0
        results['algorithms']['v18_community_detection'] = {
            'length': length_v18,
            'time': v18_time,
            'improvement_percent': v18_improvement
        }
    except Exception as e:
        results['algorithms']['v18_community_detection'] = {
            'error': str(e)
        }
    
    # Test v19 OPTIMIZED: Christofides with Hybrid Structural Analysis
    try:
        start = time.time()
        solver_v19 = ChristofidesHybridStructuralOptimized(points, seed=seed)
        tour_v19, length_v19, time_v19 = solver_v19.solve(
            percentile_threshold=70,
            within_community_weight=0.8,
            between_community_weight=0.3,
            apply_2opt=True
        )
        v19_time = time.time() - start
        v19_improvement = (nn_length - length_v19) / nn_length * 100 if nn_length > 0 else 0
        results['algorithms']['v19_hybrid_structural_optimized'] = {
            'length': length_v19,
            'time': v19_time,
            'improvement_percent': v19_improvement
        }
    except Exception as e:
        results['algorithms']['v19_hybrid_structural_optimized'] = {
            'error': str(e)
        }
    
    return results

def run_benchmark():
    """Run comprehensive benchmark at n=500 with multiple seeds."""
    n = 500
    seeds = [42, 123, 456, 789, 1011, 2022, 3033, 4044, 5055, 6066]  # 10 seeds
    
    print(f"Running n={n} benchmark with {len(seeds)} seeds...")
    print("=" * 60)
    
    all_results = []
    
    for i, seed in enumerate(seeds):
        print(f"\nSeed {i+1}/{len(seeds)}: {seed}")
        
        # Generate points
        points = generate_random_points(n, seed=seed)
        
        # Run tests
        results = test_single_instance(points, seed)
        all_results.append(results)
        
        # Print progress
        print(f"  NN+2opt: {results['algorithms']['nn_2opt']['length']:.2f}")
        
        if 'v16_path_centrality' in results['algorithms'] and 'length' in results['algorithms']['v16_path_centrality']:
            v16 = results['algorithms']['v16_path_centrality']
            print(f"  v16: {v16['length']:.2f} ({v16['improvement_percent']:+.2f}%) in {v16['time']:.2f}s")
        
        if 'v18_community_detection' in results['algorithms'] and 'length' in results['algorithms']['v18_community_detection']:
            v18 = results['algorithms']['v18_community_detection']
            print(f"  v18: {v18['length']:.2f} ({v18['improvement_percent']:+.2f}%) in {v18['time']:.2f}s")
        
        if 'v19_hybrid_structural_optimized' in results['algorithms'] and 'length' in results['algorithms']['v19_hybrid_structural_optimized']:
            v19 = results['algorithms']['v19_hybrid_structural_optimized']
            print(f"  v19 (OPTIMIZED): {v19['length']:.2f} ({v19['improvement_percent']:+.2f}%) in {v19['time']:.2f}s")
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"v19_optimized_n500_benchmark_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Analyze results
    analyze_results(all_results)
    
    return all_results

def analyze_results(all_results):
    """Analyze benchmark results."""
    print("\n" + "=" * 60)
    print("RESULTS ANALYSIS")
    print("=" * 60)
    
    # Collect improvements
    v16_improvements = []
    v18_improvements = []
    v19_improvements = []
    
    for result in all_results:
        if 'v16_path_centrality' in result['algorithms'] and 'improvement_percent' in result['algorithms']['v16_path_centrality']:
            v16_improvements.append(result['algorithms']['v16_path_centrality']['improvement_percent'])
        
        if 'v18_community_detection' in result['algorithms'] and 'improvement_percent' in result['algorithms']['v18_community_detection']:
            v18_improvements.append(result['algorithms']['v18_community_detection']['improvement_percent'])
        
        if 'v19_hybrid_structural_optimized' in result['algorithms'] and 'improvement_percent' in result['algorithms']['v19_hybrid_structural_optimized']:
            v19_improvements.append(result['algorithms']['v19_hybrid_structural_optimized']['improvement_percent'])
    
    # Calculate statistics
    def stats(improvements, name):
        if not improvements:
            print(f"{name}: No valid results")
            return
        
        avg = sum(improvements) / len(improvements)
        above_threshold = sum(1 for x in improvements if x > 0.1)  # Vera's threshold
        below_threshold = sum(1 for x in improvements if x < -0.1)
        within_threshold = len(improvements) - above_threshold - below_threshold
        
        print(f"{name}:")
        print(f"  Average improvement: {avg:.3f}%")
        print(f"  Range: [{min(improvements):.3f}%, {max(improvements):.3f}%]")
        print(f"  Above +0.1% threshold: {above_threshold}/{len(improvements)} ({above_threshold/len(improvements)*100:.1f}%)")
        print(f"  Below -0.1% threshold: {below_threshold}/{len(improvements)}")
        print(f"  Within ±0.1%: {within_threshold}/{len(improvements)}")
        
        # Check consistency (Vera's criterion)
        if above_threshold >= len(improvements) * 0.5:  # At least 50% above threshold
            print(f"  ✓ CONSISTENT: Majority above threshold")
        else:
            print(f"  ✗ INCONSISTENT: Less than 50% above threshold")
        
        return avg
    
    print(f"\nTotal instances: {len(all_results)}")
    
    v16_avg = stats(v16_improvements, "v16 (Path-Based Centrality)")
    v18_avg = stats(v18_improvements, "v18 (Community Detection)")
    v19_avg = stats(v19_improvements, "v19 (Hybrid Structural - OPTIMIZED)")
    
    # Compare v19 to parents
    if v16_avg is not None and v19_avg is not None:
        print(f"\nv19 vs v16: {v19_avg - v16_avg:+.3f}% difference")
        if v19_avg > v16_avg:
            print(f"  ✓ v19 outperforms v16")
        else:
            print(f"  ✗ v19 does not outperform v16")
    
    if v18_avg is not None and v19_avg is not None:
        print(f"v19 vs v18: {v19_avg - v18_avg:+.3f}% difference")
        if v19_avg > v18_avg:
            print(f"  ✓ v19 outperforms v18")
        else:
            print(f"  ✗ v19 does not outperform v18")
    
    # Check publication criteria
    print("\n" + "=" * 60)
    print("PUBLICATION ASSESSMENT (Vera's Criteria)")
    print("=" * 60)
    
    if v19_improvements:
        above_threshold = sum(1 for x in v19_improvements if x > 0.1)
        ratio = above_threshold / len(v19_improvements)
        
        print(f"1. Performance vs NN+2opt: Average improvement = {v19_avg:.3f}%")
        print(f"2. Consistency: {above_threshold}/{len(v19_improvements)} above +0.1% threshold ({ratio*100:.1f}%)")
        
        if v19_avg > 0.1 and ratio >= 0.5:
            print(f"✓ POTENTIALLY NOVEL: Meets both criteria")
            print(f"  - Average improvement > 0.1%: {v19_avg:.3f}% > 0.1%")
            print(f"  - Consistency ≥ 50%: {ratio*100:.1f}% ≥ 50%")
        else:
            print(f"✗ NEEDS IMPROVEMENT:")
            if v19_avg <= 0.1:
                print(f"  - Average improvement {v19_avg:.3f}% ≤ 0.1%")
            if ratio < 0.5:
                print(f"  - Consistency {ratio*100:.1f}% < 50%")

if __name__ == "__main__":
    run_benchmark()