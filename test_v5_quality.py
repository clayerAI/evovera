#!/usr/bin/env python3
"""Test v5 optimized algorithm with 2-opt against original."""

import sys
sys.path.append(".")

import random
import time
from typing import List, Tuple
import numpy as np

# Import both algorithms
from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp as original_solve
from solutions.tsp_v19_optimized_fixed_v5 import solve_tsp as optimized_solve

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points."""
    random.seed(seed)
    return [(random.random() * 100, random.random() * 100) for _ in range(n)]

def test_quality_comparison():
    """Compare quality between original and optimized algorithms."""
    sizes = [20, 50, 100]
    seeds = [42, 123, 456, 789, 999]
    
    results = []
    
    for n in sizes:
        for seed in seeds:
            points = generate_random_points(n, seed)
            
            # Run original
            start = time.time()
            orig_tour, orig_length = original_solve(points, seed=seed)
            orig_time = time.time() - start
            
            # Run optimized
            start = time.time()
            opt_tour, opt_length = optimized_solve(points, seed=seed)
            opt_time = time.time() - start
            
            # Calculate improvement/deterioration
            if orig_length > 0:
                pct_diff = (opt_length - orig_length) / orig_length * 100
            else:
                pct_diff = 0.0
            
            results.append({
                'n': n,
                'seed': seed,
                'orig_length': orig_length,
                'opt_length': opt_length,
                'pct_diff': pct_diff,
                'orig_time': orig_time,
                'opt_time': opt_time,
                'speedup': orig_time / opt_time if opt_time > 0 else 0.0
            })
            
            print(f"n={n}, seed={seed}: "
                  f"orig={orig_length:.2f}, opt={opt_length:.2f}, "
                  f"diff={pct_diff:+.2f}%, "
                  f"orig_time={orig_time:.3f}s, opt_time={opt_time:.3f}s, "
                  f"speedup={orig_time/opt_time:.1f}x")
    
    # Summary statistics
    print("\n=== SUMMARY ===")
    
    for n in sizes:
        n_results = [r for r in results if r['n'] == n]
        avg_diff = np.mean([r['pct_diff'] for r in n_results])
        avg_speedup = np.mean([r['speedup'] for r in n_results])
        print(f"n={n}: avg_diff={avg_diff:+.2f}%, avg_speedup={avg_speedup:.1f}x")
    
    # Overall
    avg_diff_all = np.mean([r['pct_diff'] for r in results])
    avg_speedup_all = np.mean([r['speedup'] for r in results])
    print(f"\nOverall: avg_diff={avg_diff_all:+.2f}%, avg_speedup={avg_speedup_all:.1f}x")
    
    # Count wins/losses
    wins = sum(1 for r in results if r['pct_diff'] < 0)  # optimized better
    losses = sum(1 for r in results if r['pct_diff'] > 0)  # optimized worse
    ties = sum(1 for r in results if abs(r['pct_diff']) < 0.01)  # within 0.01%
    
    print(f"Wins: {wins}, Losses: {losses}, Ties: {ties}")
    
    return results

if __name__ == "__main__":
    test_quality_comparison()
