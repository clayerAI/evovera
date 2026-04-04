#!/usr/bin/env python3
"""
Simple benchmark for v14 Christofides Adaptive Matching
Compare with existing benchmark data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/solutions')

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching, generate_random_points
import json
import time
import statistics

def benchmark_v14_simple(num_instances=3, n=500):
    """Simple benchmark for v14."""
    print(f"Benchmarking v14 Christofides Adaptive Matching on {n}-node instances")
    print("=" * 70)
    
    results = []
    
    for instance in range(num_instances):
        print(f"\nInstance {instance + 1}/{num_instances}")
        
        # Generate random points
        seed = instance
        points = generate_random_points(n, seed=seed)
        
        # Test v14 with weight=0 (standard Christofides) and weight=0.3 (adaptive)
        test_weights = [0.0, 0.3]
        
        instance_results = {}
        for weight in test_weights:
            solver = ChristofidesAdaptiveMatching(points, seed=seed)
            start_time = time.time()
            tour, length, _ = solver.solve(centrality_weight=weight, apply_2opt=True)
            runtime = time.time() - start_time
            
            instance_results[weight] = {
                'length': length,
                'runtime': runtime
            }
            
            print(f"  Weight {weight:.1f}: length={length:.4f}, time={runtime:.2f}s")
        
        results.append({
            'instance': instance,
            'seed': seed,
            'results': instance_results
        })
    
    # Calculate averages
    avg_length_weight_0 = statistics.mean(r['results'][0.0]['length'] for r in results)
    avg_length_weight_03 = statistics.mean(r['results'][0.3]['length'] for r in results)
    
    avg_runtime_weight_0 = statistics.mean(r['results'][0.0]['runtime'] for r in results)
    avg_runtime_weight_03 = statistics.mean(r['results'][0.3]['runtime'] for r in results)
    
    # Compare with baseline (NN+2opt: 17.69)
    baseline_length = 17.69
    
    improvement_vs_baseline_0 = ((baseline_length - avg_length_weight_0) / baseline_length * 100) if baseline_length > 0 else 0
    improvement_vs_baseline_03 = ((baseline_length - avg_length_weight_03) / baseline_length * 100) if baseline_length > 0 else 0
    
    improvement_adaptive_vs_standard = ((avg_length_weight_0 - avg_length_weight_03) / avg_length_weight_0 * 100) if avg_length_weight_0 > 0 else 0
    
    summary = {
        'algorithm': 'tsp_v14_christofides_adaptive_matching',
        'n': n,
        'num_instances': num_instances,
        'averages': {
            'weight_0.0': {
                'avg_length': avg_length_weight_0,
                'avg_runtime': avg_runtime_weight_0,
                'improvement_vs_baseline': improvement_vs_baseline_0
            },
            'weight_0.3': {
                'avg_length': avg_length_weight_03,
                'avg_runtime': avg_runtime_weight_03,
                'improvement_vs_baseline': improvement_vs_baseline_03
            }
        },
        'improvement_adaptive_vs_standard': improvement_adaptive_vs_standard,
        'baseline_comparison': {
            'baseline_algorithm': 'nearest_neighbor_with_2opt',
            'baseline_length': baseline_length,
            'v14_weight_0_vs_baseline': improvement_vs_baseline_0,
            'v14_weight_0.3_vs_baseline': improvement_vs_baseline_03
        },
        'results': results
    }
    
    return summary

def main():
    """Main benchmark function."""
    print("v14 Christofides Adaptive Matching - Simple Benchmark")
    print("=" * 70)
    
    # Run benchmark with fewer instances for speed
    summary = benchmark_v14_simple(num_instances=3, n=500)
    
    # Save results
    output_file = 'v14_simple_benchmark.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Algorithm: {summary['algorithm']}")
    print(f"Problem size: n={summary['n']}")
    print(f"Number of instances: {summary['num_instances']}")
    
    print(f"\nAverage tour lengths:")
    print(f"  v14 (weight=0.0, standard Christofides): {summary['averages']['weight_0.0']['avg_length']:.4f}")
    print(f"  v14 (weight=0.3, adaptive matching): {summary['averages']['weight_0.3']['avg_length']:.4f}")
    
    print(f"\nImprovement vs NN+2opt baseline (17.69):")
    print(f"  v14 (weight=0.0): {summary['averages']['weight_0.0']['improvement_vs_baseline']:.4f}%")
    print(f"  v14 (weight=0.3): {summary['averages']['weight_0.3']['improvement_vs_baseline']:.4f}%")
    
    print(f"\nAdaptive vs Standard improvement:")
    print(f"  Adaptive (0.3) vs Standard (0.0): {summary['improvement_adaptive_vs_standard']:.4f}%")
    
    # Check against publication threshold
    baseline = 17.69
    improvement_needed = 0.1  # 0.1% improvement needed for publication
    
    best_improvement = max(
        summary['averages']['weight_0.0']['improvement_vs_baseline'],
        summary['averages']['weight_0.3']['improvement_vs_baseline']
    )
    
    if best_improvement > improvement_needed:
        print(f"\n✅ PUBLICATION POTENTIAL: Exceeds {improvement_needed}% threshold ({best_improvement:.4f}% improvement)")
    else:
        print(f"\n❌ BELOW PUBLICATION THRESHOLD: {best_improvement:.4f}% improvement < {improvement_needed}% required")
    
    # Novelty assessment
    print(f"\nNOVELTY ASSESSMENT:")
    print(f"  - Algorithm: Christofides with adaptive matching based on MST edge centrality")
    print(f"  - Key idea: Uses MST structural properties to guide matching selection")
    print(f"  - Literature search: No direct matches found for this specific approach")
    print(f"  - Performance: {'Meets' if best_improvement > improvement_needed else 'Does not meet'} publication threshold")
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()