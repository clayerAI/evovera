#!/usr/bin/env python3
"""
Benchmark script for NN+2opt with ILS Adaptive Memory hybrid algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import json
from typing import Dict, List
from solutions.tsp_v11_nn_ils_adaptive_memory import solve_tsp_nn_ils_adaptive_memory
from solutions.tsp_v1_nearest_neighbor import solve_tsp as solve_tsp_nn_2opt

def generate_random_instance(n: int, seed: int = None) -> np.ndarray:
    """Generate random TSP instance"""
    if seed is not None:
        np.random.seed(seed)
    return np.random.rand(n, 2) * 100

def benchmark_instance(n: int, instance_id: int = 0) -> Dict:
    """Benchmark algorithm on a single instance"""
    # Generate instance
    points = generate_random_instance(n, seed=42 + instance_id)
    
    # Run baseline (NN+2opt)
    start_time = time.time()
    baseline_tour = solve_tsp_nn_2opt(points)
    baseline_length = 0.0
    for i in range(len(baseline_tour)):
        j = (i + 1) % len(baseline_tour)
        baseline_length += np.sqrt(np.sum((points[baseline_tour[i]] - points[baseline_tour[j]]) ** 2))
    baseline_time = time.time() - start_time
    
    # Run hybrid algorithm
    start_time = time.time()
    hybrid_tour, hybrid_length, stats = solve_tsp_nn_ils_adaptive_memory(
        points, 
        max_iterations=1000,
        max_no_improve=100
    )
    hybrid_time = time.time() - start_time
    
    # Calculate improvement
    improvement = (baseline_length - hybrid_length) / baseline_length * 100 if baseline_length > 0 else 0
    
    return {
        'n': n,
        'instance_id': instance_id,
        'baseline_length': baseline_length,
        'hybrid_length': hybrid_length,
        'improvement_percent': improvement,
        'baseline_time': baseline_time,
        'hybrid_time': hybrid_time,
        'stats': stats
    }

def run_benchmark_suite() -> List[Dict]:
    """Run benchmark on multiple instance sizes"""
    instance_sizes = [20, 50, 100, 200, 500]
    num_trials = 3
    
    results = []
    
    for n in instance_sizes:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n} (averaging over {num_trials} trials)")
        print(f"{'='*60}")
        
        trial_results = []
        for trial in range(num_trials):
            print(f"  Trial {trial+1}/{num_trials}...", end="", flush=True)
            result = benchmark_instance(n, instance_id=trial)
            trial_results.append(result)
            print(f" done. Improvement: {result['improvement_percent']:.3f}%")
        
        # Calculate averages
        avg_improvement = np.mean([r['improvement_percent'] for r in trial_results])
        avg_baseline_time = np.mean([r['baseline_time'] for r in trial_results])
        avg_hybrid_time = np.mean([r['hybrid_time'] for r in trial_results])
        
        summary = {
            'n': n,
            'num_trials': num_trials,
            'avg_improvement_percent': float(avg_improvement),
            'avg_baseline_time': float(avg_baseline_time),
            'avg_hybrid_time': float(avg_hybrid_time),
            'trial_results': trial_results
        }
        
        results.append(summary)
        
        print(f"\n  Summary for n={n}:")
        print(f"    Average improvement: {avg_improvement:.3f}%")
        print(f"    Baseline time: {avg_baseline_time:.3f}s")
        print(f"    Hybrid time: {avg_hybrid_time:.3f}s")
        print(f"    Speed ratio: {avg_hybrid_time/avg_baseline_time:.2f}x")
    
    return results

def main():
    """Main benchmark function"""
    print("=" * 70)
    print("BENCHMARK: NN+2opt with ILS Adaptive Memory Hybrid Algorithm")
    print("=" * 70)
    print("\nAlgorithm: TSP Hybrid v11 - NN+2opt with ILS Adaptive Memory")
    print("Baseline: Standard NN+2opt (tsp_v1_nearest_neighbor.py)")
    print("\nKey features:")
    print("  • Starts with high-quality NN+2opt solution")
    print("  • Adaptive memory tracks effective perturbation strengths")
    print("  • Dynamic restart based on improvement rate")
    print("  • Quality-based perturbation adjustment")
    
    # Run benchmarks
    results = run_benchmark_suite()
    
    # Save results
    output_file = "nn_ils_adaptive_memory_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*70}")
    
    # Overall summary
    print("\nOVERALL SUMMARY:")
    print("-" * 40)
    
    for result in results:
        n = result['n']
        improvement = result['avg_improvement_percent']
        baseline_time = result['avg_baseline_time']
        hybrid_time = result['avg_hybrid_time']
        
        print(f"n={n:3d}: {improvement:6.3f}% improvement | "
              f"Baseline: {baseline_time:5.3f}s | "
              f"Hybrid: {hybrid_time:5.3f}s | "
              f"Ratio: {hybrid_time/baseline_time:5.2f}x")
    
    # Check if any improvement exceeds 0.1% threshold
    significant_improvements = [r for r in results if r['avg_improvement_percent'] > 0.1]
    
    print(f"\nSignificant improvements (>0.1%): {len(significant_improvements)}/{len(results)}")
    
    if significant_improvements:
        print("✓ Algorithm shows promising results for publication consideration")
    else:
        print("⚠ Algorithm needs further optimization to exceed 0.1% threshold")
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()