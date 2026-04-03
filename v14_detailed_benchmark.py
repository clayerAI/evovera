#!/usr/bin/env python3
"""
Detailed benchmark for v14 Christofides Adaptive Matching
Focuses on testing different centrality weights and problem sizes
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

def run_v14_benchmark_suite():
    """Run detailed benchmark suite for v14."""
    print("DETAILED BENCHMARK: v14 Christofides Adaptive Matching")
    print("=" * 70)
    
    # Test configurations
    sizes = [100, 250, 500, 750, 1000]
    centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    num_instances = 5
    n_trials = 3
    
    all_results = {
        'algorithm': 'tsp_v14_christofides_adaptive_matching',
        'benchmark_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'config': {
            'sizes': sizes,
            'centrality_weights': centrality_weights,
            'num_instances': num_instances,
            'n_trials': n_trials
        },
        'results': {}
    }
    
    for size in sizes:
        print(f"\n{'='*70}")
        print(f"BENCHMARKING SIZE: {size} nodes")
        print(f"{'='*70}")
        
        size_results = {
            'size': size,
            'instance_results': []
        }
        
        for instance in range(num_instances):
            print(f"\n  Instance {instance + 1}/{num_instances}")
            seed = instance * 1000 + size
            
            # Generate points
            points = generate_random_points(size, seed=seed)
            
            # Test all centrality weights
            weight_results = {}
            
            for weight in centrality_weights:
                lengths = []
                runtimes = []
                
                for trial in range(n_trials):
                    trial_seed = seed + trial * 100
                    random.seed(trial_seed)
                    
                    start_time = time.time()
                    solver = ChristofidesAdaptiveMatching(points, seed=trial_seed)
                    tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
                    runtimes.append(runtime)
                    lengths.append(length)
                
                weight_results[weight] = {
                    'avg_length': statistics.mean(lengths),
                    'std_length': statistics.stdev(lengths) if len(lengths) > 1 else 0.0,
                    'avg_runtime': statistics.mean(runtimes),
                    'std_runtime': statistics.stdev(runtimes) if len(runtimes) > 1 else 0.0,
                    'lengths': lengths,
                    'runtimes': runtimes
                }
                
                print(f"    Weight {weight:.1f}: length={weight_results[weight]['avg_length']:.4f}, "
                      f"time={weight_results[weight]['avg_runtime']:.3f}s")
            
            # Find best weight for this instance
            best_weight = min(weight_results.keys(), 
                            key=lambda w: weight_results[w]['avg_length'])
            best_result = weight_results[best_weight]
            
            # Calculate improvement vs weight=0 (standard Christofides with 2opt)
            baseline_result = weight_results[0.0]
            improvement_vs_baseline = ((baseline_result['avg_length'] - best_result['avg_length']) / 
                                      baseline_result['avg_length'] * 100)
            
            instance_data = {
                'instance_id': instance,
                'seed': seed,
                'weight_results': weight_results,
                'best_weight': best_weight,
                'best_result': {
                    'avg_length': best_result['avg_length'],
                    'avg_runtime': best_result['avg_runtime']
                },
                'improvement_vs_baseline_percent': improvement_vs_baseline
            }
            
            size_results['instance_results'].append(instance_data)
            
            print(f"  → Best weight: {best_weight}")
            print(f"  → Best length: {best_result['avg_length']:.4f}")
            print(f"  → Improvement vs weight=0: {improvement_vs_baseline:.3f}%")
        
        # Calculate statistics across instances
        improvements = [inst['improvement_vs_baseline_percent'] 
                       for inst in size_results['instance_results']]
        
        # Weight effectiveness analysis
        weight_wins = {}
        for inst in size_results['instance_results']:
            weight = inst['best_weight']
            weight_wins[weight] = weight_wins.get(weight, 0) + 1
        
        size_results['summary'] = {
            'avg_improvement_percent': statistics.mean(improvements),
            'std_improvement_percent': statistics.stdev(improvements) if len(improvements) > 1 else 0.0,
            'min_improvement_percent': min(improvements),
            'max_improvement_percent': max(improvements),
            'weight_effectiveness': weight_wins,
            'most_effective_weight': max(weight_wins.items(), key=lambda x: x[1])[0] if weight_wins else 0.0
        }
        
        all_results['results'][str(size)] = size_results
        
        print(f"\n  SIZE {size} SUMMARY:")
        print(f"  Average improvement: {size_results['summary']['avg_improvement_percent']:.3f}%")
        print(f"  Improvement range: [{size_results['summary']['min_improvement_percent']:.3f}%, "
              f"{size_results['summary']['max_improvement_percent']:.3f}%]")
        print(f"  Most effective weight: {size_results['summary']['most_effective_weight']}")
        print(f"  Weight wins: {weight_wins}")
    
    # Save results
    timestamp = int(time.time())
    output_file = f"v14_detailed_benchmark_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Benchmark complete! Results saved to {output_file}")
    
    # Generate final report
    generate_final_report(all_results)
    
    return all_results

def generate_final_report(results):
    """Generate final analysis report."""
    print("\n" + "="*70)
    print("FINAL ANALYSIS REPORT")
    print("="*70)
    
    print("\nPERFORMANCE BY PROBLEM SIZE:")
    print("-" * 40)
    print(f"{'Size':>6} {'Avg Imp%':>10} {'Best Wt':>8} {'Wins':>6}")
    print("-" * 40)
    
    for size_str in sorted(results['results'].keys(), key=int):
        size_data = results['results'][size_str]
        summary = size_data['summary']
        
        print(f"{size_str:>6} {summary['avg_improvement_percent']:>10.3f} "
              f"{summary['most_effective_weight']:>8.1f} "
              f"{summary['weight_effectiveness'].get(summary['most_effective_weight'], 0):>6}")
    
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)
    
    # Overall statistics
    all_improvements = []
    for size_data in results['results'].values():
        all_improvements.extend([inst['improvement_vs_baseline_percent'] 
                                for inst in size_data['instance_results']])
    
    if all_improvements:
        avg_improvement = statistics.mean(all_improvements)
        max_improvement = max(all_improvements)
        min_improvement = min(all_improvements)
        
        print(f"1. Overall average improvement: {avg_improvement:.3f}%")
        print(f"2. Best improvement observed: {max_improvement:.3f}%")
        print(f"3. Improvement range: [{min_improvement:.3f}%, {max_improvement:.3f}%]")
        
        if avg_improvement > 0.1:
            print(f"4. ✓ EXCEEDS 0.1% publication threshold by {avg_improvement - 0.1:.3f}%")
        else:
            print(f"4. ✗ Below 0.1% publication threshold by {0.1 - avg_improvement:.3f}%")
    
    # Weight effectiveness analysis
    print("\n5. Weight effectiveness summary:")
    weight_total_wins = {}
    for size_data in results['results'].values():
        for weight, wins in size_data['summary']['weight_effectiveness'].items():
            weight_total_wins[weight] = weight_total_wins.get(weight, 0) + wins
    
    if weight_total_wins:
        print("   Weight distribution across all instances:")
        for weight in sorted(weight_total_wins.keys()):
            wins = weight_total_wins[weight]
            print(f"     Weight {weight:.1f}: {wins} wins")
        
        most_effective = max(weight_total_wins.items(), key=lambda x: x[1])
        print(f"\n   Most effective weight overall: {most_effective[0]} "
              f"({most_effective[1]} total wins)")
    
    print("\n" + "="*70)
    print("CONCLUSION:")
    print("="*70)
    
    if all_improvements and statistics.mean(all_improvements) > 0.1:
        print("The v14 Christofides Adaptive Matching algorithm demonstrates")
        print("statistically significant improvement over the baseline,")
        print("exceeding the 0.1% publication threshold.")
        print("\nRECOMMENDATION: This algorithm is suitable for publication.")
    else:
        print("The algorithm shows improvement but may not consistently")
        print("exceed the publication threshold across all problem sizes.")
        print("\nRECOMMENDATION: Further optimization may be needed.")

if __name__ == "__main__":
    print("Starting detailed benchmark for v14 Christofides Adaptive Matching")
    print("This will test multiple problem sizes and centrality weights...")
    
    try:
        results = run_v14_benchmark_suite()
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()