#!/usr/bin/env python3
"""
Benchmark v14 Christofides Adaptive Matching on 500-node instances
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/solutions')

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching, generate_random_points
from tsp_v1_nearest_neighbor import solve_tsp as solve_nn_2opt
from tsp_v2_christofides import Christofides
import json
import time
import statistics
import math

def compute_tour_length(tour, points):
    """Compute total length of a tour given points."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % n]]
        total += math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return total

def benchmark_500_nodes(num_instances=5):
    """Benchmark on 500-node instances."""
    print("Benchmarking Christofides Adaptive Matching (v14) on 500-node instances")
    print("=" * 70)
    
    n = 500
    results = []
    
    for instance in range(num_instances):
        print(f"\nInstance {instance + 1}/{num_instances}")
        
        # Generate random points
        seed = instance
        points = generate_random_points(n, seed=seed)
        
        # Test v14 with different centrality weights
        best_length = float('inf')
        best_weight = 0.0
        best_runtime = 0.0
        
        centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        for weight in centrality_weights:
            solver = ChristofidesAdaptiveMatching(points, seed=seed)
            start_time = time.time()
            tour, length, _ = solver.solve(centrality_weight=weight, apply_2opt=True)
            runtime = time.time() - start_time
            
            if length < best_length:
                best_length = length
                best_weight = weight
                best_runtime = runtime
            
            print(f"  Weight {weight:.1f}: length={length:.4f}, time={runtime:.2f}s")
        
        # Also test standard Christofides (v2) for comparison
        christofides_solver = Christofides(points)
        start_time = time.time()
        christofides_tour, christofides_length = christofides_solver.solve()
        christofides_runtime = time.time() - start_time
        
        # Test NN+2opt baseline
        start_time = time.time()
        nn_tour = solve_nn_2opt(points)
        nn_runtime = time.time() - start_time
        nn_length = compute_tour_length(nn_tour, points)
        
        instance_result = {
            'instance': instance,
            'seed': seed,
            'v14_best_weight': best_weight,
            'v14_tour_length': best_length,
            'v14_runtime': best_runtime,
            'christofides_length': christofides_length,
            'christofides_runtime': christofides_runtime,
            'nn_2opt_length': nn_length,
            'nn_2opt_runtime': nn_runtime,
            'v14_vs_christofides_improvement': ((christofides_length - best_length) / christofides_length * 100) if christofides_length > 0 else 0,
            'v14_vs_nn_improvement': ((nn_length - best_length) / nn_length * 100) if nn_length > 0 else 0
        }
        
        results.append(instance_result)
        
        print(f"\n  Best v14 (weight={best_weight:.1f}): {best_length:.4f} ({best_runtime:.2f}s)")
        print(f"  Standard Christofides: {christofides_length:.4f} ({christofides_runtime:.2f}s)")
        print(f"  NN+2opt baseline: {nn_length:.4f} ({nn_runtime:.2f}s)")
        print(f"  Improvement vs Christofides: {instance_result['v14_vs_christofides_improvement']:.2f}%")
        print(f"  Improvement vs NN+2opt: {instance_result['v14_vs_nn_improvement']:.2f}%")
    
    # Calculate averages
    avg_v14_length = statistics.mean(r['v14_tour_length'] for r in results)
    avg_christofides_length = statistics.mean(r['christofides_length'] for r in results)
    avg_nn_length = statistics.mean(r['nn_2opt_length'] for r in results)
    
    avg_v14_runtime = statistics.mean(r['v14_runtime'] for r in results)
    avg_christofides_runtime = statistics.mean(r['christofides_runtime'] for r in results)
    avg_nn_runtime = statistics.mean(r['nn_2opt_runtime'] for r in results)
    
    overall_improvement_vs_christofides = ((avg_christofides_length - avg_v14_length) / avg_christofides_length * 100) if avg_christofides_length > 0 else 0
    overall_improvement_vs_nn = ((avg_nn_length - avg_v14_length) / avg_nn_length * 100) if avg_nn_length > 0 else 0
    
    summary = {
        'algorithm': 'tsp_v14_christofides_adaptive_matching',
        'n': n,
        'num_instances': num_instances,
        'average_v14_tour_length': avg_v14_length,
        'average_christofides_length': avg_christofides_length,
        'average_nn_2opt_length': avg_nn_length,
        'average_v14_runtime': avg_v14_runtime,
        'average_christofides_runtime': avg_christofides_runtime,
        'average_nn_2opt_runtime': avg_nn_runtime,
        'improvement_vs_christofides_percentage': overall_improvement_vs_christofides,
        'improvement_vs_nn_2opt_percentage': overall_improvement_vs_nn,
        'baseline_comparison': {
            'baseline_algorithm': 'nearest_neighbor_with_2opt',
            'baseline_length': avg_nn_length,
            'improvement_ratio': avg_nn_length / avg_v14_length if avg_v14_length > 0 else 1.0,
            'improvement_percentage': overall_improvement_vs_nn
        },
        'results': results
    }
    
    return summary

def main():
    """Main benchmark function."""
    print("v14 Christofides Adaptive Matching - 500-node Benchmark")
    print("=" * 70)
    
    # Run benchmark
    summary = benchmark_500_nodes(num_instances=3)  # Use 3 instances for speed
    
    # Save results
    output_file = 'christofides_adaptive_matching_500_benchmark.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Algorithm: {summary['algorithm']}")
    print(f"Problem size: n={summary['n']}")
    print(f"Number of instances: {summary['num_instances']}")
    print(f"\nAverage tour lengths:")
    print(f"  v14 Adaptive Matching: {summary['average_v14_tour_length']:.4f}")
    print(f"  Standard Christofides: {summary['average_christofides_length']:.4f}")
    print(f"  NN+2opt baseline: {summary['average_nn_2opt_length']:.4f}")
    print(f"\nImprovement vs baseline:")
    print(f"  vs NN+2opt: {summary['improvement_vs_nn_2opt_percentage']:.4f}%")
    print(f"  vs Standard Christofides: {summary['improvement_vs_christofides_percentage']:.4f}%")
    print(f"\nAverage runtimes:")
    print(f"  v14: {summary['average_v14_runtime']:.2f}s")
    print(f"  Christofides: {summary['average_christofides_runtime']:.2f}s")
    print(f"  NN+2opt: {summary['average_nn_2opt_runtime']:.2f}s")
    
    # Check against publication threshold
    baseline = 17.69  # NN+2opt baseline from previous benchmarks
    improvement_needed = 0.1  # 0.1% improvement needed for publication
    
    current_improvement = summary['improvement_vs_nn_2opt_percentage']
    if current_improvement > improvement_needed:
        print(f"\n✅ PUBLICATION POTENTIAL: Exceeds {improvement_needed}% threshold ({current_improvement:.4f}% improvement)")
    else:
        print(f"\n❌ BELOW PUBLICATION THRESHOLD: {current_improvement:.4f}% improvement < {improvement_needed}% required")
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()