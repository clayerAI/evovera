#!/usr/bin/env python3
"""
Comprehensive n=500 benchmark for v16 (Christofides with Path-Based Centrality).
Uses 5 seeds matching Vera's publication criteria.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import json
import numpy as np
from datetime import datetime

def generate_random_points(n: int = 500, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_benchmark_seed(seed: int):
    """Run benchmark for a single seed."""
    print(f"\nSeed {seed}:")
    print("-" * 40)
    
    points = generate_random_points(n=500, seed=seed)
    
    # Get baseline (NN+2opt)
    start = time.time()
    baseline_tour, baseline_length = nn2opt_solve(points)
    baseline_time = time.time() - start
    
    # Test v16 with optimized parameters
    start = time.time()
    solver = ChristofidesPathCentrality(points, seed=seed)
    # Use adaptive weight: 0.7 for n=500 based on previous optimization
    v16_tour, v16_length, _ = solver.solve(centrality_weight=0.7, apply_2opt=True)
    v16_time = time.time() - start
    
    improvement = ((baseline_length - v16_length) / baseline_length) * 100
    exceeds_threshold = improvement > 0.1
    
    print(f"  Baseline (NN+2opt): {baseline_length:.4f} ({baseline_time:.1f}s)")
    print(f"  v16:                {v16_length:.4f} ({v16_time:.1f}s)")
    print(f"  Improvement:        {improvement:.2f}%")
    print(f"  Status:             {'✅ Exceeds 0.1% threshold' if exceeds_threshold else '❌ Below threshold'}")
    
    return {
        "seed": seed,
        "baseline_length": float(baseline_length),
        "baseline_time": float(baseline_time),
        "v16_length": float(v16_length),
        "v16_time": float(v16_time),
        "improvement": float(improvement),
        "exceeds_threshold": exceeds_threshold
    }

def main():
    """Run comprehensive benchmark with 5 seeds."""
    print("=" * 60)
    print("COMPREHENSIVE v16 n=500 BENCHMARK")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seeds: 5 (matching Vera's publication criteria)")
    print(f"Baseline: NN+2opt")
    print(f"Threshold: +0.1% improvement required")
    
    seeds = [42, 123, 456, 789, 1011]  # Same seeds used for v19 benchmark
    
    all_results = []
    start_total = time.time()
    
    for i, seed in enumerate(seeds):
        print(f"\n[{i+1}/5] ", end="")
        result = run_benchmark_seed(seed)
        all_results.append(result)
    
    total_time = time.time() - start_total
    
    # Analysis
    improvements = [r["improvement"] for r in all_results]
    avg_improvement = np.mean(improvements)
    std_improvement = np.std(improvements)
    above_threshold = sum(1 for r in all_results if r["exceeds_threshold"])
    total_seeds = len(all_results)
    
    print("\n" + "=" * 60)
    print("RESULTS ANALYSIS")
    print("=" * 60)
    print(f"v16 (Path-Based Centrality):")
    print(f"  Average improvement vs NN+2opt: {avg_improvement:.3f}%")
    print(f"  Standard deviation: {std_improvement:.3f}%")
    print(f"  Range: [{min(improvements):.3f}%, {max(improvements):.3f}%]")
    print(f"  Above +0.1% threshold: {above_threshold}/{total_seeds} ({above_threshold/total_seeds*100:.1f}%)")
    print(f"  Below -0.1% threshold: {sum(1 for imp in improvements if imp < -0.1)}/{total_seeds}")
    print(f"  Within ±0.1%: {sum(1 for imp in improvements if -0.1 <= imp <= 0.1)}/{total_seeds}")
    
    # Publication assessment
    print("\n" + "=" * 60)
    print("PUBLICATION ASSESSMENT (Vera's Criteria)")
    print("=" * 60)
    print(f"1. Performance vs NN+2opt: Average improvement = {avg_improvement:.3f}%")
    print(f"2. Consistency: {above_threshold}/{total_seeds} above +0.1% threshold ({above_threshold/total_seeds*100:.1f}%)")
    
    if avg_improvement > 0.1 and above_threshold >= total_seeds * 0.5:
        print("✅ POTENTIALLY NOVEL: Meets both criteria")
        print(f"   - Average improvement > 0.1%: {avg_improvement:.3f}% > 0.1%")
        print(f"   - Consistency ≥ 50%: {above_threshold/total_seeds*100:.1f}% ≥ 50%")
    else:
        print("❌ NEEDS WORK: Does not meet criteria")
        if avg_improvement <= 0.1:
            print(f"   - Average improvement ≤ 0.1%: {avg_improvement:.3f}% ≤ 0.1%")
        if above_threshold < total_seeds * 0.5:
            print(f"   - Consistency < 50%: {above_threshold/total_seeds*100:.1f}% < 50%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"v16_n500_comprehensive_benchmark_{timestamp}.json"
    
    results_summary = {
        "timestamp": datetime.now().isoformat(),
        "n": 500,
        "seeds": seeds,
        "results": all_results,
        "summary": {
            "average_improvement": float(avg_improvement),
            "std_improvement": float(std_improvement),
            "min_improvement": float(min(improvements)),
            "max_improvement": float(max(improvements)),
            "above_threshold": above_threshold,
            "total_seeds": total_seeds,
            "consistency_percentage": float(above_threshold / total_seeds * 100),
            "total_time_seconds": float(total_time)
        },
        "publication_assessment": {
            "meets_performance_criterion": avg_improvement > 0.1,
            "meets_consistency_criterion": above_threshold >= total_seeds * 0.5,
            "potentially_novel": avg_improvement > 0.1 and above_threshold >= total_seeds * 0.5
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total benchmark time: {total_time:.1f}s")

if __name__ == "__main__":
    main()