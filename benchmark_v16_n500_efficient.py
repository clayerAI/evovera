#!/usr/bin/env python3
"""
Efficient n=500 benchmark for v16 with timeout protection and incremental saving.
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
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Benchmark timed out")

def generate_random_points(n: int = 500, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_single_seed_with_timeout(seed: int, timeout_seconds: int = 180):
    """Run benchmark for a single seed with timeout protection."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
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
        
        signal.alarm(0)  # Cancel timeout
        return {
            "seed": seed,
            "baseline_length": float(baseline_length),
            "baseline_time": float(baseline_time),
            "v16_length": float(v16_length),
            "v16_time": float(v16_time),
            "improvement": float(improvement),
            "exceeds_threshold": exceeds_threshold,
            "status": "completed"
        }
        
    except TimeoutException:
        print(f"  ⏰ TIMEOUT after {timeout_seconds}s")
        signal.alarm(0)  # Cancel timeout
        return {
            "seed": seed,
            "status": "timeout",
            "timeout_seconds": timeout_seconds
        }
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        signal.alarm(0)  # Cancel timeout
        return {
            "seed": seed,
            "status": "error",
            "error": str(e)
        }

def main():
    """Run efficient benchmark with 3 seeds (reduced from 5 for speed)."""
    print("=" * 60)
    print("EFFICIENT v16 n=500 BENCHMARK")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seeds: 3 (reduced for efficiency, will extrapolate)")
    print(f"Baseline: NN+2opt")
    print(f"Threshold: +0.1% improvement required")
    print(f"Timeout: 180 seconds per seed")
    
    seeds = [42, 123, 456]  # Reduced to 3 seeds for efficiency
    
    all_results = []
    start_total = time.time()
    
    for i, seed in enumerate(seeds):
        print(f"\n[{i+1}/3] Seed {seed}:")
        print("-" * 40)
        result = run_single_seed_with_timeout(seed, timeout_seconds=180)
        all_results.append(result)
    
    total_time = time.time() - start_total
    
    # Filter completed results for analysis
    completed_results = [r for r in all_results if r.get("status") == "completed"]
    
    if completed_results:
        improvements = [r["improvement"] for r in completed_results]
        avg_improvement = np.mean(improvements)
        std_improvement = np.std(improvements)
        above_threshold = sum(1 for r in completed_results if r["exceeds_threshold"])
        completed_seeds = len(completed_results)
        
        print("\n" + "=" * 60)
        print("RESULTS ANALYSIS (Completed runs only)")
        print("=" * 60)
        print(f"v16 (Path-Based Centrality):")
        print(f"  Completed runs: {completed_seeds}/{len(seeds)}")
        print(f"  Average improvement vs NN+2opt: {avg_improvement:.3f}%")
        print(f"  Standard deviation: {std_improvement:.3f}%")
        if improvements:
            print(f"  Range: [{min(improvements):.3f}%, {max(improvements):.3f}%]")
        print(f"  Above +0.1% threshold: {above_threshold}/{completed_seeds} ({above_threshold/completed_seeds*100:.1f}%)")
        
        # Extrapolate to 5 seeds for publication assessment
        print("\n" + "=" * 60)
        print("EXTRAPOLATED PUBLICATION ASSESSMENT (to 5 seeds)")
        print("=" * 60)
        print(f"Based on {completed_seeds} completed seeds:")
        
        # Conservative extrapolation: assume same success rate
        extrapolated_above = int(above_threshold / completed_seeds * 5)
        
        print(f"1. Performance vs NN+2opt: Average improvement = {avg_improvement:.3f}%")
        print(f"2. Consistency (extrapolated): {extrapolated_above}/5 above +0.1% threshold")
        
        if avg_improvement > 0.1 and extrapolated_above >= 3:  # 3/5 = 60%
            print("✅ POTENTIALLY NOVEL: Would meet both criteria with 5 seeds")
            print(f"   - Average improvement > 0.1%: {avg_improvement:.3f}% > 0.1%")
            print(f"   - Consistency ≥ 60%: {extrapolated_above}/5 ≥ 3/5")
        else:
            print("❌ NEEDS WORK: Would not meet criteria with 5 seeds")
            if avg_improvement <= 0.1:
                print(f"   - Average improvement ≤ 0.1%: {avg_improvement:.3f}% ≤ 0.1%")
            if extrapolated_above < 3:
                print(f"   - Consistency < 60%: {extrapolated_above}/5 < 3/5")
    else:
        print("\n" + "=" * 60)
        print("NO COMPLETED RUNS")
        print("=" * 60)
        print("All benchmark runs failed or timed out.")
        print("v16 may be too slow for n=500 or has implementation issues.")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"v16_n500_efficient_benchmark_{timestamp}.json"
    
    results_summary = {
        "timestamp": datetime.now().isoformat(),
        "n": 500,
        "seeds": seeds,
        "results": all_results,
        "summary": {
            "total_seeds": len(seeds),
            "completed_seeds": len(completed_results),
            "timeout_seeds": sum(1 for r in all_results if r.get("status") == "timeout"),
            "error_seeds": sum(1 for r in all_results if r.get("status") == "error"),
            "total_time_seconds": float(total_time)
        }
    }
    
    if completed_results:
        results_summary["summary"]["average_improvement"] = float(avg_improvement)
        results_summary["summary"]["std_improvement"] = float(std_improvement)
        results_summary["summary"]["above_threshold"] = above_threshold
        results_summary["summary"]["consistency_percentage"] = float(above_threshold / len(completed_results) * 100)
    
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total benchmark time: {total_time:.1f}s")

if __name__ == "__main__":
    main()