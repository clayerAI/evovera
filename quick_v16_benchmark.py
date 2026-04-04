#!/usr/bin/env python3
"""
Quick benchmark for v16 to verify performance at n=500.
Uses fewer seeds but tests the critical n=500 case.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import numpy as np
import random
import time
from typing import List, Tuple
import json

def generate_random_points(n: int = 100, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_benchmark(n: int = 500, seeds: List[int] = None, num_seeds: int = 5):
    """Run benchmark with specified parameters."""
    if seeds is None:
        seeds = list(range(42, 42 + num_seeds))
    
    print(f"Running v16 benchmark (n={n}, seeds={seeds})")
    print("=" * 60)
    
    results = []
    
    for seed in seeds:
        print(f"\nSeed {seed}:")
        
        # Generate points
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Run NN+2opt baseline
        print("  Running NN+2opt...")
        start_time = time.time()
        nn2opt_tour, nn2opt_len = nn2opt_solve(points_array)
        nn2opt_time = time.time() - start_time
        
        # Run v16
        print("  Running v16...")
        start_time = time.time()
        v16_tour, v16_len = v16_solve(points, seed=seed)
        v16_time = time.time() - start_time
        
        # Calculate improvement
        improvement = ((nn2opt_len - v16_len) / nn2opt_len) * 100
        
        result = {
            'seed': seed,
            'n': n,
            'nn2opt_length': nn2opt_len,
            'nn2opt_time': nn2opt_time,
            'v16_length': v16_len,
            'v16_time': v16_time,
            'improvement': improvement,
            'beats_threshold': improvement > 0.1
        }
        results.append(result)
        
        print(f"  NN+2opt: {nn2opt_len:.4f} ({nn2opt_time:.2f}s)")
        print(f"  v16:     {v16_len:.4f} ({v16_time:.2f}s)")
        print(f"  Improvement: {improvement:.2f}%")
        
        if improvement > 0.1:
            print(f"  ✅ BEATS 0.1% novelty threshold")
        else:
            print(f"  ❌ Below 0.1% threshold")
    
    # Calculate statistics
    improvements = [r['improvement'] for r in results]
    avg_improvement = np.mean(improvements)
    std_improvement = np.std(improvements)
    positive_count = sum(1 for r in results if r['improvement'] > 0.1)
    
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY:")
    print(f"Problem size: n={n}")
    print(f"Number of seeds: {len(seeds)}")
    print(f"Average improvement: {avg_improvement:.2f}%")
    print(f"Standard deviation: {std_improvement:.2f}%")
    print(f"Seeds beating 0.1% threshold: {positive_count}/{len(seeds)}")
    
    if avg_improvement > 0.1:
        print("✅ v16 CONSISTENTLY BEATS 0.1% NOVELTY THRESHOLD!")
    else:
        print("❌ v16 does NOT consistently beat 0.1% threshold")
    
    # Save results
    output_data = {
        'benchmark_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'n': n,
        'seeds': seeds,
        'results': results,
        'statistics': {
            'avg_improvement': avg_improvement,
            'std_improvement': std_improvement,
            'positive_count': positive_count,
            'total_seeds': len(seeds)
        }
    }
    
    output_file = f"v16_benchmark_n{n}_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    return output_data

def main():
    # Run quick benchmark with n=500 (publication standard)
    print("V16 PERFORMANCE VALIDATION BENCHMARK")
    print("Testing at n=500 (publication standard)")
    print("=" * 60)
    
    # Use fewer seeds for quick test
    results = run_benchmark(n=500, seeds=[42, 43, 44], num_seeds=3)
    
    # Check if we should run more comprehensive test
    avg_imp = results['statistics']['avg_improvement']
    if avg_imp > 0.1:
        print(f"\n{'='*60}")
        print("INITIAL RESULTS PROMISING! Running additional validation...")
        
        # Run with 2 more seeds for better confidence
        additional_results = run_benchmark(n=500, seeds=[45, 46], num_seeds=2)
        
        # Combine results
        all_results = results['results'] + additional_results['results']
        all_improvements = [r['improvement'] for r in all_results]
        final_avg = np.mean(all_improvements)
        final_positive = sum(1 for r in all_results if r['improvement'] > 0.1)
        
        print(f"\n{'='*60}")
        print("FINAL VALIDATION (5 seeds total):")
        print(f"Average improvement: {final_avg:.2f}%")
        print(f"Seeds beating 0.1% threshold: {final_positive}/5")
        
        if final_avg > 0.1 and final_positive >= 4:
            print("✅ STRONG EVIDENCE: v16 consistently beats novelty threshold!")
        elif final_avg > 0.1:
            print("⚠️  MODERATE EVIDENCE: v16 beats threshold on average but inconsistent")
        else:
            print("❌ INSUFFICIENT EVIDENCE: v16 does not beat threshold")

if __name__ == "__main__":
    main()