#!/usr/bin/env python3
"""
Final comparison between optimized and original algorithms.
"""

import sys
import os
import random
import time
import numpy as np
sys.path.append('.')

from solutions.tsp_v19_optimized_fixed import ChristofidesHybridStructuralOptimized
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42):
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def run_comprehensive_comparison():
    """Run comprehensive comparison."""
    print("=== COMPREHENSIVE ALGORITHM COMPARISON ===\n")
    
    # Test sizes
    test_sizes = [50, 100, 150, 200]
    seeds = [42, 123, 456, 789, 999]
    threshold = 70.0
    
    results = []
    
    for n in test_sizes:
        print(f"\n{'='*60}")
        print(f"Testing n = {n}")
        print(f"{'='*60}")
        
        size_results = []
        
        for seed_idx, seed in enumerate(seeds):
            points = generate_random_points(n, seed=seed)
            
            # Run optimized algorithm
            start_time = time.time()
            solver_opt = ChristofidesHybridStructuralOptimized(points=points, seed=seed)
            tour_opt, length_opt = solver_opt.solve(percentile_threshold=threshold)
            opt_time = time.time() - start_time
            
            # Run original algorithm
            start_time = time.time()
            solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=seed)
            result_orig = solver_orig.solve(percentile_threshold=threshold)
            orig_time = time.time() - start_time
            
            # Extract original tour and length
            tour_orig, length_orig, _ = result_orig
            
            # Quality difference (positive = optimized is worse)
            quality_diff_pct = (length_opt - length_orig) / length_orig * 100
            
            # Speedup factor
            speedup = orig_time / opt_time if opt_time > 0 else float('inf')
            
            size_results.append({
                'seed': seed,
                'opt_length': length_opt,
                'orig_length': length_orig,
                'quality_diff_pct': quality_diff_pct,
                'opt_time': opt_time,
                'orig_time': orig_time,
                'speedup': speedup
            })
            
            print(f"  Seed {seed_idx+1}:")
            print(f"    Optimized: {length_opt:.2f} ({opt_time:.3f}s)")
            print(f"    Original:  {length_orig:.2f} ({orig_time:.3f}s)")
            print(f"    Quality:   {quality_diff_pct:+.1f}%")
            print(f"    Speedup:   {speedup:.1f}x")
        
        # Compute averages
        avg_quality_diff = np.mean([r['quality_diff_pct'] for r in size_results])
        avg_speedup = np.mean([r['speedup'] for r in size_results])
        avg_opt_time = np.mean([r['opt_time'] for r in size_results])
        avg_orig_time = np.mean([r['orig_time'] for r in size_results])
        
        print(f"\n  AVERAGES for n={n}:")
        print(f"    Quality difference: {avg_quality_diff:+.1f}%")
        print(f"    Speedup: {avg_speedup:.1f}x")
        print(f"    Optimized time: {avg_opt_time:.3f}s")
        print(f"    Original time: {avg_orig_time:.3f}s")
        
        results.append({
            'n': n,
            'avg_quality_diff': avg_quality_diff,
            'avg_speedup': avg_speedup,
            'avg_opt_time': avg_opt_time,
            'avg_orig_time': avg_orig_time
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for r in results:
        print(f"n={r['n']:3d}: {r['avg_speedup']:5.1f}x speedup, "
              f"quality {r['avg_quality_diff']:+5.1f}%, "
              f"time {r['avg_opt_time']:6.3f}s (orig {r['avg_orig_time']:6.3f}s)")
    
    # Project TSPLIB instances
    print(f"\n{'='*60}")
    print("PROJECTED TSPLIB PERFORMANCE")
    print(f"{'='*60}")
    
    # Fit power law to timing data
    n_vals = [r['n'] for r in results]
    t_vals = [r['avg_opt_time'] for r in results]
    
    # Log-log fit: t = a * n^b
    log_n = np.log(n_vals)
    log_t = np.log(t_vals)
    
    # Linear regression
    A = np.vstack([log_n, np.ones(len(log_n))]).T
    b, log_a = np.linalg.lstsq(A, log_t, rcond=None)[0]
    a = np.exp(log_a)
    
    print(f"Scaling law: time = {a:.6f} * n^{b:.3f}")
    
    # Project for TSPLIB instances
    tsplib_instances = [
        ('a280', 280),
        ('att532', 532),
        ('dsj1000', 1000)
    ]
    
    print("\nInstance projections:")
    for name, n in tsplib_instances:
        projected_time = a * (n ** b)
        print(f"  {name:10s} (n={n:4d}): {projected_time:7.2f}s")
    
    # Check against targets
    print("\nTarget compliance:")
    a280_time = a * (280 ** b)
    att532_time = a * (532 ** b)
    
    print(f"  a280:  {a280_time:6.2f}s vs target 30s → {'✓' if a280_time <= 30 else '✗'}")
    print(f"  att532: {att532_time:6.2f}s vs target 120s → {'✓' if att532_time <= 120 else '✗'}")

if __name__ == "__main__":
    run_comprehensive_comparison()
