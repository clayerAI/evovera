#!/usr/bin/env python3
"""
Test tuned v18 (threshold=0.6) at n=500.
"""

import sys
sys.path.append('/workspace/evovera/solutions')

from test_v18_community_tuning import TunedChristofidesCommunityDetection
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import statistics

def test_tuned_v18_n500():
    """Test tuned v18 algorithm at n=500."""
    print("Test: Tuned v18 (threshold=0.6) at n=500")
    print("=" * 70)
    
    seeds = [42, 43, 44]  # Fewer seeds due to computational cost
    n = 500
    
    improvements = []
    v18_times = []
    baseline_times = []
    
    for seed_idx, seed in enumerate(seeds):
        print(f"\nRunning test with seed {seed} (n={n})...")
        random.seed(seed)
        points = [(random.random(), random.random()) for _ in range(n)]
        
        # Get baseline
        print("  Running baseline (NN+2opt)...")
        start = time.time()
        baseline_tour, baseline_length = nn2opt_solve(points)
        baseline_time = time.time() - start
        
        # Test tuned v18
        print("  Running tuned v18 (threshold=0.6)...")
        start = time.time()
        solver = TunedChristofidesCommunityDetection(points, seed=seed, merge_threshold=0.6)
        v18_tour, v18_length, runtime = solver.solve()
        v18_time = time.time() - start
        
        improvement = ((baseline_length - v18_length) / baseline_length) * 100
        
        improvements.append(improvement)
        v18_times.append(v18_time)
        baseline_times.append(baseline_time)
        
        print(f"  Results: Baseline={baseline_length:.4f}, v18={v18_length:.4f}, "
              f"Improvement={improvement:.2f}%")
        print(f"  Times: Baseline={baseline_time:.2f}s, v18={v18_time:.2f}s")
    
    # Calculate statistics
    avg_improvement = statistics.mean(improvements)
    std_improvement = statistics.stdev(improvements) if len(improvements) > 1 else 0
    avg_v18_time = statistics.mean(v18_times)
    avg_baseline_time = statistics.mean(baseline_times)
    
    positive_count = sum(1 for imp in improvements if imp > 0)
    above_threshold_count = sum(1 for imp in improvements if imp > 0.1)
    
    print(f"\n{'='*70}")
    print(f"SUMMARY for n={500} (tuned v18, threshold=0.6):")
    print(f"  Average improvement: {avg_improvement:.2f}% ± {std_improvement:.2f}%")
    print(f"  Range: {min(improvements):.2f}% to {max(improvements):.2f}%")
    print(f"  Positive improvements: {positive_count}/{len(seeds)}")
    print(f"  Above 0.1% threshold: {above_threshold_count}/{len(seeds)}")
    print(f"  Time: v18={avg_v18_time:.2f}s, baseline={avg_baseline_time:.2f}s")
    
    if avg_improvement > 0.1:
        print(f"  ✅ Exceeds 0.1% publication threshold")
    elif avg_improvement > 0:
        print(f"  ⚠️  Positive but below threshold")
    else:
        print(f"  ❌ Worse than baseline")
    
    # Compare with original v18
    print(f"\nComparison with original v18 (threshold=0.5):")
    print(f"  Original: -0.16% average improvement, 1/3 above threshold")
    print(f"  Tuned: {avg_improvement:.2f}% average improvement, {above_threshold_count}/{len(seeds)} above threshold")

if __name__ == "__main__":
    test_tuned_v18_n500()