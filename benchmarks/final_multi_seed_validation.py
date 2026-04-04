#!/usr/bin/env python3
"""
Final multi-seed validation for TSP algorithms.
Runs 10 seeds for n=30 (small enough for v8 to complete within reasonable time).
Includes statistical significance testing.
"""

import sys
import os
import time
import numpy as np
import math

# Add solutions directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'solutions'))

# Import algorithms
from tsp_v1_nearest_neighbor import solve_tsp as v1_nn_2opt
from tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_christofides_ils
from tsp_v19_christofides_hybrid_structural import solve_tsp as v19_hybrid

def generate_random_points(n, seed):
    """Generate n random points in unit square."""
    np.random.seed(seed)
    return np.random.rand(n, 2)

def euclidean_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_tour_length(points, tour):
    """Calculate total length of a tour."""
    total = 0.0
    n = len(points)
    
    # Handle both cycle format (n+1 vertices) and permutation format (n vertices)
    if len(tour) == n + 1 and tour[0] == tour[-1]:
        # Cycle format: remove duplicate end vertex
        tour_indices = tour[:-1]
    else:
        # Permutation format
        tour_indices = tour
    
    for i in range(len(tour_indices)):
        j = (i + 1) % len(tour_indices)
        total += euclidean_distance(points[tour_indices[i]], points[tour_indices[j]])
    
    return total

def run_single_experiment(n, seed, timeout=60):
    """Run all algorithms on a single problem instance."""
    points = generate_random_points(n, seed)
    
    results = {}
    
    # v1: Nearest Neighbor with 2-opt (correct baseline)
    start = time.time()
    v1_result = v1_nn_2opt(points)
    v1_time = time.time() - start
    # v1 returns (tour, distance) tuple
    v1_tour, v1_length = v1_result if isinstance(v1_result, tuple) else (v1_result, calculate_tour_length(points, v1_result))
    results['v1_nn_2opt'] = {'length': v1_length, 'time': v1_time}
    
    # v8: Christofides-ILS (slow but works)
    try:
        start = time.time()
        v8_result = v8_christofides_ils(points)
        v8_time = time.time() - start
        if v8_time > timeout:
            print(f"  v8 timed out after {v8_time:.1f}s")
            results['v8_christofides_ils'] = {'length': None, 'time': v8_time, 'status': 'timeout'}
        else:
            # v8 returns (tour, distance) tuple
            v8_tour, v8_length = v8_result if isinstance(v8_result, tuple) else (v8_result, calculate_tour_length(points, v8_result))
            results['v8_christofides_ils'] = {'length': v8_length, 'time': v8_time, 'status': 'success'}
    except Exception as e:
        print(f"  v8 failed: {e}")
        results['v8_christofides_ils'] = {'length': None, 'time': None, 'status': 'error'}
    
    # v19: Christofides Structural Hybrid
    start = time.time()
    v19_result = v19_hybrid(points)
    v19_time = time.time() - start
    # v19 returns (tour, distance) tuple
    v19_tour, v19_length = v19_result if isinstance(v19_result, tuple) else (v19_result, calculate_tour_length(points, v19_result))
    results['v19_hybrid'] = {'length': v19_length, 'time': v19_time, 'status': 'success'}
    
    return results

def calculate_improvement_percentage(baseline_length, algorithm_length):
    """Calculate percentage improvement (positive = better)."""
    if baseline_length is None or algorithm_length is None:
        return None
    return ((baseline_length - algorithm_length) / baseline_length) * 100

def main():
    print("=" * 80)
    print("FINAL MULTI-SEED VALIDATION FOR TSP ALGORITHMS")
    print("=" * 80)
    print("\nConfiguration:")
    print(f"  Problem size: n = 30")
    print(f"  Number of seeds: 10")
    print(f"  Baseline: v1_nn_2opt (Nearest Neighbor with 2-opt)")
    print(f"  Statistical test: Paired t-test (p < 0.05 for significance)")
    print()
    
    n = 30
    seeds = list(range(42, 52))  # 10 seeds: 42-51
    
    all_results = []
    v19_improvements = []
    v8_improvements = []
    
    for i, seed in enumerate(seeds):
        print(f"Seed {seed} ({i+1}/{len(seeds)}):")
        
        results = run_single_experiment(n, seed, timeout=10)
        all_results.append(results)
        
        # Calculate improvements vs v1 baseline (NN with 2-opt)
        baseline_length = results['v1_nn_2opt']['length']
        
        if results['v19_hybrid']['status'] == 'success':
            v19_improvement = calculate_improvement_percentage(baseline_length, results['v19_hybrid']['length'])
            v19_improvements.append(v19_improvement)
            print(f"  v19: {v19_improvement:+.2f}% improvement")
        
        if results['v8_christofides_ils'].get('status') == 'success':
            v8_improvement = calculate_improvement_percentage(baseline_length, results['v8_christofides_ils']['length'])
            v8_improvements.append(v8_improvement)
            print(f"  v8: {v8_improvement:+.2f}% improvement")
        
        print()
    
    # Statistical analysis
    print("\n" + "=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)
    
    # v19 analysis
    if len(v19_improvements) > 0:
        v19_mean = np.mean(v19_improvements)
        v19_std = np.std(v19_improvements)
        v19_wins = sum(1 for x in v19_improvements if x > 0)
        v19_losses = sum(1 for x in v19_improvements if x < 0)
        v19_ties = sum(1 for x in v19_improvements if x == 0)
        
        print(f"\nv19 Christofides Structural Hybrid (vs v1_nn_2opt):")
        print(f"  Mean improvement: {v19_mean:+.2f}%")
        print(f"  Std deviation: {v19_std:.2f}%")
        print(f"  Wins/Losses/Ties: {v19_wins}/{v19_losses}/{v19_ties}")
        print(f"  Win rate: {v19_wins/len(v19_improvements)*100:.1f}%")
        
        # Simple t-test calculation (one-sample)
        if len(v19_improvements) >= 2 and v19_std > 0:
            t_stat = (v19_mean - 0) / (v19_std / math.sqrt(len(v19_improvements)))
            # Approximate p-value using t-distribution (two-tailed)
            # For simplicity, we'll use a threshold approach
            degrees_of_freedom = len(v19_improvements) - 1
            # Critical t-value for 95% confidence (two-tailed)
            # For df=9 (10 samples), t_critical ≈ 2.262
            t_critical = 2.262  # for 10 samples, 95% confidence
            print(f"  t-statistic: {t_stat:.3f} (critical: {t_critical:.3f})")
            if abs(t_stat) > t_critical:
                print(f"  RESULT: Statistically significant (|t| > {t_critical:.3f})")
            else:
                print(f"  RESULT: NOT statistically significant (|t| ≤ {t_critical:.3f})")
    
    # v8 analysis
    if len(v8_improvements) > 0:
        v8_mean = np.mean(v8_improvements)
        v8_std = np.std(v8_improvements)
        v8_wins = sum(1 for x in v8_improvements if x > 0)
        v8_losses = sum(1 for x in v8_improvements if x < 0)
        v8_ties = sum(1 for x in v8_improvements if x == 0)
        
        print(f"\nv8 Christofides-ILS (vs v1_nn_2opt):")
        print(f"  Mean improvement: {v8_mean:+.2f}%")
        print(f"  Std deviation: {v8_std:.2f}%")
        print(f"  Wins/Losses/Ties: {v8_wins}/{v8_losses}/{v8_ties}")
        print(f"  Win rate: {v8_wins/len(v8_improvements)*100:.1f}%")
        
        # Simple t-test calculation (one-sample)
        if len(v8_improvements) >= 2 and v8_std > 0:
            t_stat = (v8_mean - 0) / (v8_std / math.sqrt(len(v8_improvements)))
            # Critical t-value for 95% confidence (two-tailed)
            t_critical = 2.262  # for 10 samples, 95% confidence
            print(f"  t-statistic: {t_stat:.3f} (critical: {t_critical:.3f})")
            if abs(t_stat) > t_critical:
                print(f"  RESULT: Statistically significant (|t| > {t_critical:.3f})")
            else:
                print(f"  RESULT: NOT statistically significant (|t| ≤ {t_critical:.3f})")
    
    # Save results to file
    output_file = "multi_seed_validation_results.txt"
    with open(output_file, 'w') as f:
        f.write("MULTI-SEED VALIDATION RESULTS\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Problem size: n = {n}\n")
        f.write(f"Seeds: {seeds}\n")
        f.write(f"Baseline: v1_nn_2opt (Nearest Neighbor with 2-opt)\n\n")
        
        f.write("v19 Christofides Structural Hybrid:\n")
        if len(v19_improvements) > 0:
            f.write(f"  Improvements: {v19_improvements}\n")
            f.write(f"  Mean: {v19_mean:+.2f}%\n")
            f.write(f"  Std: {v19_std:.2f}%\n")
            f.write(f"  Wins/Losses/Ties: {v19_wins}/{v19_losses}/{v19_ties}\n")
            if len(v19_improvements) >= 2 and v19_std > 0:
                t_stat = (v19_mean - 0) / (v19_std / math.sqrt(len(v19_improvements)))
                f.write(f"  t-statistic: {t_stat:.3f}\n")
        
        f.write("\nv8 Christofides-ILS:\n")
        if len(v8_improvements) > 0:
            f.write(f"  Improvements: {v8_improvements}\n")
            f.write(f"  Mean: {v8_mean:+.2f}%\n")
            f.write(f"  Std: {v8_std:.2f}%\n")
            f.write(f"  Wins/Losses/Ties: {v8_wins}/{v8_losses}/{v8_ties}\n")
            if len(v8_improvements) >= 2 and v8_std > 0:
                t_stat = (v8_mean - 0) / (v8_std / math.sqrt(len(v8_improvements)))
                f.write(f"  t-statistic: {t_stat:.3f}\n")
    
    print(f"\nResults saved to {output_file}")
    
    # Final assessment
    print("\n" + "=" * 80)
    print("FINAL ASSESSMENT")
    print("=" * 80)
    
    if len(v19_improvements) > 0:
        print(f"\nv19 Status:")
        if abs(v19_mean) < 0.1:
            print(f"  PERFORMANCE: No meaningful improvement ({v19_mean:+.2f}%)")
        elif v19_mean > 0:
            print(f"  PERFORMANCE: Positive improvement ({v19_mean:+.2f}%)")
        else:
            print(f"  PERFORMANCE: Negative impact ({v19_mean:+.2f}%)")
        
        if len(v19_improvements) >= 2 and v19_std > 0:
            t_stat = (v19_mean - 0) / (v19_std / math.sqrt(len(v19_improvements)))
            t_critical = 2.262
            if abs(t_stat) > t_critical:
                print(f"  STATISTICAL SIGNIFICANCE: YES (|t| = {abs(t_stat):.3f} > {t_critical:.3f})")
            else:
                print(f"  STATISTICAL SIGNIFICANCE: NO (|t| = {abs(t_stat):.3f} ≤ {t_critical:.3f})")
        else:
            print(f"  STATISTICAL SIGNIFICANCE: INSUFFICIENT DATA")
        
        # Novelty assessment (from Vera's review)
        print(f"  NOVELTY: CONFIRMED (structural analysis + ILS hybrid)")
        
        # Check statistical significance
        is_significant = False
        if len(v19_improvements) >= 2 and v19_std > 0:
            t_stat = (v19_mean - 0) / (v19_std / math.sqrt(len(v19_improvements)))
            t_critical = 2.262
            is_significant = abs(t_stat) > t_critical
        
        if v19_mean > 0.1 and is_significant:
            print(f"  OVERALL: POTENTIAL FOR PUBLICATION")
        else:
            print(f"  OVERALL: NOT PUBLICATION-READY (insufficient performance/significance)")
    
    print("\n" + "=" * 80)
    print("METHODOLOGICAL LESSONS LEARNED")
    print("=" * 80)
    print("1. Always compare against strongest available baseline (NN+2opt, not plain NN)")
    print("2. Use multiple random seeds (≥10) to avoid cherry-picking")
    print("3. Apply statistical significance tests (p < 0.05 threshold)")
    print("4. Report mean ± standard deviation, not single best results")
    print("5. Distinguish between performance (statistical significance) and novelty (literature review)")

if __name__ == "__main__":
    main()