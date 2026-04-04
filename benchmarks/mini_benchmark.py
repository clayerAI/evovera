#!/usr/bin/env python3
"""
Mini benchmark with just 3 seeds to test the methodology.
"""

import sys
import os
import time
import random
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import algorithms
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as christofides_structural_solve

def generate_random_points(n, seed=None):
    """Generate random points in unit square."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

print("=" * 60)
print("MINI BENCHMARK (n=30, 3 seeds)")
print("=" * 60)

n = 30
seeds = [42, 43, 44]  # Just 3 seeds for quick test
algorithms = [
    ('NN+2opt (v1)', nn_solve),
    ('Christofides Structural (v19)', christofides_structural_solve)
]

results = {name: [] for name, _ in algorithms}

for seed in seeds:
    print(f"\nSeed {seed}:")
    points = generate_random_points(n, seed)
    
    for algo_name, algo_func in algorithms:
        start_time = time.time()
        try:
            tour, distance = algo_func(points)
            end_time = time.time()
            results[algo_name].append(distance)
            print(f"  {algo_name}: {distance:.3f} ({end_time-start_time:.2f}s)")
        except Exception as e:
            print(f"  {algo_name}: ERROR - {e}")
            results[algo_name].append(None)

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

# Calculate statistics
baseline_results = [r for r in results['NN+2opt (v1)'] if r is not None]
v19_results = [r for r in results['Christofides Structural (v19)'] if r is not None]

if baseline_results and v19_results:
    baseline_mean = np.mean(baseline_results)
    v19_mean = np.mean(v19_results)
    
    improvement = ((baseline_mean - v19_mean) / baseline_mean) * 100
    
    print(f"\nBaseline (NN+2opt): {baseline_mean:.3f} (mean of {len(baseline_results)} runs)")
    print(f"v19 (Christofides Structural): {v19_mean:.3f} (mean of {len(v19_results)} runs)")
    print(f"Improvement: {improvement:+.2f}%")
    
    # Count wins
    wins = sum(1 for b, v in zip(baseline_results, v19_results) if v < b)
    losses = sum(1 for b, v in zip(baseline_results, v19_results) if v > b)
    ties = len(baseline_results) - wins - losses
    
    print(f"\nWins/Losses/Ties: {wins}/{losses}/{ties}")
    
    if wins == 3:
        print("PRELIMINARY: All 3 seeds show improvement (promising)")
    elif wins >= 2:
        print("PRELIMINARY: Majority show improvement (needs more seeds)")
    else:
        print("PRELIMINARY: No consistent improvement")
else:
    print("\nERROR: Missing results")

print("\n" + "=" * 60)
print("NOTE: This is a mini benchmark with only 3 seeds.")
print("Full validation requires ≥10 seeds for statistical significance.")
print("=" * 60)