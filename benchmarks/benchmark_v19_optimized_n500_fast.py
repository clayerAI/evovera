#!/usr/bin/env python3
"""
Fast benchmark for OPTIMIZED v19 at n=500.
Focuses on v19 performance only, uses simpler baseline computation.
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

def compute_nn_tour(points: List[Tuple[float, float]]) -> Tuple[List[int], float]:
    """Compute simple Nearest Neighbor tour (faster than NN+2opt)."""
    n = len(points)
    
    # Compute distance matrix (this is the bottleneck, but we need it)
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
    length = 0.0
    for i in range(len(tour)):
        j = (i + 1) % len(tour)
        length += dist[tour[i]][tour[j]]
    
    return tour, length

def test_single_instance(points: List[Tuple[float, float]], seed: int) -> dict:
    """Test v19 optimized on a single instance."""
    results = {
        'n': len(points),
        'seed': seed,
        'algorithms': {}
    }
    
    n = len(points)
    
    # Test NN baseline (simpler, faster)
    start = time.time()
    nn_tour, nn_length = compute_nn_tour(points)
    nn_time = time.time() - start
    results['algorithms']['nn'] = {
        'length': nn_length,
        'time': nn_time
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
        import traceback
        traceback.print_exc()
    
    return results

def run_benchmark():
    """Run benchmark at n=500 with multiple seeds."""
    n = 500
    seeds = [42, 123, 456, 789, 1011]  # 5 seeds for now
    
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
        print(f"  NN: {results['algorithms']['nn']['length']:.2f} (took {results['algorithms']['nn']['time']:.2f}s)")
        
        if 'v19_hybrid_structural_optimized' in results['algorithms'] and 'length' in results['algorithms']['v19_hybrid_structural_optimized']:
            v19 = results['algorithms']['v19_hybrid_structural_optimized']
            print(f"  v19 (OPTIMIZED): {v19['length']:.2f} ({v19['improvement_percent']:+.2f}%) in {v19['time']:.2f}s")
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"v19_optimized_n500_fast_benchmark_{timestamp}.json"
    
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
    v19_improvements = []
    
    for result in all_results:
        if 'v19_hybrid_structural_optimized' in result['algorithms'] and 'improvement_percent' in result['algorithms']['v19_hybrid_structural_optimized']:
            v19_improvements.append(result['algorithms']['v19_hybrid_structural_optimized']['improvement_percent'])
    
    # Calculate statistics
    if not v19_improvements:
        print("No valid v19 results")
        return
    
    avg = sum(v19_improvements) / len(v19_improvements)
    above_threshold = sum(1 for x in v19_improvements if x > 0.1)  # Vera's threshold
    below_threshold = sum(1 for x in v19_improvements if x < -0.1)
    within_threshold = len(v19_improvements) - above_threshold - below_threshold
    
    print(f"v19 (Hybrid Structural - OPTIMIZED):")
    print(f"  Average improvement vs NN: {avg:.3f}%")
    print(f"  Range: [{min(v19_improvements):.3f}%, {max(v19_improvements):.3f}%]")
    print(f"  Above +0.1% threshold: {above_threshold}/{len(v19_improvements)} ({above_threshold/len(v19_improvements)*100:.1f}%)")
    print(f"  Below -0.1% threshold: {below_threshold}/{len(v19_improvements)}")
    print(f"  Within ±0.1%: {within_threshold}/{len(v19_improvements)}")
    
    # Check consistency (Vera's criterion)
    if above_threshold >= len(v19_improvements) * 0.5:  # At least 50% above threshold
        print(f"  ✓ CONSISTENT: Majority above threshold")
    else:
        print(f"  ✗ INCONSISTENT: Less than 50% above threshold")
    
    # Check publication criteria
    print("\n" + "=" * 60)
    print("PUBLICATION ASSESSMENT (Vera's Criteria)")
    print("=" * 60)
    
    ratio = above_threshold / len(v19_improvements)
    
    print(f"1. Performance vs NN: Average improvement = {avg:.3f}%")
    print(f"2. Consistency: {above_threshold}/{len(v19_improvements)} above +0.1% threshold ({ratio*100:.1f}%)")
    
    if avg > 0.1 and ratio >= 0.5:
        print(f"✓ POTENTIALLY NOVEL: Meets both criteria")
        print(f"  - Average improvement > 0.1%: {avg:.3f}% > 0.1%")
        print(f"  - Consistency ≥ 50%: {ratio*100:.1f}% ≥ 50%")
    else:
        print(f"✗ NEEDS IMPROVEMENT:")
        if avg <= 0.1:
            print(f"  - Average improvement {avg:.3f}% ≤ 0.1%")
        if ratio < 0.5:
            print(f"  - Consistency {ratio*100:.1f}% < 50%")

if __name__ == "__main__":
    run_benchmark()