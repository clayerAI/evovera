#!/usr/bin/env python3
"""
Quick benchmark for v14 Christofides Adaptive Matching
Tests key configurations to verify the 1.32% improvement claim
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching
import json
import time
import statistics
import math
import random

def generate_random_points(n, seed=42):
    """Generate n random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_quick_benchmark():
    """Run quick benchmark focusing on 500-node instances."""
    print("QUICK BENCHMARK: v14 Christofides Adaptive Matching")
    print("Verifying 1.32% improvement claim")
    print("=" * 70)
    
    # Focus on 500 nodes (same as original claim)
    size = 500
    centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    num_instances = 3
    n_trials = 2  # Fewer trials for speed
    
    results = {
        'algorithm': 'tsp_v14_christofides_adaptive_matching',
        'size': size,
        'benchmark_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'instances': []
    }
    
    print(f"\nBenchmarking {size}-node instances")
    print(f"Testing weights: {centrality_weights}")
    print(f"Instances: {num_instances}, Trials per weight: {n_trials}")
    print("-" * 50)
    
    for instance in range(num_instances):
        print(f"\nInstance {instance + 1}/{num_instances}")
        seed = instance * 100
        
        # Generate points
        points = generate_random_points(size, seed=seed)
        
        # Test all centrality weights
        weight_results = {}
        
        for weight in centrality_weights:
            lengths = []
            runtimes = []
            
            for trial in range(n_trials):
                trial_seed = seed + trial * 10
                random.seed(trial_seed)
                
                start_time = time.time()
                solver = ChristofidesAdaptiveMatching(points, seed=trial_seed)
                tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
                runtimes.append(runtime)
                lengths.append(length)
            
            weight_results[weight] = {
                'avg_length': statistics.mean(lengths),
                'avg_runtime': statistics.mean(runtimes),
                'lengths': lengths,
                'runtimes': runtimes
            }
            
            print(f"  Weight {weight:.1f}: length={weight_results[weight]['avg_length']:.4f}, "
                  f"time={weight_results[weight]['avg_runtime']:.2f}s")
        
        # Find best weight
        best_weight = min(weight_results.keys(), 
                         key=lambda w: weight_results[w]['avg_length'])
        best_result = weight_results[best_weight]
        
        # Calculate improvement vs weight=0
        baseline_result = weight_results[0.0]
        improvement = ((baseline_result['avg_length'] - best_result['avg_length']) / 
                      baseline_result['avg_length'] * 100)
        
        instance_data = {
            'instance_id': instance,
            'seed': seed,
            'weight_results': weight_results,
            'best_weight': best_weight,
            'best_length': best_result['avg_length'],
            'baseline_length': baseline_result['avg_length'],
            'improvement_percent': improvement
        }
        
        results['instances'].append(instance_data)
        
        print(f"  → Best weight: {best_weight}")
        print(f"  → Best length: {best_result['avg_length']:.4f}")
        print(f"  → Baseline (weight=0): {baseline_result['avg_length']:.4f}")
        print(f"  → Improvement: {improvement:.3f}%")
    
    # Calculate overall statistics
    improvements = [inst['improvement_percent'] for inst in results['instances']]
    avg_improvement = statistics.mean(improvements)
    
    # Weight effectiveness
    weight_wins = {}
    for inst in results['instances']:
        weight = inst['best_weight']
        weight_wins[weight] = weight_wins.get(weight, 0) + 1
    
    results['summary'] = {
        'avg_improvement_percent': avg_improvement,
        'min_improvement_percent': min(improvements),
        'max_improvement_percent': max(improvements),
        'weight_wins': weight_wins,
        'most_effective_weight': max(weight_wins.items(), key=lambda x: x[1])[0] if weight_wins else 0.0
    }
    
    # Save results
    output_file = f"v14_quick_benchmark_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("BENCHMARK SUMMARY")
    print("="*70)
    print(f"Average improvement: {avg_improvement:.3f}%")
    print(f"Improvement range: [{min(improvements):.3f}%, {max(improvements):.3f}%]")
    print(f"Most effective weight: {results['summary']['most_effective_weight']}")
    print(f"Weight wins: {weight_wins}")
    
    # Compare with claimed 1.32% improvement
    print(f"\n{'='*70}")
    print("VERIFICATION OF CLAIM")
    print("="*70)
    print(f"Claimed improvement: 1.32%")
    print(f"Measured average: {avg_improvement:.3f}%")
    
    if abs(avg_improvement - 1.32) < 0.1:
        print("✓ Measurement confirms claimed improvement (within 0.1%)")
    elif avg_improvement > 1.32:
        print(f"✓ Measurement exceeds claimed improvement by {avg_improvement - 1.32:.3f}%")
    else:
        print(f"✗ Measurement is {1.32 - avg_improvement:.3f}% below claimed improvement")
    
    # Check publication threshold
    print(f"\nPublication threshold: 0.1%")
    if avg_improvement > 0.1:
        print(f"✓ EXCEEDS publication threshold by {avg_improvement - 0.1:.3f}%")
    else:
        print(f"✗ Below publication threshold by {0.1 - avg_improvement:.3f}%")
    
    print(f"\nResults saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    print("Starting quick benchmark for v14...")
    start_time = time.time()
    
    try:
        results = run_quick_benchmark()
        total_time = time.time() - start_time
        print(f"\nTotal benchmark time: {total_time:.1f} seconds")
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()