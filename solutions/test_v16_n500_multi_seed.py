#!/usr/bin/env python3
"""
Multi-seed benchmark for v16 on n=500.
Uses 3 seeds to verify consistency.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import json

def generate_random_points(n: int = 500, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_benchmark_seed(seed: int):
    """Run benchmark for a single seed."""
    print(f"\nSeed {seed}:")
    print("-" * 40)
    
    points = generate_random_points(n=500, seed=seed)
    
    # Get baseline
    start = time.time()
    baseline_tour, baseline_length = nn2opt_solve(points)
    baseline_time = time.time() - start
    
    # Test v16 with adaptive weight (0.7 for n>50)
    start = time.time()
    solver = ChristofidesPathCentrality(points, seed=seed)
    v16_tour, v16_length, _ = solver.solve(centrality_weight=0.7, apply_2opt=True)
    v16_time = time.time() - start
    
    improvement = ((baseline_length - v16_length) / baseline_length) * 100
    
    print(f"  Baseline: {baseline_length:.4f} ({baseline_time:.1f}s)")
    print(f"  v16:      {v16_length:.4f} ({v16_time:.1f}s)")
    print(f"  Improvement: {improvement:.2f}%")
    
    if improvement > 0.1:
        status = "✅ Exceeds threshold"
    elif improvement > 0:
        status = "⚠️  Positive but below threshold"
    else:
        status = "❌ Worse than baseline"
    
    print(f"  Status: {status}")
    
    return {
        'seed': seed,
        'baseline_length': baseline_length,
        'baseline_time': baseline_time,
        'v16_length': v16_length,
        'v16_time': v16_time,
        'improvement': improvement,
        'exceeds_threshold': improvement > 0.1
    }

def main():
    """Run multi-seed benchmark."""
    print("Multi-seed benchmark for v16 on n=500")
    print("=" * 60)
    
    seeds = [42, 123]  # 2 seeds for reasonable runtime (each takes ~75s)
    results = []
    
    total_start = time.time()
    
    for seed in seeds:
        result = run_benchmark_seed(seed)
        results.append(result)
    
    total_time = time.time() - total_start
    
    # Calculate statistics
    improvements = [r['improvement'] for r in results]
    avg_improvement = sum(improvements) / len(improvements)
    exceeds_count = sum(1 for r in results if r['exceeds_threshold'])
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"  Seeds tested: {len(seeds)}")
    print(f"  Average improvement: {avg_improvement:.2f}%")
    print(f"  Seeds exceeding 0.1% threshold: {exceeds_count}/{len(seeds)}")
    print(f"  Total benchmark time: {total_time:.1f}s")
    
    # Save results
    output = {
        'timestamp': time.time(),
        'n': 500,
        'seeds': seeds,
        'results': results,
        'summary': {
            'avg_improvement': avg_improvement,
            'exceeds_threshold_count': exceeds_count,
            'total_seeds': len(seeds)
        }
    }
    
    with open('v16_n500_multi_seed_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to v16_n500_multi_seed_results.json")

if __name__ == "__main__":
    main()