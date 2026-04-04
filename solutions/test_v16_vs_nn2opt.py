#!/usr/bin/env python3
"""
Comprehensive test of v16 against NN+2opt baseline with multiple test scenarios.

Includes:
1. Standard benchmark (n=500) with consistent seeds for publication validation
2. Vera's test scenario (n=100) with her seeds for discrepancy investigation
3. Adaptive weight selection testing for optimization
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

def test_standard_benchmark(n: int = 500, seeds: List[int] = None):
    """Standard benchmark for publication validation (n=500)."""
    if seeds is None:
        seeds = [42, 43, 44, 45, 46]
    
    print(f"\n{'='*60}")
    print(f"STANDARD BENCHMARK (n={n})")
    print(f"Seeds: {seeds}")
    print(f"{'='*60}")
    
    nn2opt_results = []
    v16_results = []
    improvements = []
    
    for seed in seeds:
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Test NN+2opt
        start_time = time.time()
        nn2opt_tour, nn2opt_len = nn2opt_solve(points_array)
        nn2opt_time = time.time() - start_time
        
        # Test v16
        start_time = time.time()
        v16_tour, v16_len = v16_solve(points, seed=seed)
        v16_time = time.time() - start_time
        
        # Calculate improvement
        improvement = ((nn2opt_len - v16_len) / nn2opt_len) * 100
        
        nn2opt_results.append(nn2opt_len)
        v16_results.append(v16_len)
        improvements.append(improvement)
        
        print(f"\nSeed {seed}:")
        print(f"  NN+2opt: {nn2opt_len:.4f} ({nn2opt_time:.2f}s)")
        print(f"  v16:     {v16_len:.4f} ({v16_time:.2f}s)")
        print(f"  Improvement: {improvement:.2f}%")
        
        if improvement > 0.1:
            print(f"  ✅ BEATS 0.1% novelty threshold")
        else:
            print(f"  ❌ Below 0.1% threshold")
    
    # Calculate averages
    avg_nn2opt = np.mean(nn2opt_results)
    avg_v16 = np.mean(v16_results)
    avg_improvement = np.mean(improvements)
    
    print(f"\n{'='*60}")
    print("SUMMARY (Standard Benchmark):")
    print(f"Average NN+2opt: {avg_nn2opt:.4f}")
    print(f"Average v16:     {avg_v16:.4f}")
    print(f"Average Improvement: {avg_improvement:.2f}%")
    
    positive_count = sum(1 for imp in improvements if imp > 0.1)
    print(f"Seeds beating 0.1% threshold: {positive_count}/{len(seeds)}")
    
    if avg_improvement > 0.1:
        print("✅ v16 CONSISTENTLY BEATS 0.1% NOVELTY THRESHOLD!")
    else:
        print("❌ v16 does NOT consistently beat 0.1% threshold")
    
    return {
        'test_type': 'standard_benchmark',
        'n': n,
        'seeds': seeds,
        'nn2opt_results': nn2opt_results,
        'v16_results': v16_results,
        'improvements': improvements,
        'avg_nn2opt': avg_nn2opt,
        'avg_v16': avg_v16,
        'avg_improvement': avg_improvement,
        'positive_count': positive_count
    }

def test_vera_scenario(n: int = 100, seeds: List[int] = None):
    """Test Vera's scenario for discrepancy investigation."""
    if seeds is None:
        seeds = [42, 123, 456, 789, 999]
    
    print(f"\n{'='*60}")
    print(f"VERA'S SCENARIO (n={n})")
    print(f"Seeds: {seeds}")
    print(f"{'='*60}")
    
    results = []
    
    for seed in seeds:
        points = generate_random_points(n=n, seed=seed)
        
        # NN+2opt baseline
        baseline_tour, baseline_length = nn2opt_solve(points)
        
        # v16
        v16_tour, v16_length = v16_solve(points, seed=seed)
        
        # Calculate improvement
        improvement = (baseline_length - v16_length) / baseline_length * 100
        
        result = {
            'seed': seed,
            'baseline_length': baseline_length,
            'v16_length': v16_length,
            'improvement': improvement
        }
        results.append(result)
        
        print(f"\nSeed {seed}:")
        print(f"  NN+2opt: {baseline_length:.4f}")
        print(f"  v16:     {v16_length:.4f}")
        print(f"  Improvement: {improvement:.2f}%")
        
        if improvement > 0:
            print(f"  ✅ v16 better than NN+2opt")
        else:
            print(f"  ❌ v16 worse than NN+2opt")
    
    # Summary
    avg_baseline = sum(r['baseline_length'] for r in results) / len(results)
    avg_v16 = sum(r['v16_length'] for r in results) / len(results)
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    
    print(f"\n{'='*60}")
    print("SUMMARY (Vera's Scenario):")
    print(f"Average NN+2opt: {avg_baseline:.4f}")
    print(f"Average v16:     {avg_v16:.4f}")
    print(f"Average improvement: {avg_improvement:.2f}%")
    
    positive_count = sum(1 for r in results if r['improvement'] > 0)
    print(f"Positive improvements: {positive_count}/{len(seeds)}")
    
    # Compare with Vera's reported results
    print(f"\n{'='*60}")
    print("COMPARISON WITH VERA'S REPORTED RESULTS:")
    print("Seed | My Improvement | Vera's Reported | Match?")
    print("-" * 60)
    
    vera_results = {
        42: 1.61,
        123: -1.24,
        456: 1.21,
        789: -0.39,
        999: 6.60
    }
    
    matches = 0
    for r in results:
        seed = r['seed']
        my_imp = r['improvement']
        vera_imp = vera_results.get(seed, 0)
        
        # Check if sign matches (positive/negative)
        sign_match = (my_imp > 0 and vera_imp > 0) or (my_imp <= 0 and vera_imp <= 0)
        
        if sign_match:
            matches += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{seed:4d} | {my_imp:6.2f}% | {vera_imp:6.2f}% | {status}")
    
    print(f"\nSign matches: {matches}/{len(seeds)}")
    
    return {
        'test_type': 'vera_scenario',
        'n': n,
        'seeds': seeds,
        'results': results,
        'avg_baseline': avg_baseline,
        'avg_v16': avg_v16,
        'avg_improvement': avg_improvement,
        'positive_count': positive_count,
        'sign_matches': matches
    }

def test_adaptive_weights(n: int = 100, seed: int = 42):
    """Test adaptive weight selection in v16."""
    print(f"\n{'='*60}")
    print(f"ADAPTIVE WEIGHT SELECTION TEST (n={n}, seed={seed})")
    print(f"{'='*60}")
    
    points = generate_random_points(n=n, seed=seed)
    
    # Test with different weight parameters
    weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    baseline_tour, baseline_length = nn2opt_solve(points)
    
    results = []
    for weight in weights:
        # v16 with specific weight
        v16_tour, v16_length = v16_solve(points, seed=seed, centrality_weight=weight)
        
        improvement = (baseline_length - v16_length) / baseline_length * 100
        
        results.append({
            'weight': weight,
            'v16_length': v16_length,
            'improvement': improvement
        })
    
    # Find best weight
    best_result = max(results, key=lambda x: x['improvement'])
    
    print(f"Baseline (NN+2opt): {baseline_length:.4f}")
    print(f"\nWeight | v16 Length | Improvement")
    print("-" * 40)
    
    for r in results:
        print(f"{r['weight']:6.1f} | {r['v16_length']:10.4f} | {r['improvement']:8.2f}%", end="")
        if r['weight'] == best_result['weight']:
            print(" ⭐ BEST")
        else:
            print()
    
    print(f"\nBest weight: {best_result['weight']}")
    print(f"Best improvement: {best_result['improvement']:.2f}%")
    
    return {
        'test_type': 'adaptive_weights',
        'n': n,
        'seed': seed,
        'baseline_length': baseline_length,
        'results': results,
        'best_weight': best_result['weight'],
        'best_improvement': best_result['improvement']
    }

def main():
    print("COMPREHENSIVE v16 vs NN+2opt BENCHMARK SUITE")
    print("=" * 60)
    
    all_results = {}
    
    # Run standard benchmark (n=500)
    standard_result = test_standard_benchmark(n=500, seeds=[42, 43, 44, 45, 46])
    all_results['standard_benchmark'] = standard_result
    
    # Run Vera's scenario (n=100)
    vera_result = test_vera_scenario(n=100, seeds=[42, 123, 456, 789, 999])
    all_results['vera_scenario'] = vera_result
    
    # Test adaptive weights
    adaptive_result = test_adaptive_weights(n=100, seed=42)
    all_results['adaptive_weights'] = adaptive_result
    
    # Save results
    output_file = "v16_comprehensive_benchmark_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Results saved to {output_file}")
    
    # Final assessment
    print(f"\n{'='*60}")
    print("FINAL ASSESSMENT:")
    
    standard_imp = standard_result['avg_improvement']
    vera_imp = vera_result['avg_improvement']
    
    print(f"Standard benchmark (n=500): {standard_imp:.2f}% improvement")
    print(f"Vera's scenario (n=100): {vera_imp:.2f}% improvement")
    
    if standard_imp > 0.1:
        print("✅ v16 EXCEEDS 0.1% NOVELTY THRESHOLD at n=500 (publication standard)")
    else:
        print("❌ v16 does NOT exceed 0.1% threshold at n=500")
    
    if vera_result['sign_matches'] >= 4:
        print("✅ Results consistent with Vera's analysis")
    else:
        print("⚠️  Discrepancy with Vera's analysis detected")

if __name__ == "__main__":
    main()