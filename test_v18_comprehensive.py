#!/usr/bin/env python3
"""
Comprehensive test for v18 Christofides with Community Detection.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import solve_tsp as v18_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import statistics

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_v18_comprehensive():
    """Comprehensive test of v18 algorithm."""
    print("Comprehensive Test: v18 Christofides with Community Detection")
    print("=" * 70)
    
    test_cases = [
        {'n': 30, 'seeds': [42, 43, 44, 45, 46], 'name': 'small'},
        {'n': 50, 'seeds': [42, 43, 44, 45, 46], 'name': 'medium'},
        {'n': 75, 'seeds': [42, 43, 44, 45, 46], 'name': 'large'},
        {'n': 100, 'seeds': [42, 43, 44], 'name': 'xlarge'},
    ]
    
    results_summary = {}
    
    for test_case in test_cases:
        n = test_case['n']
        seeds = test_case['seeds']
        name = test_case['name']
        
        print(f"\nTesting {name} (n={n}) with {len(seeds)} seeds:")
        print("-" * 40)
        
        improvements = []
        v18_times = []
        baseline_times = []
        
        for seed_idx, seed in enumerate(seeds):
            points = generate_random_points(n=n, seed=seed)
            
            # Get baseline
            start = time.time()
            baseline_tour, baseline_length = nn2opt_solve(points)
            baseline_time = time.time() - start
            
            # Test v18
            start = time.time()
            v18_tour, v18_length = v18_solve(points, seed=seed)
            v18_time = time.time() - start
            
            improvement = ((baseline_length - v18_length) / baseline_length) * 100
            
            improvements.append(improvement)
            v18_times.append(v18_time)
            baseline_times.append(baseline_time)
            
            print(f"  Seed {seed}: Baseline={baseline_length:.4f}, v18={v18_length:.4f}, "
                  f"Improvement={improvement:.2f}%")
        
        # Calculate statistics
        avg_improvement = statistics.mean(improvements)
        std_improvement = statistics.stdev(improvements) if len(improvements) > 1 else 0
        avg_v18_time = statistics.mean(v18_times)
        avg_baseline_time = statistics.mean(baseline_times)
        
        positive_count = sum(1 for imp in improvements if imp > 0)
        above_threshold_count = sum(1 for imp in improvements if imp > 0.1)
        
        print(f"\n  Summary for n={n}:")
        print(f"    Average improvement: {avg_improvement:.2f}% ± {std_improvement:.2f}%")
        print(f"    Range: {min(improvements):.2f}% to {max(improvements):.2f}%")
        print(f"    Positive improvements: {positive_count}/{len(seeds)}")
        print(f"    Above 0.1% threshold: {above_threshold_count}/{len(seeds)}")
        print(f"    Time: v18={avg_v18_time:.3f}s, baseline={avg_baseline_time:.3f}s")
        
        if avg_improvement > 0.1:
            print(f"    ✅ Exceeds 0.1% publication threshold (avg)")
        elif avg_improvement > 0:
            print(f"    ⚠️  Positive but below threshold (avg)")
        else:
            print(f"    ❌ Worse than baseline (avg)")
        
        results_summary[n] = {
            'avg_improvement': avg_improvement,
            'std_improvement': std_improvement,
            'improvements': improvements,
            'avg_v18_time': avg_v18_time,
            'avg_baseline_time': avg_baseline_time,
            'positive_count': positive_count,
            'above_threshold_count': above_threshold_count
        }
    
    # Overall assessment
    print(f"\n{'='*70}")
    print("OVERALL ASSESSMENT:")
    
    all_improvements = []
    for n, data in results_summary.items():
        all_improvements.extend(data['improvements'])
    
    overall_avg = statistics.mean(all_improvements)
    overall_positive = sum(1 for imp in all_improvements if imp > 0)
    overall_above_threshold = sum(1 for imp in all_improvements if imp > 0.1)
    total_tests = len(all_improvements)
    
    print(f"  Total tests: {total_tests}")
    print(f"  Overall average improvement: {overall_avg:.2f}%")
    print(f"  Positive improvements: {overall_positive}/{total_tests} ({overall_positive/total_tests*100:.1f}%)")
    print(f"  Above 0.1% threshold: {overall_above_threshold}/{total_tests} ({overall_above_threshold/total_tests*100:.1f}%)")
    
    if overall_avg > 0.1 and overall_above_threshold / total_tests >= 0.8:
        print(f"  ✅ STRONG CANDIDATE: Consistently exceeds publication threshold")
    elif overall_avg > 0.1:
        print(f"  ⚠️  MODERATE CANDIDATE: Exceeds threshold on average but inconsistent")
    elif overall_avg > 0:
        print(f"  ⚠️  WEAK CANDIDATE: Positive but below threshold")
    else:
        print(f"  ❌ REJECT: Worse than baseline")
    
    return results_summary

if __name__ == "__main__":
    results = test_v18_comprehensive()